# Docker-compose

安装docker-compose前请先安装docker

docker-compose教程：https://blog.csdn.net/pushiqiang/article/details/78682323

## 安装

### 二进制安装（个人推荐）

1.从github上下载docker-compose二进制文件安装
Linux 上我们可以从 Github 上下载它的二进制包来使用，最新发行的版本地址：https://github.com/docker/compose/releases

```shell
sudo curl -L https://github.com/docker/compose/releases/download/v2.2.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```

 若是github访问太慢，可以用daocloud下载(推荐)

```shell
sudo curl -L https://get.daocloud.io/docker/compose/releases/download/v2.2.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```

2.添加可执行权限

```shell
sudo chmod +x /usr/local/bin/docker-compose
```

3.测试安装结果

```shell
$ docker-compose --version
```

### pip安装

```shell
sudo pip install docker-compose
```

## 卸载

```
docker-compose卸载只需要删除二进制文件就可以了。
sudo rm /usr/local/bin/docker-compose
```

## 示例

通过docker-compose构建一个在docker中运行的基于python flask框架的web应用。

**注意：**确保你已经安装了Docker Engine和Docker Compose。 您不需要安装Python或Redis，因为这两个都是由Docker镜像提供的。

#### Step 1: 

定义python应用

```
1.创建工程目录
$ mkdir compose_test
$ cd compose_test
$ mkdir src      # 源码文件夹
$ mkdir docker  # docker配置文件夹
目录结构如下： 
└── compose_test
    ├── docker
    │   └── docker-compose.yml
    ├── Dockerfile
    └── src
        ├── app.py
        └── requirements.txt
2.在compose_test/src/目录下创建python flask应用 compose_test/src/app.py文件。
from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/')
def hello():
    count = redis.incr('hits')
    return 'Hello World! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
3 .创建python 需求文件 compose_test/src/requirements.txt
flask
redis
```

#### Step 2: 

创建容器的Dockerfile文件

```
一个容器一个Dockerfile文件，在compose_test/目录中创建Dockerfile文件：

FROM python:3.7

COPY src/ /opt/src
WORKDIR /opt/src

RUN pip install -r requirements.txt
CMD ["python", "app.py"]
Dockerfile文件告诉docker了如下信息：

从Python 3.7的镜像开始构建一个容器镜像。 

复制src（即compose_test/src）目录到容器中的/opt/src目录。 

将容器的工作目录设置为/opt/src（通过docker exec -it your_docker_container_id_or_name bash 进入容器后的默认目录）。 
安装Python依赖关系。
将容器的默认命令设置为python app.py。
```

#### Step 3: 

定义docker-compose脚本

```
在compose_test/docker/目录下创建docker-compose.yml文件，并在里面定义服务，内容如下：

version: '3'
services:
  web:
    build: ../
    ports:
     - "5000:5000"
  redis:
    image: redis:3.0.7
这个compose文件定义了两个服务，即定义了web和redis两个容器。 
web容器： 
	使用当前docker-compose.yml文件所在目录的上级目录（compose_test/Dockerfile）中的Dockerfile构建映像。 
	将容器上的暴露端口5000映射到主机上的端口5000。 我们使用Flask Web服务器的默认端口5000。 
redis容器： 
	redis服务使用从Docker Hub提取的官方redis镜像3.0.7版本。
```

#### Step 4: 

使用Compose构建并运行您的应用程序

```
在compose_test/docker/目录下执行docker-compose.yml文件：
$ docker-compose up
#若是要后台运行： $ docker-compose up -d
#若不使用默认的docker-compose.yml 文件名：
$ docker-compose -f server.yml up -d 
然后在浏览器中输入http://0.0.0.0:5000/查看运行的应用程序。
```

#### Step 5: 

编辑compose文件以添加文件绑定挂载

```yaml
上面的代码是在构建时静态复制到容器中的，即通过Dockerfile文件中的COPY src /opt/src命令实现物理主机中的源码复制到容器中，这样在后续物理主机src目录中代码的更改不会反应到容器中。 
可以通过volumes 关键字实现物理主机目录挂载到容器中的功能（同时删除Dockerfile中的COPY指令，不需要创建镜像时将代码打包进镜像，而是通过volums动态挂载，容器和物理host共享数据卷）：
version: '3'
services:
  web:
    build: ../
    ports:
     - "5000:5000"
    volumes:
     - ../src:/opt/src
  redis:
    image: "redis:3.0.7"
```

通过volumes（卷）将主机上的项目目录（compose_test/src）挂载到容器中的/opt/src目录，允许您即时修改代码，而无需重新构建镜像。

#### Step 6: 

重新构建和运行应用程序

```
使用更新的compose文件构建应用程序，然后运行它。
$ docker-compose up -d
```

## 常用命令

地址：[(*´∇｀*) 欢迎回来！ (cnblogs.com)](https://www.cnblogs.com/itoak/p/12925540.html)

1.up [options]

该命令十分强大，它将尝试自动完成包括构建镜像，（重新）创建服务，启动服务，并关联服务相关容器的一系列操作。链接的服务都将会被自动启动，除非已经处于运行状态。

选项：

- -d 在后台运行服务容器
- --no-color 不使用颜色来区分不同的服务的控制台输出
- --no-deps 不启动服务所链接的容器
- --force-recreate 强制重新创建容器，不能与--no-recreate同时使用
- --no-recreate 如果容器已经存在了，则不重新创建，不能与 --force-recreate 同时使用
- --no-build不自动构建缺失的服务镜像
- -t，--timeout TIMEOUT 停止容器时候的超时（默认为10秒）

2.build [options]

格式为：docker-compose build [选项] [服务 ...]

构建（重新构建项目中的服务容器）。

可以随时在项目目录下运行docker-compose build来中心构建服务。

选项包括：

- --force-rm删除构建过程中的临时容器。
- --no-cache构建镜像过程中不使用cache（这将加长构建过程，默认使用cache可能导致更新没用）
- --pull始终尝试通过pull来获取更新版本的镜像

3.version

格式为docker-compose version

打印版本信息

4.config

验证Compose文件格式是否正确，若正确显示配置，若格式错误显示错误原因