import httpx

api_key = "sk-79a82c1787b14b23820fa96ea8f47800"
api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 测试当前代码使用的格式（错误格式）
print("测试当前格式:")
try:
    response = httpx.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个测试助手。"},
                    {"role": "user", "content": "你好"}
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        },
        timeout=30.0
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*50 + "\n")

# 测试正确的格式
print("测试正确格式:")
correct_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
try:
    response = httpx.post(
        correct_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen-turbo",
            "messages": [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "你好"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        },
        timeout=30.0
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")