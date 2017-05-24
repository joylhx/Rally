#概述
在用于创建 deployment 的 Json 文件中，可以使用待部署的 Openstack 环境中 admin 用户的信息和已存在的普通用户信息。
#分析
- 优点
 1. 测试流程更可控，编写插件更容易，排除错误更简单。
- 缺点
 1. 需要预先创建用来测试的租户
 2. 使用原生插件时，需要配合原生插件来传递资源，略繁琐。
- 示例
```
{
    "type": "ExistingCloud",
    "creds": {
        "openstack": {
            "auth_url": "http://25.0.0.2:5000/v2.0/",
            "region_name": "RegionOne",
            "endpoint_type": "public",
            "endpoint": "http://25.0.0.2:35357/v2.0/",
            "admin": {
                "username": "rally_admin",
                "password": "rally",
                "tenant_name": "rally_admin"
            },
            "users": [
                {
                    "username": "rally_user",
                    "password": "rally",
                    "tenant_name": "rally_user"
                }
            ]
        }
    }
}
```
