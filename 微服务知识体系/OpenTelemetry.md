# OpenTelemetry

## 概念

OpenTelemetry（也称为 OTel）是一个开源可观测能力框架，由一系列工具、API 和 SDK 组成，使 IT 团队能够检测、生成、收集和导出远程监测数据以进行分析和了解软件性能和行为。\
quickStart：https://opentelemetry.io/docs/instrumentation/go/getting-started/

otlp协议：https://opentelemetry.io/docs/reference/specification/protocol/otlp/

OpenTelemetry的核心工作目前主要集中在3个部分：

- 规范的制定和协议的统一，规范包含数据传输、API的规范，协议的统一包含：HTTP W3C的标准支持及GRPC等框架的协议标准；
- 多语言SDK的实现和集成，用户可以使用SDK进行代码自动注入和手动埋点，同时对其他三方库（Log4j、LogBack等）进行集成支持；
- 数据收集系统的实现，当前是基于OpenCensus Service的收集系统，包括Agent和Collector。

由此可见，OpenTelemetry的自身定位很明确：数据采集和标准规范的统一，对于数据如何去使用、存储、展示、告警，官方是不涉及的，我们目前推荐使用Prometheus + Grafana做Metrics存储、展示，使用Jaeger做分布式跟踪的存储和展示，使用Fluentd做日志存储和展示。

## 终极目标

实现Metrics、Tracing、Logging的融合，作为APM的数据采集终极解决方案。

- Tracing：提供了一个请求从接收到处理完成整个生命周期的跟踪路径，一次请求通常过经过N个系统，因此也被称为分布式链路追踪
- Metrics：例如cpu、请求延迟、用户访问数等Counter、Gauge、Histogram指标
- Logging：传统的日志，提供精确的系统记录

这三者的组合可以形成大一统的APM解决方案：

- 基于Metrics告警发现异常 通过Tracing定位到具体的系统和方法
- 根据模块的日志最终定位到错误详情和根源
- 调整Metrics等设置，更精确的告警/发现问题

## 安装

OpenTelemetry 分为两部分：用于检测代码的 API 和实现 API 的 SDK。

