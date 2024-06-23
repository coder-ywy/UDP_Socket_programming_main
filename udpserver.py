import socket
import random
import time
import struct
import select

# 定义UDP服务器的IP和端口
UDP_IP = "127.0.0.1"
UDP_PORT = 12345

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)  # 设置套接字为非阻塞模式
seq_que = {}  # 用于记录已经接受到的每个客户端发送的数据包序列号，避免处理重复的数据包
print(f"Server is running on {UDP_IP}:{UDP_PORT}")

# 处理客户端请求
try:
    while True:
        readable, _, _ = select.select([sock], [], [], 0.5)
        for i in readable:
            client_data, client_address = i.recvfrom(4096)  # 从客户端接收数据
            data = client_data.decode()
            if data == 'SYN':
                print(f"Received SYN packet from client {client_address}")
                i.sendto(b'SYN-ACK', client_address)  # 收到SYN消息，回复SYN-ACK
                print(f"Sent SYN-ACK packet to client {client_address}")

            elif data == 'CONNECT-ACK':
                print(f"Successfully established connection with client {client_address}!")
                break

            elif data == 'FIN':
                print(f"\nReceived FIN packet from client {client_address}, sending FIN-ACK acknowledgment packet")
                sock.sendto(b'FIN-ACK', client_address)  # 收到FIN消息，回复FIN-ACK
                print(f"Sent FIN packet, server is also ready to close the connection")
                sock.sendto(b'FIN', client_address)  # 收到FIN消息，回复FIN

            elif data == 'RELEASE-ACK':
                print(f"Successfully released connection with client {client_address}!\n")
                break

            else:
                # 解析序列号和版本号
                seq_no, ver = int.from_bytes(client_data[:2], 'big'), client_data[2]
                if client_address not in seq_que:
                    seq_que[client_address] = []
                if seq_no in seq_que[client_address]:
                    print(f"Received retransmitted data packet from client {client_address}: Sequence number {seq_no}, Version {ver}")
                    # 将服务器时间附加到响应中
                    server_time = time.strftime('%H:%M:%S', time.localtime())
                    # 构建响应数据包，包含序列号、版本号和服务器系统时间
                    response = struct.pack('!HB8s', seq_no, ver, server_time.encode())
                    # 发送响应到客户端
                    sock.sendto(response, client_address)
                    print(f"Replying to client {client_address} with a message containing server time: {server_time}")
                    continue  # 如果序列号已经处理过，跳过此次处理

                seq_que[client_address].append(seq_no)  # 记录序列号
                print(f"\nReceived data packet from client {client_address}: Sequence number {seq_no}, Version {ver}")

                if random.random() < 0.3:
                    print(f"Simulating packet loss")
                    continue  # 根据设置的丢包概率随机丢弃一些包

                # 将服务器时间附加到响应中
                server_time = time.strftime('%H:%M:%S', time.localtime())
                # 构建响应数据包，包含序列号、版本号和服务器系统时间
                response = struct.pack('!HB8s', seq_no, ver, server_time.encode())
                # 发送响应到客户端
                sock.sendto(response, client_address)
                print(f"Replying to client {client_address} with a message containing server time: {server_time}")
finally:
    sock.close()  # 最终关闭服务器套接字
    print("Server socket closed.")









