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
