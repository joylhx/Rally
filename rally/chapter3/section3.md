# context插件开发
##context插件简介
　　context插件在rally测试流程中主要用来创建测试用例中的前置条件所需的资源，通常context用来创建测试过程中与测试功能无关却必不可少的资源。
##范例
```
@context.configure(name="create_network", order=800)
class CreateNetWorkContext(context.Context):
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"}
        },
    }

    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(self.context["users"][0]["credential"]).neutron()#使用user认证信息创建client
                body = {"network": dict(name=self.config.get("name"))}#完善访问API传递的body
                self.context["user_network"] = neutron.create_network(body=body)["network"]# 将资源保存在self.context中，需要按不同用户使用不同的key加以区分。
                LOG.debug("User Network with id '%s'" % self.context["user_network"]["id"])
            except Exception as e:
                msg = "Can't create network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_setup():
            try:
                neutron = osclients.Clients(self.context["admin"]["credential"]).neutron()
                body = {"network": dict(name=self.config.get("name"))}
                self.context["admin_network"] = neutron.create_network(body=body)["network"]
                LOG.debug("Admin Network with id '%s'" % self.context["admin_network"]["id"])
            except Exception as e:
                msg = "Can't create network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)
        _user_setup()
        _admin_setup()

    def cleanup(self):
        """This method is called after the task finish."""

        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron() #使用user的认证信息创建client
                neutron.delete_network(self.context["user_network"]["id"])#调用API，执行操作
                LOG.debug("User Network %s is deleted" % self.context["user_network"]["id"])#记录LOG
            except Exception as e:
                msg = "Can't delete network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        def _admin_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["admin"]["credential"]).neutron()#使用admin认证信息
                neutron.delete_network(self.context["admin_network"]["id"])
                LOG.debug("Admin Network %s is deleted" % self.context["admin_network"]["id"])
            except Exception as e:
                msg = "Can't delete network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        _admin_cleanup()
```
##task.json 文件中的使用
```
{
    ...: {#场景插件
        "args": {...},#传递给场景插件的参数
        "context": {
            "create_network": {#此插件的配置
                "name": {...}
            },
            ...#其他 context 插件
        },
        ...#runner 和 sla插件
    }
}
```
##编写要点
- 与场景插件类似，context 插件也需要直接或间接继承 `context.Context` 类，同样的，自己创建的 context 插件需要定义 setup 和 cleanup 方法。setup 方法用来创建资源，cleanup 方法用来删除资源

- context 插件类需要被装饰器 `context.configure` 装饰，其装饰器作用与 scenario 插件中的装饰器大致相同。但其 `order` 参数对 context 插件的运行方式至关重要：在 task 文件中存在多个 context 插件的时候，order 决定了创建资源的顺序。order越小的 context 插件其setup方法越早被调用，其 cleanup 方法越迟被调用（类似栈的规则）。

- context 插件包含编写中需要用到的成员
 - **CONFIG_SCHEMA** 
 使用 JSON_SCHEMA 对 task.json 中传给对应 context 插件的配置信息进行语法检测。

 - **self.config**
 记录了 context 插件从task文件文件中获取的配置信息。

 - **self.context**
  记录了 context 插件的上下文信息，包括了用于认证的用户信息，优先执行的 context 插件创建的资源等信息。当出现如上述示例所示的多个 context 插件时，可以使用 self.context 来将 order 值较小的插件创建的资源传递给order较大的插件，从而使资源直接产生耦合关系，从而可以自动化创建像`network->subnet`这种具有依赖关系的资源。在所有资源创建完成后，最终的 self.context 将用来初始化 scenario 插件，scenario 插件可通过 self.context的方式获取预先创建的资源。

 - **user_setup 和 user_cleanup**
  由于存在场景插件对不同用户权限进行测试的需求，context 插件需要对不同的用户生成其独有的资源。此二函数是我用来区分admin与user创建资源的放法的，并不必须，可修改。