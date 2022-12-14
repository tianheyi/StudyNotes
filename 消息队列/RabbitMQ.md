# 消息队列

## 协议：AMQP和JMS

主流实现方式：AMQP（高级消息队列协议，例如erlang的rabbitmq），JMS（Java信息服务应用程序接口，rocketmq）

两者的区别和联系:

- JMS是定义了统一的接口，来对消息操作进行统一；AMQP是通过规定协议来统一数据交互的格式
- JMS限定了必须使用Java语言；AMQP只是协议，不规定实现方式，因此是跨语言的。
- JMS规定了两种消息模型；而AMQP的消息模型更加丰富

## 消息队列的优缺点

优点：

1. 解耦（应用解耦），增强扩展性；
2. 削峰（流量削峰）；
3. 异步；

缺点：

1. 系统可用性降低
   系统引入的外部依赖越多，系统稳定性越差。一旦MQ宕机，就会对业务产生影响。
2. 系统复杂度提高
   MQ的加入大大增加了系统复杂度，以前系统是同步的远程调用，现在是通过MQ进行异步调用。
   如果保证消息没有被重复消费？如何保证消息正确消费（丢失情况）？如何保证消息传递顺序性？
3. 存在数据一致性问题
   MQ给B、C、D三个系统发送消息数据，如果B、C系统处理成功，D系统处理失败，则如何保证消息数据处理的一致性？

## 选型

| 特性                    | ActiveMQ                     | RabbitMQ                                                     | RocketMQ                                                  | Kafka                                                        |
| ----------------------- | ---------------------------- | ------------------------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------------------ |
| 单机吞吐量              | 万级别                       | 万级别                                                       | 十万级别                                                  | 十万级别，这是kafka最大的优点，就是吞吐量高。一般配合大数据类的系统来进行实时数据计算、日志采集等场景。**吞吐量最大** |
| topic数量对吞吐量的影响 |                              |                                                              | topic可以达到几百、几千个的级别，吞吐量会有较小幅度的下降 | topic可以达到几百、几千个的级别，吞吐量会有较小幅度的下降    |
| 时效性                  | ms级                         | 微秒级别，rabbitmq的一大特点，**延迟是最低的**。得益于erlang | ms级                                                      | ms级                                                         |
| 可用性                  | 高，基于主从架构实现高可用性 | 高，基于主从架构实现高可用性                                 | 非常高，分布式架构                                        | 非常高，分布式架构，一个数据多个副本，少数机器宕机，不会丢失数据，不会导致不可用。**可用性最高** |
| 消息可靠性              | 有较低的概率丢失             |                                                              |                                                           |                                                              |
| 功能支持                |                              | 基于erlang开发，并发能力很强，性能及其好，延时很低           | MQ功能较为完善，分布式、扩展性好                          | 功能最为简单，主要支持简单的MQ功能，在大数据领域的实时计算以及日志采集被大规模使用，是事实上的标准 |
| 优劣势总结              | 用的比较少了                 | 社区最活跃，erlang开发，性能高，时延低，MQ功能比较完备且提供了管理界面。吞吐量比较低，因为实现机制较重，erlang开发难看懂源码。 | 分布式、java                                              | 只提供较少核心功能，但拥有超高的吞吐量，一点劣势可能是消息重复，提供的功能简单 |

**结论**：

（1）中小型公司，建议选Rabbitmq：数据量没那么大、应该首选功能比较完备的，所以kafka排除；rocketmq是阿里开源的，但阿里开源的大部分东西后面都不维护了，不过rocketmq已经交给apache基金会管理，所以未来趋势不错。

（2）大型公司，根据场景选用rocketmq与kafka。

## 选用RabbitMQ的理由

目前还是有很多种消息队列的，各有特点。
对于选用RabbitMQ的理由，大概因为：延时低是它最大的特点，同时单机吞吐量也很不错；也能进行分布式集群扩展；社区非常活跃。

# RabbitMQ

RabbitMQ（Rabbit Message Queue）是流行的开源消息队列系统，用erlang语言开发。
RabbitMQ 是 AMQP（高级消息队列协议）的标准实现。

## 整体架构

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/0.png)

## 概念

| routingKey | queue  |
| ---------- | ------ |
| key1       | queue2 |
| key1       | queue1 |

- Message：消息，消息是不具名的，它由消息头和消息体组成。消息体是不透明的，而消息头则由一系列的可选属性组成，这些属性包括 routing-key（路由键）、priority（相对于其他消息的优先权）、delivery-mode （指出该消息可能需要持久性存储）等。
  - Routing Key：路由关键字，exchange根据这个关键字进行消息投递。
- Broker：消息队列服务器实体。
- Exchange：消息交换机，它指定消息按什么规则，路由到哪个队列。具体有四种类型，默认Direct Exchange
- Queue：消息队列载体，每个消息都会被投入到一个或多个队列。
- Binding：绑定，它的作用就是把exchange和queue按照路由规则绑定起来。 routingKey, headers
- Virtual Host：虚拟主机，表示一批交换器、消息队列和相关对象。一个broker里可以开设多个vhost，用作不同用户的权限分离。虚拟主机是共享相同的身份认证和加密环境的独立服务器域。每个 vhost 本质上就是一个 mini 版的 RabbitMQ 服务器，拥有自己的队列、交换器、绑定和 权限机制。vhost 是 AMQP 概念的基础，必须在连接时指定，RabbitMQ 默认的 vhost 是 
- producer：消息生产者，就是投递消息的程序(一个向交换器发布消息的客户端应用程序)。
- consumer：消息消费者，就是接受消息的程序。
- channel：信道，多路复用连接中的一条独立的双向数据流通道。信道是建立在真实的 TCP 连接内的虚拟连接，AMQP 命令都是通过信道发出去的，不管是发布消息、订阅队列还是接收消息，这些动作都是通过信道完成。因 为对于操作系统来说建立和销毁 TCP 都是非常昂贵的开销，所以引入了信道的概念，以复用一条TCP连接。

