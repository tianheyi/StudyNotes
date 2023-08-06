# Docker

*将运用与运行的环境打包形成容器运行，运行可以伴随着容器
*容器之间希望有可能共享数据

## 三大概念（镜像、容器、仓库）：

镜像

容器

### 仓库

仓库(Repository)是集中存放镜像文件的场所。
仓库(Repository)和仓库注册服务器(Registry) 是有区别的。仓库注册服务器上往往存放着多个仓库，每个仓库中又包含了多个镜像，
每个镜像有不同的标签(tag) 。
仓库分为公开仓库(Public)和私有仓库(Private) 两种形式。.
最大的公开仓库是Docker Hub(https://hub.docker.com/),
存放了数量庞大的镜像供用户下载。国内的公开仓库包括阿里云、网易云等

## 安装

### CentOS7安装Docker



出现：No Presto metadata available for docker-ce-stable

使用：yum install docker-ce -y

出现：No package docker-ce available

解决：https://www.cnblogs.com/caijunchao/p/13512410.html

安装完之后运行docker run helloworld

```json
//如果出现问题，创建/etc/docker/daemon.json
{
  "registry-mirrors": ["https://gk0lyeuc.mirror.aliyuncs.com"]
}
```



## 常用命令

### 帮助命令

- docker version
- docker info
- docker --help

### 镜像命令

- docker build 路径 [options]

  根据Dockefile构建镜像，路径应该是**Dockerfile文件所在目录的路径**而不是Dockerfile文件的路径

  -t 创建的镜像名称:创建的镜像版本

  --no-cache 不使用缓存

  docker build . -t myapp:1.0.0 --no-cache

- docker images

  -a 显示本地全部镜像  -q 只显示ID

- 查找某镜像 docker search xxx 

- 下载某镜像 docker  pull xxx 

- 删除某镜像(xxx为IMAGE ID或REPOSITORY)   docker rmi -f xxx 

  -f 表示强制删除(运行中的要用-f才能删除成功)

- 删除多个 docker rmi -f xxx1 xxx2

- 删除全部 docker rmi -f $(docker images -qa) 

- 以某镜像为模板生成并且运行一个容器 

  docker run [options] 镜像id或名称 

  ​	--name xxx  (xxx为给容器取的名称)

  ​	-d：后台运行容器，并且返回容器ID，也即启动守护式容器

  ​	-i：以交互模式运行容器，通常与-t同时使用（后面一般 bash才会进入）

  ​	-t：为容器重新分配一个伪输入终端，通常与-i同时使用

  ​	-p port1:port2 ：指定端口(通过docker的端口port1访问docker运行的容器对外暴露的端口port2，例如外部通过访问8888端口来访问运行在docker容器中的tomcat，tomcat默认为8080端口，-p 8888:8080)

  ​	-P 随机分配端口

  ​	-v 主机目录:容器目录  ：数据卷

- 退出容器

  - 关闭并退出当前容器 exit

  - 退出当前容器但不关闭仍在后台运行  Ctrl+P+Q

- 显示当前正在运行的容器 docker ps [options] 

  ​	-a 列出当前所有正在运行的容器+历史上运行过的容器

  ​	-l 显示最近创建的容器(1个)

  ​	-n x : 显示最近创建的x个容器

  ​	-q 只显示容器编号

  ​	--no-trunc 不截断输出

- 启动容器  docker start xxx  (xxx为容器ID或名称) 

- 重启容器  docker restart xxx  (xxx为容器ID或名称) 

- 停止容器（慢慢关闭，相当于电脑程序中启动关机）docker stop xxx 

- 强制停止容器（强制关闭，电脑拔电源或者长按关机键）docker kill xxx 

- 删除容器 docker rm xxx

  一次性删除多个容器

  ​	docker rm -f $(docker ps -qa)

  ​	docker ps -qa | xargs docker rm

### 重要命令

- 启动守护式容器 docker run -d xxx

  - -p

- 查看容器日志

  docker logs -f -t --tail 容器ID

  ​	-t 加入时间戳

  ​	-f 跟随最新的日志打印

  ​	--tail n 显示最后n条

- 查看容器内运行的进程

  docker top xxx

- 查看容器内部细节

  docker inspect xxx

- 进入正在运行的容器并以命令行交互

  docker attach xxx

  docker exec -it xxx 要执行的相关命令(pwd等等)

  ​	区别：attach直接进入容器启动命令的终端，不会启动新的进程

  ​	exec是在容器中打开终端，执行相关命令后将结果打印，并且可以启动新的进程

  **补充：**`docker exec -it xxx /bin/bash` 进入容器内部，如果执行报错`OCI runtime exec failed: exec failed:`，可能是因为该容器镜像是用alpine制作的，需要改为`docker exec -it xxx /bin/sh`

- 从容器内拷贝文件到主机上

  docker cp xxx:path1 path2

  xxx为容器id或者名称，path1为容器内要拷贝文件的路径，path2为要拷贝到的目的主机路径

### 进入未启动的容器内部（折中方法）

原文：[(101条消息) Docker 入门系列（8）— 免 sudo 使用 docker 命令、进入未启动的容器-CSDN博客](https://blog.csdn.net/wohu1104/article/details/123982935)

在某些场景下，我们进入容器修改了配置信息或者系统配置之后重启容器，发现容器启动不了，通过日志发现原来是我们修改出错，此时我们想把配置改回来但发现因为容器启动不了，使用 docker exec 是无法进入容器内部了，这种情况下的折中解决办法是：先从容器内部把配置文件复制到宿主机内，在宿主机中修改正确后再复制回容器内。 如：

```shell
# 从容器内把 Nginx.conf 复制到宿主机当前目录 
docker  cp 容器ID:/etc/Nginx/Nginx.conf . 
# 修改 Nginx.conf 
vim Nginx.conf 
# 把修改后 Nginx.conf 复制回容器内部 
docker cp Nginx.conf 容器ID:/etc/Nginx/Nginx.conf 
```

### 如何测试连通性

在容器中安装 ping

`ping` 命令在测试 `IP` 连通性时经常用到，在容器中安装 `ping` 的方法是：

```shell
apt-get update && apt-get install iputils-ping
```

### 清除docker无用镜像和容器

none镜像包含有用镜像和无用镜像：
**有用镜像**：通过docker images -a 命令才会显示的none镜像，这些镜像是镜像分层的中间镜像，同时这些镜像不会造成空间损耗
**无用镜像**：通过docker images 命令显示的none镜像，这些镜像是由于新加镜像占用了原有镜像的标签，原有镜像就变成了none镜像。
这些none镜像有一个好听的名字：空悬镜像（dangling images）,同时docker并没有自动删除这些镜像的机制。

可以使用以下命令清理空悬镜像

```shell
docker rmi -f $(docker images | grep "<none>" | awk "{print \$3}")
//或者
docker rmi -f $(docker images -f "dangling=true" -q)
```

使用以下命令清理已经停止运行的docker容器

```shell
 docker rm $(docker ps --all -q -f status=exited)
```

### Docker镜像commit命令操作补充

docker commit提交容器副本使之成为一个新的镜像

docker commit -m="要提交的描述信息" -a="作者" 容器ID 要创建的目标镜像名:标签 

## Docker镜像

### 是什么

镜像是一一种轻量级、可执行的独立软件包，用来打包软件运行环境和基于运行环境开发的软件，它包含运行某个软件所需的所有内容
包括代码、运行时、库、环境变量和配置文件。

#### UnionFS(联合文件系统)



#### Docker镜像加载原理



![image-20211101225033079](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211101225033079.png)

#### 分层的镜像



为什么tomcat大小有四百多M？

![image-20211101225303061](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211101225303061.png)

#### 为什么采用这种分层结构

![image-20211101225438734](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211101225438734.png)



### 特点

![image-20211101225829521](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211101225829521.png)

## Docker容器数据卷

先来看看Docker的理念:
*将运用与运行的环境打包形成容器运行，运行可以伴随着容器，但是我们对数据的要求希望是持久化的
*容器之间希望有可能共享数据

Docker容器产生的数据，如果不通过docker commit生成新的镜像，使得数据做为镜像的一部分保存 下来，
那么当容器删除后，数据自然也就没有了。
为了能保存数据在docker中我们使用卷。

### 是什么

类似redis里面的rdb和aof文件

### 能干嘛

容器的持久化

容器间继承 + 共享数据（主机到容器，容器到主机）



卷就是目录或文件，存在于一个或多个容器中，由docker挂载到容器，但不属于联合文件系统，因此能够绕过Union File System提供
一些用于持续存储或共享数据的特性:
卷的设计目的就是数据的持久化，完全独立于容器的生存周期，因此Docker不 会在容器删除时删除其挂载的数据卷
特点:
1:数据卷可在容器之间共享或重用数据
2:卷中的更改可以直接生效
3:数据卷中的更改不会包含在镜像的更新中
4:数据卷的生命周期一直持续到没有容器使用它为止

### 数据卷

#### 容器内添加

##### **直接命令添加**

1. docker run -it -v 宿主机绝对路径:容器相对路径 镜像ID或者名称

   例如：docker run -it -v /etc/docker/myDataVolume:/dataVolumeContainer centos

   表示主机与镜像centos即将生成的容器通过对应的目录进行数据共享，执行命令后自动进入生成的容器中，如果目录不存在会自动创建。当在主机该目录下进行操作就相当于在对应容器目录进行操作，反之亦然

2. docker run -it -v 服务器文件夹:容器文件夹 容器ID或者名称 /bin/bash

即使容器关闭了，主机在目录对相关内容进行修改，重新启动该容器后去相关目录查看，内容也是同步

**带权限**

只允许容器读，主机可读写：docker run -it -v 宿主机绝对路径:容器相对路径:ro 镜像ID或者名称

##### **DockerFile添加**

- 根目录下新建mydocker文件夹并且进入

  可在DockerFile中使用VOLUME指令来给镜像添加一个或多个数据卷VOLUME["/dataVolumeContainer","/dataVolumeContainer2","/dataVolumeContainer3"]
  说明:

  ​	**出于可移植和分享的考虑，用-v 主机目录:容器目录这种方法不能够直接在Dockerfile中实现。由于宿主机目录是依赖于特定宿主机的，并不能够保证在所有的宿主机上都存在这样的特定目录。**

- File构建

  创建一个DockerFile文件，然后编辑输入

  FROM centos
  VOLUME ["/dataVolumeContainer1","/dataVolumeContainer2"]
  CMD echo "finished,-----success"
  CMD /bin/bash

  保存退出

- build后生成镜像 -获得一个新镜像zzyy/centos(名字自己取，注意命令后面还有个小数点)

  **docker build -f /etc/docker/DockerFile -t zzyy/centos .**

- run容器

  docker images zzyy/centos

- 通过上述步骤，容器内的卷目录已经知道

  进入容器查看 docker run -it zzyy/centos

- 找到主机对应默认地址

  docker inspect 容器ID或者名称

   找到"Mounts"，可以看到对应共享数据的目录路径以及其他信息（容器的目录路径和对应主机中的目录路径）（可以发现docker自动在主机创建了目录）

  然后就可以用对应目录进行共享数据

- 备注

  ​	Docker挂载主机目录Docker访问出现cannot open directory .: Permission denied
  解决办法:在挂载目录后多加一个--privileged=true参数即可

  例如 docker run -it -v /xxx:/xxx --privileged=true

#### 容器与主机共享

```bash
FROM java:8
#VOLUME /tmp 将容器中的 /tmp 目录映射到宿主机的目录
VOLUME /tmp /usr/tmp
COPY /target/springbootdemo.jar app.jar
RUN bash -c 'touch /app.jar'
EXPOSE 10001
ENTRYPOINT ["java","-jar","/app.jar"]
```

### 数据卷容器

**是什么**



**总体介绍**

以上一步新建的镜像zzyy/centos为模板并运行容器dc01/dc02/dc03

他们已经具有容器卷/dataVolumeContainer1 /dataVolumeContainer2

**容器间传递共享**

1. 先启动一个父容器

   - docker run -it --name dc01 zzyy/centos
   - 在/dataVolumeContainer2中新建文件dc01_add.txt

2. dc02/dc03继承自dc01

   - docker run -it --name dc02 --volumes-from dc01 zzyy/centos

     进入/dataVolumeContainer2也能看见dc1创建的文件，然后新建文件dc02_add.txt

   - docker run -it --name dc03 --volumes-from dc01 zzyy/centos

     进入/dataVolumeContainer2也能看见dc1和dc2创建的文件，然后新建文件dc03_add.txt

3. 回到dc01可以看到02、03各自添加的都能共享了

   - 所有可以看见完成了继承共享

4. 删除dc01，dc02修改后dc03可否访问

   - 删除了父容器dc01，发现dc02和dc03之间仍然可以访问

5. 新启动一个容器继承dc04

   - 发现dc04也能与dc02 共享，也能看到dc01创建的dc01_add.txt文件，即使dc01已经被删除了

结论：**容器之间配置信息的传递，数据卷的生命周期一直持续到没有容器使用它为止。**



## DockerFile解析

- 目标：
  - 1.手动编写一个dockerfile文件，当然，必须要符合file的规范
  - 2.有这个文件后，直接docker build命令执行，获得一个自定义的镜像
  - 3.run

### 是什么

​	Dockerfile是用来构建Docker镜像的陶建文件，是由一系列命令和参数构成的脚本。，



### Dockerfile构建镜像

1. 编写DockerFile文件

2. docker build Dockerfile文件位置

3. docker run

   

   文件什么样? ? ?

   ![image-20211103113544579](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211103113544579.png)

   FROM scratch 类似于Java的object类，是基础镜像
   ADD centos-7-x86_64-docker.tar.xz / 

   LABEL \
       org.label-schema.schema-version="1.0" \
       org.label-schema.name="CentOS Base Image" \
       org.label-schema.vendor="CentOS" \
       org.label-schema.license="GPLv2" \
       org.label-schema.build-date="20201113" \
       org.opencontainers.image.title="CentOS Base Image" \
       org.opencontainers.image.vendor="CentOS" \
       org.opencontainers.image.licenses="GPL-2.0-only" \
       org.opencontainers.image.created="2020-11-13 00:00:00+00:00"

   CMD ["/bin/bash"]  默认在最后一行加/bin/bash，所以我们一般用docker run -it xxx /bin/bash可以省略后面这个

   

### DockerFile构建过程解析

#### DockerFile基础

1.每条保留字指令都必须为大写字母且后面要跟至少一个参数

2.指令从上到下顺序执行

3.#表示注释

4.每条指令都会创建一个新的镜像层，并对镜像进行提交

#### Docker执行DockerFile的大致流程

1. docker从基础镜像运行一个容器
2. 执行一条指令并对容器做出修改
3. 执行类似docker commit的操作提交一个新的镜像层
4. docker再基于刚提交的镜像运行一个新容器
5. 执行dockerfile中的下一条指令直到所有指令都执行完成

#### 总结


从应用软件的角度来看，Dockerfile、 Docker镜像与Docker容器分别代表软件的三个不同阶段，

* Dockerfile是软件的原材料

* Docker镜像是软件的交付品

* Docker容器则可以认为是软件的运行态。

  Dockerfile面向开发，Docker镜像成为交付标准，Docker容 器则涉及部署与运维，三者缺一不可，合力充当Docker体系的基石。

  ![image-20211103115239455](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211103115239455.png)

  1 Dockerfile，需要定义一个Dockerfile，Dockerfile定 义了进程需要的一切东西。Dockerfile涉 及的内容包括执行代码或者是文件、环境
  变量、]依赖包、运行时环境、动态链接库、操作系统的发行版、服务进程和内核进程(当应用进程需要和系统服务和内核进程打交道，
  这时需要考虑如何设计namespace的权限控制)等等; 
  2 Docker镜像， 在用Dockerfile定义个文件之后，docker build时 会产生一个Docker镜像，当运行Docker镜像时， 会真正开始提供服
  务;
  3Docker容器，容器是直接提供服务的。

### DockerFile体系结构（保留字指令）

FROM 基础镜像，当前新镜像是基于哪个镜像的

MAINTAINER 镜像维护者的姓名和邮箱地址

RUN 容器构建时需要运行的命令

EXPOSE 当前容器对外暴露出的端口号

WORKDIR 指定在创建容器后，终端默认登录进来的工作目录，默认/

ENV 用来在构建镜像过程中设置环境变量

```
ENV MY_PATH /usr/mytest
这个环境变量可以在后续的任何RUN指令中使用，这就如同在命令前面指定了环境变量前缀一样;
也可以在其它指令中直接使用这些环境变量，
比如: WORKDIR $MY_PATHI

```

ADD 将宿主机目录下的文件拷贝进镜像且ADD命令会自动处理URL和解压tar压缩包

COPY 

- 类似ADD，拷贝文件和目录到镜像中。
- 将从构建上下文目录中<源路径>的文件/目录复制到新的一层的镜像内的<目标路径>位置。
- 写法
  - COPY src dest
  - COPY["src","dest"]

VOLUME 容器数据卷，用于数据保存和持久化工作

CMD

- 指定一个容器启动时要运行的命令
- WORKDIR 命令为后续的 RUN、CMD、COPY、ADD 等命令配置工作目录。在设置了 WORKDIR 命令后，接下来的 COPY 和 ADD 命令中的相对路径就是相对于 WORKDIR 指定的路径。
- DockerFile中可以有多个CMD指令，**但只有最后一个生效**，**CMD会被docker run之后的参数替换**

ENTRYPOINT(与CMD区别？)

- 指定一个容器启动时要运行的命令

- ENTRYPOINT的目的和CMD一样，都是在指定容器启动程序及参数。但docker run之后的参数会被当做参数传递给ENTRYPOINT，之后再执行更新后的命令。

  - 案例：

    ```
    制作CMD版可以查询IP信息的容器
    问题：如果希望显示HTTP头信息，需要加 -i参数
    但用CMD的话 -i会把参数替换掉
    所以用ENTRYOPINT版的更适合，是追加
    ```

    

ONBUILD 当构建一个被继承的DockerFile时运行命令，父镜像在被子镜像继承后父镜像的onbuild被触发

总结

### 案例

**Base镜像(scratch)**

- Docker Hub中99%的镜像都是通过在base镜像中安装和配置需要的软件构建出来的

**自定义镜像**（mycentos）

![image-20211103122706334](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211103122706334.png)

```
FROM centos
MAINTAINER thy<485280869@qq.com>

ENV MYPATH /tmp
WORKDIR $MYPATH

RUN yum -y install vim
RUN yum -y install net-tools

VOLUME ["/dataVolumeContainer1","/dataVolumeContainer2"]

EXPOSE  80

CMD echo &MYPATH
CMD echo "finished,-----success"
CMD /bin/bash
```

查看docker history mycentos:1.3

自定义操作tomcat镜像

![image-20211103211036515](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211103211036515.png)

![image-20211103211321580](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20211103211321580.png)

## .dockerignore使用

使用.gitignore文件可以配置git管理范围之外的文件或者目录列表，同样使用Dockerfile进行镜像构建，也存在着一个类似的文件.dockerignore，用于管理镜像构建上下文或者COPY/ADD的例外文件列表。

## \<none\>镜像（虚悬镜像）

为什么会有 `none` 这样命名的镜像？
这些镜像 [docker](https://so.csdn.net/so/search?q=docker&spm=1001.2101.3001.7020) 称为 **虚悬镜像**，当镜像被新的镜像覆盖时候，老版本镜像名称会变成 `none` 。

- **虚悬镜像**，当镜像被新的镜像覆盖时候，老版本镜像名称会变成 `none`。
- 可以使用 `docker image prune` 命令删除 悬壶镜像。

查看无用镜像：docker images -f dangling=true

删除无效镜像：

- 方法1：`docker rmi $(docker images -f dangling=true -q)`，删不掉会报错误信息（例如镜像被容器使用，此时需要删除这些，删除已停止的容器：`docker rm $(docker ps -qf status=exited)`）
- 方法2：`docker image prune`，删不掉不会报错误信息

## Docker常用安装

**总体步骤**

1. 搜索
2. 拉取
3. 查看
4. 启动
5. 停止
6. 移除

**安装mysql8.0**

参考：[(30条消息) docker仓库mysql所有版本_Docker 安装 MySQL8.0_吴人奔越的博客-CSDN博客](https://blog.csdn.net/weixin_29599033/article/details/113382651?spm=1001.2101.3001.6650.1&utm_medium=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~default-1.no_search_link&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~default-1.no_search_link)

1. docker search mysql
2. docker pull mysql:8.0
3. docker images mysql:8.0
4. docker run -p 12345:3306 --name mysql -v /etc/docker/mysql/conf:/etc/mysql/conf.d -v /etc/docker/mysql/logs:/logs -v /etc/docker/mysql/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:8.0
5. docker exec -it 容器ID /bin/bash 
6. mysql -uroot -p然后输入设置的密码123456进入数据库
7. 修改数据库navicate远程连接：
   - show databases;
   - use mysql;
   - select host,user,plugin from user;
   - alter user 'root'@'%' identified with mysql_native_password by 'root';

备份数据库

docker exec mysql容器ID sh -c' exec mysqldump --all- databases -uroot -p"123456"' > /mysql/all-databases. sql

**安装redis**

docker run -p 6379:6379 -v /zzyyuse/myredis/data:/data -v /zzyyuse/myredis/conf/redis.conf:/usr/local/etc/redis/redis.conf 
-d redis:3.2 redis-server /usr/local/etc/redis/redis.conf --appendonly yes 

本地镜像推送到阿里云

**安装consul**

```
#拉取
docker pulll consul
#启动 8600是dns端口 8500是http端口
docker run -d -p 8500:8500 -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8600:8600/udp consul agent -dev -client=0.0.0.0

#自动重启
docker container update --restart=always 容器名称
```

## 补充：

根据Dockefile构建镜像，使用docker build命令，路径应该是Dockerfile文件所在目录路径而不是Dockerfile文件路径

### 1.(构建Go应用docker镜像)

[构建 Go 应用 docker 镜像的十八种姿势 - 万俊峰Kevin - 博客园 (cnblogs.com)](https://www.cnblogs.com/kevinwan/p/16033634.html)

```dockerfile
FROM golang:alpine AS builder

ENV GOPROXY https://goproxy.cn,direct

WORKDIR /build

ADD go.mod .
ADD go.sum .
RUN go mod download
COPY . .
# -o参数指定编译输出的名称，将会在当前目录下生成一个叫hello的可执行文件
RUN go build -o hello ./hello.go


FROM alpine

COPY --from=builder /usr/share/zoneinfo/Asia/Shanghai /usr/share/zoneinfo/Asia/Shanghai
ENV TZ Asia/Shanghai

WORKDIR /build
COPY --from=builder /build/hello /build/hello

CMD ["./hello"]
```



### 2.构建多环境镜像

需要先拉取linux相关版本包镜像(比如centos7)，然后再安装部署相关环境。

实例

```dockerfile
# 拉取centos7镜像
FROM centos:7
LABEL description="centos7 & python3.7.8"

# 远程拉取python包并且解压
RUN yum -y install wget && wget https://www.python.org/ftp/python/3.7.8/Python-3.7.8.tar.xz && tar xf Python-3.7.8.tar.xz

# 下载安装python3环境
RUN set -ex \
    # 预安装所需组件
    && yum update -y \
    && yum install -y tar libffi-devel zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make initscripts \
    && yum clean all \
    && yum -y install wget \
    # wget远程拉取python版本包
    && wget https://www.python.org/ftp/python/3.7.8/Python-3.7.8.tar.xz \
    && tar xf Python-3.7.8.tar.xz \
    && cd Python-3.7.8 \
    && ./configure prefix=/usr/local/python3 \
    && make \
    && make install \
    && make clean \
    && rm -rf /Python-3.7.8* \
    && yum install -y epel-release \
    && yum install -y python-pip
# 设置默认为python3 pip3
RUN set -ex \
    # 备份旧版本python
    && mv /usr/bin/python /usr/bin/python27 \
    && mv /usr/bin/pip /usr/bin/pip-python2.7 \
    # 配置默认为python3
    && ln -s /usr/local/python3/bin/python3.7 /usr/bin/python3 \
    && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
# 修复因修改python版本导致yum失效问题
RUN set -ex \
    && sed -i "s#/usr/bin/python#/usr/bin/python2.7#" /usr/bin/yum \
    && sed -i "s#/usr/bin/python#/usr/bin/python2.7#" /usr/libexec/urlgrabber-ext-down \
    && yum install -y deltarpm \
    # 安装nodejs环境
    && yum install -y nodejs

# 基础环境配置
RUN set -ex \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && yum install -y vim \
    # 安装定时任务组件
    && yum -y install cronie
# 支持中文
RUN yum install kde-l10n-Chinese -y
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
# 更新pip版本
#RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --upgrade pip3
#ENV LC_ALL zh_CN.UTF-8
#ENV TZ Asia/Shanghai
#ENV PATH /usr/local/python3/bin/:$PATH
#RUN ln -sf /usr/share/zoneinfo/Asia/ShangHai /etc/localtime

# 如果只依赖python环境则直接拉取python3镜像，可略去上面部分【注意python3 pip3改为python pip】
#FROM python:3.6
#MAINTAINER thy<485280869@qq.com>
RUN mkdir app
COPY ./KaoYan_Liberary/requirements.txt /app
WORKDIR /app
#RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
#RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
COPY ./KaoYan_Liberary /app

CMD ["python3", "main.py"]
```

