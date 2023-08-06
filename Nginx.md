# Nginx

## 什么是nginx 



### 可以干什么

#### 反向代理

**正向代理**

在客户端配置代理服务器，通过代理服务器进行互联网访问。

**反向代理**

反向代理，其实客户端对代理是无感知的，因为客户端不需要任何配置就可以访问，我们只
需要将请求发送到反向代理服务器，由反向代理服务器去选择目标服务器获取数据后，在返
回给客户端，此时反向代理服务器和目标服务器对外就是一个服务器，暴露的是代理服务器
地址，隐藏了真实服务器IP地址。

#### 负载均衡

单个服务器解决不了，我们增加服务器的数量，然后将请求分发到各个服务器上，将原先
请求集中到单个服务器上的情况改为将请求分发到多个服务器上，将负载分发到不同的服
务器，也就是我们所说的负载均衡。

nginx提供了多种分配策略：

- 轮询（默认）：每个请求按时间顺序逐一分配到不同的后端服务器，如果后端服务器down掉，能自动剔除。

- weight：weight代表权重，默认为1,权重越高被分配的客户端越多。
  指定轮询几率，weight 和访问比率成正比，用于后端服务器性能不均的情况。例如: 

  ```nginx
  upstream server_pool {
      server IP weight=5;
      server IP weight=10;
  }
  ```

- ip_hash：每个请求按访问ip的hash结果分配，这样每个访客固定访问一个后端服务器，可以解决session问题。例如：

  ```nginx
  upstream server_pool {
  	ip_hash;
  	server IP:port;
  	server IP:port;
  }
  ```

- fair(第三方)

  按后端服务器的响应时间来分配请求，响应时间短的优先分配。

  ```nginx
  upstream server_pool {
      server IP:port;
      server IP:port;
      fair;
  }
  ```

#### 动静分离

Nginx动静分离简单来说就是把动态跟静态请求分开,不能理解成只是单纯的把动态页面和静态页面物理分离。严格意义上说应该是动态请求跟静态请求分开，可以理解成使用Nginx处理静态页面，Tomcat 处理动态页面。

**动静分离从目前实现角度来讲大致分为两种**：一种是纯粹把静态文件独立成单独的域名,放在独立的服务器上，也是目前主流推崇的方案；另外一种方法就是动态跟静态文件混合在一起发布，通过nginx来分开。
通过location 指定不同的后缀名实现不同的请求转发。通过expires 参数设置，可以使浏览器缓存过期时间，减少与服务器之前的请求和流量。**具体Expires 定义**:是给一个资源设定一个过期时间，也就是说无需去服务端验证,直接通过浏览器自身确认是否过期即可，所以不会产生额外的流量。**此种方法非常适合不经常变动的资源。( 如果经常更新的文件，不建议使用Expires 来缓存)**，我这里设置3d，表示在这3天之内访问这个URL，发送一个请求，比对服务器该文件最后更新时间没有变化，则不会从服务器抓取，返回状态码304，如果有修改，则直接从服务器重新下载，返回状态码200。 

**简单来说就是** 为了加快网站的解析速度，可以把动态页面和静态页面由不同的服务器来解析，加快解析速
度。降低原来单个服务器的压力。

![image-20211227161221629](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211227161221629.png)

#### 限流

地址：https://www.cnblogs.com/daozhangblog/p/12446401.html

限流算法：

令牌桶算法

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190511205451360.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI5Njc3ODY3,size_16,color_FFFFFF,t_70)

算法思想是：

- 令牌以固定速率产生，并缓存到令牌桶中；
- 令牌桶放满时，多余的令牌被丢弃；
- 请求要消耗等比例的令牌才能被处理；
- 令牌不够时，请求被缓存。

漏桶算法

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190511205511421.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzI5Njc3ODY3,size_16,color_FFFFFF,t_70)

- 水（请求）从上方倒入水桶，从水桶下方流出（被处理）；
- 来不及流出的水存在水桶中（缓冲），以固定速率流出；
- 水桶满后水溢出（丢弃）。
- 这个算法的核心是：缓存请求、匀速处理、多余的请求直接丢弃。
  相比漏桶算法，令牌桶算法不同之处在于它不但有一只“桶”，还有个队列，这个桶是用来存放令牌的，队列才是用来存放请求的。

