#概述
rally 在安装完成后，需要在本地创建 sqlite 数据库来保存测试任务，插件等信息。
#命令
可以使用 rally 自带的命令行工具来快速创建数据库，命令有下面两种：
```
rally-manager db create #创建一个新的 sqlite 数据库

rally-manager db recreate #重新创建一个新的 sqlite 数据库
```
