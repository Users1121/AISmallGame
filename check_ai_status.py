import httpx
import json

try:
    response = httpx.get("http://localhost:8000/game/debug/ai-status")
    print("状态码:", response.status_code)
    print("\nAI 状态:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")