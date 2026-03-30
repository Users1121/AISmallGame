import httpx

api_key = "sk-79a82c1787b14b23820fa96ea8f47800"
api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

print("测试修复后的阿里云API:")
try:
    response = httpx.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen-turbo",
            "messages": [
                {"role": "system", "content": "你是一个末日生存游戏的AI领导人，崇尚武力与征服。"},
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "temperature": 0.8,
            "max_tokens": 300
        },
        timeout=30.0
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        print(f"回复内容: {reply}")
    else:
        print(f"错误响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")