# 内网穿透frp工具

下载地址：[Releases · fatedier/frp (github.com)](https://github.com/fatedier/frp/releases)

需要一个公网服务器，在其上面运行frp服务端；
需要一个运行被映射的服务端的主机，在其上面运行frp客户端。

- 编辑frp服务端配置文件`frps.ini`

  ```ini
  [common]
  bind_port = 7000 # 公网服务器开放的frps服务端端口,默认7000
  ```

  linux下运行`./frps -c ./frpc_full.ini`

- 编辑frp客户端配置文件`frpc.ini`

  ```ini
  [common]
  server_addr = xxx # 公网服务器地址
  server_port = 7000 # 公网frps服务端监听的端口
  
  [ssh]
  type = tcp
  local_ip = 127.0.0.1
  local_port = 22
  remote_port = 6000
  
  [gateway]
  type = tcp  # 因为tcp是http的底层协议，所以可以用tcp
  local_ip = 127.0.0.1
  local_port = 8080  # 本地被映射服务监听的端口
  remote_port = 11000  # 公网服务器开放的端口，用于将请求映射到本地
  ```

  windows下运行`frpc.exe -c ./frpc.ini`

- frp客户端与服务端能正常通信且无错误日志

任何一个联网电脑在浏览器访问http://公网服务器IP:11000/ping均可打到本地部署的http服务http://127.0.0.1:8080/ping
