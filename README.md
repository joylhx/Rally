# Rally
###### 存放rally代码

###### 各个组件存放位置
新增的plugins（eg：trove、nova_rebuild、Lbaas）存放位置：Rally/samples/rally_plugins/plugins
新增的tasks存放位置：Rally/samples/rally_plugins/tasks
原生plugins存放位置：Rally/lhx_rally/Rally/rally/plugins/openstack/
原生tasks存放位置：Rally/samples/tasks/scenarios/

###### 新增task运行方法
rally --debug --plugin-path=～/Rally/samples/rally_plugins/plugins/ task start xxxx.yaml
