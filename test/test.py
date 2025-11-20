import os

import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("OLLAMA_API_URL")


# 发送 HTTP GET 请求
url = f"{BASE_URL}/api/tags"
response = requests.get(url)

# 检查响应状态码
response.raise_for_status()

# 解析 JSON 数据
data = response.json()

# 提取 .models[].name
names = [model["name"] for model in data.get("models", [])]

# 打印结果
for name in names:
    print(name)
