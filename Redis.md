## 安装redis

```
在/usr/local/src目录下下载redis安装包redis-6.2.6.tar.gz

# 进入/usr/local/src目录
cd /usr/local/src
# 下载redis安装包
# 解压
tar zxvf redis-6.2.6.tar.gz
# 进入
cd redis-6.2.6
# 编译
make
# 创建并且安装到指定目录
mkdir -p /usr/local/redis
make PREFIX=/usr/local/redis/ install
# 进入bin目录启动redis服务
cd /usr/local/redis/bin/
# ./redis-server是前台启动方式，我们需要使用后台启动方式，默认端口号是6379
cd /usr/local/src/redis-6.2.6
cp redis.conf /usr/local/redis/bin/
cd /usr/local/redis/bin/
vim redis.conf
找到daemonize no，将no改为yes后，保存退出
./redis-server redis.conf以指定配置文件启动redis
查看是否启动
./redis-cli
输入ping回车，出现PONG表示后台启动成功
```



	开启远程连接
	vim /usr/local/redis/bin/redis.conf
	注释掉bind 127.0.0.1
	将protected-mode yes改为 no
	增加远程登录密码
		进入底层模式
		输入/requirepass
		找到# requirepass foobared
		取消注释 修改foobared为自己需要的登录密码
	保存退出
	杀掉之前的redis进程
		ps -ef|grep redis
		kill -9 对应的pid
	
	重新启动
		./redis-server redis.conf
	
	控制台登录redis也需要输入密码
		./redis-cli
		auth 密码
		ping返回PONG即可
	
	出现了远程连接不上的问题，重装一遍redis解决



## redis基本使用

[redis 命令手册](https://redis.com.cn/commands.html)

### 基础命令

```
keys * 查看当前库所有key（阻塞式）  
type key1 查看key1类型
select x;//选择x号数据库
ttl key1 查看key1是否过期，未过期返回剩余过期时间，-1永不过期，-2已过期
expire key1 10 为key1设置10s过期时间
del key1 阻塞式删除
unlink key1 异步删除，fork一个线程去删
dbsize 查看当前数据库的key数量
flushdb 清空当前数据库
flushall 清空全部库
```

### 基本类型及其使用

五大数据类型：string，hash，list，set，有序集合sortedSet

#### String

地址：https://zhuanlan.zhihu.com/p/386706054

- set
- setnx
- setex
- get
- getset
- 

二进制安全，底层数据结构是SDS，可以存储任何数据【图片，视频等】，
使用场景：缓存、全局session、分布式锁、计数器
限制：value最大512M

#### 

string：
	存键值对
		set key value
	根据键取值
		get key
	一次性存多个键值对
		mset key1 value1 key2 value2 [keyn valuen...]
	一次性取多个值
		mget key1 key2 key3

#### Hash

地址：https://zhuanlan.zhihu.com/p/388650262

Redis Hash是 `键-值` 类型，值类型类似map结构，即 `key-{{field1,value1},...,{fieldN，valueN}}`，更适合来保存对象。

比如我们要保存用户的个人信息，在String类型中，我们会把这个对象序列号为 JSON 字符串保存，这种方式方便存取而不方便更新，如果想要新增一个属性，就需要更新整个value；而使用Hash类型可以保存到属性粒度，新增和删除属性都比较方便。

#### list:

地址：https://zhuanlan.zhihu.com/p/390177950

适用场景：队列、栈、

​	左添加
​		lpush redis_key value1 value2 ...
​			如果push张三和李四
​			首先放入张三
​				|张三|   |   |
​			放入李四的时候，先把张三往后移一位，再把李四放进来
​				|   |张三|   |
​				|李四|张三|  |
​				取的时候李四在前面，相当于向左旋转90°的栈（后进先出）

​	返回指定下标到指定下标的序列，从左边开始取
​		lrange redis_key start(从0开始) end(结束地方)
​			从左边开始取，以上面为例子，
​			返回
​				1)李四
​				2)张三
​	左弹出
​		lpop(key);
​		从左边弹出第一个数

​	右添加
​		rpush redis_key value1 value2 ...
​			相当于向右旋转90°的栈（后进先出）

​		rrange redis_key start(从0开始) end(结束地方)
​			从右边开始取
​			如果与上面的左添加添加的是同一个list
​			则现在的情况为
​				|李四|张三|王五|赵六|

​	查询list有多少数据
​		llen redis_key

