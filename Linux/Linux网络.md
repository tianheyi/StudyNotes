# Linux网络

## tcp

全连接队列长度 = min(backlog, net.core.somaxconn)

半连接队列长度 = 【max(min(backlog, net.core.somaxcon, tcp_max_syn_backlog), 8) + 1】--> 向上取整到2的n次幂(比如8就是8，9则是16)
所以也可知半连接队列最小长度为16，因为max(min(backlog, net.core.somaxcon, tcp_max_syn_backlog), 8) + 1的最小值是9，向上取整为16.

### net.core.somaxconn

`net.core.somaxconn`是Linux中的一个内核(kernel)参数，表示`socket`监听(`listen`)的`backlog`上限。

- 查看（腾讯云服务器查看默认128）

  - `sysctl -a | grep net.core.somaxconn`
  - `cat /proc/sys/net/core/somaxconn`

- 修改

  - 临时（重启机器后失效）

    sysctl -w net.core.somaxconn=1024

  - 永久（修改配置文件，配置文件生效）

    在`/etc/sysctl.conf`文件中新增一行`net.core.somaxconn=1024`；
    执行`sysctl -p`使配置文件生效

### backlog

什么是`backlog`？`backlog`就是 `socket`的监听队列，当一个请求(`request`)尚未被处理或者建立时，它就会进入`backlog`。

而`socket server`可以一次性处理`backlog`中的所有请求，处理后的请求不再位于监听队列中。
当`Server`处理请求较慢时，导致监听队列被填满后，新来的请求就会被拒绝。

`backlog`参数主要用于底层方法`int listen(int sockfd, int backlog)`， 在解释`backlog`参数之前，我们先了解下`tcp`在内核的请求过程，其实就是`tcp`的三次握手：

