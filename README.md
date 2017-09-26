# Rally
## 存放rally代码

### 各个组件存放位置:
<font size="2">新增的plugins（eg：trove、nova_rebuild、Lbaas）存放位置：Rally/samples/rally_plugins/plugins</font><br />

<font size="2">新增的tasks存放位置：Rally/samples/rally_plugins/tasks/</font><br /> 

<font size="2">原生plugins存放位置：Rally/lhx_rally/Rally/rally/plugins/openstack/</font><br />

<font size="2">原生tasks存放位置：Rally/samples/tasks/scenarios/</font><br /> 

### 新增task运行方法:
<font size="2"><font color="#dd0000">rally --debug --plugin-path=～/Rally/samples/rally_plugins/plugins/ task start xxxx.yaml</font><br />