​	从左边开始删除num个对应值，删的个数大于实际存在的个数时默认删除全部，不报错（注意：没有右删除）
​		lrem list_key num value 

​	右弹出
​		rpop(key);
​		从右边弹出第一个数			

#### set:

**适用场景**：

- 点赞、签到、打卡

- 标签

- 抽奖(spop命令会随机移除n个元素)

- 好友关系、用户关注、推荐模型

  - 对于一个用户 A，将它的关注和粉丝的用户 id 都存放在两个 set 中：
    A:follow：存放 A 所有关注的用户 id
    A:follower：存放 A 所有粉丝的用户 id

    **那么通过`sinter`命令便可以根据A:follow和A:follower的交集得到与 A 互相关注的用户**。当 A 进入另一个用户 B 的主页后，A:follow和B:follow的交集便是 A 和 B 的共同专注，A:follow和B:follower的交集便是 A 关注的人也关注了 B。

- 倒排索引

  倒排索引是构造搜索功能的最常见方式，在 Redis 中也可以通过set进行建立倒排索引，这里以简单的拼音 + 前缀搜索城市功能举例：
  假设一个城市北京，通过拼音词库将北京转为beijing，再通过前缀分词将这两个词分为若干个前缀索引，有：北、北京、b、be…beijin和beijing。将这些索引分别作为set的 key（例如:index:北）并存储北京的 id，倒排索引便建立好了。接下来只需要在搜索时通过关键词取出对应的set并得到其中的 id 即可。

**常用命令**

​		set存入数据：
​			sadd set_key value1 value2 ...
​			存入的是无序的，只要不添加或者删除，smembers set_key每次展示的顺序不会变
​		查看某个set中全部值
​			smembers set_key
​		查看某个set中数据个数
​			scard set_key
​		删除某set中数据
​			srem set_key value1 value2 ...

#### zset(sorted set):

**应用场景**

- 排行榜

**底层数据结构**

- 压缩列表

- 跳表

**命令**

1)基本命令： zadd/ zrange/ zrevrange/zrem/zcard

2)常用命令： zrangebyscore/zrevrangebyscore/zcount

- zadd

  作用：向集合中添加一个元素

  语法：zadd key [NX|XX] [CH] [INCR] score member [score member…]

  - XX: 仅仅更新存在的成员，不添加新成员。

    NX: 不更新存在的成员。只添加新成员。

- zincrby

  作用：对有序集合中指定成员的分数加上增量 increment

  语法：ZINCRBY key increment member
  分数值可以是整数值或双精度浮点数，可以是负数。
  当 key 不存在，或分数不是 key 的成员时， ZINCRBY key increment member 等同于 ZADD key increment member 。

- zrange
  语法：zrange key start stop [WITHSCORES]

  作用：查询有序集合，指定区间的内的元素。集合成员按 score 值从小到大来排序。

  start，stop 都是 从 0 开始。0 是第一个元素，1 是第二个元素，依次类推。

  以 -1 表示最后一个成员，-2 表示倒数第二 个成员。WITHSCORES 选项让 score 和 value 一同返回。

  返回值：自定区间的成员集合

- **zrevrange**语法：zrevrange key start stop [WITHSCORES]

  作用：返回有序集 key 中，指定区间内的成员。

  其中成员的位置按 score 值递减(从大到小)来排列。 其它同 zrange 命令。

  返回值：自定区间的成员集合

- **zrem**

  语法：zrem key member [member…]

  作用：删除有序集合 key 中的一个或多个成员，不存在的成员被忽略

  返回值：被成功删除的成员数量，不包括被忽略的成员。

- **zcard**

  语法：zcard key

  作用：获取有序集 key 的元素成员的个数

  返回值：key 存在返回集合元素的个数， key 不存在，返回 0