## 简述

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/1.png)

生产者发消息是通过channel发，channel会将消息发给exchange，而不是直接发到对应队列。
exchange会查看消息的RoutingKey(理解为目的队列名，exchange【默认类型】会维护一张路由表)，如果不在表里就丢弃这个消息而不会报错。

消费者拿消息都是通过channel拿，而channel是直接根据传入的routingKey找到对应的queue去拿数据，如果从一个不存在的queue拿消息会直接报错。

## 详解

### queue、channel

- Queue（队列）是RabbitMQ的内部对象，用于存储消息。
- Channel是我们与RabbitMQ打交道的最重要的一个接口，我们大部分的业务操作是在Channel这个接口中完成的，包括定义Queue、定义Exchange、绑定Queue与Exchange、发布消息等。**每个channel都有自己独立的线程，最常用的做法是一个channel对应一个消费者，也就是意味着消费者之间彼此没有任何关联。当然也可以在一个channel中维持多个消费者，但是要注意一个问题，如果channel中的一个消费者一直在运行，那么其他消费者的callback会被”耽搁“。**

### Exchange

**为什么需要 Exchange 而不是直接将消息发送至队列？**
AMQP 协议中的核心思想就是生产者和消费者的解耦，生产者从不直接将消息发送给队列。生产者通常不知道是否一个消息会被发送到队列中，只是将消息发送到一个交换机。先由 Exchange 来接收，然后 Exchange 按照特定的策略转发到 Queue 进行存储。Exchange 就类似于一个交换机，将各个消息分发到相应的队列中。

**Exchange 收到消息时，他是如何知道需要发送至哪些 Queue 呢？**
这里就需要了解 Binding 和 RoutingKey 的概念：
		Binding 表示 Exchange 与 Queue 之间的关系，我们也可以简单的认为队列对该交换机上的消息感兴趣，绑定可以附带一个额外的参数 RoutingKey。Exchange 就是根据这个 RoutingKey 和当前 Exchange 所有绑定的 Binding 做匹配，如果满足匹配，就往 Exchange 所绑定的 Queue 发送消息，这样就解决了我们向 RabbitMQ 发送一次消息，可以分发到不同的 Queue。**RoutingKey 的意义依赖于交换机的类型。**

exchange有三种主要类型（`Fanout`、`Direct` 和 `Topic`），两种特殊类型（Headers Exchange、Default Exchange）

#### Fanout

Fanout Exchange 会忽略 RoutingKey 的设置，直接将 Message 广播到所有绑定的 Queue 中。

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/2.jpg)

**应用场景**

以日志系统为例：假设我们定义了一个 Exchange 来接收日志消息，同时定义了两个 Queue 来存储消息：一个记录将被打印到控制台的日志消息；另一个记录将被写入磁盘文件的日志消息。我们希望 Exchange 接收到的每一条消息都会同时被转发到两个 Queue，这种场景下就可以使用 Fanout Exchange 来广播消息到所有绑定的 Queue。

#### Direct

**Direct Exchange 是 RabbitMQ 默认的 Exchange**，完全根据 RoutingKey 来路由消息。设置 Exchange 和 Queue 的 Binding 时需指定 RoutingKey（一般为 Queue Name），发消息时也指定一样的 RoutingKey，消息就会被路由到对应的Queue。

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/3.jpg)

**应用场景**

现在我们考虑只把重要的日志消息写入磁盘文件，例如只把 Error 级别的日志发送给负责记录写入磁盘文件的 Queue。这种场景下我们可以使用指定的 RoutingKey（例如 error）将写入磁盘文件的 Queue 绑定到 Direct Exchange 上。

#### Topic

Topic Exchange 和 Direct Exchange 类似，也需要通过 RoutingKey 来路由消息，区别在于Direct Exchange 对 RoutingKey 是精确匹配，而 Topic Exchange 支持模糊匹配。分别支持`*`和`#`通配符，`*`表示匹配一个单词，`#`则表示匹配没有或者多个单词。



![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/4.jpg)

**应用场景**

假设我们的消息路由规则除了需要根据日志级别来分发之外还需要根据消息来源分发，可以将 RoutingKey 定义为 `消息来源.级别` 如 `order.info`、`user.error`等。处理所有来源为 `user` 的 Queue 就可以通过 `user.*` 绑定到 Topic Exchange 上，而处理所有日志级别为 `info` 的 Queue 可以通过 `*.info` 绑定到 Exchange上。

#### Headers

headers

Headers Exchange 会忽略 RoutingKey 而根据消息中的 Headers 和创建绑定关系时指定的 Arguments 来匹配决定路由到哪些 Queue。(Headers Exchange 的性能比较差，而且 Topic Exchange 完全可以代替它，所以不建议使用。)

arguments是一个字典，有一个固定key x-match,两个值：all，any

### 死信队列

“死信”是RabbitMQ中的一种消息机制，当你在消费消息时，如果队列里的消息出现以下情况：

publisher -> exchange -> queue  -> consumer

