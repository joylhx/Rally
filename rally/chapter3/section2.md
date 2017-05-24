# scenario插件开发
##scenario插件概述
- 地位：核心插件，使用rally执行任何测试用例都需要此插件。
- 范例
 ```
 from rally.task import atomic
 from rally.task import scenario

 @scenario.configure(name="EayunTrove.list_datastores")#注册插件，插件名字是EayunTrove.list_datastores
 class ListDatastore(scenario.OpenStackScenario):#插件对应的class，继承scenario.OpenstackScenario

        @atomic.action_timer("list_datastores")#普通用户列出datastore数据
        def _list_all_datastores(self):
            self.clients("trove").datastores.list()

        @atomic.action_timer("list_datastores_as_admin")
        def _list_all_datastores_as_admin(self):
            self.admin_clients("trove").datastores.list()

        def run(self):
            self._list_all_datastores()
            self._list_all_datastores_as_admin()
 ```
- 代码分析
 - 装饰器 scenario.configure
 将场景插件注册到 rally 中，rally 引擎可以通过 task 文件中scenario插件的名字找到此插件。
 - 装饰器 atomic.action_timer
 此装饰器用来标识测试执行步骤，被装饰的函数会在被调用时记录时间，返回时记录结束时间，从而将测试时间记录到测试结果中。
 - run 通用接口，rally 引擎找到插件之后会自动调用run方法
 - self.clients与 self.admin_clients 是分别用 rally deployment 中的 users 和 admin 认证信息生成的接口，通过传递所需模块的名称，和版本号，自动返回进过认证的对应模块和版本号的client。
- 注意
 1. scenario.configure 装饰器可以装饰类的方法，从而使一个类包含多个 scenario 插件。
 2. 可以使用 rally 封装好API的原生scenario类来快速调用API，其原生插件位于（省略）/rally/plugin/scenarios/{模块名}/utils.py
 
