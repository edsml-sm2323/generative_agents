"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""
import time 
import json
from pathlib import Path
from openai import AzureOpenAI, OpenAI
import json
from pathlib import Path
from openai import AzureOpenAI, OpenAI

from global_methods import clean_json_tags
from utils import *
from openai_cost_logger import DEFAULT_LOG_PATH
from persona.prompt_template.openai_logger_singleton import OpenAICostLogger_Singleton

# import星火大模型
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
# import星火的嵌入api
from persona.prompt_template.sparkai_embedding import get_sparkai_embedding
from sparkai.embedding.spark_embedding import Embeddingmodel

# # 设置代理环境变量,以便VPN起作用
# import os
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

config_path = Path("../../llm_config.json")
with open(config_path, "r") as f:
    llm_config = json.load(f) 

def setup_client(type: str, config: dict):
  """Setup the OpenAI client.

  Args:
      type (str): the type of client. Either "azure" or "openai".
      config (dict): the configuration for the client.

  Raises:
      ValueError: if the client is invalid.

  Returns:
      The client object created, either AzureOpenAI or OpenAI.
  """
  if type == "azure":
    client = AzureOpenAI(
        azure_endpoint=config["endpoint"],
        api_key=config["key"],
        api_version=config["api-version"],
    )
  elif type == "openai":
    client = OpenAI(
        api_key=config["key"],
    )
  elif type == "sparkai":
    # client=ChatSparkLLM(
    #   spark_api_url=config["sparkai-url"],
    #   spark_app_id=config["sparkai-app-id"],
    #   spark_api_key=config["sparkai-api-key"],
    #   spark_api_secret=config["sparkai-api-secret"],
    #   spark_llm_domain=config["sparkai-domin"],
    #   streaming=False,
    # )
        # 控制台获取key和secret拼接，假使控制台获取的APIPassword是123456
    client = OpenAI(
        api_key = config["key"],
        base_url = config["url"] # 指向讯飞星火的请求地址
    )
  else:
    raise ValueError("Invalid client")
  return client

# 设置 OpenAI 客户端
if llm_config["client"] == "azure":
    client = setup_client("azure", {
        "endpoint": llm_config["model-endpoint"],
        "key": llm_config["model-key"],
        "api-version": llm_config["model-api-version"],
    })
elif llm_config["client"] == "openai":
    client = setup_client("openai", {"key": llm_config["model-key"]})
elif llm_config["client"] == "sparkai":
    # client = setup_client("sparkai", {
    #     "sparkai-url":llm_config["sparkai-url"],
    #     "sparkai-app-id":llm_config["sparkai-app-id"],
    #     "sparkai-api-key":llm_config["sparkai-api-key"],
    #     "sparkai-api-secret":llm_config["sparkai-api-secret"],
    #     "sparkai-domin":llm_config["sparkai-domin"],
    # })
    client = setup_client("sparkai", {"key": llm_config["sparkai-apipassword"],
                                      "url":llm_config["sparkai-openai-url"]})
else:
    raise ValueError("Invalid client type")

# 设置嵌入客户端（如果有）
if llm_config["embeddings-client"] == "azure":  
    embeddings_client = setup_client("azure", {
        "endpoint": llm_config["embeddings-endpoint"],
        "key": llm_config["embeddings-key"],
        "api-version": llm_config["embeddings-api-version"],
    })
elif llm_config["embeddings-client"] == "openai":
    embeddings_client = setup_client("openai", {"key": llm_config["embeddings-key"]})
elif llm_config["client"] == "sparkai": # 这部分星火的嵌入API没有client调用形式,后续更改get_embedding
    # embeddings_client = None
    embeddings_client = Embeddingmodel(
        spark_embedding_app_id=llm_config["sparkai-app-id"],
        spark_embedding_api_key=llm_config["sparkai-api-key"],
        spark_embedding_api_secret=llm_config["sparkai-api-secret"],
        spark_embedding_domain="para", # 可选值qurey和para
    )
else:
    raise ValueError("Invalid embeddings client")

cost_logger = OpenAICostLogger_Singleton(
  experiment_name = llm_config["experiment-name"],
  log_folder = DEFAULT_LOG_PATH,
  cost_upperbound = llm_config["cost-upperbound"]
)

def temp_sleep(seconds=0.1):
  time.sleep(seconds)



def ChatGPT_single_request(prompt): 
  temp_sleep()
  completion = client.chat.completions.create(
    model=llm_config["model"],
    messages=[{"role": "user", "content": prompt}]
  )
  cost_logger.update_cost(completion, input_cost=llm_config["model-costs"]["input"], output_cost=llm_config["model-costs"]["output"])
  return completion.choices[0].message.content


