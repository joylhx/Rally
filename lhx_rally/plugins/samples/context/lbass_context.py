#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context
from time import sleep

LOG = logging.getLogger(__name__)

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
                neutron = osclients.Clients(self.context["users"][0]["credential"]).neutron()
                body = {"network": dict(name=self.config.get("name"))}
                self.context["user_network"] = neutron.create_network(body=body)["network"]["id"]
                LOG.debug("User Network with id '%s'" % self.context["user_network"])
            except Exception as e:
                msg = "Can't create network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)
        _user_setup()

    def cleanup(self):
        """This method is called after the task finish."""

        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                neutron.delete_network(self.context["user_network"])
                LOG.debug("User Network %s is deleted" % self.context["user_network"])
            except Exception as e:
                msg = "Can't delete network: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)
        sleep(10)
        _user_cleanup()



@context.configure(name="create_subnet", order=801)
class CreateSubnetContext(context.Context):
    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "network_id": {"type": "string"},
            "subnet_name": {"type": "string"},
            "cidr": {"type": "string"},
            "allocation_pools": {
                "type": "array",
                "additionalItems": False,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    }
                },
            },
            "dns_nameservers": {
                "type": "array",
                "items": {"type": "string"},
                "additionalItems": False,
                "uniqueItems": True
            }
        }
    }

    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                body = {
                    "subnet": {
                        "network_id": self.config.get("network_id", self.context["user_network"]),
                        "dns_nameservers": self.config.get("dns_nameservers", ["114.114.114.114"]),
                        "cidr": self.config.get("cidr"),
                        "ip_version": self.config.get("ip_version", 4)
                    }
                }

                # if get allocation_pools, add into body
                if self.config.get("allocation_pools"):
                    body["subnet"]["allocation_pools"] = self.config.get("allocation_pools")

                self.context["user_subnet"] = neutron.create_subnet(body=body)["subnet"]["id"]
                LOG.debug("User Subnet with id {0}".format(self.context["user_subnet"]))
            except Exception as e:
                msg = "Can't create subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_setup()
        sleep(10)

    def cleanup(self):

        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()

                neutron.delete_subnet(self.context["user_subnet"])
                LOG.debug("User Subnet '%s' deleted" % self.context["user_subnet"])
            except Exception as e:
                msg = "Can't delete subnet: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()
        sleep(10)


@context.configure(name="create_router", order=802)
class CreateRouterContext(context.Context):
    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "external_gateway_info": {
                "type": "object",
                "properties": {
                    "network_id": {"type": "string"}
                }
            }
        }
    }


    def setup(self):

        def _user_setup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()
                self.context["user_router"] = neutron.create_router(body={"router": self.config})["router"]["id"]
                sleep(10)

                # if subnet has created, add_interface
                if self.context.get("user_subnet"):
                    neutron.add_interface_router(self.context["user_router"], {"subnet_id": self.context["user_subnet"]})
                sleep(10)
                LOG.debug("User Router with id {0}".format(self.context["user_router"]))
            except Exception as e:
                msg = "Can't create Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)
        _user_setup()
        sleep(20)

    def cleanup(self):
        def _user_cleanup():
            try:
                neutron = osclients.Clients(
                    self.context["users"][0]["credential"]).neutron()

                # if subnet has created, delete_interce
                if self.context.get("user_subnet"):
                    neutron.remove_interface_router(self.context["user_router"], {"subnet_id": self.context["user_subnet"]})
                # sleep(10)

                neutron.delete_router(self.context["user_router"])
                LOG.debug("Router '%s' deleted" % self.context["user_router"])
            except Exception as e:
                msg = "Can't delete Route: %s" % e
                if logging.is_debug():
                    LOG.exception(msg)
                else:
                    LOG.warning(msg)

        _user_cleanup()


@context.configure(name="create_floatingip", order=820)
class CreateFloatingipContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "external_net": {"type": "string"}
        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "floatingip": {
                    "floating_network_id": self.config['external_net']
                }
            }
            floating_ip = client.create_floatingip(body)['floatingip']
            self.context['floatingip'] = floating_ip
            LOG.debug("Floatingip with id '%s'" % floating_ip['id'])
        except Exception as e:
            msg = "Can't create floatingip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_floatingip(self.context['floatingip']['id'])
            LOG.debug("Floatingip '%s' has deleted" % self.context["floatingip"]["id"])
        except Exception as e:
            msg = "Can't delete floatingip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_instance", order=805)
class CreateInstanceContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": { "type": "string" },
            "flavor": { "type": "string"},
            "nics": {
                "type": "array",
                "items": {
                    "properties": {"net-id": {"type": "string" }}
                }
            },
            "block_device_mapping_v2": {
                "type": "array",
                "properties": {
                    "boot_index": {
                        "type": "string"
                    },
                    "uuid": {
                        "type": "string"
                    },
                    "source_type": {
                        "type": "string"
                    },
                    "volume_size": {
                        "type": "string"
                    },
                    "destination_type": {
                        "type": "string"
                    },
                    "delete_on_termination": {
                        "type": "boolean"
                    }
                }
            },
            "userdata": {
                "type": "string"
            }
        }
    }
    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).nova()
            server = client.servers.create(
                name=self.config.get('name', 'test-instance'),
                image=None,
                userdate=self.config.get('userdata'),
                flavor=client.flavors.get(self.config.get('flavor', 2)),
                block_device_mapping_v2=list(self.config['block_device_mapping_v2']),
                nics=self.config.get(['nics'], self.context['user_network'])
            )
            self.context['server'] = server.to_dict()
            LOG.debug("Server with id '%s'" % server.id)
        except Exception as e:
            msg = "Can't create server %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        sleep(30)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).nova().servers
            server = client.get(self.context['server']['id'])
            server.force_delete()
            LOG.debug("Server '%s' deleted" % self.context["server"]["id"])
        except Exception as e:
            msg = "Can't delete server:%s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_pool", order=803)
