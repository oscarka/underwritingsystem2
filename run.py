import os
import socket
from app import create_app
from app.utils.logging import init_logging
import logging

logger = logging.getLogger(__name__)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except OSError:
            return True

def find_available_port(start_port, max_attempts=10):
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"无法找到可用端口(尝试范围: {start_port}-{start_port+max_attempts-1})")

if __name__ == '__main__':
    try:
        app = create_app()
        init_logging(app)
        
        # 尝试使用默认端口,如果被占用则寻找其他可用端口
        default_port = int(os.environ.get('PORT', 5001))
        port = find_available_port(default_port) if is_port_in_use(default_port) else default_port
        
        logger.info(f'应用将在端口 {port} 上启动')
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f'应用启动失败: {str(e)}')
        raise