1. 消息被否定确认，使用 `channel.basicNack` 或 `channel.basicReject` ，并且此时`requeue` 属性被设置为`false`。
2. 消息在队列的存活时间超过设置的TTL时间。
3. 消息队列的消息数量已经超过最大队列长度。

那么该消息将成为“死信”。

“死信”消息会被RabbitMQ进行特殊处理，如果配置了死信队列信息，那么该消息将会被丢进死信队列中，如果没有配置，则该消息将会被丢弃。

```python
channel.queue_declare(queue=delay_queue, durable=durable, arguments={
    'x-dead-letter-exchange': 死信交换机名称,
    # 'x-dead-letter-routing-key': 死信routingkey
})
```



### 延迟队列

需要搭配死信队列+TTL实现

#### TTL

在介绍延时队列之前，还需要先介绍一下RabbitMQ中的一个高级特性——`TTL（Time To Live）`。

`TTL`是什么呢？`TTL`是RabbitMQ中一个消息或者队列的属性，表明`一条消息或者该队列中的所有消息的最大存活时间`，单位是毫秒。换句话说，如果一条消息设置了TTL属性或者进入了设置TTL属性的队列，那么这条消息如果在TTL设置的时间内没有被消费，则会成为“死信”。

如果同时配置了队列的TTL和消息的TTL，那么较小的那个值将会被使用。
但这两种方式是有区别的，**如果设置了队列的TTL属性，那么一旦消息过期，就会被队列丢弃，而第二种方式，消息即使过期，也不一定会被马上丢弃，因为消息是否过期是在即将投递到消费者之前判定的，如果当前队列有严重的消息积压情况，则已过期的消息也许还能存活较长时间。**

另外，还需要注意的一点是，**如果不设置TTL**，表示消息永远不会过期，**如果将TTL设置为0**，则表示除非此时可以直接投递该消息到消费者，否则该消息将会被丢弃。

### 优先级队列

根据消息优先级进行消费

要声明优先级队列，使用 `x-max-priority` 参数。此参数应为介于 1 和 255 之间的正整数，指示队列应支持的最大优先级。

**队列**需要设置**优先级队列**，**消息**需要设置消息的**优先级**。消费者需要等待消息已经发送到队列中，然后对队列中的消息进行排序，最后再去消费。

### 惰性队列

**lazy queue，3.6.0版本引入**
队列声明的时候属性设置`arguments={"x-queue-mode": "lazy"}`

惰性队列会尽可能的将消息存入磁盘中，而在消费者消费到相应的消息时才会被加载到内存中，它的一个重要设计目标是能够支持更长的队列，即支持更多的消息存储。当消费者由于各种各样的原因（比如消费者下线、跌机、或者由于维护而关闭等）致使长时间不能消费消息而造成堆积时，惰性队列就很必要了。

默认情况下，当生产者将消息发送到RabbitMQ的时候，队列中的消息会尽可能地存储在内存之中，这样可以更加快速地将消息发送给消费者。即使是持久化的消息，在被写入磁盘的同时也会在内存中驻留一份备份。当RabbitMQ需要释放内存的时候，会将内存中的消息换页至磁盘中，这个操作会耗费较长的时间，也会阻塞队列的操作，进而无法接收新的消息。

**惰性队列和普通队列相比，只有很小的内存开销。**这里很难对每种情况给出一个具体的数值，但是我们可以类比一下：发送1千万条消息，每条消息的大小为1KB，并且此时没有任何的消费者，那么普通队列会消耗1.2GB内存，而惰性队列只能消耗1.5MB的内存。

根据官方测试数据显示，对于普通队列，如果要发送1千万条消息，需要耗费801秒，平均发送速度约为13000条/秒。如果使用惰性队列，那么发送同样多的消息时，耗时是421秒，平均发送速度约为24000条/秒。出现性能偏差的原因是普通队列会由于内存不足而不得不将消息换页至磁盘。如果有消费者消费时，惰性队列会耗费将近40MB的空间来发送消息，对于一个 消费者的情况，平均的消费速度约为14000条/秒。

如果要将普通队列转变为惰性队列，我们需要忍受同样的性能损耗，首先需要将缓存中的消息换页至磁盘中，然后才能接收新的消息。反之，当将一个惰性队列转变为一个普通队列的时候，和恢复一个队列执行同样的操作，会将磁盘中的消息批量的导入到内存中。

## 相关

- **问题：运行一段时间后, pika会丢失与RabbitMQ的连接.**

AMQP协议规定消息队列有心跳检测机制, 即消息队列的消息代理会设置一个心跳超时时间.

当客户端与消息队列的消息代理建立连接后, 客户端隔一定时间就会发送一个心跳检测包, 如果消息代理在心跳超时时间内没有收到心跳检测包, 该连接就会被断开. 对于消息队列来说这是好事情, 因为不用维持一个不常使用的连接, 但对我们编写的客户端(生产者/消费者)来说可不友好. 怎么办呢? 有两种解决的方法.

1) 方法一

使用pika提供的process_data_events方法, 该方法定时自动向RabbitMQ的消息代理发送心跳包来维持连接

connection.process_data_events()  # 保持连接, 程序会阻塞在此处

该方法可选填time_limit参数表示最长的阻塞时间. 参数默认为0, 即有消息需要发送或接收时会立即结束阻塞并进行处理. 阻塞期间连接不会被消息代理断开, 该方法起到了保活作用.

2) 方法二

关闭RabbitMQ的心跳检测机制