![img](https://img2020.cnblogs.com/blog/1583990/202109/1583990-20210908153111149-801446571.png)

1. `client`发送`SYN`到`server`，将状态修改为`SYN_SEND`，如果`server`收到请求，则将状态修改为`SYN_RCVD`，并把该请求放到`syns queue`队列中。
2. `server`回复`SYN+ACK`给`client`，如果`client`收到请求，则将状态修改为`ESTABLISHED`，并发送`ACK`给`server`。
3. `server`收到`ACK`，将状态修改为`ESTABLISHED`，并把该请求从`syns queue`中放到`accept queue`。

在linux系统内核中维护了两个队列：`syns queue`和`accept queue`

**syns queue**
用于保存半连接状态的请求，其大小通过`/proc/sys/net/ipv4/tcp_max_syn_backlog`指定，腾讯云服务器查看是128，不过这个设置有效的前提是系统的`syncookies`功能被禁用。互联网常见的`TCP SYN FLOOD`恶意`DOS`攻击方式就是建立大量的半连接状态的请求，然后丢弃，导致`syns queue`不能保存其它正常的请求。

**accept queue**
用于保存全连接状态的请求，其大小通过`/proc/sys/net/core/somaxconn`指定，在使用listen函数时，内核会根据传入的`backlog`参数与系统参数`somaxconn`，取二者的较小值。

如果`accpet queue`队列满了，server将发送一个`ECONNREFUSED`错误信息Connection refused到client。

### 优化

#### 配置充足的端口范围

查看本地端口范围：`cat /proc/sys/net/ipv4/ip_local_port_range`，腾讯云服务器查询默认32768	60999

```shell
vi /etc/sysctl.conf
net.ipv4.ip_local_port_range = 5000 65000 // 在文件中加入这，如果有则修改值
sysctl -p //使得配置生效
```

如果端口加大了仍然不够用，那么可以考虑开启端口`reuse`和`recycle`。这样端口在连接、端口的时候就不需要等待2MSL的时间了，可以快速回收。开启这两个参数之前需要保证`tcp_timestamps`是开启的：

```shell
vi /etc/sysctl.conf
net.ipv4.tcp_timestamps = 1  // 默认1
net.ipv4.tcp_tw_reuse = 1	// 默认0
net.ipv4.tcp_tw_recycle = 1	// 默认0
sysctl -p //使得配置生效
```



#### 小心连接队列溢出

服务端使用两个连接队列来响应来自客户端的握手请求，这两个队列的长度是在服务器调用`listen`的时候就确定好的。如果发生溢出，很可能丢包

对于半连接队列，只要保证`tcp_syncookies`是1，就能保证不会有因为半连接队列满而发生的丢包
`cat /proc/sys/net/ipv4/tcp_syncookies`查看默认是1开启。

对于全连接队列，可以通过netstat -s来观察。netstat -s可查看到当前系统全连接队列满导致的丢包统计。
`netstat -s | grep overflowed`执行后结果：  104682 times the listen queue of a socket overflowed
104682表示的总丢包数，使用watch命令动态监控，如果输出的数字在监控的过程中变了，那说明当前服务器有因为全连接队列满而产生的丢包，就需要加大全连接队列的长度了。
如果权限不够，也可以通过tcpdump抓包查看是否有SYN的TCP Retransmission。

#### 减少握手重试

如果握手发生异常，客户端或者服务端就会启动超时重传机制。如果重试到第三次以后，可能某个环节已经报错返回504，所以在这种应用场景下，维护那么多次重试次数没有意义，倒不如调小一点，尽早放弃。

`cat /proc/sys/net/ipv4/tcp_syn_retries`服务器查看默认是6（客户端syn重试最多6次）
`cat /proc/sys/net/ipv4/tcp_synack_retries`服务器查看默认是5（服务端syn ack重试最多5次）

#### 保持充足的文件描述符上限



#### 如果请求频繁，弃用短连接改用长连接

**节约了握手开销**
**规避了队列满的问题**：当全连接或者半连接队列溢出的时候，服务端直接丢包。而客户端并不知情，所以会等待定时器触发后才会重试(秒级)。TCP本身不是为了互联网服务设计的，秒级的超时时间对于互联网用户体验的影响是致命的。（1s 2s 4s 8s 16s 32s）

`cat /proc/sys/net/ipv4/tcp_syn_retries`服务器查看默认是6（syn重试最多6次）
`cat /proc/sys/net/ipv4/tcp_synack_retries`服务器查看默认是5（syn ack重试最多5次）

**端口数不容易出问题**：释放连接的时候，客户端端口会进入time_wati状态，等待2msl才能释放。如果连接频繁，端口数量很容易不够用，而使用长连接固定使用那么几十上百个端口就够用了。

#### time_wait的优化

很多线上程序使用短连接，就会出现大量time_wait
方法一：建议开启reuse和recycle
方法二：限制time_wait状态的连接的最大数量：net.ipv4.tcp_max_tw_buckets
方法三：用长连接替代频繁的短连接

### Nagle算法

#### 为什么要引入它

Nagle算法主要是**为了防止网络连接中充斥着小于MSS的分组**。小的分组一方面会造成网络拥塞，另外一方面由于网络传输过程中，用户程序需要传递的内容需要附上TCP头和IP头封装成为TCP包/IP包，会造成资源浪费。为了解决这个问题，Nagle就提出一种算法（Nagle算法）。

#### 原理

该算法要求在TCP连接中，如果还有未被确认的分组，在收到ACK确认包之前禁止发送其他小的分组。

该算法的伪码如下：

```python
if there is new data to send
  if the window size >= MSS and available data is >= MSS
    send complete MSS segment now
  else
    if there is unconfirmed data still in the pipe
      enqueue data in the buffer until an acknowledge is received
    else
      send data immediately
    end if
  end if
end if
```


由以上可以看出，Nagle算法适用于：发送方存在许多小的分组需要发送，接收方又能够及时发送ACK的场景。**Nagle算法在Linux，macOS，Windows平台默认都是打开的**。为了能够禁止使用Nagle算法，你可以设置socket为TCP_NODELAY，从而能够保证，发送方的包及时地发送给接收方。

##### 发送条件

以下就是在开启Nagle算法后可以触发发送端发包的几个原因【当然若Nagle算法关闭，这些情况下也会发包，而且要特别增加一条就是：只要一有数据包就会发送，一般情况（只是一般情况，会有特殊情况的出现，比如发送大文件，稍后进行解释）下上述几种条件在达到之前，包已经被发送了】：

1. 收到对端发送的上一个包的ACK时，允许发送。

2. 包长度大于MSS时，允许发送。

   MSS（MaxitumSegment Size）最大报文分段大小，它是TCP中一个可设置的OPTION，表示TCP数据包每次能够传输的最大的数据分段。这也很容易理解，一旦数据包大于MSS还不进行发送的话，显然是在浪费时间。

3. 包中包含FIN时，允许发送。

   包含FIN时，说明发送端在请求断开连接，既然要断开连接了，肯定会立即发送，因为后面不会再有数据了。

4. 一旦发生了超时（一般200ms），允许发送。

   等待超时，这里的等待是包括等待以上三种情况出现的时间，这个时间肯定是有限制，不可能无限制等待。

#### 开启好处

答案是减少网络流量，防止通信阻塞。这点可以从上图中看出，同样发送一个“Hello”字符串，开启Nagle算法后使用了4个数据包，而关闭Nagle算法后却要使用10个数据包，可见Nagle算法的开启可以减少网络流量防止通信阻塞。

#### 是不是所有的TCP传输中都需要开启Nagle算法？

当然不是，Nagle算法并不是适合于所有的情况，传输大文件就是一种。在传输大文件时，发送端在等待上一包的ack到来之前，输出缓冲区就已经被填满，若此时开启了Nagle算法，程序就会在等待ack的过程中阻塞，就影响到了传输速度，因此要根据实际情况选择性的开启和关闭Nagle算法。

## 问题

1. 端口被占用

   查看端口被哪个进程占用？ `lsof -i(可选协议过滤) :8080 `
   杀掉占用端口的进程 `kill -9 进程PID`
