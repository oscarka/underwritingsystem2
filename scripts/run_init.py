import os
import sys

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root_dir = os.path.dirname(current_dir)
# 将项目根目录添加到 Python 路径
sys.path.insert(0, root_dir)

# 导入并运行初始化函数
from init_data import init_all

if __name__ == '__main__':
    init_all() 