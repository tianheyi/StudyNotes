# Protobuf

## 安装Protoc

### Go

参考：
1.[windows下安装golang使用protobuf - Go语言中文网 - Golang中文社区 (studygolang.com)](https://studygolang.com/articles/17700)
2.[【转】windows 下 goprotobuf 的安装与使用 - 苍洱 - 博客园 (cnblogs.com)](https://www.cnblogs.com/a9999/p/7659769.html)

1.安装 protoc

- 在[该链接](https://github.com/google/protobuf/releases/tag/v3.3.0)下下
  载[protoc-3.3.0-win32.zip](https://github.com/google/protobuf/releases/download/v3.3.0/protoc-3.3.0-win32.zip)的包
- 将文件解压到某一文件夹
- 将解压出来的文件夹下的 /bin 路径添加到环境变量path中

2、下载protobuf模块以及插件

```shell
# protoc-gen-go是用来将protobuf的的代码转换成go语言代码的一个插件
$ go get -u github.com/golang/protobuf/protoc-gen-go
# proto是protobuf在golang中的接口模块
$ go get -u github.com/golang/protobuf/proto
```

3.进入protobuf文件所在目录下，执行：

`protoc -I . --go_out=plugins=grpc:. *.proto`
即可生成相关go 文件（**详情查看编译protobuf部分**）

**注意**：如果出现protoc-gen-go: unable to determine Go import path for "myproto.proto"
解决：在myproto.proto文件中的代码`package pb;`下面加入`option go_package = ".;proto";`详情见go_package

### python

1.下载依赖

```
pip install grpcio
pip install grpcio-tools  # python的grpc tools包含了protoc及其插件，用来生成客户端和服务端代码
```

2.在protobuf文件所在目录下执行
`python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I . *.proto`
即可生成相关py文件

注意：会生成两个py文件，如果运行报错，要修改xxx_pb2_grpc.py中的`import user_pb2 as user__pb2`改成`from . import user_pb2 as user__pb2`

## 注意事项

- **package主要是用于避免命名冲突的**，不同的项目（project）需要指定不同的package。同一package下msg名称必须唯一。
- import，如果proto文件需要使用在其他proto文件中已经定义的结构，可以使用import引入。
- option go_package = "github.com/protocolbuffers/protobuf/examples/go/tutorialpb"; 
  **go_packge有两层意思**，一层是表明如果要引用这个proto生成的文件的时候import后面的路径；一层是如果不指定--go_opt（默认值），生成的go文件存放的路径。
- message成员编号，可以不从1开始，但不能重复，且数字19000-19999不能用，若在 .proto 文件中使用了这些预留的编号 protocol buffer 编译器会发出警告。（最小的字段编号为 1，最大的为 2^29 - 1，或 536,870,911。）
- 可以使用message嵌套
- 定义数组、切片用repeated关键字
- 可以使用枚举enum
- 可以使用联合体。oneof关键字，成员编号，不能重复。



**示例:**

```protobuf
//  指定版本号，默认是proto2
syntax = "proto3";
//  指定所在包包名
package pb;
//定义枚举
enum Week {
  Monday = 0;//枚举值必须从0开始
  Turesday = 1;
}
//  定义消息体
message Student {
  //  =1 =2 是标识该字段在二进制编码中的唯一"标记"
  int32 age = 1;  // 可以不从1开始，但是不能重复，也不能用19000-19999，不同message下的可以重复
  string name = 2;
  People p = 3;
  repeated int32 score = 4;//数组或切片
  //枚举
  Week w = 5;
  //联合体
  oneof data {
    string teacher = 6;
    string class = 7;
  }
}
// 消息体可以嵌套
message People {
  int32 weight = 1;
}
```

## 编译protobuf

### Go

go语言中编译命令，进入probuf文件所在目录下，执行：
`protoc -I (1) (2) --go_out=plugins=grpc:(3) `  --->  生成xxx.pb.go 文件

(1)proto文件所在目录，如果是当前目录则为`.`

(2)编译哪些proto文件，*.proto表示全部proto文件

(3)将生成的文件存放到的位置，`.`表示当前目录，目录必须存在

**注意**：如果出现protoc-gen-go: unable to determine Go import path for "myproto.proto"
解决：在myproto.proto文件中的代码`package pb;`下面加入`option go_package = "../pb";`

### Python

在protobuf文件所在目录下执行：
`python -m grpc_tools.protoc -I . *.proto --python_out=. --grpc_python_out=.`
即可生成相关py文件

注意：会生成两个py文件，如果运行报错，要修改xxx_pb2_grpc.py中的`import user_pb2 as user__pb2`改成`from . import user_pb2 as user__pb2`

## protobuf中添加rpc服务

* 语法：

  ```protobuf
  service 服务名称 {
      rpc 函数名(参数:消息体) returns (返回值:信息体)
  }
  message People {
  	string name = 1;
  }
  message Student {
  	int32 age = 2;
  }
  例：
  service hello {
  	rpc HelloWorld(People) returns (Student);
  }
  ```

* 知识点：

  * 默认，protobuf在编译期间，不编译服务。要想使之编译，需要使用gRPC。
  * go使用的编译指令为：
    * `protoc --go_out=plugins=grpc:. *.proto`
    * `protoc --go_out=plugins=grpc:生成go文件的位置 proto文件位置`

## protobuf类型

一个标量消息字段可以含有一个如下的类型——该表格展示了定义于.proto文件中的类型，以及与之对应的、在自动生成的访问类中定义的类型：

| .proto Type | Notes                                                        | Python Type | Go Type |
| ----------- | ------------------------------------------------------------ | ----------- | ------- |
| double      |                                                              | float       | float64 |
| float       |                                                              | float       | float32 |
| int32       | 使用变长编码，对于负值的效率很低，如果你的域有可能有负值，请使用sint64替代 | int         | int32   |
| uint32      | 使用变长编码                                                 | int         | uint32  |
| uint64      | 使用变长编码                                                 | int         | uint64  |
| sint32      | 使用变长编码，这些编码在负值时比int32高效的多                | int         | int32   |
| sint64      | 使用变长编码，有符号的整型值。编码时比通常的int64高效。      | int         | int64   |
| fixed32     | 总是4个字节，如果数值总是比总是比228大的话，这个类型会比uint32高效。 | int         | uint32  |
| fixed64     | 总是8个字节，如果数值总是比总是比256大的话，这个类型会比uint64高效。 | int         | uint64  |
| sfixed32    | 总是4个字节                                                  | int         | int32   |
| sfixed64    | 总是8个字节                                                  | int         | int64   |
| bool        |                                                              | bool        | bool    |
| string      | 一个字符串必须是UTF-8编码或者7-bit ASCII编码的文本。         | str         | string  |
| bytes       | 可能包含任意顺序的字节数据。                                 | str         | []byte  |

你可以在文章[Protocol Buffer 编码](https://developers.google.com/protocol-buffers/docs/encoding?hl=zh-cn)中，找到更多“序列化消息时各种类型如何编码”的信息

### 类型默认值

当一个消息被解析的时候，如果被编码的信息不包含一个特定的singular元素，被解析的对象锁对应的域被设置位一个默认值，对于不同类型指定如下：

- 对于string，默认是一个空string
- 对于bytes，默认是一个空的bytes
- 对于bool，默认是false
- 对于数值类型，默认是0
- 对于枚举，默认是第一个定义的枚举值，必须为0;
- 对于消息类型（message），域没有被设置，确切的消息是根据语言确定的，详见[generated code guide](https://developers.google.com/protocol-buffers/docs/reference/overview?hl=zh-cn)
  对于可重复域的默认值是空（通常情况下是对应语言中空列表）。
  注：对于标量消息域，一旦消息被解析，就无法判断域释放被设置为默认值（例如，例如boolean值是否被设置为false）还是根本没有被设置。你应该在定义你的消息类型时非常注意。例如，比如你不应该定义boolean的默认值false作为任何行为的触发方式。也应该注意如果一个标量消息域被设置为标志位，这个值不应该被序列化传输。
  查看[generated code guide](https://developers.google.com/protocol-buffers/docs/reference/overview?hl=zh-cn)选择你的语言的默认值的工作细节。

### go_package

`option go_package=".;proto";`	//前一个参数用于指定生成文件的位置，后一个参数指定生成的 .go 文件的 package(如果第二个参数不写默认对应位置下的package)

`option go_package="../../common/stream/proto/v1";`	//指定生成的.go文件位置

使用go_package了就不用package了，并且go_package不会影响到其他语言的生成

java也有java_package

### protobuf引用其他protobuf文件

```protobuf
//base.proto
syntax = "proto3";

option go_package = ".;proto";
message Pong{
    string id = 1;
}
```

```protobuf
//hello.proto 与base同级
syntax = "proto3";
import "base.proto";    //引入base中定义的
import "google/protobuf/empty.proto";//引入公共内置的
option go_package = ".;proto";
service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
    rpc Ping(google.protobuf.Empty) returns (Pong);
}

message HelloRequest {
    string url = 1;
    string name = 2;
}

message HelloReply {
    string message = 1;

    message Result {
        string name = 1;
        string url = 2;
    }

    repeated Result data = 2;
}
```

### message嵌套

```protobuf
message Hello {
	string name = 1;
	message Result{
		string r = 1;
	}
}
```

### 枚举类型

```protobuf
enum Gender {
	MALE = 0;
	FEMALE = 1;
}
```

### map类型

```protobuf
message H{
	string name = 1;
	string url	= 2;
	Gender g = 3;
	map<string,string> mp = 4;
}
```

### protobuf内置timestamp类型

```protobuf
import "google/protobuf/timestamp.proto"

message H{
	string name = 1;
	string url	= 2;
	Gender g = 3;
	map<string,string> mp = 4;
	google.protobuf.Timestamp addTime = 5;
}
```

# grpc

https://www.topgoer.cn/docs/grpc/grpc-1d2ud3fh1d74h

## 调试工具

- 命令行：

  ```
  # 查看所有的服务
  $ grpc_cli ls localhost:50051 
  
  # 查看 Greeter 服务的详细信息
  $ grpc_cli ls localhost:50051 helloworld.Greeter -l
  
  # 查看 Greeter.SayHello 方法的详细信息
  $ grpc_cli ls localhost:50051 helloworld.Greeter.SayHello -l
  
  # 远程调用
  $ grpc_cli call localhost:50051 SayHello "name: 'gRPC CLI'"
  ```

- 界面：https://github.com/fullstorydev/grpcui

- **go和python使用grpc调试的前置条件**

  **go**

  1. 执行`go install github.com/fullstorydev/grpcui/cmd/grpcui@latest`
  2. 会在环境变量`$GOPATH`的`bin`目录下生成一个`grpcui.exe`，只需要把`$GOPATH/bin`添加到环境变量`PATH`中即可。
  3. 控制台执行`grpcui -help`，查看是否安装成功
  4. 注册反射：在grpc服务器代码中添加`reflection.Register(server)`，这样就不需要指定proto文件位置了
  5. 启动grpc服务
  6. 控制台执行`grpcui -plaintext 被调试的grpc地址:被调试的grpc端口`，会在浏览器打开一个调试页面

  **python**

  - 需要手动安装grpc reflection：`pip install grpcio-reflection`

  - grpc服务端代码引入安装的reflection包，实例：

    ```python
    # 生成grpc服务器实例
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册本地服务到服务器中
    goods_pb2_grpc.add_GoodsServicer_to_server(GoodsServicer(), server)
    # 使用grpc调试只需要添加以下代码
    from grpc_reflection.v1alpha import reflection
    reflection.enable_server_reflection([header.service_name() for header in server._state.generic_handlers], server)
    # 启动grpc服务器
    ```

  - 控制台执行`grpcui -plaintext 被调试的grpc地址:被调试的grpc端口`，会在浏览器打开一个调试页面

## 安装

python：

1. `pip install grpcio`
2. `pip install grpcio-tools googleapis-common-protos`

go:

## 四种通信模式及其应用场景选型

gRPC有四种通信方式,分别是：简单 RPC（Unary RPC）、服务端流式 RPC （Server streaming RPC）、客户端流式 RPC （Client streaming RPC）、双向流式 RPC（Bi-directional streaming RPC）。它们主要有以下特点：

| 服务类型       | 特点                                                         |
| -------------- | ------------------------------------------------------------ |
| 简单 RPC       | 一般的rpc调用，传入一个请求对象，返回一个返回对象            |
| 服务端流式 RPC | 传入一个请求对象，服务端可以返回多个结果对象                 |
| 客户端流式 RPC | 客户端传入多个请求对象，服务端返回一个结果对象               |
| 双向流式 RPC   | 结合客户端流式RPC和服务端流式RPC，可以传入多个请求对象，返回多个结果对象 |

### 简单 RPC	

一般的rpc调用，传入一个请求对象，返回一个返回对象

proto语法：

```protobuf
rpc simpleHello(Person) returns (Result) {}
```

客户端发起一次请求，服务端响应一个数据，即标准RPC通信。
这种模式，一个每一次都是发起一个独立的tcp连接，走一次三次握手和四次挥手！

### 服务端流式 RPC	

传入一个请求对象，服务端可以返回多个结果对象

proto语法 :

```protobuf
rpc serverStreamHello(Person) returns (stream Result) {}
```

服务端流 RPC 下，客户端发出一个请求，但不会立即得到一个响应，而是在服务端与客户端之间建立一个单向的流，服务端可以随时向流中写入多个响应消息，最后主动关闭流，而客户端需要监听这个流，不断获取响应直到流关闭

**应用场景举例**：
典型的例子是客户端向服务端发送一个股票代码，服务端就把该股票的实时数据源源不断的返回给客户端。

### 客户端流式 RPC	

客户端传入多个请求对象，服务端返回一个结果对象

proto语法 :

```protobuf
rpc clientStreamHello(stream Person) returns (Result) {}
```

**应用场景**：
物联网终端向服务器报送数据。

### 双向流式 RPC	

结合客户端流式RPC和服务端流式RPC，可以传入多个请求对象，返回多个结果对象

proto语法 :

```protobuf
rpc biStreamHello(stream Person) returns (stream Result) {}
```

应用场景：聊天应用。

#### **server**

```go
func (*greeter) SayHelloStream(stream proto.Greeter_SayHelloStreamServer) error {
    for {
        args, err := stream.Recv()
        if err != nil {
            if err == io.EOF {
                return nil
            }
            return err
        }
        fmt.Println("Recv: " + args.Name)
        reply := &proto.HelloReply{Message: "hi " + args.Name}
        err = stream.Send(reply)
        if err != nil {
            return err
        }
    }
}
```

#### **client**

通过一个 goroutine 发送消息，主程序的 `for` 循环接收消息。

```go
func main() {
    ....
    client := proto.NewGreeterClient(conn)
    // 流处理
    stream, err := client.SayHelloStream(context.Background())
    if err != nil {
        log.Fatal(err)
    }

    // 发送消息
    go func() {
        for {
            if err := stream.Send(&proto.HelloRequest{Name: "zhangsan"}); err != nil {
                log.Fatal(err)
            }
            time.Sleep(time.Second)
        }
    }()

    // 接收消息
    for {
        reply, err := stream.Recv()
        if err != nil {
            if err == io.EOF {
                break
            }
            log.Fatal(err)
        }
        fmt.Println(reply.Message)
    }
}
```

## metadata机制

类似于http的header

### 新建metadata

MD 类型实际上是map，key是string，value是string类型的slice。

```go
type MD map[string][]string
```

创建的时候可以像创建普通的map类型一样使用new关键字进行创建：

```go
// 第一种方式,通过给New方法传入一个map
// 由于map的key不能重复，因为默认key会被转成小写，所以如果要kv一对多需要使用不同大小写的key，比较麻烦，所以这种一般只用于kv一对一的时候
md := metadata.New(map[string]string{"key1": "val1", "key2": "val2"})
// 最终变成：
//	name: []string{"bobo"}
//	password: []string{"123456"}
// 源码:
func New(m map[string]string) MD {
	md := make(MD, len(m))
	for k, val := range m {
		key := strings.ToLower(k)
		md[key] = append(md[key], val)
	}
	return md
}

//第二种方式 key不区分大小写，会被默认统一转成小写。
md := metadata.Pairs(
    "key1", "val1",
    "key1", "val1-2", // "key1" will have map value []string{"val1", "val1-2"}
    "key2", "val2",
)
// 源码
func Pairs(kv ...string) MD {
	if len(kv)%2 == 1 {
		panic(fmt.Sprintf("metadata: Pairs got the odd number of input pairs for metadata: %d", len(kv)))
	}
	md := make(MD, len(kv)/2)
	for i := 0; i < len(kv); i += 2 {
		key := strings.ToLower(kv[i])
		md[key] = append(md[key], kv[i+1])
	}
	return md
}
```

###  发送metadata

- NewOutgoingContext：创建一个附加了传出 md 的新上下文，可供外部的 gRPC 客户端、服务端使用

```go
// 两种构建方式，参考上面
md := metadata.Pairs("key", "val")

// 新建一个有 metadata 的 context
ctx := metadata.NewOutgoingContext(context.Background(), md)
// 需要注意一点，在新增 metadata 信息时，务必使用 Append 类别的方法，否则如果直接 New 一个全新的 md，将会导致原有的 metadata 信息丢失（除非你确定你希望得到这样的结果）。
newCtx := metadata.AppendToOutgoingContext(ctx, "eddycjy", "Go 语言编程之旅")
// 单向 RPC
response, err := client.SomeRPC(ctx, someRequest)
```

### 接收metadata

- NewIncomingContext：创建一个附加了所传入的 md 新上下文，仅供自身的 gRPC 服务端内部使用。

```go
func (s *server) SomeRPC(ctx context.Context, in *pb.SomeRequest) (*pb.SomeResponse, err) {
	// 从上下文中通过FromIncomingContext接收
    md, ok := metadata.FromIncomingContext(ctx)
    // do something with metadata
}
```

## 拦截器机制

### interceptor

server端(可以实现验证token等)

```go
// 1.先实现这样一个函数 相当于中间件
interceptor := func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (resp interface{}, err error) {
		fmt.Println("接收到了一个新的请求")
		res, err := handler(ctx, req) // 继续处理请求
		fmt.Println("请求已经完成")
		return res, err
	}
// 2.使用，
opt := grpc.UnaryInterceptor(interceptor)
g := grpc.NewServer(opt)
proto.RegisterGreeterServer(g, &Server{})
lis, err := net.Listen("tcp", "0.0.0.0:50051")
if err != nil {
    panic("failed to listen:" + err.Error())
}
err = g.Serve(lis)
if err != nil {
    panic("failed to start grpc:" + err.Error())
}
```

client端

```go
interceptor := func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		start := time.Now()
		err := invoker(ctx, method, req, reply, cc, opts...)
		fmt.Printf("耗时：%s\n", time.Since(start))
		return err
	}
var opts []grpc.DialOption
opts = append(opts, grpc.WithInsecure())
opts = append(opts, grpc.WithUnaryInterceptor(interceptor))//还有grpc.WithPerRPCCredentials()方法，也是对interceptor的一种封装
conn, err := grpc.Dial("127.0.0.1:50051", opts...)
if err != nil {
    panic(err)
}
defer conn.Close()

c := proto.NewGreeterClient(conn)
r, err := c.SayHello(context.Background(), &proto.HelloRequest{Name: "bobby"})
if err != nil {
    panic(err)
}
fmt.Println(r.Message)
```

### 自定义认证

#### 实现Token认证

##### 先改造服务端

有了上文验证器的经验，那么可以采用同样的方式，写一个拦截器，然后在初始化 server 时候注入。（基于metadata+拦截器+token）

1. **实现认证函数：**

   ```go
   func Auth(ctx context.Context) error {
       // metadata.FromIncomingContext 从上下文读取token，然后判断是否通过认证。
       md, ok := metadata.FromIncomingContext(ctx)
       if !ok {
           return fmt.Errorf("missing credentials")
       }
   
       var token string
       if val, ok := md["x-token"]; ok {
           token = val[0]
       }
   
       if !ValidateToken(token) {
           return grpc.Errorf(codes.Unauthenticated, "invalid token")
       }
       return nil
   }
   ```

   

2. **构造拦截器：**

   ```go
   var authInterceptor grpc.UnaryServerInterceptor
   authInterceptor = func(
       ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
   ) (resp interface{}, err error) {
       //拦截普通方法请求，验证 Token
       err = Auth(ctx)
       if err != nil {
           return
       }
       // 继续处理请求
       return handler(ctx, req)
   }
   ```

3. **初始化：**

   ```go
   server := grpc.NewServer(
       grpc.UnaryInterceptor(
           grpc_middleware.ChainUnaryServer(
               authInterceptor,
               grpc_validator.UnaryServerInterceptor(),//下面的验证器
           ),
       ),
       grpc.StreamInterceptor(
           grpc_middleware.ChainStreamServer(
               grpc_validator.StreamServerInterceptor(),
           ),
       ),
   )
   ```

##### 最后是客户端改造

1. 客户端需要实现 `PerRPCCredentials` 接口。

   在 gRPC 中所提供的 PerRPCCredentials，是 gRPC 默认提供用于自定义认证 Token 的接口，它的作用是将所需的安全认证信息添加到每个 RPC 方法的上下文中。其包含两个接口方法，如下：

   - GetRequestMetadata：获取当前请求认证所需的元数据（metadata）。
   - RequireTransportSecurity：是否需要基于 TLS 认证进行安全传输。

   ```go
   type PerRPCCredentials interface {
       GetRequestMetadata(ctx context.Context, uri ...string) (
           map[string]string, error,
       )
       RequireTransportSecurity() bool
   }
   ```

   `GetRequestMetadata` 方法返回认证需要的必要信息，`RequireTransportSecurity` 方法表示是否启用安全链接，在生产环境中，一般都是启用的，但为了测试方便，暂时这里不启用了。

   **实现接口：**

   ```go
   type Authentication struct {
       Token     string
   }
   
   func (a *Authentication) GetRequestMetadata(context.Context, ...string) (
       map[string]string, error,
   ) {
       return map[string]string{"x-token": a.Token}, nil
   }
   
   func (a *Authentication) RequireTransportSecurity() bool {
       return false
   }
   ```

2. **连接：**

   ```go
   conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithPerRPCCredentials(&auth))
   ```

   好了，现在我们的服务就有 Token 认证功能了。如果token验证错误，客户端就会收到：

   ```text
   2021/10/11 20:39:35 rpc error: code = Unauthenticated desc = invalid token
   exit status 1
   ```

   如果token正确，则可以正常返回。

#### 证书认证

证书认证分两种方式：单向认证，双向认证

##### 单向证书认证

先看一下单向认证方式：

生成证书

首先通过 openssl 工具生成自签名的 SSL 证书。

**1、生成私钥：**

```text
openssl genrsa -des3 -out server.pass.key 2048
```

**2、去除私钥中密码：**

```text
openssl rsa -in server.pass.key -out server.key
```

**3、生成 csr 文件：**

```text
openssl req -new -key server.key -out server.csr -subj "/C=CN/ST=beijing/L=beijing/O=grpcdev/OU=grpcdev/CN=example.grpcdev.cn"
```

**4、生成证书：**

```text
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

**gRPC 代码**

证书有了之后，剩下的就是改造程序了，首先是服务端代码。

```text
// 证书认证-单向认证
creds, err := credentials.NewServerTLSFromFile("keys/server.crt", "keys/server.key")
if err != nil {
    log.Fatal(err)
    return
}
server := grpc.NewServer(grpc.Creds(creds))
```

只有几行代码需要修改，很简单，接下来是客户端。

由于是单向认证，不需要为客户端单独生成证书，只需要把服务端的 crt 文件拷贝到客户端对应目录下即可。

```text
// 证书认证-单向认证
creds, err := credentials.NewClientTLSFromFile("keys/server.crt", "example.grpcdev.cn")
if err != nil {
    log.Fatal(err)
    return
}
conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(creds))
```

好了，现在我们的服务就支持单向证书认证了。

但是还没完，这里可能会遇到一个问题：

```text
2021/10/11 21:32:37 rpc error: code = Unavailable desc = connection error: desc = "transport: authentication handshake failed: x509: certificate relies on legacy Common Name field, use SANs or temporarily enable Common Name matching with GODEBUG=x509ignoreCN=0"
exit status 1
```

原因是 Go 1.15 开始废弃了 CommonName，推荐使用 SAN 证书。如果想要兼容之前的方式，可以通过设置环境变量的方式支持，如下：

```text
export GODEBUG="x509ignoreCN=0"
```

但是需要注意，从 Go 1.17 开始，环境变量就不再生效了，必须通过 SAN 方式才行。所以，为了后续的 Go 版本升级，还是早日支持为好。

##### 双向证书认证

最后来看看双向证书认证。

还是先生成证书，但这次有一点不一样，我们需要生成带 SAN 扩展的证书。
什么是 SAN？**SAN（Subject Alternative Name）是 SSL 标准 x509 中定义的一个扩展。使用了 SAN 字段的 SSL 证书，可以扩展此证书支持的域名，使得一个证书可以支持多个不同域名的解析。**

将默认的 OpenSSL 配置文件拷贝到当前目录。

Linux 系统在：

```text
/etc/pki/tls/openssl.cnf
```

Mac 系统在：

```text
/System/Library/OpenSSL/openssl.cnf
```

修改临时配置文件，找到 `[ req ]` 段落，然后将下面语句的注释去掉。

```text
req_extensions = v3_req # The extensions to add to a certificate request
```

接着添加以下配置：

```text
[ v3_req ]
# Extensions to add to a certificate request

basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = www.example.grpcdev.cn
```

`[ alt_names ]` 位置可以配置多个域名，比如：

```text
[ alt_names ]
DNS.1 = www.example.grpcdev.cn
DNS.2 = www.test.grpcdev.cn
```



为了测试方便，这里只配置一个域名。

**1、生成 ca 证书：**

```text
openssl genrsa -out ca.key 2048

openssl req -x509 -new -nodes -key ca.key -subj "/CN=example.grpcdev.com" -days 5000 -out ca.pem
```

**2、生成服务端证书：**

```text
# 生成证书
openssl req -new -nodes \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=grpcdev/OU=grpcdev/CN=www.example.grpcdev.cn" \
    -config <(cat openssl.cnf \
        <(printf "[SAN]\nsubjectAltName=DNS:www.example.grpcdev.cn")) \
    -keyout server.key \
    -out server.csr

# 签名证书
openssl x509 -req -days 365000 \
    -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
    -extfile <(printf "subjectAltName=DNS:www.example.grpcdev.cn") \
    -out server.pem
```

**3、生成客户端证书：**

```text
# 生成证书
openssl req -new -nodes \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=grpcdev/OU=grpcdev/CN=www.example.grpcdev.cn" \
    -config <(cat openssl.cnf \
        <(printf "[SAN]\nsubjectAltName=DNS:www.example.grpcdev.cn")) \
    -keyout client.key \
    -out client.csr

# 签名证书
openssl x509 -req -days 365000 \
    -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
    -extfile <(printf "subjectAltName=DNS:www.example.grpcdev.cn") \
    -out client.pem
```

**gRPC 代码**

接下来开始修改代码，先看服务端：

```text
// 证书认证-双向认证
// 从证书相关文件中读取和解析信息，得到证书公钥、密钥对
cert, _ := tls.LoadX509KeyPair("cert/server.pem", "cert/server.key")
// 创建一个新的、空的 CertPool
certPool := x509.NewCertPool()
ca, _ := ioutil.ReadFile("cert/ca.pem")
// 尝试解析所传入的 PEM 编码的证书。如果解析成功会将其加到 CertPool 中，便于后面的使用
certPool.AppendCertsFromPEM(ca)
// 构建基于 TLS 的 TransportCredentials 选项
creds := credentials.NewTLS(&tls.Config{
    // 设置证书链，允许包含一个或多个
    Certificates: []tls.Certificate{cert},
    // 要求必须校验客户端的证书。可以根据实际情况选用以下参数
    ClientAuth: tls.RequireAndVerifyClientCert,
    // 设置根证书的集合，校验方式使用 ClientAuth 中设定的模式
    ClientCAs: certPool,
})
```

再看客户端：

```text
// 证书认证-双向认证
// 从证书相关文件中读取和解析信息，得到证书公钥、密钥对
cert, _ := tls.LoadX509KeyPair("cert/client.pem", "cert/client.key")
// 创建一个新的、空的 CertPool
certPool := x509.NewCertPool()
ca, _ := ioutil.ReadFile("cert/ca.pem")
// 尝试解析所传入的 PEM 编码的证书。如果解析成功会将其加到 CertPool 中，便于后面的使用
certPool.AppendCertsFromPEM(ca)
// 构建基于 TLS 的 TransportCredentials 选项
creds := credentials.NewTLS(&tls.Config{
    // 设置证书链，允许包含一个或多个
    Certificates: []tls.Certificate{cert},
    // 要求必须校验客户端的证书。可以根据实际情况选用以下参数
    ServerName: "www.example.grpcdev.cn",
    RootCAs:    certPool,
})
```

大功告成。

## 验证器机制

地址：（[grpc实战：跨语言的rpc框架到底好不好用，试试就知道 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/451998058)）

这个需求是很自然会想到的，因为涉及到接口之间的请求，那么对参数进行适当的校验是很有必要的。
**如果是内部的一些可以不用验证，毕竟验证也耗费资源**

在这里我们使用 **protoc-gen-govalidators** 和 **go-grpc-middleware** 来实现。

1. 先安装：

   ```shell
   go get github.com/mwitkow/go-proto-validators/protoc-gen-govalidators
   go get github.com/grpc-ecosystem/go-grpc-middleware
   ```

2. 接下来修改 proto 文件：

   proto

   ```protobuf
   import "github.com/mwitkow/go-proto-validators@v0.3.2/validator.proto";
   
   message HelloRequest {
       string name = 1 [
           (validator.field) = {regex: "^[z]{2,5}$"}
       ];
   }
   ```

   在这里对 `name` 参数进行校验，需要符合正则的要求才可以正常请求。

   还有其他验证规则，比如对数字大小进行验证等，这里不做过多介绍。

3. 接下来生成 *.pb.go 文件：

   ```
   protoc  \
       --proto_path=${GOPATH}/pkg/mod \
       --proto_path=${GOPATH}/pkg/mod/github.com/gogo/protobuf@v1.3.2 \
       --proto_path=. \
       --govalidators_out=. --go_out=plugins=grpc:.\
       *.proto
   ```

   执行成功之后，目录下会多一个 helloworld.validator.pb.go 文件。

   这里需要特别注意一下，使用之前的简单命令是不行的，需要使用多个 `proto_path` 参数指定导入 proto 文件的目录。

   官方给了两种依赖情况，一个是 google protobuf，一个是 gogo protobuf。我这里使用的是第二种。

   **注意**：即使使用上面的命令，也有可能会遇到这个报错：

   ```text
   Import "github.com/mwitkow/go-proto-validators/validator.proto" was not found or had errors
   ```

   但不要慌，大概率是引用路径的问题，一定要看好自己的安装版本，以及在 `GOPATH` 中的具体路径。

4. 最后是服务端代码改造：

   - 引入包：

     ```
     grpc_middleware "github.com/grpc-ecosystem/go-grpc-middleware"
     grpc_validator "github.com/grpc-ecosystem/go-grpc-middleware/validator"
     ```

   - 然后在初始化的时候增加验证器功能（即添加到拦截器中）：

     ```
     server := grpc.NewServer(
         grpc.UnaryInterceptor(
             grpc_middleware.ChainUnaryServer(
                 grpc_validator.UnaryServerInterceptor(),
             ),
         ),
         grpc.StreamInterceptor(
             grpc_middleware.ChainStreamServer(
                 grpc_validator.StreamServerInterceptor(),
             ),
         ),
     )
     ```

5. 启动程序之后，我们再用之前的客户端代码来请求，会收到报错：

   ```
   2021/10/11 18:32:59 rpc error: code = InvalidArgument desc = invalid field Name: value 'zhangsan' must be a string conforming to regex "^[z]{2,5}$"
   exit status 1
   ```

   因为 `name: zhangsan` 是不符合服务端正则要求的，但是如果传参 `name: zzz`，就可以正常返回了。

## 错误处理机制

地址：https://zhuanlan.zhihu.com/p/435011704

### **判断Error的错误原理**

要了解怎么处理`gRPC`的`error`之前，我们首先来看下`Go`普通的`error`是怎么处理的。

我们在判断一个`error`的根因，需要根因`error`是一个固定地址的指针类型，这样我们才能够使用官方的`errors.Is`方法判断他是否为根因。

我们先看这个代码`errors.Is(wrapNewPointerError(), fmt.Errorf("i am error"))`的执行步骤，首先构造了一个`error`，然后使用官方`%w`的方式将`error`进行了包装，我们在使用`errors.Is`方法判断的时候，底层函数会将`error`解包来判断两个`error`的地址是否一致。

### gRPC网络传输的Error

**grpc网络传输的error不能简单通过官方提供的errors.Is()来进行判断。**
我们客户端在获取到`gRPC`的`error`的时候，是否可以使用上文说的官方`errors.Is`进行判断呢。如果我们直接使用该方法，通过判断error地址是否相等，是无法做到的。原因是因为我们在使用`gRPC`的时候，在远程调用过程中，客户端获取的服务端返回的`error`，在`tcp`传递的时候实际上是一串文本。客户端拿到这个文本，是要将其反序列化转换为`error`，在这个反序列化的过程中，其实是`new`了一个新的`error`地址，这样就无法判断`error`地址是否相等。

**grpc与http对比：**

1. grpc的meta对应http的请求头，code对应http的状态码，error对应http的具体报错信息。
2. grpc客户端远程调用服务端方法时，得到的是(resp,error)，我们需要通过status.FromError将error转化为status，继而通过status获取响应的code和error。
3. grpc服务端向客户端返回响应的时候，返回的格式也是(resp, status.Error(code,err.Error()))。

为了更好的解释`gRPC`网络传输的`error`，以下描述了整个`error`的处理流程。

- 客户端通过`invoker`方法将请求发送到服务端。
- 服务端通过`processUnaryRPC`方法，获取到用户代码的`error`信息。
- 服务端通过`status.FromError`方法，将`error`转化为`status.Status`。
- 服务端通过`WriteStatus`方法将`status.Status`里的数据，写入到`grpc-status`、`grpc-message`、`grpc-status-details-bin`的`header`头里。
- 客户端通过网络获取到这些`header`头，使用`strconv.ParseInt`解析到`grpc-status`信息、`decodeGrpcMessage`解析到`grpc-message`信息、`decodeGRPCStatusDetails`解析为`grpc-status-details-bin`信息。
- 客户端通过`a.Status().Err()`获取到用户代码的错误。

![img](https://pic1.zhimg.com/80/v2-6d616348cfbe3e5d679b5935fc8c2998_720w.webp)

## 超时机制

进行超时控制。网络抖动，网络断开

```go
	ctx, _ := context.WithTimeout(context.Background(), time.Second*3)
	_, err = c.SayHello(ctx, &proto.HelloRequest{Name: "bobby"})
```

## 负载均衡

## Demo

1. 创建并且编写proto文件

2. 执行插件生成相关语言类型的文件

3. 实习服务端和客户端代码逻辑

   - 服务器

     ```go
     const (
         port = ":50051"
     )
     
     type server struct{} //服务对象
     
     // SayHello 实现服务的接口 在proto中定义的所有服务都是接口
     func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
         return &pb.HelloReply{Message: "Hello " + in.Name}, nil
     }
     
     func main() {
         lis, err := net.Listen("tcp", port)
         if err != nil {
             log.Fatalf("failed to listen: %v", err)
         }
         s := grpc.NewServer() //起一个服务 
         pb.RegisterGreeterServer(s, &server{})
         
         // 注册反射服务 这个服务是CLI使用的 跟服务本身没有关系
         reflection.Register(s)
         
         if err := s.Serve(lis); err != nil {
             log.Fatalf("failed to serve: %v", err)
         }
     }
     ```

   - 客户端

     ```go
     const (
         address     = "localhost:50051"
         defaultName = "world"
     )
     
     func main() {
         //建立链接
         conn, err := grpc.Dial(address, grpc.WithInsecure())
         if err != nil {
             log.Fatalf("did not connect: %v", err)
         }
         defer conn.Close()
         c := pb.NewGreeterClient(conn)
     
         // Contact the server and print out its response.
         name := defaultName
         if len(os.Args) > 1 {
             name = os.Args[1]
         }
         // 1秒的上下文
         ctx, cancel := context.WithTimeout(context.Background(), time.Second)
         defer cancel()
         r, err := c.SayHello(ctx, &pb.HelloRequest{Name: name})
         if err != nil {
             log.Fatalf("could not greet: %v", err)
         }
         log.Printf("Greeting: %s", r.Message)
     }
     ```

     

### 连接consul

注册到consul中后，consul会根据注册信息定期向服务器发送健康检查请求。
如果没有设置健康检查，注册后会因为健康检查机制立马下线。

一般用HTTP或者GRPC方式，一般HTTP项目用HTTP方式，GRPC项目用GRPC方式

#### HTTP方式

```go
// 开放一个 /health 接口，用于服务注册中心向此接口发送健康检查请求
r.GET("/health", func(ctx *gin.Context) {
    ctx.JSON(http.StatusOK, gin.H{
    "code": http.StatusOK,
    "msg":  "",
    })
})
```

然后注册到consul的时候配置是HTTP方式，及其健康检查请求url

```go
type Registry struct {
   Host string
   Port int
}
type RegistryClient interface {
   Register(address string, port int, name string, tags []string, id string) error
   DeRegister(serviceId string) error
}

func NewRegistryClient(host string, port int) RegistryClient {
   return &Registry{Host: host, Port: port}
}

func (r *Registry) Register(address string, port int, name string, tags []string, id string) error {
   cfg := api.DefaultConfig()
   cfg.Address = fmt.Sprintf("%s:%d", r.Host, r.Port)

   client, err := api.NewClient(cfg)
   if err != nil {
      panic(err)
   }
   //生成对应grpc的检查对象
   check := &api.AgentServiceCheck{
      //HTTP方式
      HTTP:                           fmt.Sprintf("http://%s:%d/health", address, port),
      Timeout:                        "5s",
      Interval:                       "5s",
      DeregisterCriticalServiceAfter: "15s",
   }

   //生成注册对象
   registration := new(api.AgentServiceRegistration)
   registration.Name = name
   registration.ID = id
   registration.Port = port
   registration.Tags = tags
   registration.Address = address
   registration.Check = check

   err = client.Agent().ServiceRegister(registration)
   if err != nil {
      panic(err)
   }
   return nil
}

func (r *Registry) DeRegister(serviceId string) error {
   cfg := api.DefaultConfig()
   cfg.Address = fmt.Sprintf("%s:%d", r.Host, r.Port)

   client, err := api.NewClient(cfg)
   if err != nil {
      return err
   }
   err = client.Agent().ServiceDeregister(serviceId)
   return err
}
```

#### GRPC方式

比较简单，官方直接提供了，只需要注册到服务器实例中就行

```go
// 6.1 生成grpc服务器实例
l, err := net.Listen("tcp", fmt.Sprintf("%s:%d", initialize.ServerConfig.Host, initialize.ServerConfig.Port))
if err != nil {
    zap.S().Panic(err)
}
server := grpc.NewServer()
zap.S().Debugf("启动服务器，端口：%d", initialize.ServerConfig.Port)
// 6.2 本地rpc服务注册到服务器
pb.RegisterInventoryServer(server, &api.InventoryServer{})
// 6.3 健康检查注册注册到服务器
hsrv := health.NewServer()
hsrv.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
grpc_health_v1.RegisterHealthServer(server, hsrv)
// 6.4 启动实例
go func(){
    if err := server.Serve(l); err != nil {
        log.Fatal(err)
    }
}

// 相关信息注册到consul中
registerClient := NewRegistryClient(initialize.ServerConfig.ConsulConfig.Host, initialize.ServerConfig.ConsulConfig.Port)
serviceId := uuid.NewV4().String()
if err := registerClient.Register(initialize.ServerConfig.Host, initialize.ServerConfig.Port, initialize.ServerConfig.Name, initialize.ServerConfig.Tags, serviceId); err != nil {
    zap.S().Panic("服务注册失败：", err.Error())
}
```

consul部分只需要把HTTP修改为GRPC相关

```go
check := &api.AgentServiceCheck{
    //启用GRPC
    GRPC:                           fmt.Sprintf("%s:%d", address, port),
    GRPCUseTLS:                     false,
    Timeout:                        "5s",
    Interval:                       "5s",
    DeregisterCriticalServiceAfter: "15s",
}
```

## 源码分析

some blogs about analyzing grpc source code.  

[1]: https://juejin.cn/post/7089739785035579429	"gRPC 源码分析 (一) : 概述"
[2]: https://juejin.cn/post/7092698813265100831	"gRPC 源码分析(二): gRPC Server 的 RPC 连接阶段"
[3]: https://juejin.cn/post/7092738387471237127	"gRPC 源码分析(三): gRPC Server 的 RPC 交互阶段"
[4]: https://juejin.cn/post/7092975446257565726	"gRPC 源码分析(四): gRPC server 中 frame 的处理"
[5]: https://juejin.cn/post/7093091458437087262	"gRPC 源码分析(五): gRPC server 的流量控制 - 采样流量控制"
[6]: https://juejin.cn/post/7093131025470980126	"gRPC 源码分析(六): gRPC server 的流量控制 - connection 和 stream level 的流量控制"
[7]: https://juejin.cn/post/7094606537036922917	"gRPC 流量控制详解"

Additions are welcome!
