import httpx
import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

api_key = os.getenv("ALIYUN_API_KEY")

print("测试 Aliyun API 响应格式...")
print("="*50)

response = httpx.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "qwen-turbo",
        "input": {
            "messages": [{"role": "user", "content": "你好"}]
        },
        "parameters": {
            "max_tokens": 100
        }
    },
    timeout=30.0
)

print(f"状态码: {response.status_code}")
print(f"\n完整响应:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))