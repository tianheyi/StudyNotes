## 本文主要探究gRPC客户端的resolver模块是如何与balancer模块进行通信的。
掘金地址：[gRPC客户端之resolver与balancer通信](https://juejin.cn/post/7241575425028259896)

resolver服务地址解析器，balancer负载均衡器

当客户端调用DialContext方法获取grpc.ClientConn时，resolver和balancer在这个过程中究竟做了什么？（为了省略篇幅，所有代码均只展示resolver和balancer相关重要部分）

0.  进入到grpc.DialContext函数内部

    ```go
    func DialContext(ctx context.Context, target string, opts ...DialOption) (conn *ClientConn, err error) {
        // 初始化连接
        cc := &ClientConn{
           target:            target,
           ...
        }
        ...
        // 1.解析target并且根据target解析出的scheme找到对应的resolverBuilder对象，是resolver.Builder接口类型
        resolverBuilder, err := cc.parseTargetAndFindResolver()
        ...
        // 2.初始化balancer
        cc.balancerWrapper = newCCBalancerWrapper(cc, balancer.BuildOptions{
           DialCreds:        credsClone,
           CredsBundle:      cc.dopts.copts.CredsBundle,
           Dialer:           cc.dopts.copts.Dialer,
           Authority:        cc.authority,
           CustomUserAgent:  cc.dopts.copts.UserAgent,
           ChannelzParentID: cc.channelzID,
           Target:           cc.parsedTarget,
        })

        // 3.根据resolverBuilder初始化resolver.
        rWrapper, err := newCCResolverWrapper(cc, resolverBuilder)
        if err != nil {
           return nil, fmt.Errorf("failed to build resolver: %v", err)
        }
        cc.mu.Lock()
        cc.resolverWrapper = rWrapper
        cc.mu.Unlock()
        ...

    }
    ```

2.  解析target并且根据target解析出的scheme找到对应的resolverBuilder对象，是resolver.Builder接口类型

    ```go
    func (cc *ClientConn) parseTargetAndFindResolver() (resolver.Builder, error) {
        ...
        var rb resolver.Builder
        // 解析target
        parsedTarget, err := parseTarget(cc.target)
        if err != nil {
            channelz.Infof(logger, cc.channelzID, "dial target %q parse failed: %v", cc.target, err)
        } else {
            channelz.Infof(logger, cc.channelzID, "parsed dial target is: %+v", parsedTarget)
            // 根据scheme（即解析方案名或者称为协议名）获取对应的resolver.Builder接口对象
            rb = cc.getResolver(parsedTarget.URL.Scheme)
            // 获取到了直接返回该对象
            if rb != nil {
                cc.parsedTarget = parsedTarget
                return rb, nil
            }
        }

        // 如果解析target出现错误或者没有找到对应scheme的resolver.Builder，则使用默认的passthrough方案。
        // 在passthrough方案中，客户端会直接将请求发送到指定的服务器地址，并不进行负载均衡或其他处理。
        // 如果该地址无法响应请求，客户端会立即返回错误
        ...

    }
    ```

    1.1 getResolver（通过scheme获取对应resolver.Builder对象）

    ```go
    func (cc *ClientConn) getResolver(scheme string) resolver.Builder {
       // 先去配置中的resolvers中寻找，即客户端在拨号时通过grpc.WithResolvers()传入的resolvers
       for _, rb := range cc.dopts.resolvers {
          if scheme == rb.Scheme() {
             return rb
          }
       }
       // 找不到则再去全局resolvers中寻找，即通过resolver.Register()注入的resolvers，最终保存在一个map中
       return resolver.Get(scheme)
    }
    ```

3.  初始化balancer，即调用newCCBalancerWrapper方法去初始化grpc.ClientConn的属性balancerWrapper。

    该方法先将传入的grpc.ClientConn对象包装成实现了balancer.ClientConn接口的ccBalancerWrapper对象（该结构体对象所在位置：`google.golang.org\grpc@v1.55.0\balancer_conn_wrappers.go`），该对象有一个属性updateCh，其本质是一个长度为1的chan interface{}，然后会通过goroutine启动其watcher方法用来监听updateCh中的数据。

    ```go
    func newCCBalancerWrapper(cc *ClientConn, bopts balancer.BuildOptions) *ccBalancerWrapper {
       // ccBalancerWrapper实现了balancer.ClientConn接口，即实质是将grpc.ClientConn包装成了balancer.ClientConn
       ccb := &ccBalancerWrapper{
          cc:       cc,  // grpc.ClientConn
          updateCh: buffer.NewUnbounded(),  // 更新通道，接收更新变化，本质是一个缓冲区长度为1的chan interface{}
          resultCh: buffer.NewUnbounded(),  // 结果通道，接收执行结果，本质是一个缓冲区长度为1的chan interface{}
          ...
       }
       // 启动一个goroutine去监听updateCh
       go ccb.watcher()
       ccb.balancer = gracefulswitch.NewBalancer(ccb, bopts)
       return ccb
    }
    ```

    2.1 **watcher对收到的数据进行类型断言，根据不同的数据类型做出不同的处理。**\
    例如收到的数据是\*ccStateUpdate类型（该类型的属性ccs包含了resolver.State类型），则会调用handleClientConnStateChange方法。

    ```go
    func (ccb *ccBalancerWrapper) watcher() {
       for {
          select {
          case u := <-ccb.updateCh.Get():
             ...
             switch update := u.(type) {
             case *ccStateUpdate:
                ccb.handleClientConnStateChange(update.ccs)
             ...
             }
          case <-ccb.closed.Done():
          }
          ...
       }
    }
    ```

    2.2 handleClientConnStateChange方法处理来自更新通道updateCh的数据，并调用其底层平衡器上的UpdateClientConnState方法，并且将执行结果放入到结果通道resultCh中。（此刻只需找到resolver向balancer的updateCh发送\*ccStateUpdate类型数据的地方即可将resolver模块与balancer模块联系起来）。

    ```go
    func (ccb *ccBalancerWrapper) handleClientConnStateChange(ccs *balancer.ClientConnState) {
        // 如果更新中指定的地址包含grpcb类型的地址，并且所选的LB策略不是grpclb
        // 则这些地址将被过滤掉，并且ccs将使用更新的地址列表进行修改
        if ccb.curBalancerName != grpclbName {
           var addrs []resolver.Address
           for _, addr := range ccs.ResolverState.Addresses {
              if addr.Type == resolver.GRPCLB {
                 continue
              }
              addrs = append(addrs, addr)
           }
           ccs.ResolverState.Addresses = addrs
        }
        // 调用其底层平衡器上的UpdateClientConnState方法，并且将执行结果放入到结果通道resultCh中
        ccb.resultCh.Put(ccb.balancer.UpdateClientConnState(*ccs))
    }
    ```

4.  根据resolverBuilder初始化resolver，即调用newCCResolverWrapper方法去初始化grpc.ClientConn的属性resolverWrapper。

    该方法先将传入的grpc.ClientConn对象包装成实现了resolver.ClientConn接口的grpc.ccResolverWrapper对象（该结构体对象所在位置：`google.golang.org\grpc@v1.55.0\resolver_conn_wrapper.go`），最后调用resolver.Builder的Build()方法来初始化resolver。

    ```go
    func newCCResolverWrapper(cc *ClientConn, rb resolver.Builder) (\*ccResolverWrapper, error) {
        // ccResolverWrapper实现了resolver.ClientConn接口，即实质是将grpc.ClientConn包装成了resolver.ClientConn
        ccr := &ccResolverWrapper{
            cc:   cc,
            done: grpcsync.NewEvent(),
        }
        ...
        // 此处真正调用resolver.Builder接口对象的Build方法
        ccr.resolver, err = rb.Build(cc.parsedTarget, ccr, rbo)
        ...
    }
    ```

    resolver包下的Builder接口定义如下：

    ```go
    type Builder interface {
       Build(target Target, cc ClientConn, opts BuildOptions) (Resolver, error)
       Scheme() string
    }
    ```

    **可知grpc.ccResolverWrapper对象就是resolver.ClientConn接口的具体实现。**\
    查看grpc.ccResolverWrapper对象实现的UpdateState方法，可知其调用了grpc.ClientConn的updateResolverState方法，此方法内部最终调用了gprc.ClientConn的属性balancerWrapper的updateClientConnState方法，并且将类型resolver.State包装成了类型\*balancer.ClientConnState，然后传入进去，而updateClientConnState方法内部又将类型\*balancer.ClientConnState包装成了类型\*ccStateUpdate，然后发送到balancerWrapper的updateCh中（跟2中连起来了，找到并且验证了balancer模块和resolver通信的全过程）。

    ```go
    // resolver.ClientConn的UpdateState方法
    func (ccr *ccResolverWrapper) UpdateState(s resolver.State) error {
       ...
       ccr.curState = s
       if err := ccr.cc.updateResolverState(ccr.curState, nil); err == balancer.ErrBadResolverState {
          return balancer.ErrBadResolverState
       }
       return nil
    }
    // resolver.ClientConn的UpdateState方法内部调用了grpc.ClientConn的updateResolverState方法
    func (cc *ClientConn) updateResolverState(s resolver.State, err error) error {
       ...
       // 获取grpc.Client的balancer
       bw := cc.balancerWrapper
       ...
       // 此处调用balancer的updateClientConnState
       uccsErr := bw.updateClientConnState(&balancer.ClientConnState{ResolverState: s, BalancerConfig: balCfg})
       ...
    }
    // grpc.ClientConn的updateResolverState方法内部又调用了balancer.ClientConn的updateClientConnState方法
    func (ccb *ccBalancerWrapper) updateClientConnState(ccs *balancer.ClientConnState) error {
       // 由此处可知resolver模块可通过resolver的ClientConn.UpdateState方法将更新的数据发送给balancer，即将resolver与balancer联系起来了，balancer的ClientConn.watcher方法读取到该联系数据后会调用handleClientConnStateChange方法进行处理。
       ccb.updateCh.Put(&ccStateUpdate{ccs: ccs})
       ...
    }
    ```

**总结：**
balancer与resolver使用同一个grpc.Client对象做为其字段，并且通过此grpc.Client对象进行联系。balancer初始化后一直监听updateCh来获取更新后的数据，resolver通过其UpdateState方法，将数据发送到balancer的updateCh中（因为grpc.Client中含有balancer.Client和resolver.Client属性，而balancer.Client和resolver.Client又各自含义grpc.Client属性，所以resolver可以很容易的通过grpc.Client访问balancer.Client的updateCh），完成通信。