pika.ConnectionParameters(host=self.host, port=self.port, heartbeat=0)  # 该方法用于生成连接参数

heartbeat表示心跳超时时间, 如果设置的是大于0的数, 则该数会被作为消息代理与该客户端间连接的心跳超时时间. 如果设置的是None, 则会使用消息代理的默认心跳超时时间. 如果是0, 则关闭对该连接的心跳超时检测.



**稳定性**

- **如何保证消息的可靠性传输（如何处理消息丢失的问题）？**

  - **保证消息尽量发送成功**

    - 发送方确认模式：`channel.confirm_delivery()`
      将信道设置成confirm模式（发送方确认模式），则所有在信道上发布的消息都会被指派一个唯一的ID。一旦消息被投递到目的队列后，或者消息被写入磁盘后（可持久化的消息），信道会发送一个确认给生产者（包含消息唯一ID）。如果RabbitMQ发生内部错误从而导致消息丢失，会发送一条nack（not acknowledged，未确认）消息。
    - 事务：比较耗性能
      生产者发送数据之前开启rabbitmq事务（channel.txSelect），然后发送消息，如果消息没有成功被rabbitmq接收到，那么生产者会收到异常报错，此时就可以回滚事务（channel.txRollback），然后重试发送消息；如果收到了消息，那么可以提交事务（channel.txCommit）。但是问题是，rabbitmq事务机制一搞，基本上吞吐量会下来，因为太耗性能。

  - **保证消息被正确消费**

    - 接收方消息确认机制：消费者接收每一条消息后都必须进行确认（消息接收和消息确认是两个不同操作）。只有消费者确认了消息，RabbitMQ才能安全地把消息从队列中删除。

      这里并没有用到超时机制，RabbitMQ仅通过Consumer的连接中断来确认是否需要重新发送消息。也就是说，只要连接不中断，RabbitMQ给了Consumer足够长的时间来处理消息。

      下面罗列几种特殊情况：

      - 如果消费者接收到消息，在确认之前断开了连接或取消订阅，RabbitMQ会认为消息没有被分发，然后重新分发给下一个订阅的消费者。（可能存在消息重复消费的隐患，需要根据bizId去重）
      - 如果消费者接收到消息却没有确认消息，连接也未断开，则RabbitMQ认为该消费者繁忙，将不会给该消费者分发更多的消息。

  - **消息持久化**

    - 消息持久化的前提是：将交换器/队列的`durable`属性设置为`true`，表示交换器/队列是持久交换器/队列，在服务器崩溃或重启之后不需要重新创建交换器/队列（交换器/队列会自动创建）。

    - 如果消息想要从Rabbit崩溃中恢复，那么消息必须：

      - 消息持久化：在消息发布前，通过把它的`delivery_mode`选项设置为2（持久）来把消息标记成持久化
      - 将消息发送到持久交换器（交换机持久化）：交换器的持久化是通过在声明交换器时将 durable 参数置为 true 实现的，如果交换器不设置持久化，那么在 RabbitMQ 服务重启之后，相关的交换器元数据会丢失， 不过消息不会丢失，只是不能将消息发送到这个交换器中了。对一个长期使用的交换器来说，建议将其置为持久化的。
      - 消息到达持久队列（队列持久化）：队列的持久化是通过在声明队列时将 durable 参数置为 true 实现的，如果队列不设置持久化，那么在 RabbitMQ 服务重启之后，相关队列的元数据会丢失，此时数据也会丢失。

      RabbitMQ确保持久性消息能从服务器重启中恢复的方式是，将它们写入磁盘上的一个持久化日志文件，当发布一条持久性消息到持久交换器上时，Rabbit会在消息提交到日志文件后才发送响应（如果消息路由到了非持久队列，它会自动从持久化日志中移除）。一旦消费者从持久队列中消费了一条持久化消息，RabbitMQ会在持久化日志中把这条消息标记为等待垃圾收集。如果持久化消息在被消费之前RabbitMQ重启，那么Rabbit会自动重建交换器和队列（以及绑定），并重播持久化日志文件中的消息到合适的队列或者交换器上。

    - 在这段时间内 RabbitMQ 服务节点发生了岩机、重启等异常情况，消息保存还没来得及落盘，那么这些消息将RabbitMQ 实战指南会丢失。这个问题怎么解决呢?
      可以引入 RabbitMQ 的镜像队列机制，相当于配置了副本，如果主节点 Cmaster) 在此特殊时间内挂掉，可以自动切换到从节点 Cslave ), 这样有效地保证了高可用性

- **在消费者接收到消息后，如果想明确拒绝当前的消息而不是确认，那么应该怎么做呢?**

  - RabbitMQ 在 2.0.0 版本开始引入了 Basic .Reject 这个命令，消费者客户端可以调用与其对 应的 channel.basicReject 方法来告诉 RabbitMQ 拒绝这个消息。
    `basic_reject(self, delivery_tag=0, requeue=True)`：

    ​	`delivery_tag`：mq内部生成的消息投递序号，每个channel对应一个(long类型)，从1开始到9223372036854775807范围，在手动消息确认时可以对指定delivery_tag的消息进行ack、nack、reject等操作。每次消费或者重新投递requeue后，delivery_tag都会增加，理论上该正常业务范围内，该值永远不会达到最大范围上限【假设每秒钟一个消费者可以消费1000w个消息(假设每个消费者一个channel)，则 9223372036854775807 / (60 * 60 * 24 * 365 * 1000w) = 29247年后能达到上限数值】。

    ​	`requeue`：如果requeue为`true`，则RabbitMQ 会重新将这条消息存入 队列，以便可以发送给下一个订阅的消费者；如果设置为 `false`，则 RabbitMQ 立即会把消息从队列中移除(配置了死信交换机会发给死信)，而不会把它发送给新的消费者。

  - Basic.Reject 命令一次只能拒绝一条消息 ，如果想要批量拒绝消息 ，则可以使用 Basic.Nack 这个命令
    `basic_nack(self, delivery_tag=0, multiple=False, requeue=True)`：

    ​	`multiple`：如果为`false`，则表示拒绝编号为 deliveryTag的这一条消息，这时候 basicNack 和 basicReject 方法一样；如果设置为 `true` 则表示拒绝 deliveryTag 编号之前所有未被当前消费者确认的消息。

