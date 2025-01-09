import hmac
import hashlib
import base64
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode

import time
import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import pickle
import json
import chardet
import numpy as np

from sparkai.embedding.spark_embedding import Embeddingmodel, SparkEmbeddingFunction
import chromadb


# 加载配置文件
from pathlib import Path
# config_path = Path("../../../../llm_config.json")
config_path = Path("../../llm_config.json")
with open(config_path, "r") as f:
    llm_config = json.load(f) 

class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    # print(u.host,u.path)
    return u


# 生成鉴权url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # print(authorization_origin)
    values = {
        "authorization": authorization,
        "date": date,
        "host": host,
    }
    auth_url = requset_url + "?" + urlencode(values)
    # print(auth_url)

    return auth_url


def get_Body(appid,text,style):
    """
    style参数注解:
    特性标识	     特性描述	     数据类型
    domain=query	用户问题向量化	string
    domain=para	    知识原文向量化	string
    """
    # org_content = json.dumps(text).encode('utf-8')
    # print(org_content)
    body= {
    "header": {
        "app_id": appid,
        "status": 3
    },
    "parameter": {
        "emb": {
            "domain": style,
            "feature": {
                "encoding": "utf8"
            }
        }
    },
    "payload": {
        "messages": {
            "text": base64.b64encode(json.dumps(text).encode('utf-8')).decode()
        }
    }
    }
    return body

# desc = {"messages":[{"content":"cc","role":"user"}]}
def convet_text_to_dict(text):
    dtext = {}
    dtext["content"]=text
    dtext["role"]="user"
    return dtext


def convet_dict_to_message(msg):
    demessage = {}
    demessage["messages"] = [msg]
    return demessage


# 发起请求并返回结果（通过style设置获取的类型）
def get_embqp_embedding(text,appid,apikey,apisecret, style):
    host = llm_config["embeddings"]
    url = assemble_ws_auth_url(host,method='POST',api_key=apikey,api_secret=apisecret)
    text = convet_text_to_dict(text)
    text = convet_dict_to_message(text)
    # print("传入的message:",text)
    content = get_Body(appid,text,style) # style指定向量化的类型
    # print(time.time())
    response = requests.post(url,json=content,headers={'content-type': "application/json"}).text
    # print("请求结果：",response)
    # print(time.time())
    return response


# 解析结果并输出
def parser_Message(message):
    data = json.loads(message)
    # print("data" + str(message))
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        return []
    else:
        sid = data['header']['sid']
        # print("本次会话的id为：" + sid)
        text_base = data["payload"]["feature"]["text"]
        # 使用base64.b64decode()函数将text_base解码为字节串text_data
        text_data = base64.b64decode(text_base)
        # 创建一个np.float32类型的数据类型对象dt，表示32位浮点数。
        dt = np.dtype(np.float32)
        # 使用newbyteorder()方法将dt的字节序设置为小端（"<"）
        dt = dt.newbyteorder("<")
        # 使用np.frombuffer()函数将text_data转换为浮点数数组text，数据类型为dt。
        text = np.frombuffer(text_data, dtype=dt)

        return text.tolist()
    
# 复合函数以便其他调用
def get_sparkai_embedding(text,style="para"):
    APPID =llm_config["sparkai-app-id"]
    APIKEY = llm_config["sparkai-api-key"]
    APISecret = llm_config["sparkai-api-secret"]
    res = get_embqp_embedding(text=text,appid=APPID,apikey=APIKEY,apisecret=APISecret,style=style)
    return parser_Message(res)


if __name__ == '__main__':
    #运行前请配置以下鉴权三要素，获取途径：https://console.xfyun.cn/services/bm3
    APPID =llm_config["sparkai-app-id"]
    APIKEY = llm_config["sparkai-api-key"]
    APISecret = llm_config["sparkai-api-secret"]
    # desc = {"messages":[{"content":"refrigerator is idle","role":"user"}]}
    desc = "refrigerator is idle"
    # 当上传文档时 ，需要将文本切分为多块，然后将切分的chunk 填充到上面的content中
    # get_embqp_embedding   是将文本、知识库内容进行向量化的服务
    res = get_embqp_embedding(text=desc,appid=APPID,apikey=APIKEY,apisecret=APISecret,style="para")
    text = parser_Message(res)
    print("返回的向量化数组为:")
    print(text)
    print("向量维度为：",len(text))


def test_embedding():
    model = Embeddingmodel(
        spark_embedding_app_id="eac29dad",
        spark_embedding_api_key="9d4ccbbc9701104f467d8bc533032ce3",
        spark_embedding_api_secret="N2QzNDg0ODEwZjA5MTVhYzAyZjIzNmQ0",
        spark_embedding_domain="query",
    )
    # desc = {"messages":[{"content":"cc","role":"user"}]}
    desc = {"content": "closet is idle", "role": "user"}
    # 调用embedding方法
    a = model.embedding(text=desc, kind='text')
    print("向量维度为：",len(a))
    print(a)


def test_chroma_embedding():
    chroma_client = chromadb.Client()
    sparkmodel = SparkEmbeddingFunction(
        spark_embedding_app_id="eac29dad",
        spark_embedding_api_key="9d4ccbbc9701104f467d8bc533032ce3",
        spark_embedding_api_secret="N2QzNDg0ODEwZjA5MTVhYzAyZjIzNmQ0",
        spark_embedding_domain="para",
    )
    a = sparkmodel(["This is a document", "This is another document"])
    # print(type(a))
    # print(a[0])
    # print(a[0][1])
    # 可以正确的生成embedding结果
    collection = chroma_client.get_or_create_collection(name="my_collection", embedding_function=sparkmodel)
    # 为什么是None
    collection.add(
        documents=["This is a document", "cc", "1122"],
        metadatas=[{"source": "my_source"}, {"source": "my_source"}, {"source": "my_source"}],
        ids=["id1", "id2", "id3"]
    )
    # print(collection.peek())  #显示前五条数据
    print(collection.count())  # 数据库中数据量
    results = collection.query(
        query_texts=["ac", 'documents'],
        n_results=2
    )
    print(results)  # 查询结果


# if __name__ == "__main__":
#     test_embedding()
#     # test_chroma_embedding()