- **zrangebyscore**

  语法：zrangebyscore key min max [WITHSCORES ] [LIMIT offset count]

  - min ,max 是包括在内 ， 使用符号 ( 表示不包括。

    min，max可以使用 -inf ，+inf 表示 最小和最大 limit 用来限制返回结果的数量和区间。

    withscores 显示 score 和 value

  作用：获取有序集 key 中，所有 score 值介于 min 和 max 之间（包括 min 和 max）的成员，有序 成员是按递增（从小到大）排序。

  返回值：指定区间的集合数据

- **zrevrangebyscore**

  语法：zrevrangebyscore key max min [WITHSCORES ] [LIMIT offset count]

  作用：返回有序集 key 中， score 值介于 max 和 min 之间(默认包括等于 max 或 min )的所有的成 员。

  有序集成员按 score 值递减(从大到小)的次序排列。其他同 zrangebyscore

- **zcount**

  语法：zcount key min max

  作用：返回有序集 key 中， score 值在 min 和 max 之间(默认包括 score 值等于 min 或 max ) 的成员的数量

### 其他类型

#### bitmap

Bitmap不属于Redis的基本数据类型，而是**基于String类型进行的位操作**。而Redis中字符串的最大长度是 512M，所以 BitMap 的 **offset 值也是有上限的（0<=offset<2^32）**，其最大值是：`8 * 1024 * 1024 * 512  =  2^32`

详细：https://zhuanlan.zhihu.com/p/401726844

- SETBIT：设置比特位
- GETBIT：查询比特值
- BITCOUNT：统计比特值为1的数量
- BITPOS：查询第一个比特值为0或1的偏移量
- BITOP：对Bitmap做逻辑与、或、异或、非操作
- BITFIELD：将Bitmap看作由多个整数组成的，对其中的整数操作

适合一些数据量大且使用二值统计的场景。例如：签到、访问量

- setbit 

  可用版本：>= 2.2.0
  时间复杂度：O(1)

  语法：`setbit key offset value`

  **注意：**
  **如果设置较大的offset，内存分配可能会导致Redis阻塞。**
  如果key对应的字符串不存在或长度较短，但是设置的offset较大（比如最大为 `2^32 -1`），Redis需要对中间的位数进行内存分配，Redis可能会阻塞。
  拿2010 MacBook Pro举例，offset = 2^32 -1 (分配512MB内存)，需要耗时300ms左右；offset = 2^30 -1 (分配128内存)，需要耗时80ms左右；offset = 2^28 -1 (分配32MB内存)，需要耗时30ms左右；offset = 2^26 -1 (分配8MB内存)，需要耗时80ms左右。
  第一次分配内存后，后续对该key的相同操作不会再有内存分配开销。

- getbit

  `GETBIT key offset`

- bitcount
  key=用户id+2022，查询用户2022年登录天数

  `BITCOUNT key [start end]`

  - 统计给定字符串中，比特值为`1`的数量
  - 默认会统计整个字符串，同时也可以通过指定 `start` 和 `end` 来限定范围
  - `start` 和 `end` 也可以是负数，`-1`表示最后一个`字节`，-2表示倒数第二个字节。注意这里是`字节`，1字节=8比特
  - 如果key不存在，返回`0`

- **BITPOS**

  `BITPOS key bit [start [end]]`

  - 返回字符串中，从左到右，第一个比特值为`bit`（0或1）的偏移量
  - 默认情况下会检查整个字符串，但是也可以通过指定`start`和`end`变量来指定`字节`范围，与BITCOUNT中的范围描述一致
  - `SETBIT`和`GETBIT`指定的都是`比特`偏移量，`BITCOUNT`和`BITPOS`指定的是`字节`范围
  - 不论是否指定查询范围，该命令返回的偏移量都是基于0开始的
  - 如果key不存在，认为是空字符串

- bitop

  BITOP operation destkey key [key ...]

  - 对多个字符串进行位操作，并将结果保存到`destkey`中
  - operation 可以是 AND、OR、XOR 或者 NOT
  - 除了 `NOT` 操作之外，其他操作都可以接受一个或多个 `key` 作为输入。
  - 当给定的参数中，字符串长度不同时，较短的那个字符串与最长字符串之间缺少的部分会被看作 `0` 。
  - 空的 `key` 也被看作是包含 `0` 的字符串序列。

- 

#### HyperLogLog

一种估计集合基数的数据结构。作为一种概率数据结构，HyperLogLog 以完美的准确性换取了高效的空间利用。

**使用场景**

- 统计注册 IP 数
- 统计每日访问 IP 数
- 统计页面实时 UV 数
- 统计在线用户数
- 统计用户每天搜索不同词条的个数

HyperLogLog 实现最多使用 12 KB，并提供 0.81% 的标准误差。
**限制**：**HyperLogLog 可以估计具有多达（2^64) 个成员的集合的基数**。
**HyperLogLog 只会根据输入元素来计算基数，而不会储存输入元素本身**，所以 HyperLogLog 不能像集合那样，返回输入的各个元素。

