## shell脚本

### 1.编写脚本（vim xxx.sh）

#### 变量

变量名区分大小写，只能数字，下划线，字母，且不能以数字开头
声明变量为MY_NAME="shellhub"不需要指定类型
要使用变量，需要在变量前加$

```bash
#!/bin/bash
MY_NAME="shellhub"
echo "Hello, I am $MY_NAME"
echo "Hello, I am ${MY_NAME}" #或者用这句
```

可以把命令执行后的输入结果赋值给一个变量

```bash
LIST=$(ls)
SERVER_NAME=$(hostname)
```

#### 用户输入

`read` 命令接收键盘的输入，标准输入(Standard Input)

```bash
read -p "PROMPT MESSAGE" VARIABLE
```

其中`PROMPT MESSAGE`为提示用户的信息，变量`VARIABLE`可以保存用户的输入，可以在程序中使用该变量

```bash
#!/bin/bash
read -p "Please Enter You Name: " NAME
echo "Your Name Is: $NAME"
```

#### 测试

测试主要用于条件判断。`[ condition-to-test-for ]` ，如`[ -e /etc/passwd ]`，注意的是`[]`前后必须有空格，如`[-e /etc/passwd]`是错误的写法

1. 文件测试操作

```bash
-d FILE_NAM  # True if FILE_NAM is a directory
-e FILE_NAM  # True if FILE_NAM exists
-f FILE_NAM  # True if FILE_NAM exists and is a regular file
-r FILE_NAM  # True if FILE_NAM is readable
-s FILE_NAM  # True if FILE_NAM exists and is not empty
-w FILE_NAM  # True if FILE_NAM has write permission
-x FILE_NAM  # True if FILE_NAM is executable
```

1. 字符串测试操作

```bash
-z STRING  # True if STRING is empty
-n STRING  # True if STRING is not empty
STRING1 = STRIN2 # True if strings are equal
STRING1 != STRIN2 # True if strings are not equal
```

1. 算术测试操作

```bash
var1 -eq var2  # True if var1 is equal to var2
var1 -ne var2  # True if var1 not equal to var2
var1 -lt var2  # True if var1 is less than var2
var1 -le var2  # True if var1 is less than or equal to var2
var1 -gt var2  # True if var1 is greater than var2
var1 -ge var2  # True if var1 is greater than or equal to var2
```

#### 条件判断

##### if 语句

```bash
if [ condition-is-true ]
then
  command 1
  command 2
    ...
    ...
  command N
fi
```

if-else

```bash
if [ condition-is-true ]
then
  command 1
elif [ condition-is-true ]
then
  command 2
elif [ condition-is-true ]
then
  command 3
else
  command 4
fi
```

##### case语句

`case`语句`case`可以实现和`if`一样的功能，但是当条件判断很多的时候，使用`if`不太方便，比如使用`if`进行值的比较

```bash
case "$VAR" in
  pattern_1)
    # commands when $VAR matches pattern 1
    ;;
  pattern_2)
    # commands when $VAR matches pattern 2
    ;;
  *)
    # This will run if $VAR doesnt match any of the given patterns
    ;;
esac
```

#### 迭代语句 - 循环

可以通过循环执行同一个代码块很多次

##### for循环

```bash
for VARIABLE_NAME in ITEM_1 ITEM_N
do
  command 1
  command 2
    ...
    ...
  command N
done
```

**Example**

```bash
#!/bin/bash
COLORS="red green blue"
for COLOR in $COLORS
do
  echo "The Color is: ${COLOR}"
done
```

**Another Example**

```bash
for (( VAR=1;VAR<N;VAR++ ))
do
  command 1
  command 2
    ...
    ...
  command N
done
```

在当前所有txt文件前面追加`new`实现重命名

```bash
#!/bin/bash
FILES=$(ls *txt)
NEW="new"
for FILE in $FILES
do
  echo "Renaming $FILE to new-$FILE"
  mv $FILE $NEW-$FILE
done
```

##### while循环

当所给的条件为`true`时，循环执行`while`里面的代码块

```bash
while [ CONNDITION_IS_TRUE ]
do
  # Commands will change he entry condition
  command 1
  command 2
    ...
    ...
  command N
done
```

