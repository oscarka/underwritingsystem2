from app.models.business.channel import Channel
from app.services.business.channel import ChannelService
from app.extensions import db

def test_channel_flow():
    # 1. 准备数据
    data = {
        'name': 'Test Channel',
        'code': 'TEST_CHANNEL',
        'description': 'This is a test channel'
    }
    print("\n1. 准备的数据:")
    print(data)
    
    # 2. 服务层处理
    service = ChannelService()
    print("\n2. 服务层处理:")
    try:
        # 打印过滤后的数据
        channel_data = {k: v for k, v in data.items() if v is not None}
        print("过滤后的数据:", channel_data)
        
        # 创建实例
        channel = Channel(**channel_data)
        print("\n创建的实例属性:")
        print(f"name: {channel.name}")
        print(f"code: {channel.code}")
        print(f"description: {channel.description}")
        print(f"status: {channel.status}")
        
        # 转换为字典
        channel_dict = channel.to_dict()
        print("\n转换为字典的结果:")
        for key, value in channel_dict.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_channel_flow() 