- pfadd members value
  将项目添加到 HyperLogLog。时间复杂度O(1)
- pfcount members
  返回集合中项目数的估计值（一个带有 0.81% 标准错误的近似值.）。时间复杂度为O(N)
- pfmerge
  将两个或多个HyperLogLog合并为一个



#### geospatial

**底层原理是使用 zset来实现的，因此我们也可以使用 zset 的命令操作 geo。**

**应用场景：**

- 实现定位
- 社交软件附近的人
- 打车APP/地图导航上距离的计算
- 打车时，附近的空车

**命令**

- geoadd 添加地址位置
  - geoadd key 纬度 经度 名称
    - 示例
      geoadd city 116.40 39.90 beijing
- geopos 返回给定名称的经度和纬度
  - geopos key member
- geodist 返回两个给定位置之间的距离
  - geodist key member1 member2 距离单位
- geohash 返回给定的名称的11位的字符哈希值
  - geohash key member
    - 示例：
      输入`geohash city beijing` 
      返回 `wx4fbxxfke0`
- georadius 以给定经纬度为中心，找到某一个半径内的元素(member):
  - georadius key longitude latitude radius 单位。
    经纬度可以是随意值，radius是半径，还要加上距离单位。
- georadiusbymember 以一个成员为中心，查找指定范围内的元素(member)
  - georadiusbymember key member radius 单位
    单位：【m|km|ft|mi】

### 通用命令：

​	层级：
​		例子：
​		set cart:user01:item1 apple
​		cart:user01:item1相当于三级目录

	失效时间：
		redis有四个不同的命令可以用于设置键的生存时间
		expire <key> <ttl>:用于将键key的生存时间设置为ttl秒
		pexpire <key> <ttl>:用于将键key的生存时间设置为ttl毫秒
		expireat <key> <timestamp>:用于将key的过期时间设置为timestamp所指定的秒数时间戳
		pexpireat <key> <timestamp>:用于将key的过期时间设置为timestamp所指定的毫秒数时间戳
		ttl：获取的值为-1说明没有设置有效期（即永不过期），当值为-2证明过了有效期
	
		ttl key：查看key的有效剩余时间
	
		在初始化时设置有效期
			set key value ex(pex为毫秒) 10 [nx|xx]
			[]为可选，nx在key不存在时成功，xx在key存在时操作成功
		给已存在的键设置有效期
			expire(pexpire为毫秒) key 10
	
	通用删除命令：
		del key

## redis持久化方案：

​	1.redis关闭之后在内存的数据会消失，如果关闭后重启需要还能看见，需要备份到磁盘，命令为：
​		bgsave
​		此时宕机重启后，执行bgsave之前的数据都会存在
​		缺点：需要频繁使用

	2.rdb
		在redis.conf配置文件中查找save ，设置
			save 900 1   表示在900s内有1个key发生变化时，将数据持久化到磁盘
			save 300 10   表示在300s内有10个key发生变化时，将数据持久化到磁盘
			save 60 1000   表示在60s内有1000个key发生变化时，将数据持久化到磁盘
			缺点：如果save 60 1000，在58s宕机数据不会保存，所以还是可能数据丢失
	
	3.aof
		在redis.conf配置文件中查找appendonly，将no改为yes，则之前的rdb方案会自动失效
		aof是将我们的命令存储在一个aof文件中，每当服务器宕机再次重启时，redis会从这个文件中读取所有的命令，相当于模仿我们把这些命令重新敲一遍。
		缺点：随着时间积累，这个文件会越来越大，当服务器宕机下次重启时，redis重新读这个文件过程会非常慢

## redis主从

​	读写分离：
​	整个集群为基数台，因为规定集群环境下，大于百分之五十不可用表示集群不可用



## 哨兵



## 集群



## 分布式锁

线程A上锁：set lock value ex 60 nx 

如果value是未来某时间点的时间戳则可以不设置过期时间，等其他线程获取这个时间戳t1，然后与当前时间比较

- 如果还没有过期，返回false
- 如果过期了，计算新的时间戳t2，通过getset lock t2命令获取t3（这期间可能被其他线程修改）,如果t1==t3，获得锁；t1!=t3则说明锁被别的线程获取了。

获取到锁后，处理完业务逻辑，再去判断锁是否超时

- 如果没超时删除锁
- 超时则不用处理（防止删除其他线程的锁）

