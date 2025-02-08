import os
import signal
import subprocess
import sys
import time

def kill_process_on_port(port):
    try:
        # 尝试使用 sudo 获取进程 ID
        cmd = f"sudo lsof -t -i:{port}"
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        if result.stdout:
            pid = int(result.stdout.strip())
            # 先尝试正常终止
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)  # 等待进程正常关闭
            except:
                pass
            
            # 如果还在运行，强制终止
            try:
                os.kill(pid, signal.SIGKILL)
                print(f"已强制关闭端口 {port} 上的进程 (PID: {pid})")
            except:
                print(f"进程 {pid} 已经终止")
        else:
            print(f"端口 {port} 没有被占用")
            
    except Exception as e:
        print(f"处理端口 {port} 时出错: {str(e)}")
        print("尝试使用 sudo 命令强制关闭...")
        try:
            os.system(f"sudo kill -9 $(lsof -t -i:{port})")
            print("已执行强制关闭命令")
        except:
            print("强制关闭失败")
            sys.exit(1)

if __name__ == '__main__':
    port = 9527
    kill_process_on_port(port)
    # 等待端口完全释放
    time.sleep(2)