# UDP Socket Programming

## 项目说明

本项目通过UDP实现了模拟TCP的连接建立和释放过程，包括三次握手和四次挥手。
客户端和服务器通过自定义的应用层协议进行通信，该协议支持丢包模拟、超时重传机制，以及往返时间（RTT）的计算。

## 功能描述

*   **连接控制**：模拟TCP的三次握手和四次挥手过程，确保UDP连接的建立和安全释放。
*   **数据传输**：客户端向服务器连续发送12个数据包，服务器根据设定的丢包率随机响应。
*   **超时与重传**：客户端设定超时时间为100ms，未收到响应时进行重传，最多重传两次。
*   **性能统计**：计算并输出--丢包率、RTT（最小、最大、平均值及标准差）和服务器的系统时间等统计数据。

## 运行环境

*   Python 3.x
*   标准 Python 库：`socket`、`random`、`select`、`sys`、`struct`、`time`、`datetime`

## 文件结构

*   `udpclient.py`：UDP客户端程序，负责发送数据包并接收服务器响应。
*   `udpserver.py`：UDP服务器程序，运行在接收和处理客户端请求的模式下。

## 运行步骤

1.  **启动服务器**： 服务器端需要手动配置监听的IP地址和端口，在udpserver.py文件中修改UDP_IP和UDP_PORT的值。在服务器所在的机器上运行以下命令：
    ```bash
    python udpserver.py
    ```

2.  **启动客户端**：
    在客户端机器上，运行以下命令，并指定服务器的IP地址和端口：
    ```bash
    python udpclient.py <server_ip> <server_port>
    ```
    例如：
    ```bash
    python udpclient.py 192.168.138.128 12345
    ```

## 注意事项

*   确保客户端的IP和端口配置正确，以便它们可以在指定的网络环境中通信。
*   服务器和客户端的时间应保持同步，以确保RTT计算的准确性。
*   运行客户端和服务器程序的系统应具备Python环境，并正确安装必需的库。

