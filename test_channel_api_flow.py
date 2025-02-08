from app.api.business.channel import create_channel
from app.services.business.channel import ChannelService
from flask import Request, request
from app import create_app
import jwt
import datetime
import json
import time

class MockRequest:
    def __init__(self, json_data, headers=None):
        self._json = json_data
        self.headers = headers or {}
    
    def get_json(self):
        return self._json

def test_api_flow():
    # 创建应用
    app = create_app()
    
    # 1. 准备请求数据
    timestamp = int(time.time())
    data = {
        'name': 'Test Channel',
        'code': f'TEST_CHANNEL_{timestamp}',
        'description': 'This is a test channel'
    }
    print("\n1. 准备的请求数据:")
    print(json.dumps(data, indent=2))
    
    # 2. 准备认证头
    # 生成有效的token
    token_payload = {
        'user_id': 1,
        'username': 'admin',
        'is_admin': True,
        'tenant_id': 1,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(token_payload, 'your-secret-key', algorithm='HS256')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # 3. 模拟请求
    mock_request = MockRequest(data, headers)
    print("\n2. 模拟请求处理:")
    
    with app.test_request_context():
        try:
            # 设置请求上下文
            request.headers = mock_request.headers
            request.get_json = mock_request.get_json
            
            # 调用 API 函数
            response = create_channel()
            if isinstance(response, tuple):
                response_data, status_code = response
                print("\nAPI 响应:")
                print(f"状态码: {status_code}")
                print("响应数据:")
                print(json.dumps(response_data, indent=2))
            else:
                print("\nAPI 响应:")
                print(json.dumps(response.get_json(), indent=2))
            
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print(f"错误类型: {type(e)}")
            import traceback
            print(f"错误堆栈:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_api_flow() 