class CreateLbPoolContext(context.Context):

    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {
                "type": "string"
            },
            "method_name": {
                "type": "string"
            },
            "protocol": {
                "type": "string"
            },
            "subnet_id": {
                "type": "string"
            },
            "tenant_id": {
                "type": "string"
            },
            "admin_state_up": {
                "type": "boolean"
            }
        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "pool":{
                    "name": self.config.get('name', 'test-pool'),
                    "lb_method": self.config.get('lb_method', 'ROUND_ROBIN'),
                    "protocol": self.config.get('protocol', "HTTP"),
                    "subnet_id": self.config.get('subnet_id', self.context['user_subnet'])
                }
            }
            self.context['pool'] = client.create_pool(body=body)['pool']['id']
            LOG.debug("LbPool with id '%s'" % self.context['pool'])
        except Exception as e:
            msg = "Can't create pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_pool(self.context['pool'])
            LOG.debug("LbPool '%s' deleted" % self.context['pool'])
        except Exception as e:
            msg = "Can't delete pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)



@context.configure(name="create_member", order=804)
class CreateLbMemberContext(context.Context):

    CONFIG_SCHEMA={
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "address": {
                "type": "string"
            },
            "pool_id": {
                "type": "string"
            },
            "protocol_port": {
                "type": "integer"
            },
            "tenant_id": {
                "type": "string"
            },
            "weight": {
                "type": "integer"
            },
            "admin_state_up": {
                "type": "boolean"
            }
        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "member":{
                    "address": self.config.get("address", '8.8.8.20'),
                    "protocol_port": self.config.get("protocol_port", 80),
                    "pool_id": self.config.get("pool_id", self.context['pool']),
                    "weight": self.config.get("weight", 1),
                    "admin_state_up": self.config.get("admin_state_up", True)
                }
            }
            LOG.warning("body:%s" % body)
            self.context["member"] = client.create_member(body=body)["member"]["id"]
            LOG.debug("LbMember with id '%s'" % self.context["member"])
        except Exception as e:
            msg = "Can't create member: %s" % e
            if logging.is_debug():
                LOG.Exception(msg)
            else:
                LOG.warning(msg)




    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_member(self.context["member"])
            LOG.debug("LbMember '%s' deleted" % self.context["member"])
        except Exception as e:
            msg = "Can't delete member: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
    sleep(10)


@context.configure(name="create_vip", order=805)
class CreateLbVipContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "address": {
                "type": "string"
            },
            "admin_state_up": {
                "type": "boolean"
            },
            "connection_limit": {
                "type": "integer"
            },
            "description": {
                "type": "string"
            },
            "name": {
                "type": "string"
            },
            "pool_id": {
                "type": "string"
            },
            "protocol": {
                "type": "string"
            },
            "protocol_port": {
                "type": "integer"
            },
            "session_persistence": {
                "type": "object",
                "properties": {
                    "type": "string"
                }
            },
            "subnet_id": {
                "type": "string"
            },
            "tenant_id": {
                "type": "string"
            }
        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "vip": {
                    "admin_state_up": self.config.get("admin_state_up", True),
                    "name": self.config.get("name", "test-vip"),
                    "session_persistence": self.config.get("session_persistence"),
                    "pool_id": self.config.get("pool_id", self.context['pool']),
                    "protocol": self.config.get("protocol", "HTTP"),
                    "protocol_port": self.config.get("protocol_port", "80"),
                    "subnet_id": self.config.get("subnet_id", self.context['subnet'])
                }
            }
            self.context['vip'] = client.create_vip(body=body)['vip']['id']
            LOG.debug("LbVip with id '%s'" % self.context['vip'])
        except Exception as e:
            msg = "Can't create vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.exception(msg)

        sleep(10)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_vip(self.context["vip"])
            LOG.debug("LbVip '%s' deleted" % self.context["vip"])
        except Exception as e:
            msg = "Can't delete vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

        sleep(10)

@context.configure(name="create_healthmonitor", order=806)
class CreateLbHealthmonitorContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "admin_state_up": {
                "type": "boolean"
            },
            "delay": {
                "type": "integer"
            },
            "http_method": {
                "type": "string"
            },
            "max_retries": {
                "type": "integer"
            },
            "tenant_id": {
                "type": "string"
            },
            "timeout": {
                "type": "string"
            },
            "url_path": {
                "type": "string"
            },
            "type": {
                "type": "string"
            }
        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "health_monitor": {
                    "admin_state_up": self.config.get("admin_state_up", True),
                    "delay": self.config.get("delay"),
                    "http_method": self.config.get("http_method"),
                    "max_retries": self.config.get("max_retries"),
                    "pool_id": self.config.get("pool_id", self.context["pool"]["id"]),
                    "timeout": self.config.get("timeout"),
                    "type": self.config.get("type"),
                    "url_path": self.config.get("url_path")
                }
            }
            self.context["health_monitor"] = client.create_health_monitor(body=body)["health_monitor"]["id"]
            LOG.debug("LbHealthmonitor with id '%s'" % self.context["health_monitor"])
        except Exception as e:
            msg = "Can't create server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_health_monitor(self.context["health_monitor"])
            LOG.debug("LbHealthmonitor '%s' deleted" % self.context["health_monitor"])
        except Exception as e:
            msg = "Can't delete lb_healthmonitor: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

