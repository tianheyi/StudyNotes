# php环境搭建

1. 安装phpstudy，安装好之后会自动安装php

2. 设置php.exe路径到环境变量，执行php -v判断是否成功

3. 下载Xdebug，根据php版本下载对应版本，地址：https://xdebug.org/download/historical，下载到php的ext目录下

4. 配置php.ini文件：

   ```ini
   ;新增
   [Xdebug]
   xdebug.mode=debug
   ;下载的xdebug所在路径
   zend_extension=D:\phpstudy_pro\Extensions\php\php7.3.4nts\ext\php_xdebug-3.1.6-7.3-vc15-nts-x86_64.dll
   ```

5. 安装composer

   官网下载安装：[作曲家 (getcomposer.org)](https://getcomposer.org/download/)

   命令行执行`composer -v`不报错即安装成功

   **常用操作ps：**

   在项目根目录执行`composer install`会根据项目composer.json文件内容下载项目依赖，类似python pip

6. 配置composer

   - 修改为国内镜像源：`composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/`


# 搭建Laravel环境

用编辑器打开phpstudy（或者其他类似工具）的`/WWW`目录，在该目录执行下面命令。

## 方法1(不用额外下载laravel安装器)

直接通过composer命令搭建项目（默认框架最新版本）：`composer create-project --prefer-dist laravel/laravel 项目名`

如果需要安装指定版本（例如7.x版本）：`composer create-project --prefer-dist laravel/laravel=7.* 项目名`

## 方法2

1. 使用composer安装laravel安装器：`composer global require laravel/installer`，执行`laravel -v`不报错即可，如果提示命令不存在则添加到环境变量。
2. 使用laravel命令创建laravel项目：`laravel new 项目名`

