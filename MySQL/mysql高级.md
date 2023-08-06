# MySQL

## 数据类型

### 整数类型

| tinyint   | 8bit  | -128 ~ 127 |
| --------- | ----- | ---------- |
| smallint  | 16bit |            |
| mediumint | 24bit |            |
| int       | 32    |            |
| bigint    | 64    |            |

**int(10)中的10只是表示显示字符的个数，并无实际意义。一般和unsigned zerofill配合使用才有意义。**
例如int(3)，如果属性为unsigned zerofill，则实际存储的数据为003

### 浮点数类型

**注意：float、double类型无法确保精度，很容易产生误差，特别是在求和计算的时候，所以当存储小数，特别是涉及金额时推荐使用DECIMAL类型。但是DECIMAL效率更低。**

DECIMAL从[MySQL](https://cloud.tencent.com/product/cdb?from=10680) 5.1引入，列的声明语法是DECIMAL(M,D)。NUMERIC与DECIMAL同义，如果字段类型定义为NUMERIC，则将自动转成DECIMAL。

- **设计实践**

  - 经常使用`DECIMAL`数据类型的货币数据，如价格，工资，账户余额等。如果要设计一个处理货币数据的数据库，则可参考以下语法 -

    ```sql
    amount DECIMAL(19,2);
    ```

    但是，如果您要遵守公认会计原则(GAAP)规则，则货币栏必须至少包含`4`位小数，以确保舍入值不超过`$0.01`。 在这种情况下，应该定义具有`4`位小数的列，如下所示：

    ```sql
    amount DECIMAL(19,4);
    ```

- **DECIMAL使用总结**

  - DECIMAL(M,D)中，M范围是1到65，D范围是0到30。

  - M默认为10，D默认为0，D不大于M。

  - DECIMAL(5,2)可存储范围是从-999.99到999.99，超出存储范围会报错。

  - 存储数值时，小数位不足会自动补0，首位数字为0自动忽略。

  - 当数值在其取值范围之内，小数位超出会截断，产生告警，并按四舍五入处理。

    若数值在其取值范围之外，则直接报Out of range value错误。

  - 使用DECIMAL字段时，建议M，D参数手动指定，并按需分配。

### 字符串类型

varchar用于存储可变长字符串，比char更省空间。
char是定长的，根据定义时的字符串长度分配空间。

**存储方式区别**：

char(M)类型的数据列里，每个值都占用M个字节，如果某个长度小于M，MySQL就会在它的右边用空格字符补足。（在检索操作中那些填补出来的空格字符将被去掉）
在varchar(M)类型的数据列里，每个值只占用刚好够用的字节再加上一个用来记录其长度的字节（即总长度为L+1字节）。

**应用场景**：

经常变更的数据用char更好，不容易产生碎片。对于非常短的列也是使用char更好，因为char效率比varchar高。一般避免使用text/blob等类型，因为查询时会使用临时表，造成严重的性能开销。

### 日期类型

| 类型      | 大小(字节) | 范围                                                         | 格式                | 用途                     |
| --------- | ---------- | ------------------------------------------------------------ | ------------------- | ------------------------ |
| year      | 1          | 1901/2155                                                    | YYYY                | 年份值                   |
| date      | 3          | 1000-01-01/9999-12-31                                        | YYYY-MM-DD          | 日期值                   |
| time      | 3          | '-838:59:59'/'838:59:59'                                     | HH:MM:SS            | 时间值或持续时间         |
| datetime  | 8          | 1000-01-01 00:00:00/9999-12-31 23:59:59                      | YYYY-MM-DD HH:MM:SS | 混合日期和时间值         |
| timestamp | 4          | 1970-01-01 00:00:00/2038结束时间是第 **2147483647** 秒，北京时间 **2038-1-19 11:14:07**，格林尼治时间 2038年1月19日 凌晨 03:14:07 | 10位时间戳          | 混合日期和时间值，时间戳 |

**TIMESTAMP和DATETIME比较**

- 相同点：两者都可用来表示YYYY-MM-DD HH:MM:SS 类型的日期。

- 不同点：他们的的存储方式，大小(字节)，表示的范围不同。

  **TIMESTAMP**，它把客户端插入的时间从当前时区转化为UTC（世界标准时间）进行存储。查询时，将其又转化为客户端当前时区进行返回。 

  - 4个字节储存
  - 值以UTC格式保存
  - 时区转化 ，存储时对当前的时区进行转换，检索时再转换回当前的时区。
  - TIMESTAMP值不能早于1970或晚于2037

  **DATETIME**，不做任何改变，基本上是原样输入和输出。 

  - 8个字节储存
  - 与时区无关
  - 以'YYYY-MM-DD HH:MM:SS'格式检索和显示DATETIME值。
    支持的范围为'1000-01-01 00:00:00'到'9999-12-31 23:59:59'

  总结：TIMESTAMP和DATETIME 都可用来表示YYYY-MM-DD HH:MM:SS 类型的日期， 除了存储方式和存储范围以及大小不一样，没有太大区别。但对于跨时区的业务，TIMESTAMP更为合适。

**13位时间戳存储要么存为bigint，要么存为varchar(13)类型。不能使用int，因为“13位时间戳只能存bigint ，因为13位时间戳超出了int的范围”。（TIMESTAMP只能存10位）**

## 基本语法

```sql
查看所有数据库名称：SHOW DATABASES；
切换数据库：USE mydb1;
创建数据库：CREATE DATABASE [IF NOT EXISTS] mydb1；
删除数据库：DROP DATABASE [IF EXISTS] mydb1；
修改数据库编码：ALTER DATABASE mydb1 CHARACTER SET utf8

```

```sql
create table if not exists table_A(
    
)engine=innodb default charset=utf8mb4;
```

```sql
insert into table_A(id, name) values(1, 'thy');
insert into table_A values(1,'thy','男');

update table_A set name='thy' where id=1;

select distinct * from A whrer id>1 or name like 't%' group by name having avg(grade) > 60 order by asc limit 5 offset 0;  

delete from table_A where id=1;
DELETE FROM stu; 
# truncate 是先DROP TABLE，再CREATE TABLE。而且TRUNCATE删除的记录是无  法回滚的，但DELETE删除的记录是可以回滚的
TRUNCATE TABLE stu;
```



## 设计表的经验准则

- 命名规范
- 选择合适的字段类型
  - 尽可能选择存储空间小的字段类型
  - 小数用decimal，禁止使用float、double
  - 如果存储的字符串长度几乎相等，使用char定长字符串类型
  - varchar是可变长字符串，不预先分配空间，长度不要超过5000
  - 如果存储的值太大，建议修改类型为text，同时抽出单独一张表，用主键与之对应
- 主键设计要合理：最好是毫无意义的一串独立不重复的数字
- 选择合适的字段长度
- 优先考虑逻辑删除，而不是物理删除：恢复数据很困难、物理删除会使自增主键不再连续、
- 每个表都应该具备id、created_time、updated_time，逻辑删除再加上is_deleted
- 一张表的字段不宜过多，尽量不超过20个：字段多时拆分为两张表 条件查询表、详细内容表
- 尽可能使用not null定义字段：null值存储也需要额外空间，会导致比较运算复杂，使优化器难以优化；null值会导致索引失效
- 一张表索引不要超过5个；区分度高的才建立索引；数据量大的建立索引
- 不需要严格遵守3NF，适当通过字段冗余来减少表关联
- 不用外键关联，在代码维护：外键不方便（delete、update需要考虑外键约束）、分库分表不能用外键
- 时间类型尽量使用datetime：datetime够全面，datetime与时区无关、timestamp与时区有关

## 外键策略

### 1.no action (拒绝执行 restrict)

例子：

alter table t_student  add constraint fk_cno_student foreign key (classno) references t_class(cno);

这种策略不能直接删，如果要删则先将2班所有学生的外键classno(班级号)改为null，然后再删除2班这个班级就可以了。

update t_student set cno=null where cno=2;

delete from t_class where cno=2; 

### 2. cascade (级联操作)

比如 删除班级5，则5班的同学也会被删除；更新班级3为5，则3班同学所有的班级号都会变为5

例如：在更新和删除外键的时候t_student会执行级联操作。（慎用）

alter table t_student  add constraint t_B foreign key (classno) references B(cno) on update cascade on delete cascade;

### 3.set null (置空操作)

例如 删除班级5，则5班的同学班级号会被置为空

alter table t_student  add constraint t_B foreign key (classno) references B(cno) on update set null on delete set null;

```sql
注意：

策略2和策略3可以混着写:
alter table t_student  add constraint t_B foreign key (classno) references B(cno) on update cascade on delete set null;

应用场合：
级联操作：删除朋友圈，则该条朋友圈的点赞评论信息也同样删掉
置空操作：解散班级，将同学分散到其他班级，则班级中同学的班级号置为null，班级同学的信息不应该删掉
```

技巧：

复制表A结构和数据：create table B as select * from A;

复制表A结构：create table B as select * from A where 1=2;

复制部分表A结构和数据：create table B as select col1,col2 from A where col1=1;

```
delete与truncate区别:
虽然delete与truncate都能删除表中全部数据，但还是有一些区别：
1.delete为数据操纵语言DML；truncate为数据定义语言DDL
2.delete操作是将表中所有记录一条一条删除直到删除完；truncate操作则是保留了表的结构，重新创建了这个表，所有状态都相当于新表，所以truncate效率更高
3.delete操作可以回滚；truncate操作会导致隐式提交，因此不能回滚
4.delete操作执行成功会返回已删除的行数(affected rows:4)；truncate操作不会返回已删除的行数,结果通常为 affected rows:0
5.delete删除表中记录后，再次向表中添加新纪录时，对于设置自增约束字段的值会从删除前表中该字段的最大值加1开始自增；truncate操作则会重新从1开始自增。
```



## 事务

### 事务并发问题

1.脏读

2.不可重复读

3.幻读

```
不可重复读与幻读区别：
不可重复读的重点是修改，幻读的重点在于新增或者删除。

解决不可重复读的问题只需锁住满足条件的行，解决幻读需要锁表
```

### 事务隔离级别

| 隔离级别                           | 脏读 | 不可重复读 | 幻读 |
| ---------------------------------- | ---- | ---------- | ---- |
| read uncommitted(没提交的也能读到) | y    | y          | y    |
| read committed(只读提交后的数据)   | n    | y          | y    |
| repeatable read                    | n    | n          | y    |
| serializable                       | n    | n          | n    |

一般不用serilizable(序列化)，因为效率太低，要锁表。一般默认是repeatable read。

```
查看数据库当前默认隔离级别 
select @@transaction_isolation;

设置当前会话的隔离级别
set session transaction isolation level 对应隔离级别;
```

## 存储过程

简单来说，存储过程就是数据库中保存的一系列SQL命令的集合。sql基本是一个命令实现一个处理，是所谓的非程序语言，在不能编写流程的情况下，所有的处理只能通过一个个命令来实现。当然，通过连接和子查询也能实现一些高级的处理，但局限性显而易见，例如在SQL中就很难实现针对不同的条件进行不同处理以及循环等功能，所以就出现了存储过程这个概念，相当于java中的方法。

优点：

- 提高执行性能。存储过程执行效率之所以高，在于普通的SQL语句，每次都会对语法分析，编译，执行，而存储过程只是在第一次执行语法分析，编译，执行，以后都是对结果进行调用。
- 减轻网络负担。使用存储过程，复杂的数据库操作也可以在数据库服务器中完成，只需要从客户端传递给数据库必要的参数就行。
- 可将数据库的处理黑匣子化。应用程序中完全不用考虑存储过程的内部详细处理，只需要知道调用那个存储过程就行了。

定义一个存储过程

```sql
1.定义一个无返回值的存储过程
create procedure mypro01(name varchar(10))
begin
	if name is null or name = "" then
		select * from emp;
	else
		select * from emp where ename like concat('%',name,'%');
	endif;
end;
存储过程中拼接字符串不能直接+，要用concat函数

删除存储过程：
drop procedure mypro01;

调用存储过程：
call mypro01('x'); 
call mypro01(null);

2.定义一个有返回值的存储过程
	in表示参数（可省略），out表示返回值
	found_rows() 是mysql中定义的一个函数，作用返回查询结果的条数。
create procedure mypro02(in name varchar(10),out num int(3))
begin
	if name is null or name = "" then
		select * from emp;
	else
		select * from emp where ename like concat('%',name,'%');
	endif;
	select found_rows() into num;
end;

调用存储过程：
call mypro02(null,@null);
查看返回值
select @num;
```

## 索引优化分析

### 索引

是什么？是帮助mysql高效获取数据的数据结构。（排好序的快速查找数据结构）

目的？提高查询效率，类比字典

分类（一个表最好最多只建立5个索引，但不是必须）

- 单值索引
  - 一个索引只包含一个列，一个表可有多个单列索引
  - create index index_tableA on tableA(column1)
- 唯一索引
  - 索引列的值必须唯一，但允许有空值
- 复合索引
  - 一个索引包含多个列

语法

```
create [unique] index index_name on table1(col1);
alter table1 add index index_name (col1);//普通索引
alter table1 add unique index_name (column);//唯一索引，可以为null
alter table1 add primary key (col1);//主键也算一种唯一索引，且不能为null
alter table1 add fulltext index_name (col1);//全文索引
drop index index_name on table1;//删除索引
show index from table1;//查看索引
```

mysql索引结构：

- BTree索引
- Hash索引
- full-text全文索引
- R-Tree索引

需要创建索引的情况：

- 主键自动创建唯一索引
- 频繁作为查询条件的字段应该创建索引
- 查询中与其他表关联的字段，即外键关系建立索引
- 频繁更新的字段不适合创建索引(每次更新记录、索引)
- where条件中用不到的字段不创建索引
- 单键/组合索引的选择问题（高并发下倾向创建组合索引）
- 查询中排序的字段，排序字段若通过索引去访问将大大提高排序速度
- 查询中统计或者分组字段

不需要创建索引的情况：

- 表记录太少（300w左右性能才开始下架）

- 经常增删改的表（提高了查询速度，同时却会降低更新表的速度，因为更新表时不仅要保存数据，还要保存索引文件）

- 数据重复且分布平均的表字段，因此应该只为最经常查询和最经常排序的数据列建立索引。（如果某个数据列包含许多重复的内容，为它建立索引就没有太大的实际效果。）

  ```
  	假如一个表有10万行记录，有一个字段A只有T和F两种值，且每个值的分布概率大约为50%，那么对这种表A字段建索引一般不会提高数据库的查询速度。
  	索引的选择性是指索引列中不同值的数目与表中记录数的比。如果一个表中有2000条记录，表索引列有1980个中不同的值，那么这个索引的选择性就是1980/2000=0.99。
  一个索引的选择性越接近于1,这个索引的效率就越高。
  
  ```

  

#### InnoBD与MyISAM的区别

存储引擎InnoDB,MyISAM索引底层用的是B+树，MEMORY索引底层用的是hash

InnoBD支持自适应hash，即人为不能控制，系统会把b+树转成hash索引。

- .frm存储的数据的结构
- .ibd存储的数据的真实文件和索引

MyISAM数据和索引是分开存放的

- .frm存储的数据的结构
- .MYD存储的数据的真实文件
- .MYI存储的索引



mysql5.5之后默认存储引擎为InnoDB，其与MyISAM的区别：

|          | InnoDB                                                       | MyISAM                                                 |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| 主外键   | 支持                                                         | 不支持                                                 |
| 事务     | 支持                                                         | 不支持                                                 |
| 锁的粒度 | 行锁，适合高并发操作                                         | 表锁，即使操作一条数据也会锁住整个表，不适合高并发操作 |
| 缓存     | 缓存索引和真实数据，对内存要求较高，且内存大小对性能有决定性影响 | 只缓存索引，不缓存真实数据                             |
| 表空间   | 大                                                           | 小                                                     |
| 关注点   | 事务                                                         | 性能                                                   |
| 适应场景 | 写多读少                                                     | 读多写少                                               |
| 默认安装 | y                                                            | y                                                      |

#### InnoDB索引

InnoDB存储索引支持以下常见索引：

- B+树索引
- 全文索引
- 哈希索引
  - InnoDB支持的哈希索引是自适应的，它会根据表的使用情况自动为表生成哈希索引，不能人为干预是否在一张表中生成哈希索引。

为什么InnoDB默认用B+树索引？

首先，hash虽然在增删改查为O(1)，但是在范围/排序的时候会退化到O(n)，例如查找学号在1~n之间的需要找n次。

然后用到普通二叉树，稳定在(O(logn))，比哈希范围/排序退化后的O(n)要好。但是普通二叉树可能会出现极端情况退化成链表(左倾右倾)的情况，所以考虑用AVL树(平衡二叉树)来解决左倾右倾的情况，但是虽然从算法的数学逻辑上来说二叉树的查找速度和比较速度都是最小的， 但是事实上，当数据很大时(比如100万数据)，树的深度也会变很大，导致查找次数增多即IO次数增多（磁盘IO次数最坏情况下就等于树的高度）。所以需要将树”瘦高“的形状尽量压缩成”矮胖“，即通过减少树的高度来减少磁盘IO次数。

再考虑B树(也叫B-树，2-3树)，首先数据库的索引是存储在磁盘上的，如果数据很大，必然导致索引的大小也会很大，可能超过几个G，但当我们利于索引查询的时候，是不可能将全部几个G的索引都加载到内存的，只能逐一加载每一个磁盘页，因为磁盘页（系统从磁盘读取数据到内存是以磁盘块为基本单位的，InnoDB磁盘页默认大小为16KB，页是innodb操作数据的最小逻辑单位，一页有若干块）对应着索引树的节点。比AVL树减少了IO次数。

最终的B+树：



### explain之性能分析

使用explain关键字可以模拟优化器执行sql查询语句，从而知道mysql是如何处理sql语句的。分析查询语句或表结构的性能瓶颈。

**使用**：explain + sql语句

#### 能查到什么：

- 表的读取顺序
- 数据读取操作的操作类型
- 哪些索引可以使用
- 哪些索引被实际使用
- 表之间的引用
- 每张表有多少行被优化器查询

#### 字段解析：

执行计划包含的信息：

id，type，key，rows，extra划重点。

- id（用于获取表的读取顺序）

  - select查询的序列号，包含一组数字，表示查询中执行select子句或操作表的顺序。

  - id相同可以看成是一组，从上往下顺序执行；在所有组中，id值越大，优先级越高，越先执行。

    - 

      ![img](file:///C:\Users\田何义\AppData\Roaming\Tencent\Users\485280869\QQ\WinTemp\RichOle\4YRP}{6@7DFO1I_D2DS9QWX.png)

      ![image-20220101013019086](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20220101013019086.png)

- select_type（用于获取数据读取操作的操作类型）

  - 有哪些：simple，primary，subquery，derived，union，union result
    - simple：简单的select查询，查询中不包括子查询或者union
    - primary：查询中若包含任何复杂的子部分，最外层查询则被标记为primary
    - subquery：在select或者where列表中包含的子查询
    - derived：在from列表中包含的子查询被标记为derived(衍生)，mysql会递归执行这些子查询，把结果放在临时表中(derived2表示是由id为2的查询衍生出)
    - union：若第二个select出现在union之后，则被标记为union，若union包含在from子句的子查询中，外层select将被标记为derived
    - union result：从union表获取结果的select
  - 作用：查询类型，用于区别普通查询、联合查询、子查询等的复杂查询

- table（用于显示是来自第几张表）

- type（显示查询使用了何种类型）

  - 从最好到最差(常见的)：system>const>eq_ref>ref>range>index>ALL
    - system：表只有一行记录(等于系统表)，这是const类型的特例，平时不会出现，可忽略不计，掌握理论
    - const：**表示通过索引一次就找到了，const用于比较primary key或者unique索引。因为只匹配一行数据，所以很快。常见于操作单表**。（例如将主键置于where列表中，mysql就能将该查询转换为一个常量。select * from s where s.id=1;）
    - eq_ref：**唯一性索引扫描，对于每个索引键，表中只有一条记录与之匹配。常见于多表联合操作中主键或唯一索引扫描**。（例如表a主键id1，表b主键id2 ，expalin select * from a,b where a.id1=b.id2中表a就是eq_ref）
    - ref：**非唯一性索引扫描**，返回匹配某个单独值的所有行，本质上也是一种索引访问，它返回所有匹配某个单独值的行，**然而，它可能会找到多个符合条件的行**，所以它应该属于查找和扫描的混合体。（例如student有一个复合索引(name,age)，explain select * from student where name=xxx;）
    - range：只检索给定范围的行，使用一个索引来选择行。key列显示使用了哪个索引一般就是在你的where语句中出现了between、<、>、in等的查询。这种范围扫描索引扫描比全表扫描要好，因为它只需要开始于索引的某一点，而结束于另一点，不用扫描全部索引。
    - index：full index scan，全索引扫描，index与all区别为index类型只遍历索引树。通常比all快，因为索引文件通常比数据文件小。(也就是说虽然all和index都是读全表，但index是从索引中读取的，而all是从硬盘中读的)（例如select id from t1，id为索引列）
    - ALL：全表扫描，遍历全表找到需要的行
  - 一般来说，得保证查询至少达到range级别，最好能达到ref
  - 不要为了优化而优化，mysql百万级别性能才开始下降

- possible_keys（可能会用到的索引）

  - 显示可能应用在这张表中的索引，一个或多个。查询涉及到的字段上若存在索引，则该索引将被列出，**但不一定被查询实际使用**。

- key（实际使用的索引，不一定在possible_keys中）（判断索引失效）

  - 如果为NULL，则没有使用索引。查询中若使用了覆盖索引，则该索引仅出现在key列表中。

- key_len（表示索引中使用的字节数，可通过该列计算查询中使用的索引的长度。在不损失精确性的情况下，长度越短越好）

  - key_len显示的值为索引字段的最大可能长度，并非实际使用长度，即key_len是根据表定义计算而得，不是通过表内检索出的。

- ref（显示索引的那一列被使用了，如果可能的话，最好是一个常数。说明哪些列或常量用于查找索引列上的值）

  - 类型：const、数据库名.表名.列名

- rows（根据表统计信息及索引选用情况，大致估算出找到所需记录需要读取的行数，越少越好）

- extra（包含不适合在其他列中显示但十分重要的额外信息）

  using filesort,using temporary,using index划重点

  - using filesort（mysql自己内部查询排一序，出现了应该尽快优化）
    - 说明mysql会对数据使用一个外部的索引排序，而不是按照表内的索引顺序进行读取。mysql中无法利用索引完成的排序操作称为“文件排序”。
    - ![img](file:///C:\Users\田何义\AppData\Roaming\Tencent\Users\485280869\QQ\WinTemp\RichOle\X8G1QXPOH7FO3GBG1%[_3DB.png)
  - using temporary（比using filesort更差）
    - 使用临时表保存中间结果，mysql在对查询结果排序时使用临时表。常见于order by和分组查询group by；
    - 一般要么不建索引，要么group by跟索引的顺序和个数来。例子中创建了索引(idx_col1_col2)，在group by中以col2和(col1，col2)来查询的性能完全不一样。
    - ![image-20220101221851681](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20220101221851681.png)
  - using index
    - 表示相应的select操作中使用了覆盖索引，避免访问了表的数据行，**效率不错**！(例如创建了一个复合索引idx_col1_col2，查询使用select col1,col2 from A就是使用了覆盖索引，即select的列要是某复合索引的子集)
    - 复合索引：就是select的数据列只用从索引中就能直接获取，不必读取数据行，mysql可以利于索引返回select列表中的字段，而不必根据索引再次读取数据文件，换句话说就是查询的列要被所建的索引覆盖。
    - 如果同时出现了using where，表明索引被用来执行索引键值的查找。
      - ![img](file:///C:\Users\田何义\AppData\Roaming\Tencent\Users\485280869\QQ\WinTemp\RichOle\6B0M2CM]B3Z{ZYFD]XDO_3K.png)
    - 如果没有出现using where，表明索引用来读取数据而非执行查找动作。
      - ![image-20220101223005976](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20220101223005976.png)
  - using where(使用了where子句)
  - using join buffer(使用了连接缓存，在使用多个jion的时候出现，可能需要调大一点jion buffer)
  - impossible where（where子句的值总是false，不能用来获取任何元组）
  - select tables optimized away（在没有group by子句的情况下，基于索引优化min/max操作或者对于MyISAM存储引擎优化count(*)操作，不必等到执行阶段再进行计算，查询执行计划生成的阶段即完成优化）
  - distinct：优化distinct操作，在找到第一匹配的元组后即停止找同样值的操作

### 索引优化：

#### 索引分析：

单表

```sql
#初始化
CREATE TABLE IF NOT EXISTS 'article'(
'id' INT(10) UNSIGNED NOT NULL PRIMARY KEY AUTO INCREMENT,
'author' id INT(10) UNSIGNED NOT NULL,
'category_id' INT(10) UNSIGNED NOT NULL,
'views' INT(10) UNSIGNED NOT NULL,
'comments' INT(10) UNSIGNED NOT NULL,
'title' VARBINARY(255) NOT NULL,
'content' TEXT NOT NULL,
INSERT INTO articlk ( author id, category_ id', i views', ' comments', title
content ) VALUES
(1,1,1,1,'1','1'),
(2,2,2,2,'2','2'),
(1,1,3,3,'3','3');
#查询category_id为1且comments大于1的情况下,views最多的article_id
EXPLAIN SELECT id,author_id FROM article WHERE category_id=1 AND comments > 1 ORDER BY views DESC LIMIT 1;
#结论:很显然,type是ALL,即最坏的情况。Extra 里还出现了Using filesort,也是最坏的情况。优化是必须的。
```

优化

```sql
#开始优化:
# 1.1新建索引+删除索引
#ALTER TABLE article ADD INDEX idx_article_ccv(category_id,comments,views);
create index idx_article_ccv on article(category_id,comments,views);

# 1.2第2次EXPLAIN
EXPLAIN SELECT id,author_id FROM article WHERE category_id =1 AND comments >1 ORDER BY views DESC LIMIT 1;
EXPLAIN SELECT id,author_ _id FROM' article' WHERE category_ _id = 1 AND comments =3 ORDER BY views DESC LIMIT 1
#结论:
#type变成了range,这是可以忍受的。但是extra里使用Using filesort仍是无法接受的。
#但是我们已经建立了索引,为啥没用呢?
#这是因为按照BTree索引的工作原理,先排序category_id,如果遇到相同的category_id则再排序comments,如果遇到相同的comments则再排序views。当comments字段在联合索引里处于中间位置时，因comments > 1条件是一个范围值(所谓range),所以MySQL无法利用索引再对后面的views部分进行检索,即range类型查询字段后面的索引失效。

# 1.3删除第一次建立的索引
DROP INDEX idx_article_ccv ON article;

# 1.4第2次新建索引
#ALTER TABLE article ADD INDEX idx_article_cv(category_id,views);
create index idx_article_cv on article(category_id,views);

# 1.5第3次EXPLAIN
EXPLAIN SELECT id,author_id FROM article WHERE category_id=1 AND comments > 1 ORDER BY views DESC LIMIT 1;
#结论:可以看到,type变为了ref, Extra中的Using filesort 也消失了,结果非常理想。
DROP INDEX idx_ _article_ _cv ON article;
```

两表

```sql
CREATE TABLE IF NOT EXISTS 'class' (
'id' INT(10) UNSIGNED NOT NULL AUTO_ INCREMENT,
'card' INT(10) UNSIGNED NOT NULL,
PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS 'book' (
'bookid' INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
'card' INT(10) UNSIGNED NOT NULL,
PRIMARY KEY ('bookid')
);
```

分析

```sql
#分析
explain select * from class left join book on class.card=book.card;
#结果：type都为ALL
#给左连接右边的book表的card增加索引优化后 第二行的type变为了ref
#这是由左连接特性决定的。left join条件用于确定如何从右表搜索行，左边一定都有，所以右边是关键点，一定需要建立索引。（灵活使用，对调表的位置使得索引在左连接的右边）
#同理右连接左边也要建立索引。
```

三表

```sql
#基于二表再建立一张表，且同时删去二表中增加的索引
create table `phone`(
`phoneid` int(10) UNSIGNED not null auto_increment,
`card` int(10) UNSIGNED not null,
primary key(`phoneid`)
)ENGINE=INNODB;
```

分析

```sql
explain select * from 
class left join book on book.card=class.card left join phone on book.card=phone.card;
#type都为all
#基于二表索引优化原理，在book和phone的card增加索引优化后，二三行type都变为ref且总rows优化很好，因此索引最好设置在需要经常查询的字段中。

#join语句的优化：
1.尽可能减少join语句中的nestedLoop的循环总次数，不要join过多或嵌套；“永远用小结果集驱动大的结果集”
2.优先优化nestedLoop的内层循环
3.保证join语句中被驱动表上join条件字段已经被索引
4.当无法保证被驱动表的join条件字段被索引且内存资源充足的前提下，不要太吝啬joinBuffer的设置。
```

#### 索引失效(应该避免)

建表

```
CREATE TABLE `staffs`(
`id` INT PRIMARY KEY AUTO_INCREMENT,
`NAME` VARCHAR(24) NOT NULL DEFAULT '' COMMENT '姓名',
`age` INT NOT NULL DEFAULT 0 COMMENT '年龄',
`pos` VARCHAR(20) NOT NULL DEFAULT '' COMMENT '职位',
`add_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入职时间'
) CHARSET utf8 COMMENT '员工记录表' ;

alter table `staffs` add index idx_staffs_nameAgePos(`name`,`age`,`pos`);
```

##### 案例

1.全值匹配我最爱（where用到了复合索引的全部索引列）
![这里写图片描述](https://img-blog.csdn.net/20170516172041046?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

2.最佳左前缀法则

```
如果索引了多列，要遵守最左前缀法则。指的是查询从索引的最左前列开始并且不跳过索引中的列。
口诀：带头索引不能死，中间索引不能断。
```

3.不在索引列上做任何操作(计算、函数、(自动or手动)类型转换)，会导致索引失效而转向全表扫描
![这里写图片描述](https://img-blog.csdn.net/20170516174443642?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

4.存储引擎不能继续使用索引中范围条件(between,<,>,in等)右边的列（即范围之后全失效）
![这里写图片描述](https://img-blog.csdn.net/20170516174803880?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)上面例子中复合索引就只用到age，age之后的索引列没用到

5.尽量使用覆盖索引(只查询索引的列(索引列和查询列一致))，减少select*
![这里写图片描述](https://img-blog.csdn.net/20170516175319340?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

6.mysql在使用不等于(!=或者<> )的时候无法使用索引会导致全表扫描
7.is null ,is not null也导致索引失效转而全表扫描
![这里写图片描述](https://img-blog.csdn.net/20170516180529160?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

8.like以通配符开头('%字符串')时，mysql索引失效会变成全表扫描（%加like右边才不会索引失效）
![这里写图片描述](https://img-blog.csdn.net/20170516181258382?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

解决like '%字符串%' 时，索引失效问题的方法？使用覆盖索引解决
（查询列均为索引字段不能有非索引字段或者使用*）

9.字符串类型不加单引号索引失效（会隐式转换类型）
![这里写图片描述](https://img-blog.csdn.net/20170516183219285?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

10.少用or,用它来连接时会索引失效
![这里写图片描述](https://img-blog.csdn.net/20170516183409913?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

##### 总结：

![这里写图片描述](https://img-blog.csdn.net/20170516183651502?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

![这里写图片描述](https://img-blog.csdn.net/20170516232713411?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvd3VzZXl1a3Vp/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)  

## 查询截取分析

```
----分析-----
1.观察，至少跑一天，看看生产的慢SQL情况
2.开启慢查询日志，设置阈值，比如超过5s的就是慢SQL,并将它抓取出来
3.explain+慢sql分析
4.show profile
5.运维经理 or DBA 进行SQL数据库服务器的参数调优
----总结-----
1.慢查询的开启并捕获
2.explain+慢sql分析。
3.show profile查询sql在mysql服务器中的执行细节和生命周期情况。
4.sql数据库服务器的参数调优
```

### 查询优化

#### 小表驱动大表

永远**小表驱动大表**(类似嵌套循环nested Loop)，即小数据集驱动大数据集

```
（in和exists的区别）考察的小表驱动大表
select * from A where id in (select id from B)等价于
for select id from B
for select * from A where A.id = B.id
当B表的数据集小于A表的数据集时，用in优于exists

select * from A where exists (select 1 from B where A.id=B.id)等价于
for select * from A
for select * from B where B.id=A.id
当A表的数据集小于B表的数据集时，用exists优于in
注意：A与B的ID字段应建立索引。
```

#### **order by关键字优化**

order by子句，尽量使用Index方式排序，避免使用FileSort方式排序。

mysql支持两种方式的排序：FileSort和Index，Index效率高，它指mysql扫描索引本身完成排序。FileSort方式效率较低。
order by满足两种情况会使用Index排序：order by语句满足索引最佳左前缀，使用Where子句与order by子句条件列组合满足索引最左前列(where a=常量 order by b,c)。
如果不在索引列上，产生using filesort，filesort有两种算法：双路排序和单路排序

```markdown
双路排序：mysql4.1之前是使用双路排序，字面意思就是两次扫描磁盘，最终得到数据，读取行指针和order by列，对他们进行排序，然后扫描已经排序好的列表，按照列表中的值重新从列表中读取对应的数据输出。
从磁盘取排序字段，在buffer进行排序，再从磁盘取其他字段。
即取一次数据，要对磁盘进行两次扫描，众所周知，I\O是很耗时的，所以在mysql4.1之后，出现了第二种改进的算法，就是单路排序。
单路排序：从磁盘读取查询需要的所有列，按照order by列在buffer对它们进行排序，然后扫描排序后的列表进行输出，它的效率更高，避免了第二次读取数据。并且把随机IO变成了顺序IO，但是他会使用更多的空间，因为它把每一行都保存在内存中了。

由于单路是后出的，总体而言好过双路。但是单路有问题：
	在sort_buffer中，方法B比方法A要多占空间，因为B是把所有字段都取出，所以有可能取出的数据的总大小超过了sort_buffer的容量，导致每次只能取sort_buffer容量大小的数据，进行排序(创建tmp文件，多路合并)，排完再去取sort_buffer容量大小，再排...从而多次IO。即本来想省一次IO操作，反而导致了大量的IO操作，反而得不偿失。
```

```
提高Order By的速度
1.使用Order by时用select *是一个大忌，只Query需要的字段，这点非常重要。 在这里的影响是: 
	1.1当Query的字段大小总和小于max_length_for_sort_data 而且排序字段不是TEXT|BLOB类型时，会用改进后的算法单路排序，否则用老算法多路排序。
	1.2两种算法的数据都有可能超出sort_buffer的容量，超出之后，会创建tmp文件进行合并排序，导致多次I/O, 但是用单路排序算法的风险会更大一些,所以要提高sort_buffer_size.
2.尝试提高sort_buffer_size
不管用哪种算法，提高这个参数都会提高效率，当然，要根据系统的能力去提高，因为这个参数是针对每个进程的。
3.尝试提高max_length_for_sort_data
提高这个参数，会增加用改进算法的概率。但是如果设的太高，数据总容量超出sort_buffer_size的概率就增大，明显症状是高的磁盘I/O活动和低的处理器使用率.
```

总结：

```
为排序使用索引
MySq|两种排序方式:文件排序或扫描有序索引排序
MySq|能为排序与查询使用相同的索引
KEY a_b_c(a,b, c)
order by能使用索引最左前缀
	-ORDER BY a
	-ORDER BY ab
	-ORDER BYa, b, C
	-ORDERBYa DESC, b DESC, C DESC

如果WHERE使用素引的最左前缀定义为常量。则order by能使用索引
	-WHERE a=constORDERBYb,C
	-WHERE a = const AND b = const ORDER BY C
	-WHERE a=constORDERBYb,C
	-WHERE a = const AND b > const ORDERBY b, C
不能使用索引进行排序
	-ORDER BY a ASC,b DESC,C DESC /*排序不一效”/
	-WHERE g = const ORDER BY b,c /丢失a索引*/
	-WHERE a = const ORDER BY c /*丢失b素引*/
	-WHERE a = const ORDER BY a,d /* d不是素引的一郜分*/
	-WHERE a in(...) ORDER BY b,C /*对于排序来说,多个相等条件也是范围查询”/
```

![image-20220106000905588](C:\Users\田何义\AppData\Roaming\Typora\typora-user-images\image-20220106000905588.png)

#### **group by关键字优化**

group by实质是先排序后进行分组，遵照索引建的最佳左前缀。
当无法使用索引列，增大max_length_for_sort_data参数的设置+增大sort_buffer_size参数的设置。
where高于having，能写在where中的限定条件就不要用having限定了。

### 慢查询日志

MySQL的慢查询日志是MySQL提供的一种日志记录，它用来记录在MySQL中响应时间超过阀值的语句。
具体指运行时间超过long_query_time值的SQL，会被记录到慢查询日志中。long_query_time的默认值为10，意思是运行10秒以上的语句。
由它来查看哪些SQL超出了我们的最大忍耐时间值，比如一条sql执行超过5秒钟，我们就算慢SQL，希望能收集超过5秒的sql,结合之前explain进行全面分析。

**默认情况下，mysql没有开启慢查询日志**，需要手动设置这个参数。当然，**如果不是调优需要的话，一般不建议启动该参数**，因为开启慢查询日志会或多或少带来一定的性能影响。慢查询日志支持将日志记录写入文件。

```sql
# 1.查询是否开启(默认情况下slow_query_log的值为OFF，表示慢查询日志是禁用的)
show variables like '%slow_query_log%';
# 2.及如何开启（使用此命令只对当前数据库生效，如果mysql重启后则会失效）
set global slow_query_log=1;
#如果要永久生效，就必须修改配置文件my.cnf(其他系统变量也是如此)
修改my.cnf文件,[mysqld]下增加或修改参数slow_query_log和slow_query_log_file后，重启mysql。
配置：slow_query_log=1和slow_query_log_file=文件路径
关于慢查询的参数slow_query_log_file ，它指定慢查询日志文件的存放路径，系统默认会给一个缺省的文件host_name-slow.log(如果没有指定参数slow_query_log_file的话)

# 3.查看默认阈值（运行时间 > 阈值才会被记录，等于不会记录）
show VARIABLES like 'long_query_time%';
# 4.可以命令修改或者配置文件修改（执行命令后需要重新连接或者新开一个会话才能看到修改值，不然查询还是默认值，或者使用show global VARIABLES like 'long_query_time%'查看）
set global long_query_time=3;

# 5.查看慢查询日志位置
show variables like 'show_query_log_file';

# 查询当前系统中有多少条慢查询记录
show global status like '%Slow_queries%';
# 慢查询优化用explain
```

日志分析工具mysqldumpslow

```
#命令行 查看帮助信息
mysqldumpslow --help
s 表示按照何种方式排序
c 访问次数
l 锁定时间
r 返回记录
t 查询时间
al 平均锁定时间
ar 平均返回记录数
at 平均查询时间
t 即为返回前面多少条的数据
g 后面搭配一个正则匹配模式，大小写不敏感的

得到返回记录集最多的10个SQL
mysqldumpslow -s r -t 10 /var/lib/mysql/atguigu-slow.log
得到访问次数最多的10个SQL
mysqldumpslow -s c -t 10 /var/ib/mysql/atguigu-slow.log
得到按照时间排序的前10条里面含有左连接的查询语句
mysqldumpslow -s t -t 10 -g "left join" /var/lib/mysql/atguigu-slow.log
另外建议在使用这些命令时结合|和more使用，否则有可能出现爆屏情况
mysqldumpslow -s r -t 10 /var/ib/mysql/atguigu-slow.log|more
```

### 批量数据脚本

往表插入1000w数据

**建表**

```
create database bigData;
use bigData;
create table dept(
id int unsigned primary key auto_increment,
deptno mediumint unsigned not null default 0,
dname varchar(20) not null default "",
loc varchar(13) not null default ""
)engine=innodb default charset=utf8;
create table emp(
id int unsigned primary key auto_increment,
empno mediumint unsigned not null default 0,/*编号*/
ename varchar(20) not null default "",/*名字*/
job varchar(9) not null default "",/*工作*/
mgr mediumint unsigned not null default 0,/*上级编号*/
hiredate Date not null,/*入职时间*/
sal decimal(7,2) not null,/*薪水*/
comm decimal(7,2) not null,/*红利*/
deptno mediumint unsigned not null default 0/*部门编号*/
)engine=innodb default charset=utf8;
```

**设置参数log_bin_trust_function_creators**
创建函数，假如报错：This function has none of DETERMINISTIC...
#这是由于前面开启过慢查询日志，因为我们开启了bin-log，我们就必须为我们的function指定一个参数。

```sql
show variables like 'log_bin_trust_fucntion_creator';
set global log_bin_trust_function_creators=1;

#这样添加了参数以后，如果mysqld重启，上述参数又会消失，永久方法：
windows下:my.ini[mysqld]加上log_bin_trust_function_creators=1
linux下:/etc/my.cnf下my.cnf[mysqld]加上log_bin_trust_function_creators=1
```

**创建函数，保证每条数据都不同**

```sql
#模板
DELIMITER $$ #声明结束符
CREATE FUNCTION 函数名(形参名 形参类型) RETURNS 返回类型
BEGIN
	DECLARE 声明的变量名 变量类型 DEFAULT(默认值); #声明变量
	DECLARE return_a varchar(100) default("");
	WHILE i < 100 DO	#执行while语句
	SET return_a = concat(return_a,"a",1); #执行表达式
	SET i = i + 1;
	END WHILE;
	RETURN return_a;#返回
END $$
#随机产生字符串
DELIMITER $$
CREATE FUNCTION rand_string(n INT) RETURNS VARCHAR(255)
BEGIN
	DECLARE chars_str VARCHAR(100) DEFAULT('abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ');
	DECLARE return_str VARCHAR(255) DEFAULT('');
	DECLARE i INT DEFAULT(0);
	WHILE i < n DO
	SET return_str = CONCAT(return_str,SUBSTRING(chars_str,FLOOR(1+RAND()*52),1));
	SET i = i + 1;
	END WHILE;
	RETURN return_str;
END $$
#随机产生部门编号
DELIMITER $$
CREATE FUNCTION rand_num() RETURNS INT(5)
BEGIN
	DECLARE i INT DEFAULT(0);
	SET i = FLOOR(100+RAND()*10);
	RETURN i;
END $$
```

**创建存储过程**

```sql
#创建往emp表中插入数据的存储过程
DELIMITER $$
create procedure insert_emp(in start int(10),in max_num int(10))
begin
	declare i int default 0;
	#set autocommit=0把autocommit设为0,关闭自动提交，手动commit
	set autocommit=0;
	repeat
        set i = i + 1;
        insert into emp(empno,ename,job,mgr,hiredate,sal,comm,deptno) values((start+i),rand_string(6),'salesman',0001,curdate(),2000,400,rand_num());
    until i = max_num
	end repeat;
	commit;
end $$
#创建往dept表中插入数据的存储过程
DELIMITER $$
create procedure insert_dept(in start int(10),in max_num int(10))
begin
	declare i int default 0;
	set autocommit=0;
	repeat
        set i = i + 1;
        insert into dept(deptno,dname,loc) values((start+i),rand_string(10),rand_string(8));
    until i = max_num
	end repeat;
	commit;
end $$
```

**调用存储过程**
call insert_dept(100,10);#表示deptno从101开始，产生10条数据。
call insert_emp(100000, 500000); #表示empno从100001开始，产生50w条数据。

### Show Profile

是什么？是mysql提供用来分析当前会话中语句执行的资源消耗情况。可用于sql的调优测量。
默认情况下，参数处于关闭状态，并保存最近15次的运行结果。
分析步骤：

```sql
#1.查看当前mysql版本是否支持
show variables like 'profiling';

#2.开启
set profiling=on;

#3.运行sql
#如果报错 查看 https://blog.csdn.net/TWJ88936543/article/details/107505038
select * from emp GROUP BY id%10 LIMIT 150000;
select * from emp group by id%20 order by 5;

#4.查看结果
show profiles;

#5.诊断sql
show profile cpu,block io for query 上一步中对应sql的数字ID;
show profile [options] for query 第四步中相关sql的ID;
	all(显示所有开销信息),block io(显示块IO相关开销),context switches(上下文切换相关开销),cpu(显示cpu相关开销),ipc(显示发送和接收相关开销信息),memory(显示内存相关开销),page faults(显示页面错误相关开销信息),source(显示和source_function,source_file,source_line相关开销),swaps(显示交换次数相关开销信息)。
	
#6.日常开发中需要注意的四个status，如果有下面四个中任意一个都必须要优化
converting HEAP to MyISAM查询结果太大，内存都不够用了开始往磁盘上搬了
creating tmp table 创建临时表，拷贝数据到临时表，用完再删。
copying to tmp table on disk 把内存中临时表复制到磁盘
locked 锁住
```

### 全局查询日志

开启后会记录执行的所有sql语句。

**永远不要在生产环境开启这个功能。**

```
#配置启用：
#在mysql的my.cnf中，设置如下：
#开启
general_log=1
#记录日志文件的路径
general_log_file=/path/logfile
#输出格式
log_output=FILE

#编码启用
set global general_log=1;
set global log_output='TABLE';

#开启后，你所编写的sql语句，都将会记录到mysql库里的general_log表，可以用下面的命令查看
select * from mysql.general_log;
```

## Mysql锁机制

**锁是计算机协调多个进程或线程并发访问某一资源的机制。**锁冲突也是影响数据库并发访问性能的一个重要因素。

表锁(偏读)，行锁(偏写)，页锁(了解即可)

### 表锁

**特点**：偏向MyISAM存储引擎，开销小，加锁快；无死锁；锁定粒度大，发送所冲突的概率最高，并发度最低。

```
#[表级锁分析--建表SQL]
create table mylock(
id int not null primary key auto_increment,
name varchar(20)
)engine myisam;
insert into mylock(name) values('a');
insert into mylock(name) values('b');
insert into mylock(name) values('c');
insert into mylock(name) values('d');
insert into mylock(name) values('e');
select * from mylock;
#查看哪些表被上锁了，有1就是上锁了
show open tables;
#手动锁表
lock table 表名1 read(write),表名2 read(write),其他;(lock table mylock read;)
#解锁
unlock tables;
```

**加读锁**

| session_1                                     | session_2                                                    |
| --------------------------------------------- | ------------------------------------------------------------ |
| lock table mylock read; 给表加读锁            | 连接终端                                                     |
| 当前session可以查询该表记录                   | 其他session也可以查询该表记录                                |
| 当前session不能对其他没有锁定的表进行增删改查 | 其他session可以增删改查未锁定的表                            |
| 当前session对锁定的表进行增删改都会提示错误   | 其他session对锁定表进行增删改 会一直等待获得锁(即一直阻塞直到获得锁) |
| 释放锁                                        | session_2获得锁，插入更新操作完成。                          |

**加写锁**

| session_1                         | session_2                                         |
| --------------------------------- | ------------------------------------------------- |
| 给表加写锁                        | 连接终端                                          |
| 当前session可以对该表进行增删改查 | 其他session对该表进行增删改查会被阻塞直到锁被释放 |
| 不可以对其他表增删改查            | 其他session可对其他未锁定的表进行增删改查         |
| 释放锁                            | session_2获得锁，查询返回                         |

#### 结论：

对MyISAM表进行操作，会有以下情况：
1.对MyISAM表的读操作(加读锁)，不会阻塞其他进程对同一表的读请求，但会阻塞对同一表的写请求。只有当读锁释放后，才会执行其他进程的写操作。
2.对MyISAM表的写操作(加写锁)，会阻塞其他进程对同一表的读和写操作，只有当写锁释放后，才会执行其他进程的读写操作。
**简而言之，就是读锁会阻塞写，但是不会堵塞读。而写锁则会把读和写都阻塞。**

#### 表锁分析

```
【如何分析表锁定】
可以通过table_locks_waited和table_locks_immediate状态变量来分析系统上的表锁定：
show status like 'table%';

这里有两个状态变量记录MySQL内部表级锁定的情况，两个变量说明如下:
table_locks_immediate: 产生表级锁定的次数，表示可以立即获取锁的查询次数，每立即获取锁值加1 ;
table_locks_waited: 出现表级锁定争用而发生等待的次数(不能立即获取锁的次数，每等待一次锁值加1)，此值高则说明存在着较严重的表级锁争用情况;

此外，Myisam的读写锁调度是写优先，这也是myisam不适合做以写为主的表的引擎。因为写锁后，其他线程不能做任何操作，大量的更新会使查询很难得到锁，从而造成永远阻塞。
```

### 行锁

**特点**：偏向InnoDB存储引擎，开销大，加锁慢；会出现死锁；锁定粒度最小，发生锁冲突的概率最低，并发度也最高。
InnoDB与MyISAM的最大不同有两点：一是支持事务(transaction);二是采用了行级锁。

```sql
#[行级锁分析--建表SQL]
create table test_innodb_lock(
	a int(11),
	b varchar(16)
)engine=innodb;
insert into test_innodb_lock values(1,'b2');
insert into test_innodb_lock values(3,'3');
insert into test_innodb_lock values(4, '4000');
insert into test_innodb_lock values(5,'5000');
insert into test_innodb_lock values(6,'6000');
insert into test_innodb_lock values(7,'7000');
insert into test_innodb_lock values(8,'8000');
insert into test_innodb_lock values(9,'9000');
insert into test_innodb_lock values(1,'b1');
create index test_innodb_a_ind on test_innodb_lock(a);
create index test_innodb_lock_b_ind on test_innodb_lock(b);
```

mysql5.5以后innodb默认存储引擎，commit自动提交，需要先关闭自动提交(set autocommit=0;)，之后需要手动提交。因为mysql innodb默认隔离级别为可重复读，所以不提交的数据其他session看不到，commit之后其他session需要也commit提交一下才能看到改变。

| session_1                                                    | session_2                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| set autocommit=0;                                            | set autocommit=0;                                            |
| 更新但不提交，没有手动commi；<br />update test_innodb_lock set b='b1' where a=1; | session_2被阻塞，只能等待。<br />执行update test_innodb_lock set b='b1' where a=1;报错 |
| 提交更新 commit;                                             | 解除阻塞，更新正常进行;<br />执行update test_innodb_lock set b='b1' where a=1;成功 |
|                                                              | 其他已存在的session需要执行一次commit才看到session1的修改后内容。 |

#### **索引失效行锁变表锁**

例子：varchar类型不加单双引号，产生隐式类型转换导致索引失效，从而行锁变表锁，可能导致其他操作被阻塞还不容易被发现。

#### **间隙锁危害**

【间隙锁】当我们用范围条件而不是相等条件检索数据，并请求共享或排他锁时，InnoDB会给符合条件的已有数据记录的索引项加锁;对于键值在条件范围内但并不存在的记录，叫做“间隙(GAP)” ，InnoDB也会对这个“间隙”加锁，这种锁机制就是所谓的间隙锁(Next-Key锁) 。
【危害】因为Query执行过程中通过范围查找的话，他会锁定整个范围内所有的索引键值，即使这个键值并不存在（宁愿错杀，不愿放过）。
**即当锁定一个范围键值之后，即使某些不存在的键值也会被无辜的锁定，而造成在锁定的时候无法插入锁定键值范围内的任何数据。在某些场景下这可能会对性能造成很大的危害。**
例子：有数据【1,3,4,5,6】,session1执行select * from A where id>1 and id <6,在session1执行commit提交前，mysql会把2,3,4,5都锁掉(即使当前2不存在)，所以当session2执行insert into A(2) values(id)时会被一直阻塞。

```sql
#面试常考：如何锁定具体的某一行
begin;
select * from test_innodb_lock where a=8 for update;
commit;
#select xxx... for update：锁定某一行后，其他的操作会被阻塞，直到锁定行的会话提交commit
```

#### **总结：**

Innodb存储引擎由于实现了行级锁，虽然在锁机制的实现方面所带来的性能损耗可能比表级锁会要更高一些，但是在整体并发处理能力方面要远远优于MyISAM的表级锁。当系统并发量较高的时候，Innodb的整体性能和MyISAM相比就会有比较明显的优势了。
但是，Innodb的行级锁同样也有其脆弱的一面，当我们使用不当的时候(退化到表锁)，可能会让Innodb的整体性能表现不仅不能比MyISAM高，甚至可能会更差。

#### 行锁分析

```
通过检查InnoDB_row_lock状态变量来分析系统上的行锁的争夺情况
mysql> show status like 'innodb_row_lock%';
对各个状态量的说明如下:
Innodb_row_lock_current_waits: 当前正在等待锁释放的数量;
Innodb_row_lock_time: 从系统启动到现在锁定总时间长度;
Innodb_row_lock_time_avg: 每次等待所花平均时间;
Innodb_row_lock_timne_max: 从系统启动到现在等待最长的一次所花的时间;
Innodb_row_lock_waits: 系启动后到现在总共等待的次数;

对于这5个状态变量，比较重要的主要是
Innodb_row_lock_time_avg (等待平均时长),
Innodb_row_lock_waits (等待总次数),
Innodb_row_lock_time (等待总时长)这三项。
尤其是当等待次数很高，而且每次等待时长也不小的时候，我们就需要分析系统中为什么会有如此多的等待，然后根据分析结果着手指定优化计划（show profile分析）。

优化建议：
    尽可能让所有数据检索都通过索引来完成，避免无索引行锁升级为表锁。
    合理设计索引，尽量缩小锁的范围。
    尽可能较少检索条件，避免间隙锁
    尽量控制事务大小，减少锁定资源量和时间长度
    尽可能低级别事务隔离
```

### 页锁(了解一下即可)

开销和加锁时间介于表锁和行锁之间；会出现死锁；封锁的粒度介于表锁和行锁之间，并发度一般。
