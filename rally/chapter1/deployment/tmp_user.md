#概述
在用于创建 deployment 的 Json 文件中，可以只使用待部署的 Openstack 环境中 admin 用户的信息。
#分析
- 优点
1. 当只使用 admin 用户的信息时，rally 测试流程可以做到所有资源自动创建和释放。
2. 不用提前在环境中创建测试用的普通租户。
- 缺点
1. 原生 users 插件较为复杂，二次开发不便。
2. 临时用户被删除会导致相应资源难以查看。
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
                "username": "admin",
                "password": "pa55word",
                "tenant_name": "demo"
            },
            "https_insecure": false,
            "https_cacert": ""
        },
    }
}
```
