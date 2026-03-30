import httpx
import json

def test_chat(nation_id, message):
    print(f"\n{'='*50}")
    print(f"测试与 {nation_id} 聊天")
    print(f"消息: {message}")
    print(f"{'='*50}")
    
    try:
        response = httpx.post(
            f"http://localhost:8000/game/chat/{nation_id}",
            json={"content": message, "sender": "player"},
            timeout=30.0
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nAI 回复:")
            print(result.get("response", "无回复"))
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"异常: {e}")

test_messages = [
    ("nation_a", "你好，DeepSeek！"),
    ("nation_b", "你好，阿里云！"),
    ("nation_c", "你好，Kimi！"),
    ("nation_a", "你的治理理念是什么？"),
    ("nation_b", "你如何看待其他国家的存在？"),
    ("nation_c", "你的信仰是什么？"),
]

for nation_id, message in test_messages:
    test_chat(nation_id, message)

print(f"\n{'='*50}")
print("测试完成")
print(f"{'='*50}")