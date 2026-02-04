"""测试登录API"""
import requests
import json

# 测试登录
url = "http://localhost:8001/api/login"
data = {
    "username": "admin",
    "password": "admin123",
    "captcha": "test123"
}

print(f"测试登录API: {url}")
print(f"发送数据: {json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data)
    print(f"\n状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("\n✓ 登录成功！")
        token = response.json()['token']['access_token']
        print(f"Token: {token[:50]}...")
    else:
        print(f"\n✗ 登录失败: {response.json().get('detail', '未知错误')}")
except Exception as e:
    print(f"\n✗ 请求错误: {e}")
