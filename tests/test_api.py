import os
from dotenv import load_dotenv
from pathlib import Path
import httpx
import json

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

def test_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"DeepSeek API Key: {api_key[:20] if api_key else '未设置'}...")
    
    if not api_key:
        print("❌ DeepSeek API Key 未设置")
        return False
    
    try:
        response = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 50
            },
            timeout=10.0
        )
        print(f"DeepSeek API 状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ DeepSeek API 连接成功")
            return True
        else:
            print(f"❌ DeepSeek API 错误: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ DeepSeek API 异常: {e}")
        return False

def test_aliyun():
    api_key = os.getenv("ALIYUN_API_KEY")
    print(f"\nAliyun API Key: {api_key[:20] if api_key else '未设置'}...")
    
    if not api_key:
        print("❌ Aliyun API Key 未设置")
        return False
    
    try:
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
                    "max_tokens": 50
                }
            },
            timeout=10.0
        )
        print(f"Aliyun API 状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ Aliyun API 连接成功")
            return True
        else:
            print(f"❌ Aliyun API 错误: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Aliyun API 异常: {e}")
        return False

def test_kimi():
    api_key = os.getenv("KIMI_API_KEY")
    print(f"\nKimi API Key: {api_key[:20] if api_key else '未设置'}...")
    
    if not api_key:
        print("❌ Kimi API Key 未设置")
        return False
    
    try:
        response = httpx.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-8k",
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 50
            },
            timeout=10.0
        )
        print(f"Kimi API 状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ Kimi API 连接成功")
            return True
        else:
            print(f"❌ Kimi API 错误: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Kimi API 异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API 连接测试")
    print("=" * 50)
    
    results = {
        "DeepSeek": test_deepseek(),
        "Aliyun": test_aliyun(),
        "Kimi": test_kimi()
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    for name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name}: {status}")