从作用上来说，漏桶和令牌桶算法最明显的区别就是是否允许突发流量(burst)的处理，漏桶算法能够强行限制数据的实时传输（处理）速率，对突发流量不做额外处理；而令牌桶算法能够在限制数据的平均传输速率的同时允许某种程度的突发传输。

Nginx按请求速率限速模块使用的是漏桶算法，即能够强行保证请求的实时处理速度不会超过设置的阈值。

Nginx官方版本限制IP的连接和并发分别有两个模块：

- `limit_req_zone` 用来限制单位时间内的请求数，即速率限制,采用的漏桶算法 “leaky bucket”。
- `limit_req_conn` 用来限制同一时间连接数，即并发限制。

1.限制访问频率(分正常流量和突发流量)

2.限制并发连接数

#### 双向认证



## Nginx安装

命令行方式



Docker方式



## 常用命令

- 查看版本号

  nginx -v

- 启动nginx

  nginx

- 关闭nginx

  nginx -s stop

- 重新加载nginx（修改配置文件后 不重启nginx重新加载配置文件）

  进入到配置文件同级目录下 执行nginx -s reload ，如果无效则用systemctl restart nginx重启生效



## 配置文件

/etc/nginx/nginx.conf

### 组成部分

#### 第一部分：全局块

从配置文件开始到events块之前的内容。主要会设置一些影响nginx服务器整体运行的配置指令,主要包括配
置运行Nginx服务器的用户(组)、允许生成的worker process数，进程PID存放路径、日志存放路径和类型以
及配置文件的引入等。

比如worker_processes 1;	这是nginx服务器并发处理器的关键配置，worker_processes值越大，可以支持的并发处理量也越多，但是会受到硬件、软件等设备的制约。

#### 第二部分：events块

events块涉及的指令主要影响Nginx服务器与用户的网络连接

worker_connections 1024; # 每个进程允许的最大连接数
accept_mutex off; # 默认开启，多个worker将以串行方式处理请求；off后worker会争抢请求，可能会产生惊群问题；高并发时建议off
multi_accept on; # 允许一个工作进程可以同时接受所有新的连接；否则只接受一个，默认off
use epoll; # I/O多路复用机制

示例：
events {
    worker_connections 1024;
}

#### 第三部分：http块

这算是Nginx服务器配置中最频繁的部分, 代理、缓存和日志定义等绝大多数功能和第三方模块的配置都在这里。
需要注意的是: http块也可以包括http全局块、server 块。

##### http全局块

http全局块配置的指令包括文件引入、MIME-TYPE 定义、日志自定义、连接超时时间、单链接请求数上限等。

##### server块

这块和虚拟主机有密切关系,虚拟主机从用户角度看,和一台独立的硬件主机是完全一样的,该技术的产生是为了
节省互联网服务器硬件成本。
每个http块可以包括多个server块,而每个server块就相当于一个虚拟主机。
而每个server 块也分为全局server 块,以及可以同时包含多个location块。

1. 全局server块

   最常见的配置是本虚拟机主机的监听配置和本虚拟主机的名称或IP配置。

2. location块

   一个server块可以配置多个location 块。
   这块的主要作用是基于Nginx服务器接收到的请求字符串(例如server_name/uri-string ) , 对虚拟主机名称
   (也可以是IP别名)之外的字符串(例如前面的/uri-string )进行匹配,对特定的请求进行处理。地址定向、数据缓
   存和应答控制等功能,还有许多第三方模块的配置也在这里进行。

## 配置实例

### 反向代理

1.实现效果

打开浏览器，在浏览器地址栏输入地址www.123.com跳到linux系统tomcat主页

在location块中配置proxy_pass http://127.0.0.1:8080

```nginx
location / {
	proxy_pass http://127.0.0.1:8080;
}
```

2.实现效果

使用nginx反向代理，根据访问的路径跳转到不同端口的服务中

nginx监听端口为9001

例如访问 http://服务器ip:9001/pyzmd/ 跳转到服务器127.0.0.1:8080服务，访问 http://服务器ip:9001/vod/ 跳转到服务器127.0.0.1:8001服务

实例：