- **消息确认(Confirm)机制**
  RabbitMQ的消息确认机制是为了确保消息发送者知道自己发布的消息被正确接收，如果没有收到确认时就会认为消息发送过程发送了错误，此时就会马上采取措施，以保证消息能正确送达（类似于HTTP的建立连接时的确认答复）。
  具体做法如下：
  当RabbitMQ发送消息以后，如果收到消息确认，才将该消息从Quque中移除。如果RabbitMQ没有收到确认，如果检测到消费者的RabbitMQ链接断开，则RabbitMQ 会将该消息发送给其他消费者；RabbitMQ 不会为未确认的消息设置过期时间，它判断此消息是否需要重新投递给消费者的唯一依据是消费该消息连接是否已经断开，这个设置的原因是 RabbitMQ 允许消费者消费一条消息的时间可以很久很久。
  采用消息确认机制后，只要设置 autoAck 参数为 false，消费者就有足够的时间处理消息（任务），不用担心处理消息过程中消费者进程挂掉后消息丢失的问题，因为 [RabbitMQ](https://so.csdn.net/so/search?q=RabbitMQ&spm=1001.2101.3001.7020) 会一直等待持有消息直到消费者显式调用 Basic.Ack 命令为止。
  RabbitMQ的一大特性就是支持消息持久化。但是Rabbit MQ默认是不持久队列、Exchange、Binding以及队列中的消息的，这意味着一旦消息服务器重启，所有已声明的队列，Exchange，Binding以及队列中的消息都会丢失，这是因为支持持久化会对性能造成较大的影响。

- **如何避免消息重复投递或重复消费**？

  ![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/6.png)

  - 在消息生产时，MQ内部针对每条生产者发送的消息生成一个inner-msg-id，作为去重和幂等的依据（消息投递失败并重传），避免重复的消息进入队列；（图中1，2，3）
    - MQ-client生成inner-msg-id，保证上半场幂等。
    - 这个ID全局唯一，业务无关，由MQ保证。
  - 在消息消费时，要求消息体中必须要有一个bizId（对于同一业务全局唯一，如支付ID、订单ID、帖子ID等）作为去重和幂等的依据，避免同一条消息被重复消费。（图中4，5，6）
    - 业务发送方带入biz-id，业务接收方去重保证幂等。
    - 这个ID对单业务唯一，业务相关，对MQ透明。

- **RabbitMQ如何重新发送还未被确认的消息？**

  - `channel.basicRecover(requeue) `方法用来请求 RabbitMQ 重新发送还未被确认的消息。 如果 requeue 参数设置为 true，则未被确认的消息会被重新加入到队列中，这样对于同一条消息 来说，可能会被分配给与之前不同的消费者。如果 requeue 参数设置为 false，那么同一条消 息会被分配给与之前相同的消费者。

- **生产者如何获取到没有被正确路由到合适队列的消息呢**?

  - 可以通过调用`channel.add_on_return_callback(callback)`来添加一个回调函数，并且启动一个监听器。当服务器通过“Basic.Return”拒绝并返回发布的消息时，将调用该回调函数。

    `channel.basic_publish()`发布消息的时候有一个参数`mandatory`：
    为true时：当交换器无法根据自身的类型和路由键找到一个符合条件 的队列时，那么 RabbitMQ 会调用 Basic.Return 命令将消息返回给生产者，就会触发上面设置的回调函数。
    为false时：交换器无法根据自身的类型和路由键找到一个符合条件 的队列，消息会直接被丢弃。

  - 或者采用备份交换器AE（Alternate Exchange），可以将未被路由的消息存储在RabbitMQ中，通过声明交换器的时候添加AE参数实现，或者通过策略的方式实现，同时使用，前者优先级高，会覆盖掉Policy的设置。
    备份交换机可以理解为 RabbitMQ 中交换机的“备胎”，当我们为某一个交换机声明一个对应的备份交换机时，就是为它创建一个备胎，**当交换机接收到一条不可路由消息时，将会把这条消息转发到备份交换机中，由备份交换机来进行转发和处理，通常备份交换机的类型为 Fanout** ，这样就能把所有消息都投递到与其绑定的队列中，然后我们在备份交换机下绑定一个队列，这样所有那些原交换机无法被路由的消息，就会都进入这个队列了。当然，我们还可以建立一个报警队列，用独立的消费者来进行监测和报警。

    - 设置备份交换机：设置方式是在声明exchange时，argument的参数中设置alternate-exchange的值，值为备份交换机的名称。

      ```python
      alternate_exchange = {
          'alternate-exchange': 'backup_exchange'
      }
      # topic_logs交换机配了一个叫backup_exchange的备份交换机，可以为备份交换机绑定备份队列
      channel.exchange_declare(exchange='topic_logs',
                               exchange_type='topic',
                               arguments=alternate_exchange)
      ```

    - 备份交换器需要注意？
      如果设置的备份交换器不存在，客户端和RabbitMQ服务端都不会有异常出现，此时消息会丢失
      如果备份交换器没有绑定任何队列，客户端和RabbitMQ服务端都不会有异常出现，此时消息会丢失
      如果备份交换器没有任何匹配的队列，客户端和RabbitMQ服务端都不会有异常出现，此时消息会丢失
      如果备份交换器和mandatory参数一起使用，那么mandatory参数无效

- **对过期消息处理**？

  - 设置队列 TTL 属性的方法，一旦消息过期，就会从队列中抹去，队列中己过期的消息肯定在队列头部， RabbitMQ 只要定期从队头开始扫描是否有过期的消息即可，
  - 消息本身进行单独设置，即使消息过期，也不会马上从队列中抹去，因为每条消息是否过期是在即将投递到消费者之前判定的。每条消息的过期时间不同，如果要删除所有过期消息势必要扫描整个队列，所以不如等到此消息即将 被消费时再判定是否过期， 如果过期再进行删除即可。

- **什么是死信队列**？
  DLX，全称为 Dead-Letter-Exchange，可以称之为死信交换器，也有人称之为死信邮箱。当消息在一个队列中变成死信 (dead message) 之后，它能被重新被发送到另一个交换器中，这个交换器就是 DLX，绑定 DLX 的队列就称之为死信队列。
  DLX 也是一个正常的交换器，和一般的交换器没有区别，它能在任何的队列上被指定， 实 际上就是设置某个队列的属性。当这个队列中存在死信时 ， RabbitMQ 就会自动地将这个消息重新发布到设置的 DLX 上去，进而被路由到另一个队列，即死信队列。

- **什么是延迟队列**？
  延迟队列存储的对象是对应的延迟消息，所谓“延迟消息”是指当消息被发送后，并不想让消费者立刻拿到消息，而是等待特定时间后，消费者才能拿到这个消息进行消费

  - 应用场景
    订单系统，用延迟队列处理超时订单
    用户希望通过手机远程遥控家里的智能设备在指定的时间进行工作。这时候就可以将 用户指令发送到延迟队列，当指令设定的时间到了再将指令推送到智能设备。

- **消息如何实现有序处理**？

  - 生产者发送消息设置了不同的超时时间，并且设置了死信队列
  - 消息设置了优先级
  - 可以考虑在消息体内添加全局有序标识来实现

- **提高数据可靠性途径**？
  设置 mandatory 参数或者备份交换器 (immediate 参数己被陶汰)；
  设置 publisher confirm(消息确认)机制或者事务；
  设置交换器、队列和消息都为持久化；
  设置消费端对应的 autoAck 参数为 false 井在消费完消息之后再进行消息确认

- **消息基于什么传输**？

  - 由于TCP连接的创建和销毁开销较大，且并发数受系统资源限制，会造成性能瓶颈。RabbitMQ使用信道的方式来传输数据。信道是建立在真实的TCP连接内的虚拟连接，且每条TCP连接上的信道数量没有限制。

- **消息如何分发**？

  - 若该队列至少有一个消费者订阅，消息将以循环（round-robin）的方式发送给消费者。每条消息只会分发给一个订阅的消费者（前提是消费者能够正常处理消息并进行确认）。

- **消息如何刷到磁盘？**
  1.写入文件前会有一个Buffer,大小为1M,数据在写入文件时，首先会写入到这个Buffer，如果Buffer已满，则会将Buffer写入到文件（未必刷到磁盘）。
  2.有个固定的刷盘时间：25ms,也就是不管Buffer满不满，每个25ms，Buffer里的数据及未刷新到磁盘的文件内容必定会刷到磁盘。
  3.每次消息写入后，如果没有后续写入请求，则会直接将已写入的消息刷到磁盘：使用Erlang的receive x after 0实现，只要进程的信箱里没有消息，则产生一个timeout消息，而timeout会触发刷盘操作。

- **什么时候需要持久化？**

  1.我们根据自己的需求对它们进行持久化（具体方法可以参考官方的API）。
  注意：消息是存在队列里的，如果要使得消息能持久化，就必须先使队列持久化。
  2.内存紧张时，需要将部分内存中的消息转移到磁盘中。

## 选型

github地址：[pika/pika: Pure Python RabbitMQ/AMQP 0-9-1 client library (github.com)](https://github.com/pika/pika)

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/5.png)



使用：https://www.cnblogs.com/cwp-bg/p/8426188.html

# 最佳实践

使用RabbitMQ消息队列时两个重要的考虑因素是：吞吐与可靠。有的场景要求高吞吐，有的场景要求高可靠。在系统设计时候如何平衡消息队列的的吞吐量与可靠性，是使用好RabbitMQ消息队列的关键。 RabbitMQ的最佳实践，基于吞吐量与可靠性两个指标，给出怎么做是好的、怎么做是差的指导，包括队列大小、常见错误、延迟加载队列、预提取值、连接与通道、集群节点数量等，这些指导都是在实践中总结出来的。

## 队列 Queues

### 队列尽可能短

声明队列的时候通过`x-max-length`和`x-max-length-bytes`来限制最大长度(消息最大个数)和最大占用空间(以字节为单位)，当`x-max-length`与`x-max-length-bytes`都设置时，无论哪个达到限制都会触发溢出策略。溢出策略有两种：

- 丢弃最前面的消息(默认)
- 拒绝发布，修改方式为启动发布者确认机制[link](https://www.rabbitmq.com/confirms.html#publisher-confirms)

队列过长的话会占用系统较多内存，RabbitMQ为了释放内存，会将队列消息转储到硬盘，称为 **page out** 。 如果队列很长，Page out 操作会消耗较长时间，page out 过程中队列不能处理消息。

队列过长同时会加长RabbitMQ重启时间，因为启动时候需要重建索引。 队列过长还会导致集群之间节点同步消息时间变长。

### 启用 lazy queue 使得性能可预期

RabbitMQ3.6版本引入了 **lazy queue** 特性， lazy queue 开启之后队列中的消息自动存储到磁盘，消息只在需要的时候才加载到内存中。开启了 lazy queue 后内存使用量会降低，但是会增加消息处理时延。

在实践中我们观察到开启了 lazy queue 后RabbitMQ集群会更稳定，性能也更可预期。消息不会突然在没有预警的情况下被写到磁盘，也不会出现突发性能毛刺。如果你一次批量往队列写入大量消息，或者消费者对消息时延不敏感，建议启动 lazy queue 。

### 通过 TTL 或 max-length 限制队列大小

通过设置 TTL 或 max-length 来限制队列大小，从而让队列不超过设定大小。

### 队列数量

RabbitMQ中一个队列对应一个线程，一个队列的吞吐量大约为50k消息/秒。在多核服务器上，使用多个队列与消费者可以获得更好的吞吐量，将队列数量设置为等于服务器cpu核数将获得最佳吞吐量。

### 将队列分布到不同的CPU核，甚至不同节点

队列的性能极限是一个CPU核处理能力，因此，将队列分布到不同的CPU核（集群模式下可以到不同节点），将获得更好的性能。 RabbitMQ队列被绑定到第一个节点上，即使创建了集群，所有消息也是被投递到主队列所在的节点。你可以手动调整队列到不同的节点，但是带来的负面影响是你要管理这个映射关系。

有两个插件可以辅助实现队列分布到不同节点或不同CPU和（单节点集群）。
rabbimq手册之rabbitmq-plugins：https://www.jianshu.com/p/0ff7c2e5c7cb

#### Consistent hash exchange plugin

[Consistent hash exchange plugin](http://www.yunweipai.com/go?_=1a78f9c97daHR0cHM6Ly9naXRodWIuY29tL3JhYmJpdG1xL3JhYmJpdG1xLWNvbnNpc3RlbnQtaGFzaC1leGNoYW5nZQ%3D%3D) 插件可以实现 Exchange 按照负载均衡方式投递消息到队列中。插件将要投递消息的 Routing Key 哈希之后找到要投递的队列，这种方式能保证同一个 Routing key 的消息总是投递到同一个队列。 使用插件时候需要注意，消费者需要在多个队列上消息分析，不要有遗漏。

#### RabbitMQ sharding

[RabbitMQ sharding](http://www.yunweipai.com/go?_=df63813a16aHR0cHM6Ly9naXRodWIuY29tL3JhYmJpdG1xL3JhYmJpdG1xLXNoYXJkaW5n) 插件自动完成消息的分区，一旦在 Exchange 上定义了分区，插件会在集群的每个节点上创建一个分区队列；同时RabbitMQ sharding 插件对消费者只提供一个队列（但是实际后端有多个队列）。RabbitMQ sharding 插件提供消息生产与消费的中心访问点，并提供消息跨节点自动分区、管理节点上的队列等能力。

### 临时队列名字系统自动分配

给队列取一个有意义的名字很关键，生产者与消费者之间通过名字找到队列。但是对于临时队列，名字就交由给系统自动分配。

### 自动删除不再使用的队列

生产者或消费者可能异常退出导致队列被残留，大量的残留队列会影响RabbitMQ实例的性能。RabbitMQ提供了3种自动删除队列的方法。

- 设置队列的 TTL ：如 TTL 为28天的队列，当持续28天没有被消费后会被自动删除
- 配置 auto-delete 队列： auto-delete 队列在最后一个消费者取消消费、或链接关闭后被删除
- 配置 exclusive queue： exclusive queue 只能在创建此队列的 Connection/Channel 中使用，当 Connection/Channel 关闭后队列被删除

### 限制优先队列数量

每个优先队列会启动一个Erlang进程，过多的优先队列会影响性能。

## 队列消息持久化

如果消息不允许丢失，需要将队列设置为 durable ，将消息设置为 persistent 。这种方式消息与队列都会持久化到硬盘，当然相比于 transient 消息，吞吐量会下降。

## 连接数与通道数

每个连接会消耗掉大约100KB的内存（如果使用TLS会更多），成千上万的连接会导致RabbitMQ负载很高，极端情况会出现内存溢出。AMQP协议引入了Channel概念，一个连接中可以有多个Channel。 建议一个Channel对应一个线程，一个连接对应一个进程，并使用长连接。

### 不要在多个线程之间共享Channel

很多SDK并未实现Channel的线程安全，因此不要在多个线程之间共享Channel 。

### 不要频繁打开与关闭 Channel

同样是基于性能考虑。

### 生产者与消费者使用独立的连接

这么做吞吐量更高。 当生产者发送大量消息时候RabbitMQ会将压力传递到TCP连接上，如果使用同一个连接消费消息可能会得不到确认消息。

### 大量连接与通道会影响RabbitMQ管理控制台的性能

RabbitMQ会采集每个连接与通道的指标数据并分析，然后在控制台展示，大量的连接与通道会对控制台有较大压力。

## RabbitMQ不公平分发和预取值

在RabbitMQ中，队列向消费者发送消息，如果没有设置Qos的值，那么队列中有多少消息就发送多少消息给消费者，完全不管消费者是否能够消费完，这样可能就会形成大量未ack的消息在缓存区堆积，因为这些消息未收到消费者发送的ack，所以只能暂时存储在缓存区中，等待ack，然后删除对应消息。

**QoS是在接收端设置的，一般在信道声明的时候使用，确定该信道的预取数，提高性能**

```python
def basic_qos(self, prefetch_size=0, prefetch_count=0, global_qos=False):
    """
    如果消费者设置了auto_ack=True，会忽略下面两个参数
    prefetch_size：最大unacked消息的字节数,0表示不限制，推模式下rabbitmq可能出现堆积大量未确认的消息。太低的版本只能为0，会报错未实现不为0的情况。
    prefetch_count：最大unacked消息的条数（超过此限制后队列不再继续推消息），0表示不限制
    global_qos：是否将所有的信道都设置上述参数，因为一个Connection可以有多个Channel
    """
    pass
```



## Acknowledgements and Confirms

消息在传输过程中可能会丢失（如连接中断），这时候就需要重传。确认消息用于告知客户端与服务端何时重传消息。客户端需要发送确认消息当收到消息、或者对于重要消息是消息被处理后。消息确认对性能也有影响，在高吞吐场景下，尽量避免使用手动确认。

对于消费者，一些重要的消息，建议在消息消费逻辑处理完成后才确认，确保消息不丢失。

### 未确认消息 Unacknowledged messages

所有未确认的消息都存储在内存中，当有大量的为确认消息时候可能会将内存耗尽。一个高效的限制未确认消息的方法是设置消费者的预提取（prefetch）消息数量，当某消费者未确认消息达到此阈值则不会继续给该消费者分发消息。可以参考RabbitMQ的 prefect 机制：https://cloud.tencent.com/developer/article/1865649

## Prefetch

[prefetch](http://www.yunweipai.com/go?_=1dc2d5cb81aHR0cHM6Ly93d3cucmFiYml0bXEuY29tL2Jsb2cvMjAxMi8wNS8xMS9zb21lLXF1ZXVpbmctdGhlb3J5LXRocm91Z2hwdXQtbGF0ZW5jeS1hbmQtYmFuZHdpZHRoLw%3D%3D) 值用于指定一次发送多少个消息给消费者。RabbitMQ官网对 prefetch 的定义：

```
prefetch 的目的是使得消费者处于饱和工作状态，同时又要让消费者客户端内存缓存最少，并使得消息呆在队列中让其他消费者尽快消费。
```

RabbitMQ默认不设定消费者内存缓存上限，意思是一次性发送尽量多的消息给消费者，消息在消费者客户端内存中缓存直到被处理。 Prefetch 限定消费者一次消费的消息数量， 所有 Prefetch 的消息都会从队列中删除，其他消费者不再可见。

Prefetch 的值对RabbitMQ的性能有影响。

过小的值会导致RabbitMQ将时间都花费在等待发送消息与正在发送消息过程内。下图是一个 Prefetch 设置过小，导致时间都花费在网络传输上的例子：消费者处理消息只用了5ms，但是接收消息，确认消息却耗费了120ms。

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/7.png)

过大的值会导致一个消费者取走了所有消息非常繁忙，其他消费者没有消息可处理空闲等待的现象。

![在这里插入图片描述](https://github.com/thy485280869/resource-images/blob/main/RabbitMQ/8.png)

### 如何设置合适的 prefetch 值

- 消费者很少且消息处理很快：prefetch 设置尽可能大；
- 消费者很多且消息处理很快：prefetch 设置较小；比 “消费者很少且消息处理很快” 场景要小
- 消费者很多且消息处理很慢：prefetch 设置为1；这样尽可能将消息分布给不同的消费者处理

需要注意的是，**如果消费者设置了自动确认消息消费，那么 prefetch 是无效的。**

常见的错误做法是不设定 prefetch 的值，这种情况下会导致一些消费者撑死，一些消费者饿死。

## 启用HiPE

HiPE(High Performance Erlang)开启之后可以提升吞吐量，负面影响是增加启动时间；开启了 HiPE 之后，RabbitMQ会在启动时候编译，开启 HiPE 后性能会有 20%~80% 的提升，启动时长会增加 1~3 分钟。

## 禁用不需要的插件

插件会消耗CPU与内存，禁用不需要的插件。

## 不要在生产中将RabbitMQ管理统计速率模式设置为详细

Setting RabbitMQ Management statistics rate mode to detailed has a serious performance impact and should not be used in production.

## Use updated RabbitMQ client libraries

确保你使用的SDK是最新的稳定版本。

## Use latest stable RabbitMQ and Erlang version

使用最新稳定的RabbitMQ与Erlang版本。

## 谨慎使用TTL

死信投递与TTL是两个流行的特性，但是这两个特性对性能会有影响，在使用时候通常容易忽视这点。

### 死信投递

队列设置了 `x-dead-letter-exhcange` 属性将会接收到被拒绝的、或超时的消息。消息设置了 `x-dead-letter-routing-key` 后 routing key 将会在死信投递后被改变。

### TTL

队列设置了 `x-message-ttl` 属性后，消息将会被从队列中移除如果在TTL时间内未被消费。