def ChatGPT_request(prompt): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  # temp_sleep()
  try: 
    completion = client.chat.completions.create(
    model=llm_config["model"],
    messages=[{"role": "user", "content": prompt}]
    )
    cost_logger.update_cost(completion, input_cost=llm_config["model-costs"]["input"], output_cost=llm_config["model-costs"]["output"])
    return completion.choices[0].message.content

  except Exception as e: 
    print(f"Error: {e}")
    return "ChatGPT ERROR"


def ChatGPT_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
  prompt = '"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 

    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      curr_gpt_response = clean_json_tags(curr_gpt_response)
      print("更改后的gpt输出：",curr_gpt_response)
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]
      
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      
      if verbose: 
        print ("---- repeat count: \n", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass

  return False


def ChatGPT_safe_generate_response_OLD(prompt, 
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 
    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print (f"---- repeat count: {i}")
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass
  print ("FAIL SAFE TRIGGERED") 
  return fail_safe_response


def GPT_request(prompt, gpt_parameter): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  temp_sleep()
  try: 
    messages = [{
      "role": "user", "content": prompt
    }]#这里的role原始项目是system
    response = client.chat.completions.create(
                model=gpt_parameter["engine"],
                messages=messages,
                temperature=gpt_parameter["temperature"],
                max_tokens=gpt_parameter["max_tokens"],
                top_p=gpt_parameter["top_p"],
                frequency_penalty=gpt_parameter["frequency_penalty"],
                presence_penalty=gpt_parameter["presence_penalty"],
                stream=gpt_parameter["stream"],
                stop=gpt_parameter["stop"],)
    cost_logger.update_cost(response=response, input_cost=llm_config["model-costs"]["input"], output_cost=llm_config["model-costs"]["output"])
    return response.choices[0].message.content
  except Exception as e:
    print(f"Error: {e}")
    return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file): 
  """
  Takes in the current input (e.g. comment that you want to classifiy) and 
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this 
  function replaces this substr with the actual curr_input to produce the 
  final promopt that will be sent to the GPT3 server. 
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file. 
  RETURNS: 
    a str prompt that will be sent to OpenAI's GPT server.  
  """
  if type(curr_input) == type("string"): 
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):   
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt: 
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()


def safe_generate_response(prompt, 
                           gpt_parameter,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None,
                           verbose=False): 
  if verbose: 
    print (prompt)

  for i in range(repeat): 
    curr_gpt_response = GPT_request(prompt, gpt_parameter)
    try:
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print ("---- repeat count: ", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")
    except:
      pass
    try:
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print ("---- repeat count: ", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")
    except:
      pass
  return fail_safe_response

# TODO：修复embedding api
def get_embedding(text, model=llm_config["embeddings"]):
  text = text.replace("\n", " ")
  if not text: 
    text = "this is blank"
  # print("嵌入向量化输入：",text)
  # 如果是星火大模型的文本向量化
  if llm_config["embeddings-client"] == "sparkai":
    # version-1
    # response = embeddings_client.embedding(text=text, kind='text')
    # print("嵌入向量化输出：",response)
    # return response

    # version-2
    # for attempt in range(3):
    #   try:
    #       response = embeddings_client.embedding(text=text, kind='text')
    #       return response
    #       break
    #   except ValueError as e:
    #       print(f"Attempt {attempt+1} failed: {e}")
    #       time.sleep(2)  # Wait before retrying

    # version-3
    response = get_sparkai_embedding(text=text,style=llm_config["embeddings-domin"])
    # print("嵌入向量化输出：",response)
    return response
  else:
    response = embeddings_client.embeddings.create(input=[text], model=model)
    cost_logger.update_cost(response=response, input_cost=llm_config["embeddings-costs"]["input"], output_cost=llm_config["embeddings-costs"]["output"])
    return response.data[0].embedding


if __name__ == '__main__':
  gpt_parameter = {"engine": llm_config["model"], "max_tokens": 50, 
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0, 
                   "stop": ['"']}
  curr_input = ["driving to a friend's house"]
  prompt_lib_file = "prompt_template/test_prompt_July5.txt"
  prompt = generate_prompt(curr_input, prompt_lib_file)

  def __func_validate(gpt_response): 
    if len(gpt_response.strip()) <= 1:
      return False
    if len(gpt_response.strip().split(" ")) > 1: 
      return False
    return True
  def __func_clean_up(gpt_response):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  output = safe_generate_response(prompt, 
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

  print (output)