```nginx
server {
        listen 9001; #监听服务器端口9001
        server_name 服务器ip; 
		
    	//pyzmd后面可加可不加'/' 目前测试都能访问
        location /pyzmd/ {//访问thyqq.top/pyzmd
        		//(坑)端口后面一定要加‘/’ 不然报404
                proxy_pass http://127.0.0.1:10000/;
        }

        location /gozmd/ {
                proxy_pass http://127.0.0.1:8000/;
        }

        #return 301 https://110.42.158.229$request_uri; # 重定向
}
```

- 关于location：

```nginx
location [ = | ~ | ~* | ^~ ] uri {
    
}
```

1、=:用于不含正则表达式的uri前，要求请求字符串与uri严格匹配，如果匹配成功，就停止继续向下搜索并立即处理该请求。
2、~: 用于表示uri包含正则表达式，并且区分大小写。
3、~\*:用于表示uri包含正则表达式，并且不区分大小写。
4、^~: 用于不含正则表达式的uri前，要求Nginx服务器找到标识uri和请求字符串匹配度最高的location 后，立即使用此location 处理请求，而不再使用location块中的正则uri和请求字符串做匹配。

### 负载均衡

1.实现效果

浏览器地址栏输入地址 http://ip/zmd/，实现负载均衡效果，平均到10000端口和8000端口中（同理可负载均衡到多个服务器的多个端口）

实例：

```nginx
#http全局块中添加
upstream myserver {
    server 服务器IP:10000;
    server 服务器IP:8000;
}
#location块中添加
proxy_pass http://myserver; //myserver 为 http全局块中myserver名字
```

### 限流

#### 限制访问频率（正常流量）

基于漏桶算法实现。接下来我们使用 nginx limit_req_zone 和 limit_req 两个指令，限制单个IP的请求处理速率。

```nginx
http {
    limit_req_zone $binary_remote_addr zone=service1RateLimit:10m rate=10r/s;
}
server {
    location / {
        limit_req zone=service1RateLimit;
        proxy_pass http://upstream_cluster1;
    }
}
```

解释：

```
key ：定义限流对象，binary_remote_addr 是一种key，表示基于 remote_addr(客户端IP) 来做限流，binary_ 的目的是压缩内存占用量。

zone：定义共享内存区来存储访问信息， myRateLimit:10m 表示一个大小为10M，名字为myRateLimit的内存区域。1M能存储16000 IP地址的访问信息，10M可以存储16W IP地址访问信息。

rate 用于设置最大访问速率，rate=10r/s 表示每秒最多处理10个请求。Nginx 实际上以毫秒为粒度来跟踪请求信息，因此 10r/s 实际上是限制：每100毫秒处理一个请求。这意味着，自上一个请求处理完后，若后续100毫秒内又有请求到达，将拒绝处理该请求。
```

实例：

每秒处理一个请求，多的请求拒绝执行返回503 Service Temporarily Unavailable

```nginx
http{
    limit_req_zone $binary_remote_addr zone=service1RateLimit:10m rate=1r/s;
    
    upstream myserver {
        server IP1:port1;
        server IP2:port2;
    }
    
    server {
        location / {
            limit_req zone=service1RateLimit;
            proxy_pass http://myserver;
        }
    }
}
```



#### 限制访问频率（突发流量）

按上面的配置在流量突然增大时，超出的请求将被拒绝，无法处理突发流量，那么在处理突发流量的时候，该怎么处理呢？Nginx提供了 burst 参数来解决突发流量的问题，并结合 nodelay 参数一起使用。burst 译为突发、爆发，表示在超过设定的处理速率后能额外处理的请求数。

```nginx
http {
    limit_req_zone $binary_remote_addr zone=service1RateLimit:10m rate=10r/s;
}

server {
    location / {
        limit_req zone=service1RateLimit burst=20 nodelay;
        proxy_pass http://upstream_cluster;
    }
}
```

解释：

```
burst=20 nodelay表示这20个请求立马处理，不能延迟，相当于特事特办。不过，即使这20个突发请求立马处理结束，后续来了请求也不会立马处理。burst=20 相当于缓存队列中占了20个坑，即使请求被处理了，这20个位置这只能按 100ms一个来释放。这就达到了速率稳定，即使出现突发流量也能正常处理的效果。
```

实例：

每秒处理1个请求，多余的请求会被放入队列，最多20个，放满了之后再有超过频率的请求直接拒绝执行返回503，等队列有空的多余的依然可以放入。

