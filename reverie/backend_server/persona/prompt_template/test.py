import requests
import json

# 设置中转服务的基本URL和API密钥
Baseurl = "https://api.claudeshop.top"
Skey = "sk-Ypf4WUIqVKt8tFbglB4YASiIuo0vYWuLPY5Dx6bpZm7esOio"

# 构建请求的有效载荷
payload = json.dumps({
   "model": "gpt-4o",
   "messages": [
      {
         "role": "system",
         "content": "You are a helpful assistant."
      },
      {
         "role": "user",
         "content": "hello"
      }
   ]
})

# 构建完整的URL和请求头
url = Baseurl + "/v1/chat/completions"
headers = {
   'Accept': 'application/json',
   'Authorization': f'Bearer {Skey}',
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json'
}

# 发起 POST 请求
response = requests.post(url, headers=headers, data=payload)

# 解析返回的 JSON 数据
data = response.json()

# 获取 content 字段的值并打印
content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
print(content)

# import requests
# import json

# # 使用中转链接
# Baseurl = "https://api.claudeshop.top"
# Skey = "sk-Ypf4WUIqVKt8tFbglB4YASiIuo0vYWuLPY5Dx6bpZm7esOio"

# # 输入文本数据
# input_text = "Hello, world!"

# # 请求 payload 数据
# payload = json.dumps({
#    "model": "text-embedding-ada-002",  # 使用适当的模型名称
#    "input": input_text
# })

# # 构建请求的 URL
# url = Baseurl + "/v1/embeddings"

# # 设置请求头
# headers = {
#    'Accept': 'application/json',
#    'Authorization': f'Bearer {Skey}',
#    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
#    'Content-Type': 'application/json'
# }

# # 发送 POST 请求
# response = requests.request("POST", url, headers=headers, data=payload)

# # 解析 JSON 数据为 Python 字典
# data = response.json()

# # 获取嵌入结果
# embedding = data.get('data', [])[0].get('embedding', [])

# print(embedding)
