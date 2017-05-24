#部署
部署指的是提供一个部署好的 Openstack 环境来提供给 rally 进行测试。
rally 在接受`Openstack deployment`时可以使用`openrc`与`Json`两种方式来保存`Openstack deployment`的相关信息。

- openrc 方式
 ```
 . openrc
 
 rally deployment create --name xxx --fromenv
 ```

- Json 方式
 ```
 rally deployment create --name xxx --filename xxx.json
 
 ```

> 注意，更多 deployment 命令请参考官方文档和`rally help`命令
