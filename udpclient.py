import socket
import struct
import time
from datetime import datetime
import sys

# 从命令行参数获取服务器地址和端口号
if len(sys.argv) < 3:
    print('Usage: python udpclient.py <server_ip> <server_port>')
    sys.exit(1)

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

# 定义超时时间（毫秒）
TIMEOUT = 100 / 1000

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置套接字接收超时时间
sock.settimeout(TIMEOUT)

# 初始化序列号和请求计数
seq_no = 1
requests_sent = 0
responses_received = 0
rtts = []
server_times = []
MAX_RETRIES = 2  # 最大重传次数
retries = 0

#模拟TCP三次握手建立连接
try:
    print(f"Establishing connection with server {(SERVER_IP, SERVER_PORT)}...")
    sock.sendto(b'SYN', (SERVER_IP, SERVER_PORT))
    print("SYN packet sent to the server")
    response, _ = sock.recvfrom(4096)
    if response.decode() == 'SYN-ACK':
        print("Received SYN-ACK packet from the server")
        sock.sendto(b'CONNECT-ACK', (SERVER_IP, SERVER_PORT))
        print(f"CONNECT-ACK packet sent, connection established with server {(SERVER_IP, SERVER_PORT)}!\n")
except Exception:
    print(f"Failed to establish connection with server {(SERVER_IP, SERVER_PORT)}!")

# 发送12个请求
while requests_sent < 12:
    time.sleep(0.1)
    ver = 2
    if retries==0 :
        # 记录发送时间
        start_time = time.time()
        # 存放无意义的字母序列作为填充
        request = seq_no.to_bytes(2, 'big') + bytes([ver]) + b'abcdefghijklmn' * 10

    # 发送请求到服务器
    sock.sendto(request, (SERVER_IP, SERVER_PORT))
    print(f"Packet sent: Sequence number {seq_no}")

    try:
        # 接收来自服务器的响应
        data, addr = sock.recvfrom(4096)

        # 记录响应接收时间
        end_time = time.time()

        # 解析响应数据包，提取序列号和版本号
        recv_seq_no, recv_ver, server_time = struct.unpack('!HB8s', data[:11])

        # 如果版本号不为2或者序列号不匹配，则忽略该响应
        if recv_ver != 2 or recv_seq_no != seq_no:
            continue

        # 计算RTT并记录
        rtt = (end_time - start_time-0.1*retries) * 1000  # 转换为毫秒
        rtts.append(rtt)

        # 解析服务器系统时间
        server_time_str = server_time.decode('utf-8')
        server_times.append(server_time_str)

        # 打印响应信息
        print("Sequence No. {}, Server: {}, RTT: {} ms".format(seq_no, addr, rtt))
        responses_received += 1

    except socket.timeout:
        retries += 1
        if retries <= MAX_RETRIES:
            # 打印超时信息
            print("Sequence No. {}, Request timed out. Retrying... ({}/{})".format(seq_no, retries, MAX_RETRIES))
            continue
        else:
            print("Sequence No. {}, Request timed out. Maximum retries exceeded. Giving up.".format(seq_no))
            retries = 0  # 重置重传次数
            seq_no += 1  # 更新序列号
            requests_sent += 1  # 更新请求计数
            continue

    retries = 0  # 重置重传次数
    seq_no += 1  # 更新序列号
    requests_sent += 1  # 更新请求计数

#模拟TCP四次挥手释放连接
try:
    print(f"\nReleasing connection with server {(SERVER_IP, SERVER_PORT)}...")
    sock.sendto(b'FIN', (SERVER_IP, SERVER_PORT))
    print("FIN packet sent to the server")
    response1, _ = sock.recvfrom(4096)
    response2, _ = sock.recvfrom(4096)
    if response1.decode() == 'FIN-ACK' and response2.decode() == 'FIN':
        print("Received FIN-ACK packet from server, sending RELEASE-ACK...")
        sock.sendto(b'RELEASE-ACK', (SERVER_IP, SERVER_PORT))
        print(f"RELEASE-ACK packet sent, successfully released connection with server {(SERVER_IP, SERVER_PORT)}!")
except Exception:
    print("Failed to release connection with the server, connection not properly closed!")


# 关闭套接字
sock.close()

# 计算汇总信息
total_packets = requests_sent + responses_received
packet_loss_rate = (requests_sent - responses_received) / requests_sent * 100 if requests_sent != 0 else 0
max_rtt = max(rtts) if rtts else 0
min_rtt = min(rtts) if rtts else 0
avg_rtt = sum(rtts) / len(rtts) if rtts else 0
rtt_stddev = (sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)) ** 0.5 if rtts else 0

# 打印汇总信息
print("Summary:")
print("Number of UDP packets received: {}".format(responses_received))
print("Packet loss rate: {:.2f}%".format(packet_loss_rate))
print("Maximum RTT: {:.2f} ms".format(max_rtt))
print("Minimum RTT: {:.2f} ms".format(min_rtt))
print("Average RTT: {:.2f} ms".format(avg_rtt))
print("Standard deviation of RTT: {:.2f} ms".format(rtt_stddev))
#计算最后一个和第一个服务器时间的差
last_server_time = server_times[-1]
first_server_time = server_times[0]
time_difference = datetime.strptime(last_server_time, "%H:%M:%S") - datetime.strptime(first_server_time, "%H:%M:%S")
print("Overall server response time:", time_difference)