**Example** 一行一行读取文件内容

```bash
#!/bin/bash
LINE=1
while read CURRENT_LINE
do
  echo "${LINE}: $CURRENT_LINE"
  ((LINE++))
done < /etc/passwd
# This script loops through the file /etc/passwd line by line
```

#### 参数传递

当我们运行脚本的时候，可以传递参数供脚本内部使用`$ ./script.sh param1 param2 param3 param4`这些参数将被存储在特殊的变量中

```bash
$0 -- "script.sh"
$1 -- "param1"
$2 -- "param2"
$3 -- "param3"
$4 -- "param4"
$@ -- array of all positional parameters
```

这些变量可以在脚本中的任何地方使用，就像其他全局变量一样。**直接使用不用声明**

#### 退出状态码

任何一个命令执行完成后都会产生一个退出状态码，范围`0-255`，状态码可以用来检查错误 
*0 表示正确执行并正常退出*；非0表示执行过程中出错，没有正常退出
上一条命令执行后的退出状态码被保存在变量`$?`中

**例子** 使用`ping`检查主机和服务器之间是否可以抵达

```bash
#!/bin/bash
HOST="google.com"
ping -c 1 $HOST     # -c is used for count, it will send the request, number of times mentioned
RETURN_CODE=$?
if [ "$RETURN_CODE" -eq "0" ]
then
  echo "$HOST reachable"
else
  echo "$HOST unreachable"
fi
```

**自定义退出状态码**默认的状态码是上一条命令执行的结果，我们可以通过`exit`来自定义状态码

```bash
exit 0
exit 1
exit 2
  ...
  ...
exit 255
```

#### 逻辑操作符

shell脚本支持逻辑与和逻辑或
逻辑与 `&&`逻辑或 `||`

```
Example
`mkdir tempDir && cd tempDir && mkdir subTempDir`
这个例子中，如果创建tempDir成功，执行后面的`cd`，继续创建subTempDir
```

#### 函数

可以把一些列的命令或语句定义在一个函数内，从程序的其他地方调用

**注意⚠️** *函数包含了一些列你要重复调用的指令(函数**必须先定义后调用**)*
把函数定义在程序开始或主程序之前是一个最佳实践

**语法**

```bash
function function_name() {
    command 1
    command 2
    command 3
      ...
      ...
    command N
}
```

**调用函数** 简单的给出函数名字

```bash
#!/bin/bash
function myFunc () {
    echo "Shell Scripting Is Fun!"
}
myFunc # call
```

**函数参数传递**

和脚本一样，也可以给函数传递参数完成特殊的任务，第一个参数存储在变量`$1`中，第二个参数存储在变量`$2`中...，`$@`存储所有的参数，参数之间使用空格分割 `myFunc param1 param2 param3 ...`

**变量的作用范围**

**全局变量:** 默认情况下，shell中的变量都定义为全局变量，你可以从脚本中的任何位置使用变量，但是变量在使用之前必须先定义**本地变量:** 本地变量只能在方法内部访问，可以通过`local`关键词定义一个本地变量，定义一个本地变量的最佳实践是在函数内部

#### 通配符

使用通配符可以完成特定的匹配
一些常用的通配符`*` 可以通配一个或多个任意字符

```bash
*.txt
hello.*
great*.md
```

`?`匹配一个字符

```bash
?.md
Hello?
```

`[]`匹配括号内部的任意一个字符

```bash
He[loym], [AIEOU]
```

`[!]`不匹配括号内的任何字符

```bash
`[!aeiou]`
```

**预先定义的通配符** *[[:alpha:]]*
[[:alnum:]] *[[:space:]]*
[[:upper:]]] *[[:lower:]]*
[[:digit:]]

**匹配通配符** 有些情况下我们想匹配`*`或`?`等特殊字符，可以使用转义字符`\*\?`

#### 文件操作

追加写：echo 追加的内容 >> 要写入到的文件

覆盖写：echo 内容 > 要写入到的文件

### 2.赋予权限（chmod 755 xxx.sh）

### 3.执行（./xxx.sh）

