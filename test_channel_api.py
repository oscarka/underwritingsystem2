import requests
import json

def login():
    """登录获取token"""
    url = "http://localhost:3002/api/auth/login"
    data = {
        "username": "admin",  # 替换为您的用户名
        "password": "admin123"  # 替换为您的密码
    }
    
    print("\n发送登录请求...")
    print("请求数据:", json.dumps(data, ensure_ascii=False, indent=2))
    
    response = requests.post(url, json=data)
    
    print("\n登录状态码:", response.status_code)
    print("登录响应:", json.dumps(response.json(), ensure_ascii=False, indent=2))
    
    return response

def test_create_channel():
    # 登录获取token
    login_response = login()
    token = login_response.json()['data']['token']
    print(f'Login response status code: {login_response.status_code}')
    print(f'Login response data: {login_response.json()}')

    # 创建渠道
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': 'Test Channel',
        'code': 'TEST_CHANNEL',
        'description': 'This is a test channel'
    }
    print(f'\n发送创建渠道请求...')
    print(f'请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}')
    print(f'请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}')
    
    response = requests.post(
        'http://localhost:3002/api/v1/business/channels',
        headers=headers,
        json=data
    )
    print(f'Create channel response status code: {response.status_code}')
    print(f'Create channel response data: {response.json()}')
    return response

if __name__ == "__main__":
    test_create_channel() 