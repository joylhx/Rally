#概述
rally 提供了由低版本到高本版的升级方法。升级完成之后，为了避免新版 rally 与旧版本已存在的数据库产生冲突，测试人员需要手动调用 rally 相关命令对数据库进行升级
#rally 升级方法
```
cd rally/src
git pull
./install_rally -R
```
#database 升级方法
```
rally-manager db upgrade
```