```nginx
http{
    limit_req_zone $binary_remote_addr zone=service1RateLimit:10m rate=1r/s;
    
    upstream myserver {
        server IP1:port1;
        server IP2:port2;
    }
    
    server {
        location / {
            limit_req zone=service1RateLimit burst=20 nodelay;
            proxy_pass http://myserver;
        }
    }
}
```



#### 限制并发连接数

```nginx
limit_conn_zone $binary_remote_addr zone=perip:10m;
limit_conn_zone $server_name zone=perserver:10m;
server {
    ...
    limit_conn perip 20; //限制单个IP同时最多能持有10个连接
    limit_conn perserver 100;	//限制Server的最大连接数
}
```

解释：

```
limit_conn perip 20：对应的key是 $binary_remote_addr，表示限制单个IP同时最多能持有20个连接。

limit_conn perserver 100：对应的key是 $server_name，表示虚拟主机(server) 同时能处理并发连接的总数。注意，只有当 request header 被后端server处理后，这个连接才进行计数。
```



### 动静分离

准备：在linux系统中准备静态资源(根目录下创建data目录，在data中创建www和image目录)，用于进行访问html和图片。

实例：在配置文件中相关server中添加下面内容后重新加载配置文件

```nginx
location /www/ { // 访问http://thyqq.top/www/1.html可访问到/data/www目录下的1.html
	root /data/; 
	index index.html; //默认首页 即访问http://thyqq.top/www返回此
}
location /image/ { //访问http://thyqq.top/image/2.png 访问服务器/data/image目录下的2.png文件
	root /data/;
	autoindex on;	// 添加这行后访问http://thyqq.top/image/页面列出/data/image文件夹中的文件
}
```



### 高可用集群（无多台服务器测试，未学）

了解是通过keepalived来实现高可用

![image-20211227165027404](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211227165027404.png)

## 简单原理

1.master-workers的机制（一个master多个worker[worker争抢式获取资源]）
首先，对于每个worker进程来说，独立的进程，不需要加锁，所以省掉了锁带来的开销，
同时在编程以及问题查找时，也会方便很多。其次，采用独立的进程，可以让互相之间不会
影响，一个进程退出后，其它进程还在工作，服务不会中断，master 进程则很快启动新的
worker进程。当然，worker 进程的异常退出，肯定是程序有bug了，异常退出，会导致当
前worker上的所有请求失败，不过不会影响到所有请求，所以降低了风险。

![img](file:///C:\Users\田何义\AppData\Roaming\Tencent\Users\485280869\QQ\WinTemp\RichOle\N7C5GXGWRX%KQ4$ADIXHD$P.png)

**一个master和多个worker的好处：**

（1）可以使用nginx -s reload 进行热部署，利于nginx进行热部署操作。

（2）每个worker是独立的进程，如果有其中的一个worker出现问题，因为其他worker独立，继续进行争抢，实现请求过程，不会造成服务中断。

**需要设置多少个worker**？

nginx同redis类似都采用了io多路复用机制，每个worker都是一个独立的线程，但每个进程里只有一个主线程，通过异步非阻塞的方式来处理请求，即使是成千上万个请求也不在话下。每个worker的线程可以把一个cpu的性能发挥到极致。所以worker数和服务器的cpu数相等最为适宜。设置少了浪费cpu，设置多了会带来cpu频繁切换上下文造成的损耗。

**连接数worker_connection**

1.发送请求，占用了worker的几个连接数？两个(访问静态资源)或四个(访问数据库)。

2.假设nginx有一个master，有四个worker，每个worker支持最大的连接数是1024，支持的最大并发数是多少？

​	worker最大支持连接数为 4*1024（worker_connections \* worker_processes）。

- 所以对于http请求本地资源来说，能支持的最大并发数是(worker_connection * worker_processes)；
- 如果是支持http1.1的浏览器每次访问要占2个连接，所以普通的静态访问最大并发数为(worker_connection * worker_processes / 2)；
- 而如果是http作为反向代理来说，最大并发数量应该是(worker_connection * worker_processes / 4)，因为作为反向代理服务器，每个并发会建立与客户端的连接和与后端服务的连接，会占两个连接。



![img](file:///C:\Users\田何义\AppData\Roaming\Tencent\Users\485280869\QQ\WinTemp\RichOle\TV5_KOP4I]1_FY0_7HY_QKG.png)