- API安装
  要开始将 OpenTelemetry 集成到任何项目中，API 用于定义遥测数据的生成方式。要在您的应用程序中生成跟踪遥测数据，您将使用[`go.opentelemetry.io/otel/trace`](https://pkg.go.dev/go.opentelemetry.io/otel/trace)包中的 OpenTelemetry Trace API。

  - ```sh
    go get go.opentelemetry.io/otel \
           go.opentelemetry.io/otel/trace
    ```

- SDK安装
  OpenTelemetry 在其 OpenTelemetry API 的实现中被设计为模块化。OpenTelemetry Go 项目提供了一个 SDK 包，[`go.opentelemetry.io/otel/sdk`](https://pkg.go.dev/go.opentelemetry.io/otel/sdk)它实现了这个 API 并遵守 OpenTelemetry 规范。

  - ```sh
    go get go.opentelemetry.io/otel/sdk \
             go.opentelemetry.io/otel/exporters/stdout/stdouttrace
    ```

## 使用

### API

trace是一种telemetry，表示服务正在完成的工作。是处理交易的参与者之间的连接记录，通常通过客户端/服务器请求处理和其他形式的通信。

导入的包

- 创建trace

  - ```
    newCtx, span := otel.Tracer(name).Start(ctx, 一般为被检测的函数名称)
    defer span.End()
    do something...
    ```

    跨度之间通过context去关联

    Tracer()返回一个新的tracer，所有的tracer全部保存在一个map中(map[tracerName]*tracer)，如果tracer已存在map中会直接返回之前创建的tracer

- 

### SDK

SDK 将来自 OpenTelemetry API 的遥测数据连接到导出器。

导入包

```go
"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.12.0"
```

- 创建导出器（Exporter）
  导出器是允许将遥测数据(telemetry data)发送到某处的包：发送到控制台(console)（这就是我们在这里所做的），或者发送到远程系统(remote system)或收集器(collector)以进行进一步分析和/或丰富。[OpenTelemetry 通过其生态系统支持各种出口商，包括Jaeger](https://pkg.go.dev/go.opentelemetry.io/otel/exporters/jaeger)、[Zipkin](https://pkg.go.dev/go.opentelemetry.io/otel/exporters/zipkin)和[Prometheus](https://pkg.go.dev/go.opentelemetry.io/otel/exporters/prometheus)等流行的开源工具。

  参考官方示例：https://github.com/open-telemetry/opentelemetry-go/tree/main/exporters

  - 控制台

    ```go
    func newExporter(w io.Writer) (trace.SpanExporter, error) {
    	return stdouttrace.New(
    		stdouttrace.WithWriter(w),
    		// Use human-readable output.
    		stdouttrace.WithPrettyPrint(),
    		// Do not print timestamps for the demo.
    	stdouttrace.WithoutTimestamps(),
    	)
    }
    ```

    这将创建一个带有基本选项的新控制台导出器。稍后您将在配置 SDK 向其发送遥测数据时使用此功能，但首先您需要确保数据是可识别的。

  - jaeger
    参考：https://github.com/open-telemetry/opentelemetry-go/tree/main/exporters/jaeger

    先下载依赖包：`go get go.opentelemetry.io/otel/exporters/jaeger`

    ```go
    // url example = http://localhost:14268/api/traces
    func newExporterByJaeger(url string) (trace.SpanExporter, error) {
    	return jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(url)))
    }
    ```

  - 

- 创建资源（Resource）
  遥测数据(telemetry data)对于解决服务问题至关重要。问题是，您需要一种方法来识别数据来自哪个服务，甚至是哪个服务实例。OpenTelemetry 使用 [`Resource`](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/resource#Resource) 来表示生成遥测的实体。

  - ```go
    // newResource returns a resource describing this application.
    func newResource() *resource.Resource {
    	r, _ := resource.Merge(
    		resource.Default(),
    		resource.NewWithAttributes(
    			semconv.SchemaURL,
    			semconv.ServiceNameKey.String("fib"),
    			semconv.ServiceVersionKey.String("v0.1.0"),
    			attribute.String("environment", "demo"),
    		),
    	)
    	return r
    }
    ```

    您希望与 SDK 处理的所有遥测数据相关联的任何信息都可以添加到返回的[`Resource`](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/resource#Resource). 这是通过向 注册 来完成[`Resource`](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/resource#Resource)的[`TracerProvider`](https://pkg.go.dev/go.opentelemetry.io/otel/trace#TracerProvider)。您现在可以创造的东西！

- 安装跟踪器提供者（Tracer Provider）

  您已对您的应用程序进行检测以生成telemetry数据，并且您有一个导出器exporter将该数据发送到控制台collector，但它们是如何连接的？这是 [`TracerProvider`](https://pkg.go.dev/go.opentelemetry.io/otel/trace#TracerProvider) 使用的地方。这是一个集中点，instrumentation将从中获取 [`Tracer`](https://pkg.go.dev/go.opentelemetry.io/otel/trace#Tracer)，并将来自这些 Tracer 的遥测数据汇集到导出管道`export pipelines`。

  接收数据并最终将数据传输给导出器exporter的管道称为 [`SpanProcessor`](https://pkg.go.dev/go.opentelemetry.io/otel/sdk/trace#SpanProcessor)。一个 [`TracerProvider`](https://pkg.go.dev/go.opentelemetry.io/otel/trace#TracerProvider) 可以配置多个 span processors，但对于此示例，您只需要配置一个。使用以下内容更新您的`main`功能`main.go`。

  - ```go
    func main() {
    	l := log.New(os.Stdout, "", 0)
    
    	// Write telemetry data to a file.
    	f, err := os.Create("traces.txt")
    	if err != nil {
    		l.Fatal(err)
    	}
    	defer f.Close()
    
    	exp, err := newExporter(f)
    	if err != nil {
    		l.Fatal(err)
    	}
    
    	tp := trace.NewTracerProvider(
    		trace.WithBatcher(exp),
    		trace.WithResource(newResource()),
    	)
    	defer func() {
    		if err := tp.Shutdown(context.Background()); err != nil {
    			l.Fatal(err)
    		}
    	}()
    	otel.SetTracerProvider(tp)
    
        /* … */
    }
    ```

    注意`trace.NewTracerProvider()`中可规定发送span的方式是异步还是同步，当使用`trace.WithSyncer()`时是同步发送；当使用`trace.WithBatcher()`时是通过通道(默认长度2048)异步按批发送，每隔一段时间(默认批处理5s超时触发)发送 or 达到最大批处理长度(默认512)时把要批处理的span利用导出器导出(也可手动调用ForceFlush强制导出)，当通道满了之后再存入span也有两种策略：丢弃这个span(默认)或者阻塞住直到队列有空位

- 


## 参考：
官网：https://opentelemetry.io/docs/ \
https://dmathieu.com/articles/development/dissecting-opentelemetry-tracing/ 
