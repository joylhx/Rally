#替换法
优点：此方法可直接替换client，当有大量非原生api时较为简单。
缺点：rally较新的版本，使用旧版本client替换部分组件时，可能会造成各个组件间的冲突，不易解决。
##NeutronClient

 - 使用测试环境中neutronclient包替换rally中neutronclient包
 ```
 cd rally/lib/python2.7/site-packages/;mv neutronclient neutronclient_bak
 scp -r root@node-17:/usr/lib/python2.7/site-packages/neutronclient ./
 
 ```
##NovaClient
　　和NeutronClient类似NovaClient 的接口整合也可以使用类似的方法，不过需要解决一些rally调用novaclient的依赖问题与认证问题，具体步骤如下：

 1. 备份rally novaclient，同时拷贝测试环境中的novaclient到`rally/lib/python2.7/site-packages/`目录下。
 ```
 cd rally/lib/python2.7/site-packages/
 mv novaclient novaclient_bak
 scp -r root@node-17:/usr/lib/python2.7/site-packages/novaclient ./ 
 
 ```
 2. 解决oslo包依赖问题
  - 修改novaclient中对oslo包的引用更改为对rally oslo相关包的依赖
    ```
    cd ~/rally/lib/python2.7/site-packages/novaclient
    sed -i s/"oslo."/"oslo_"/g `grep "oslo." -rl --include="*.py" ./`
    ```
    
 3. 由于rally调用新版本client时会传递一些旧版本没有的关键字参数，所以需要对Client类的构造函数的参数进行修改，避免参数传递冲突：
 ```
 # 增加**kwargs用来获取rally提供的额外关键字参数。
 def __init__(self, username=None, api_key=None, project_id=None,
                 auth_url=None, insecure=False, timeout=None,
                 proxy_tenant_id=None, proxy_token=None, region_name=None,
                 endpoint_type='publicURL', extensions=None,
                 service_type='compute', service_name=None,
                 volume_service_name=None, timings=False, bypass_url=None,
                 os_cache=False, no_cache=True, http_log_debug=False,
                 auth_system='keystone', auth_plugin=None, auth_token=None,
                 cacert=None, tenant_id=None, user_id=None,
                 connection_pool=False, session=None, auth=None,
                 completion_cache=None, **kwargs):
     
 ```
 
##CinderClient
　　CinderClient和NeutronClient相同，可以直接将测试环境中的cinderclient复制到rally中，具体如下：

      cd rally/lib/python2.7/site-packages/;mv neutronclient neutronclient_bak
      scp -r root@node-17:/usr/lib/python2.7/site-packages/neutronclient ./

##CeilometerClient
1. 备份Rally CeilometeClient，将测试环境中的CeilometerClient复制到Rally目录下。
    ```
        cd rally/lib/python2.7/site-packages/;mv ceilometerclient ceilometerclient_bak
        scp -r root@node-17:/usr/lib/python2.7/site-packages/ceilometerclient ./
        
    ```
2. 由于测试环境中的Ceilometer采用自身调用keystoneclient进行认证而不是使用rally提供的keystone session进行认证，需要对这一点进行调整。
    ```
    vim rally/lib/python2.7/site-packages/rally/osclient.py
    
    class Ceilometer(OSClient):
        def create_client(self, version=None, service_type=None):
            """Return ceilometer client."""
            from ceilometerclient import client as ceilometer
    
            #新增认证用参数
            cli_kwargs = {
                'username': self.credential.username,
                'password': self.credential.password,
                'tenant_id': self.keystone.auth_ref.project_id,
                'tenant_name': self.credential.tenant_name,
                'auth_url': self.credential.auth_url,
                'region_name': self.credential.region_name,
                'service_type': service_type,
                'endpoint_type': self.credential.endpoint_type,
                'cacert': self.credential.cacert,
                'cert_file': None,
                'key_file': None,
                'token': self.keystone.auth_ref.auth_token,
            }
            #新增认证步骤
            client = ceilometer.get_client(
                self.choose_version(version),
                **cli_kwargs)
            return client
            
        #原有认证步骤
        # client = ceilometer.get_client(
        #     self.choose_version(version),
        #     session=self.keystone.get_session()[0],
        #     endpoint_override=self._get_endpoint(service_type))
        # return client
        
    ```
　　
##GlanceClient
与CeilometerClient类似，GlanceClient同样需要修改rally的认证步骤，具体如下。

1. 备份Rally GlanceClient，将测试环境中的GlanceClient复制到Rally目录下。
    ```
    cd rally/lib/python2.7/site-packages/;mv glanceclient glanceclient_bak
    scp -r root@node-17:/usr/lib/python2.7/site-packages/glanceclient ./
    ```
    
2. 修改rally传递给glanceclient的认证参数。
    ```
    vim rally/lib/python2.7/site-packages/rally/osclient.py
    
    @configure("glance", default_version="1", default_service_type="image",
           supported_versions=["1", "2"])
    class Glance(OSClient):
        def create_client(self, version=None, service_type=None):
            """Return glance client."""
            import glanceclient as glance
    
            # session = self.keystone.get_session()[0]
            # client = glance.Client(
            #    version=self.choose_version(version),
            #    endpoint_override=self._get_endpoint(service_type),
            #    session=session)
            # return client
            cli_kwargs = {
                'username': self.credential.username,
                'password': self.credential.password,
                'tenant_id': self.keystone.auth_ref.project_id,
                'tenant_name': self.credential.tenant_name,
                'auth_url': self.credential.auth_url,
                'region_name': self.credential.region_name,
                'service_type': service_type,
                'endpoint_type': self.credential.endpoint_type,
                'cacert': self.credential.cacert,
                'cert_file': None,
                'key_file': None,
                'token': self.keystone.auth_ref.auth_token,
            }
    
            client = glance.Client(
                self.choose_version(version),
                endpoint=self._get_endpoint(service_type),
                **cli_kwargs)
            return client
    
    ```

##KeystoneClient
1. 复制测试环境中的Keystoneclient到rally目录下。
    ```
    cd rally/lib/python2.7/site-packages/;mv keystoneclient keystoneclient_bak
    scp -r root@node-17:/usr/lib/python2.7/site-packages/keystoneclient ./
    
    ```
2. 使rally使用eayun版本的Keystoneclient。
    ```
    vim rally/lib/python2.7/site-packages/rally/osclient.py
    
    def create_client(self, version=None):
        """Return a keystone client.

        :param version: Keystone API version, can be one of:
            ("2", "3")

        If this object was constructed with a version in the api_info
        then that will be used unless the version parameter is passed.
        """
        import keystoneclient
        from keystoneclient import client

        # Use the version in the api_info if provided, otherwise fall
        # back to the passed version (which may be None, in which case
        # keystoneclient chooses).
        version = self.choose_version(version)

        sess = self.get_session(version=version)[0]

        kw = {"version": version, "session": sess,
              "timeout": CONF.openstack_client_http_timeout}
        if keystoneclient.__version__[0] in ("0", "1"):
            # 增加Keystone0.x.x版本(eayun使用的版本)
            # NOTE(andreykurilin): let's leave this hack for envs which uses
            #  old(<2.0.0 eayun is 0.11.1) keystoneclient version. Upstream fix:
            #  https://github.com/openstack/python-keystoneclient/commit/d9031c252848d89270a543b67109a46f9c505c86
            from keystoneauth1 import plugin
            kw["auth_url"] = sess.get_endpoint(interface=plugin.AUTH_INTERFACE)
        if self.credential.endpoint_type:
            kw["endpoint_type"] = self.credential.endpoint_type
        return client.Client(**kw)
    ```
