from app.models.business.channel import Channel
from app.extensions import db

def test_create_channel():
    # 创建一个最简单的 Channel 实例
    channel = Channel(
        name="Test Channel",
        code="TEST_CHANNEL",
        description="Test Description"
    )
    
    # 打印实例属性
    print("\n创建的 Channel 实例属性:")
    print(f"name: {channel.name}")
    print(f"code: {channel.code}")
    print(f"description: {channel.description}")
    print(f"status: {channel.status}")
    
    # 尝试转换为字典
    channel_dict = channel.to_dict()
    print("\n转换为字典的结果:")
    for key, value in channel_dict.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_create_channel() 