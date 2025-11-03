import socket
import time
import subprocess
from time import sleep
def disable_adapter(adapter_name="以太网"):
    """禁用网络适配器"""
    try:
        print(f"\n⚠ 禁用网络适配器: {adapter_name}...")
        cmd = f'netsh interface set interface "{adapter_name}" disabled'
        subprocess.run(cmd, shell=True, capture_output=True, check=False)
        print(f"✓ 网络适配器已禁用")
        sleep(2)
    except Exception as e:
        print(f"✗ 禁用网络适配器失败: {e}")

def enable_adapter(adapter_name="以太网"):
    """启用网络适配器"""
    try:
        print(f"\n✓ 启用网络适配器: {adapter_name}...")
        cmd = f'netsh interface set interface "{adapter_name}" enabled'
        subprocess.run(cmd, shell=True, capture_output=True, check=False)
        print(f"✓ 网络适配器已启用")
        sleep(2)
    except Exception as e:
        print(f"✗ 启用网络适配器失败: {e}")

def listen_for_notifications():
    """连接到服务器并持续接收通知"""
    host = '127.0.0.1'  # 服务器IP地址
    port = 65432        # 服务器端口

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print(f"尝试连接到服务器 {host}:{port}...")
                s.connect((host, port))
                print("连接成功！等待任务完成的通知...")
                while True:
                    # 这是一个简化的示例，它会阻塞在这里等待消息
                    # 在实际应用中，您可能需要更复杂的逻辑来处理断线重连
                    data = s.recv(1024)
                    if not data:
                        print("与服务器的连接已断开。")
                        break
                    print(f"\n[通知] 收到新消息: {data.decode('utf-8')}\n")
                    disable_adapter("WLAN2")
                    sleep(300)
                    enable_adapter("WLAN2")
        except ConnectionRefusedError:
            print("连接被拒绝。服务器可能未运行。5秒后重试...")
            time.sleep(5)
        except Exception as e:
            print(f"发生错误: {e}。5秒后尝试重连...")
            time.sleep(5)
        finally:
            enable_adapter("WLAN2")
            

if __name__ == "__main__":
    listen_for_notifications()