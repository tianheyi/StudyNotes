# GMP模型

G：goroutine协程，无数量限制
M：内核线程thread，可通过runtime/debug下的SetMaxThreads()来设置最大数量，默认10000(runtime)，实际达不到这么多，在程序初始化和运行时创建。
P：调度器processor，它包含了运行goroutine的资源，可通过runtime.GOMAXPROCESSOR()来设置数量，只在程序初始化时创建，**所有的P都在程序启动时创建，并保存在数组中，最多有`GOMAXPROCS`(可配置)个**。

## (1)GMP模型

在Go中，**线程是运行goroutine的实体，调度器的功能是把可运行的goroutine分配到工作线程上**。
如果线程想运行goroutine，必须先获取P，P中还包含了可运行的G队列。



![img](https://pic1.zhimg.com/80/v2-a66cb6d05fb61e74681410feb3bd1df4_720w.jpg)

1. **全局队列**（Global Queue）：存放等待运行的G。

2. **P的本地队列**：同全局队列类似，存放的也是等待运行的G，存的数量有限，不超过256个。本地队列是由一个长度为256的数组实现的环形队列。**新建G'时，G'优先加入到P的本地队列；如果发现队列已经满了，则会把本地队列中前一半的G、还有新创建的G都移动到全局队列，这些G被转移到全局队列时，会被打乱顺序**。

   ```go
   // runtime/proc.go
   // 可以发现runnext优先级比runq高
   func runqget(_p_ *p) (gp *g, inheritTime bool) {
   	// If there's a runnext, it's the next G to run.
   	for {
   		next := _p_.runnext
   		if next == 0 {
   			break
   		}
   		if _p_.runnext.cas(next, 0) {
   			return next.ptr(), true
   		}
   	}
   
   	for {
   		h := atomic.LoadAcq(&_p_.runqhead) // load-acquire, synchronize with other consumers
   		t := _p_.runqtail
   		if t == h {
   			return nil, false
   		}
   		gp := _p_.runq[h%uint32(len(_p_.runq))].ptr()
   		if atomic.CasRel(&_p_.runqhead, h, h+1) { // cas-release, commits consume
   			return gp, false
   		}
   	}
   }
   //尝试将g放入本地可运行队列。
   func runqput(_p_ *p, gp *g, next bool) {
   	if randomizeScheduler && next && fastrand()%2 == 0 {
   		next = false
   	}
   	//如果next为true，则runqput将g放入p.runnext
   	if next {
   	retryNext:
   		oldnext := _p_.runnext
   		if !_p_.runnext.cas(oldnext, guintptr(unsafe.Pointer(gp))) {
   			goto retryNext
   		}
   		if oldnext == 0 {
   			return
   		}
   		// Kick the old runnext out to the regular run queue.
   		gp = oldnext.ptr()
   	}
   
   retry://如果next为false，runqput将g添加到可运行队列的尾部。如果运行队列已满，则runnext将g放入全局队列
   	h := atomic.LoadAcq(&_p_.runqhead) // load-acquire, synchronize with consumers
   	t := _p_.runqtail
   	if t-h < uint32(len(_p_.runq)) {
   		_p_.runq[t%uint32(len(_p_.runq))].set(gp)
   		atomic.StoreRel(&_p_.runqtail, t+1) // store-release, makes the item available for consumption
   		return
   	}
   	if runqputslow(_p_, gp, h, t) {
   		return
   	}
   	// the queue is not full, now the put above must succeed
   	goto retry
   }
   ```

   

3. **P列表**：所有的P都在程序启动时创建，并保存在切片中，最多有`GOMAXPROCS`(可配置)个。

   ```go
   // runtime/runtime2.go
   var allp []*p  // 存储所有p
   
   type p struct {
       ...
       m           muintptr   // 与p绑定的m，如果p空闲则为nil
       ...
       runqhead uint32  //实现环形队列,head==tail的时候为空,  g = runq[h%len(runq)]; cas(h,h+1)
   	runqtail uint32
   	runq     [256]guintptr // 队列长度最大256
       
       runnext guintptr  // 此字段若不为nil，则表示的是下次待运行的(状态为 runnable 的) g，此时则不从 runq 中获取G，优先级高于runq。所以p最多存257个g
       ...
   }
   type guintptr uintptr
   func (gp guintptr) ptr() *g { return (*g)(unsafe.Pointer(gp)) }
   type g struct {
       ...
       // stack描述了一个Go执行堆栈。保存堆栈起始和结束地址
       stack       stack   // offset known to runtime/cgo
       // 检查栈空间是否足够的值, 低于这个值会扩张栈, 0是go代码使用的
       stackguard0 uintptr // offset known to liblink
       // 检查栈空间是否足够的值, 低于这个值会扩张栈, 1是C代码使用的
       stackguard1 uintptr // offset known to liblink
       ...
   }
   // 堆栈的边界：[lo, hi)  用于描述实际堆栈内存
   type stack struct {
   	lo uintptr
   	hi uintptr
   }
   ```

   

4. **M**：线程想运行任务就得获取P，从P的本地队列获取G，P队列为空时，先尝试从全局队列**拿**一批G放到P的本地队列，如果没拿到，则再尝试 从其他P的本地队列**偷**一半放到自己P的本地队列。M运行G，G执行之后，M会从P获取下一个G，不断重复下去。

> 有关P和M的个数问题

1、P的数量：

- 由启动时环境变量`$GOMAXPROCS`或者是由`runtime`的方法`GOMAXPROCS()`决定。这意味着在程序执行的任意时刻都只有`$GOMAXPROCS`个goroutine在同时运行。
- **如果设置了环境变量`$GOMAXPROCS`并且设置的数量大于0，则p为此数量；否则默认为cpu核心数**

2、M的数量:

- go语言本身的限制：go程序启动时，会设置M的最大数量，默认10000（runtime/proc.go中）.但是内核很难支持这么多的线程数，所以这个限制可以忽略。**如果超过最大数量会报错线程耗尽(fatal error：thread exhaustion)**，因为 M 必须持有 P 才能运行 G，通常情况 P 的数量很有限，如果 M 还超过 10000，基本上就是程序写的有问题。

  ```go
  // runtime/proc.go
  func schedinit() {
      ...
      sched.maxmcount = 10000  // 默认最大线程数量
      ...
      lock(&sched.lock)
  	sched.lastpoll = uint64(nanotime())
  	procs := ncpu  // 默认是cpu核心数
  	if n, ok := atoi32(gogetenv("GOMAXPROCS")); ok && n > 0 { //如果设置了环境变量并且>0，则设置为全局变量的值
  		procs = n
  	}
  	if procresize(procs) != nil {
  		throw("unknown runnable goroutine during bootstrap")
  	}
  	unlock(&sched.lock)
      
      ...
  }
  ```

  

- runtime/debug中的SetMaxThreads函数，设置M的最大数量

- 一个M阻塞了，会创建新的M。

M与P的数量没有绝对关系，一个M阻塞，P就会去创建或者切换另一个M，所以，即使P的默认数量是1，也有可能会创建很多个M出来。

> P和M何时会被创建

1、P何时创建：在确定了P的最大数量n后，运行时系统会根据这个数量创建n个P。

2、M何时创建：没有足够的M来关联P并运行其中的可运行的G。比如所有的M此时都阻塞住了，而P中还有很多就绪任务，就会去寻找空闲的M，而没有空闲的，就会去创建新的M。

## (2)调度器的设计策略

**复用线程**：避免频繁的创建、销毁线程，而是对线程的复用。

1）work stealing机制

```text
当本线程无可运行的G时，尝试从其他线程绑定的P偷取G，而不是销毁线程。
```

2）hand off机制

```text
当本线程因为G进行系统调用阻塞时，线程释放绑定的P，把P转移给其他空闲的线程执行。
```

**利用并行**：`GOMAXPROCS`设置P的数量，最多有`GOMAXPROCS`个线程分布在多个CPU上同时运行。`GOMAXPROCS`也限制了并发的程度，比如`GOMAXPROCS = 核数/2`，则最多利用了一半的CPU核进行并行。

**抢占**：在coroutine中要等待一个协程主动让出CPU才执行下一个协程，在Go中，一个goroutine最多占用CPU 10ms，防止其他goroutine被饿死，这就是goroutine不同于coroutine的一个地方。

**全局G队列**：在新的调度器中依然有全局G队列，但功能已经被弱化了，当M从全局G队列获取不到G时，可以利用work stealing从其他P偷G。

## (3) go func() 调度流程

![img](https://pic1.zhimg.com/80/v2-08a62309cb2c22fe765c20d2f640e15c_720w.jpg)



从上图我们可以分析出几个结论：

1、我们通过 go func()来创建一个goroutine；

2、有两个存储G的队列，一个是局部调度器P的本地队列、一个是全局G队列。新创建的G会先保存在P的本地队列中，如果P的本地队列已经满了就会保存在全局的队列中；

3、G只能运行在M中，一个M必须持有一个P，M与P是1：1的关系。M会从P的本地队列弹出一个可执行状态的G来执行，如果P的本地队列为空，就会想其他的MP组合偷取一个可执行的G来执行；

4、一个M调度G执行的过程是一个循环机制；

5、当M执行某一个G时候如果发生了syscall或则其余阻塞操作，M会阻塞，如果当前有一些G在执行，runtime会把这个线程M从P中摘除(detach)，然后再创建一个新的操作系统的线程(如果有空闲的线程可用就复用空闲线程)来服务于这个P；

6、当M系统调用结束时候，这个M会尝试获取一个空闲的P执行，并放入到这个P的本地队列。如果获取不到P，那么这个线程M变成休眠状态， 加入到空闲线程中，然后对应的G会被放入全局队列中。

## (4)调度器的生命周期

![img](https://pic4.zhimg.com/80/v2-e09c9a41a6cde3f3b7bb8810183d22a3_720w.jpg)



特殊的M0和G0

**M0**

`M0`是启动程序后的编号为0的主线程，这个M对应的实例会在全局变量runtime.m0中，不需要在heap上分配，M0负责执行初始化操作和启动第一个G， 在之后M0就和其他的M一样了。

**G0**

`G0`是每次启动一个M都会第一个创建的gourtine，G0是仅用于负责调度的G，G0不指向任何可执行的函数, 每个M都会有一个自己的G0。在调度或系统调用时会使用G0的栈空间, 全局变量的G0是M0的G0。

我们来跟踪一段代码

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello world")
}
```

接下来我们来针对上面的代码对调度器里面的结构做一个分析。

也会经历如上图所示的过程：

1. runtime创建最初的线程m0和goroutine g0，并把2者关联。
2. 调度器初始化：初始化m0、栈、垃圾回收，以及创建和初始化由GOMAXPROCS个P构成的P列表。
3. 示例代码中的main函数是`main.main`，`runtime`中也有1个main函数——`runtime.main`，代码经过编译后，`runtime.main`会调用`main.main`，程序启动时会为`runtime.main`创建goroutine，称它为main goroutine吧，然后把main goroutine加入到P的本地队列。
4. 启动m0，m0已经绑定了P，会从P的本地队列获取G，获取到main goroutine。
5. G拥有栈，M根据G中的栈信息和调度信息设置运行环境
6. M运行G
7. G退出，再次回到M获取可运行的G，这样重复下去，直到`main.main`退出，`runtime.main`执行Defer和Panic处理，或调用`runtime.exit`退出程序。

调度器的生命周期几乎占满了一个Go程序的一生，`runtime.main`的goroutine执行之前都是为调度器做准备工作，`runtime.main`的goroutine运行，才是调度器的真正开始，直到`runtime.main`结束而结束。

## (5)可视化GMP编程

有2种方式可以查看一个程序的GMP的数据。

**方式1：go tool trace**

trace记录了运行时的信息，能提供可视化的Web页面。

简单测试代码：main函数创建trace，trace会运行在单独的goroutine中，然后main打印"Hello World"退出。

> trace.go

```go
package main

import (
    "os"
    "fmt"
    "runtime/trace"
)

func main() {

    //创建trace文件
    f, err := os.Create("trace.out")
    if err != nil {
        panic(err)
    }

    defer f.Close()

    //启动trace goroutine
    err = trace.Start(f)
    if err != nil {
        panic(err)
    }
    defer trace.Stop()

    //main
    fmt.Println("Hello World")
}
```

运行程序

```bash
$ go run trace.go 
Hello World
```

会得到一个`trace.out`文件，然后我们可以用一个工具打开，来分析这个文件。

```text
$ go tool trace trace.out 
2020/02/23 10:44:11 Parsing trace...
2020/02/23 10:44:11 Splitting trace...
2020/02/23 10:44:11 Opening browser. Trace viewer is listening on http://127.0.0.1:33479
```

我们可以通过浏览器打开`http://127.0.0.1:33479`网址，点击`view trace` 能够看见可视化的调度流程。



![img](https://pic4.zhimg.com/80/v2-547c58ae6eed47bf7bb39de753931387_720w.jpg)





![img](https://pic1.zhimg.com/80/v2-10faec0fe748b1127c7eeb1db15a1af0_720w.jpg)



**G信息**

点击Goroutines那一行可视化的数据条，我们会看到一些详细的信息。



![img](https://pic1.zhimg.com/80/v2-750a71b694e819e56e062a90889cd1a4_720w.jpg)



```text
一共有两个G在程序中，一个是特殊的G0，是每个M必须有的一个初始化的G，这个我们不必讨论。
```

其中G1应该就是main goroutine(执行main函数的协程)，在一段时间内处于可运行和运行的状态。

**M信息**

点击Threads那一行可视化的数据条，我们会看到一些详细的信息。



![img](https://pic3.zhimg.com/80/v2-80415344444e57615afb299676ee9eee_720w.jpg)



一共有两个M在程序中，一个是特殊的M0，用于初始化使用，这个我们不必讨论。

**P信息**

![img](https://pic4.zhimg.com/80/v2-6f74ae466fc41d3b10a9fcfe83b248cb_720w.png)



G1中调用了`main.main`，创建了`trace goroutine g18`。G1运行在P1上，G18运行在P0上。

这里有两个P，我们知道，一个P必须绑定一个M才能调度G。

我们在来看看上面的M信息。



![img](https://pic4.zhimg.com/80/v2-348637125765327fa5148d192ad49ccf_720w.jpg)



我们会发现，确实G18在P0上被运行的时候，确实在Threads行多了一个M的数据，点击查看如下：



![img](https://pic1.zhimg.com/80/v2-6e74617f27424166724759abde01ac18_720w.jpg)



多了一个M2应该就是P0为了执行G18而动态创建的M2.

**方式2：Debug trace**

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    for i := 0; i < 5; i++ {
        time.Sleep(time.Second)
        fmt.Println("Hello World")
    }
}
```

编译

```bash
$ go build trace2.go
```

通过Debug方式运行

```bash
$ GODEBUG=schedtrace=1000 ./trace2 
SCHED 0ms: gomaxprocs=2 idleprocs=0 threads=4 spinningthreads=1 idlethreads=1 runqueue=0 [0 0]
Hello World
SCHED 1003ms: gomaxprocs=2 idleprocs=2 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0]
Hello World
SCHED 2014ms: gomaxprocs=2 idleprocs=2 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0]
Hello World
SCHED 3015ms: gomaxprocs=2 idleprocs=2 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0]
Hello World
SCHED 4023ms: gomaxprocs=2 idleprocs=2 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0]
Hello World
```

- `SCHED`：调试信息输出标志字符串，代表本行是goroutine调度器的输出；
- `0ms`：即从程序启动到输出这行日志的时间；
- `gomaxprocs`: P的数量，本例有2个P, 因为默认的P的属性是和cpu核心数量默认一致，当然也可以通过GOMAXPROCS来设置；
- `idleprocs`: 处于idle状态的P的数量；通过gomaxprocs和idleprocs的差值，我们就可知道执行go代码的P的数量；
- t`hreads: os threads/M`的数量，包含scheduler使用的m数量，加上runtime自用的类似sysmon这样的thread的数量；
- `spinningthreads`: 处于自旋状态的os thread数量；
- `idlethread`: 处于idle状态的os thread的数量；
- `runqueue=0`： Scheduler全局队列中G的数量；
- `[0 0]`: 分别为2个P的local queue中的G的数量。

下一篇，我们来继续详细的分析GMP调度原理的一些场景问题。



# GC垃圾回收机制

## v1.3之前的标记清除

STW（stop the world）：让程序暂停，程序出现卡顿

1. STW暂停程序业务逻辑，找出不可达的对象和可达对象
2. 开始标记，程序找出所有它可达的对象，并做上标记
3. 标记完了之后，然后开始清除未标记的对象
4. 停止暂停，让程序继续跑。然后循环重复这个过程，直到程序生命周期结束

缺点：

1. STW（最大的问题）
2. 标记需要扫描整个heap
3. 清除数据会产生heap碎片

STW暂停范围：（启动STW -> Mark标记 -> Sweep清除 -> 停止STW）

后面将第四步与第三步换位置，缩短STW的范围，但发现还是性能不行，遂换其他标记法

## v1.5三色标记法

起初有白、灰、黑三张标记表

程序起初阶段、将全部标记为白色，将所有的对象放入白色集合中

![img](file:///D:\Typora\localimages\GMP模型\1.png)

将程序的根节点集合展开

![img](file:///D:\Typora\localimages\GMP模型\2.png)

，遍历RootSet（非递归，只遍历一次）。得到灰色节点

![img](file:///D:\Typora\localimages\GMP模型\4.png)



![img](file:///D:\Typora\localimages\GMP模型\5.png)

灰色节点只是一种临时状态，最终要不就是白的要不就是黑的，黑的表示我已经遍历过了，白色的表示没被遍历到。重复上面步骤直到灰色表中无任何标记对象

![img](file:///D:\Typora\localimages\GMP模型\6.png)



程序起初阶段，所有的对象节点都被标记为白色（存入白色表）

### gc清除流程

1. 只要是新创建的对象，颜色都是标记为白色。
2. 遍历程序根节点集合，将一步可达的对象标记为灰色，存入灰色标记表
3. 遍历灰色标记表中所有对象节点，将一步可达的对象标记为灰色（存入灰色标记表），之前灰色表的对象节点则标记为黑色，存入黑色标记表中
4. 重复上一步操作，直到灰色标记表中无任何对象，然后收集白色标记表中的对象(垃圾)，即要清除的对象节点

### 如果不被STW保护（未开启STW）：

#### 问题图示：

![img](file:///D:\Typora\localimages\GMP模型\7.png)

![img](file:///D:\Typora\localimages\GMP模型\8.png)

某一时刻，对象4指向对象3，在同一很短时间内，对象2移除了指向对象3的指针p，会导致对象3被清除

![img](file:///D:\Typora\localimages\GMP模型\9.png)

![img](file:///D:\Typora\localimages\GMP模型\10.png)

#### 不希望发生的事：

![img](file:///D:\Typora\localimages\GMP模型\13.png)

三色标记法最不希望发生的事：

- 条件1：一个白色对象被黑色对象引用（白色挂在黑色下）
- 条件2：灰色对象与它之间的可达关系的白色对象遭到破坏（灰色同时丢了该白色）
- 若两个条件同时满足时，就会出现**对象丢失**现象（本来不是垃圾但却被清除）

最简单的方式就是使用STW，STW的过程有明显的资源浪费，对所有的用户程序都有很大影响。

如何能在保证**对象不丢失**的情况尽可能的**提高GC效率**，减少STW时间呢？

#### 破坏两个条件同时成立：

##### 强三色不变式

强三色不变式：强制性的不允许黑色对象引用白色对象

![img](file:///D:\Typora\localimages\GMP模型\11.png)

##### 弱三色不变式

弱三色不变式：黑色对象可以引用白色对象，但白色对象需存在其他灰色对象对它的引用，或者可达它的链路上游存在灰色对象。

![img](file:///D:\Typora\localimages\GMP模型\12.png)

![img](file:///D:\Typora\localimages\GMP模型\13.png)

#### 屏障机制

![img](file:///D:\Typora\localimages\GMP模型\15.png)

##### 插入写屏障

对象被引用时触发的机制，操作的是新引入的对象。不在栈上面使用

![img](file:///D:\Typora\localimages\GMP模型\16.png)



###### 具体操作：

- 在A对象引用B对象的时候，B对象会触发插入屏障被标记为灰色（将B挂在A下游，B必须被标记为灰色）

  **如果A是栈上面的对象，则引用的B不会触发插入屏障；如果A是堆上面的对象，则引用的B会触发插入屏障**（如下图：对象1引用对象9，对象9不会触发插入屏障被标记为灰色；对象4引用对象8，对象8会触发插入屏障被标记为灰色）**注意：gc清除的都是堆中对象，而下文中栈对象的含义是指栈中对象本身在堆上，而引用这个对象的指针在栈上**

  ![img](file:///D:\Typora\localimages\GMP模型\17.png)

  对象8会被标记为灰色

  ![img](file:///D:\Typora\localimages\GMP模型\18.png)

- 在清除白色标记对象前(即垃圾回收前)，会重新扫描一次栈空间(此时开启STW暂停保护栈空间，防止外界干扰[有新的白色被黑色添加]，此时栈中不允许添加或删除对象)。

  ![img](file:///D:\Typora\localimages\GMP模型\19.png)

  然后对栈中的对象再做一遍三色标记，直到没有灰色节点，然后停止STW（此时对象1引用的对象9就已经被标记为黑色）。然后再清除白色。

  ![img](file:///D:\Typora\localimages\GMP模型\20.png)

###### 不足：

结束时需要STW来重新扫描栈，大约需要10-100ms。但相比之前的标记清除已经好太多了。

##### 删除写屏障

操作的是之前引入的对象

###### ![img](file:///D:\Typora\localimages\GMP模型\21.png)

###### 具体操作

- 正常进行三色标记法，当要移除当前引用的对象时(移除或者引用了新的对象)，会触发删除写屏障。将要移除的对象标记为灰色。

  ![img](file:///D:\Typora\localimages\GMP模型\22.png)

- 然后继续正常进行三色标记直到没有灰色节点，可以发现对象5所在链路均为黑色节点（而如果按照正常的三色标记法，对象5所在链路应该都为白色节点），这样可以避免出现当对象1[灰色状态时]与对象5断开时，对象4[黑色状态时]引用对象5，导致最终对象5被清除的情况。

  ![img](file:///D:\Typora\localimages\GMP模型\24.png)

###### 不足：

回收精度低。一个对象即使被删除了，最后一个指向它的指针也依旧可以活过这一轮，在下一轮GC中被清除。但是不用依靠STW机制去保护，相当于牺牲空间来换时间。最终一致性。



alter table A add index `lianhe`(a,b,c)

create index `lianhe` on A(a,b,c)

select a from A  order by count(a) desc limit 1;

## v1.8混合写屏障机制

插入写屏障和删除写屏障的短板：

- 插入写屏障：结束时需要STW来重新扫描栈，标记栈上引用的白色对象的存活；
- 删除写屏障：回收精度低，GC开始时STW扫描堆栈来记录初始快照，这个过程会保护开始时刻的所有存活对象。

Go V1.8版本引入了混合写屏障机制（hybrid write barrier），避免了对栈re-scan的过程，极大的减少了STW的时间。结合了两者的优点。

### (1) 混合写屏障规则

`具体操作`:

1、GC开始将栈上的对象全部扫描并标记为黑色(之后不再进行第二次重复扫描，无需STW)，

2、GC期间，任何在栈上创建的新对象，均为黑色。

3、被删除的对象标记为灰色。

4、被添加的对象标记为灰色。

`满足`: 变形的**弱三色不变式**.

伪代码：

```
添加下游对象(当前下游对象slot, 新下游对象ptr) {
      //1 
        标记灰色(当前下游对象slot)    //只要当前下游对象被移走，就标记灰色
      
      //2 
      标记灰色(新下游对象ptr)
          
      //3
      当前下游对象slot = 新下游对象ptr
}
```

> 这里我们注意， 屏障技术是不在栈上应用的，因为要保证栈的运行效率。