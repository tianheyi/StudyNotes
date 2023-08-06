# Git

命令学习网站：[Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)

## 初始化配置

1. 在github注册一个帐号

2. 配置帐号和邮箱

   git config --global user.name "用户名"
   git config --global user.email "邮箱"
   git config --global --list 

3. 生成密钥，输入下面命令后连敲3次回车

   ssh-keygen -t rsa

4. 找到.ssh目录，此目录下应该有id_rsa和id_rsa.pub

   find / name .ssh

5. 然后将id_rsa.pub中的内容添加到github帐号中

6. 验证

   输入`ssh -T git@github.com`，然后输入`yes`

   如果出现：

   `Warning: Permanently added 'github.com,20.205.243.166' (ECDSA) to the list of known hosts.
   Hi xxx! You've successfully authenticated, but GitHub does not provide shell access.`

   则表示github.com不在/etc/hosts文件中，添加进去即可。



## 基本操作

Git 的工作就是创建和保存你项目的快照及与之后的快照进行对比。

Git 常用的是以下 6 个命令：**git clone**、**git push**、**git add** 、**git commit**、**git checkout**、**git pull**。



![img](https://www.runoob.com/wp-content/uploads/2015/02/git-command.jpg)

**说明：**

- workspace：工作区
- staging area：暂存区/缓存区
- local repository：版本库或本地仓库
- remote repository：远程仓库

一个简单的操作步骤：

```
$ git init    
$ git add .    
$ git commit  
```

- git init  初始化仓库。
- git add .  添加文件到暂存区。
- git commit  将暂存区内容添加到仓库中。

### 创建仓库命令

下表列出了 git 创建仓库的命令：

| 命令        | 说明                                   |
| :---------- | :------------------------------------- |
| `git init`  | 初始化仓库                             |
| `git clone` | 拷贝一份远程仓库，也就是下载一个项目。 |

### 提交与修改

Git 的工作就是创建和保存你的项目的快照及与之后的快照进行对比。

下表列出了有关创建与提交你的项目的快照的命令：

| 命令         | 说明                                     |
| :----------- | :--------------------------------------- |
| `git add`    | 添加文件到暂存区                         |
| `git status` | 查看仓库当前的状态，显示有变更的文件。   |
| `git diff`   | 比较文件的不同，即暂存区和工作区的差异。 |
| `git commit` | 提交暂存区到本地仓库。                   |
| `git reset`  | 回退版本。                               |
| `git rm`     | 将文件从暂存区和工作区中删除。           |
| `git mv`     | 移动或重命名工作区文件。                 |

### 提交日志

| 命令               | 说明                                 |
| :----------------- | :----------------------------------- |
| `git log`          | 查看历史提交记录                     |
| `git blame <file>` | 以列表形式查看指定文件的历史修改记录 |

### 远程操作

| 命令         | 说明               |
| :----------- | :----------------- |
| `git remote` | 远程仓库操作       |
| `git fetch`  | 从远程获取代码库   |
| `git pull`   | 下载远程代码并合并 |
| `git push`   | 上传远程代码并合并 |

## Git 分支管理

几乎每一种版本控制系统都以某种形式支持分支，一个分支代表一条独立的开发线。

使用分支意味着你可以从开发主线上分离开来，然后在不影响主线的同时继续工作。

![img](https://static.runoob.com/images/svg/git-brance.svg)

Git 分支实际上是指向更改快照的指针。

有人把 Git 的分支模型称为**必杀技特性**，而正是因为它，将 **Git** 从版本控制系统家族里区分出来。

创建分支命令：

```
git branch (branchname)
```

切换分支命令:

```
git checkout (branchname)
```

当你切换分支的时候，Git 会用该分支的最后提交的快照替换你的工作目录的内容， 所以多个分支不需要多个目录。

合并分支命令:

```
git merge 
```

你可以多次合并到统一分支， 也可以选择在合并之后直接删除被并入的分支。

开始前我们先创建一个测试目录：

```
$ mkdir gitdemo
$ cd gitdemo/
$ git init
Initialized empty Git repository...
$ touch README
$ git add README
$ git commit -m '第一次版本提交'
[master (root-commit) 3b58100] 第一次版本提交
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 README
```

**补充**：

 orphan 分支（将N个完全不同的项目作为N个分支放在同一个仓库中, 并且分支之间互不影响）

## git commit提交规范

Angularjs规范

```text
<type>(<scope>): <subject>

<body>

<footer>
```

大致分为三个部分(使用空行分割):

1. 标题行: 必填, 描述主要修改类型和内容
2. 主题内容: 描述为什么修改, 做了什么样的修改, 以及开发的思路等等
3. 页脚注释: 放 Breaking Changes 或 Closed Issues

### type

| 类型     | 描述                                                         |
| -------- | ------------------------------------------------------------ |
| feat     | 新增 feature，新功能、新特性                                 |
| fix      | 修复bug                                                      |
| docs     | 文档修改                                                     |
| style    | 代码格式修改,（例如修改了空格、格式缩进、逗号等，不改变代码逻辑） |
| refactor | 代码重构（重构，在不影响代码内部行为、功能下的代码修改）     |
| perf     | 更改代码，以提高性能（在不影响代码内部行为的前提下，对程序性能进行优化） |
| test     | 测试用例新增、修改，比如单元测试、集成测试等                 |
| chore    | 改变构建流程、或者增加依赖库、工具等                         |
| revert   | 回滚到上一个版本                                             |
| build    | 影响项目构建或依赖项修改                                     |
| ci       | 持续集成相关文件修改                                         |
| release  | 发布新版本                                                   |
| workflow | 工作流相关文件修改                                           |
| chore    | 其他修改（不在上述类型中的修改）                             |

### scope

commit 影响的范围（具体改动的文件或者目录）, 比如: route, component, utils, build...

### subject

commit 的概述（对正文的概括）

### body

commit 具体修改内容, 可以分为多行.

just as in <subject> use imperative, present tense: “change” not “changed” nor “changes”

includes motivation for the change and contrasts with previous behavior

### footer

一些备注, 通常是 BREAKING CHANGE 或修复的 bug 的链接.
如果当前代码和上一个版本不兼容，需要在这里以 BREAKING CHANGE 开头，后面接具体的描述

### 相关 issues

这里是和变动相关的 issues。例如：

Closed bugs should be listed on a separate line in the footer prefixed with "Closes" keyword like this:

Closes #234

or in case of multiple issues:

Closes #123, #245, #992

### 约定式提交规范

以下内容来源于：[https://www.conventionalcommits.org/zh-hans/v1.0.0-beta.4/](https://link.zhihu.com/?target=https%3A//www.conventionalcommits.org/zh-hans/v1.0.0-beta.4/)

- 每个提交都必须使用类型字段前缀，它由一个名词组成，诸如 `feat` 或 `fix` ，其后接一个可选的作用域字段，以及一个必要的冒号（英文半角）和空格。
- 当一个提交为应用或类库实现了新特性时，必须使用 `feat` 类型。
- 当一个提交为应用修复了 `bug` 时，必须使用 `fix` 类型。
- 作用域字段可以跟随在类型字段后面。作用域必须是一个描述某部分代码的名词，并用圆括号包围，例如： `fix(parser):`
- 描述字段必须紧接在类型/作用域前缀的空格之后。描述指的是对代码变更的简短总结，例如： `fix: array parsing issue when multiple spaces were contained in string.`
- 在简短描述之后，可以编写更长的提交正文，为代码变更提供额外的上下文信息。正文必须起始于描述字段结束的一个空行后。
- 在正文结束的一个空行之后，可以编写一行或多行脚注。脚注必须包含关于提交的元信息，例如：关联的合并请求、Reviewer、破坏性变更，每条元信息一行。
- 破坏性变更必须标示在正文区域最开始处，或脚注区域中某一行的开始。一个破坏性变更必须包含大写的文本 `BREAKING CHANGE`，后面紧跟冒号和空格。
- 在 `BREAKING CHANGE:` 之后必须提供描述，以描述对 API 的变更。例如： `BREAKING CHANGE: environment variables now take precedence over config files.`
- 在提交说明中，可以使用 `feat` 和 `fix` 之外的类型。
- 工具的实现必须不区分大小写地解析构成约定式提交的信息单元，只有 `BREAKING CHANGE` 必须是大写的。
- 可以在类型/作用域前缀之后，: 之前，附加 `!` 字符，以进一步提醒注意破坏性变更。当有 `!` 前缀时，正文或脚注内必须包含 `BREAKING CHANGE: description`

### 示例

#### fix

如果修复的这个BUG只影响当前修改的文件，可不加范围。如果影响的范围比较大，要加上范围描述。

例如这次 BUG 修复影响到全局，可以加个 global。如果影响的是某个目录或某个功能，可以加上该目录的路径，或者对应的功能名称。

```text
// 示例1
fix(global):修复checkbox不能复选的问题
// 示例2 下面圆括号里的 common 为通用管理的名称
fix(common): 修复字体过小的BUG，将通用管理下所有页面的默认字体大小修改为 14px
// 示例3
fix: value.length -> values.length
```

#### feat

```text
feat: 添加网站主页静态页面

这是一个示例，假设对点检任务静态页面进行了一些描述。
 
这里是备注，可以是放BUG链接或者一些重要性的东西。
```

#### chore

chore 的中文翻译为日常事务、例行工作，顾名思义，即不在其他 commit 类型中的修改，都可以用 chore 表示。

```text
chore: 将表格中的查看详情改为详情
```



# 编辑器连接github

[IntelliJ IDEA连接Github](https://www.jianshu.com/p/d5366a54a0fd)

问题解决：

[git报错ssh: connect to host github.com port 22: Connection timed out](https://blog.csdn.net/nightwishh/article/details/99647545)



# 实操

## 新建 orphan 分支

**初始化本地仓库**

`git init`

**连接到远程仓库**

`git remote add <远程仓库在本地的名称> <远程仓库地址>`

**查看远程仓库信息**

`git remote -v`

**建立orphan分支，分支虽然创建，但如果不进行提交的话远程仓库是没有该分支的**

`git checkout --orphan <new branch>`

**提交工作区代码到缓冲区**

`git add .`

**缓冲区中代码提交到本地仓库**

`git commit -m "test"`

**推送到远程仓库**

`git push <被推送到的远程仓库在本地的名称> <对应分支名称>`

如果创建其他orphan分支，建议先切换回主分支以后再新建orphan分支

## 克隆

## 问题

- git默认配置忽略大小写，因此无法正确检测大小写的更改

  `git config core.ignorecase false`：关闭git忽略大小写配置，即可检测到大小写名称更改

- `git commit -m "feat(dataStructure): disjoint-set"` 执行出现：
  On branch master
  nothing to commit, working tree clean

- 检测到文件未修改，随便改一下就行了

- `git push origin-algorithm master `执行出现：

  Connection reset by 20.205.243.160 port 443
  fatal: Could not read from remote repository.

  Please make sure you have the correct access rights
  and the repository exists.

  - https://blog.csdn.net/linda_5150/article/details/102392175

- `git clone`出现：RPC failed; curl 18 transfer closed with outstanding read data remaining

  1. 加大缓存区 git config --global http.postBuffer 524288000 这个大约是500M 
  2. 少clone一些，–depth 1 git clone https://github.com/flutter/flutter.git --depth 1 –depth 1的含义是复制深度为1，就是每个文件只取最近一次提交，不是整个历史版本。 
  3. 换协议 clone http方式换成SSH的方式，即 https:// 改为 git:// 例如git clone https://github.com/test/test.git 换成git clone git://github.com/test/test.git

  https://cloud.tencent.com/developer/article/1660797

# 命令

基础命令

```
git commit（提交）
与上一个版本进行对比，把所有差异打包到一起作为提交记录，父节点为上次提交

git branch 分支1 （在当前所在节点创建分支1）

git checkout 分支1（让HEAD指向分支1）
注意：git2.23版本引入了git switch，最终会取代git checkout
创建新分支并且同时切换到新分支的简便方式：git checkout -b 分支名

合并
    合并方法1：
        git merge 分支1（合并分支1与当前所在分支，并且指向新节点，新结点为这两个分支的子节点）
    合并方法2：
        git rebase 分支1（复制当前所在分支作为分支1的子节点，看似是串行）
```

高级

```
head分离
git checkout 提交记录1（HEAD->分支名->提交记录1 变为 HEAD->提交记录1）

相对引用：
1.使用 ^ 向上移动一个提交记录
	把^加在引用名称的后面，表示让git寻找指定提交记录的父提交。例如main^相当于main的父节点，main^^是main的第二个父节点.
2.使用 ~n 向上移动n个提交记录，例如~3,不跟数字时与^相同

强制修改分支位置：
	使用-f选项让分支指向另一个提交。
	例如执行 git branch -f main HEAD~3 会将main分支强制指向HEAD的第3级父提交
	
撤销变更：
	和提交一样，撤销变更由底层部分（暂存区的独立文件或者片段）和上层部分（变更到底是通过哪种方式被撤销的）组成。
1.使用git reset
	向上移动分支，原来指向的提交记录就跟没提交过一样。只对本地分支有用，对一起使用的远程分支无效。
	HEAD均指向C分支
	git reset HEAD~1 使用前 A<-B<-C 使用后 A<-B 相当于C没提交
2.使用git revert
	git revert HEAD 使用前 A<-B<-C 使用后 A<-B<-C<-C' C'与B状态相同 类似 A<-B<-C<-B
	

```

移动提交记录

```
git cherry-pick <提交号> ...
	如果想让一些提交复制到当前所在位置(HEAD)下面的话，cherry-pick是最直接的方式。git cherry-pick C2 C4 将C2 C4依次插入到当前分支后面，即C5<-C2'<-C4'且之前指向C5的main指向C4'

交互式rebase（指的是带参数--interactive的rebase命令，简写-i）
	如果增加了这个选项，git会打开一个UI界面并列出将要被复制到目标分支的备选提交记录，还会显示每个提交记录的哈希值和提交说明。
	当rebase UI界面打开时，你能做3件事：调整提交记录的顺序，删除你不想要的提交，合并提交。在UI界面提交后，会根据你的调整重新复制一个新的链路。
```

杂项

```
本地栈式提交
	例如在main分支中调试，经过debug，在bugFix完成，需要将bugFix提交到main后面。当前是C1(main)<-C2(debug)<-C3(bugFix),使用git checkout main和git cherry-pick C3实现目的（或者使用git rebase -i也可以实现） 
	
```

