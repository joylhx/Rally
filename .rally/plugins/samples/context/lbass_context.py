#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context

LOG = logging.getLogger(__name__)


@context.configure(name="create_floatingip", order=400)
class CreateFloatingip(context.Context):

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
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "floatingip": {
                    "floating_network_id": self.config['external_net']
                }
            }
            floating_ip = neutron.create_floatingip(body)['floatingip']
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
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            neutron.delete_floatingip(self.context['floatingip']['id'])
            LOG.debug("Floatingip '%s' has deleted" % self.context["floatingip"]["id"])
        except Exception as e:
            msg = "Can't delete floatingip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_instance", order=300)
class CreateInstance(context.Context):

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
            server = client.server.create(
                name=self.config.get('name', 'test'),
                image=None,
                userdate=self.config.get('userdata'),
                flavor=client.flavors.get(self.config.get('flavor', 2)),
                block_device_mapping_v2=list(self.config['block_device_mapping_v2']),
                nics=list(self.config['nics'])
            )
            LOG.debug("Server with id '%s'" % server.id)
        except Exception as e:
            msg = "Can't create server %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

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


@context.configure(name="create_lb_pool", order=500)
class CreateLbPool(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "pool": {
                "type": "object"
            },
            "name": {
                "type": "string"
            },
            "lb_method": {
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
            neutron = osclients.Clients(self.context["users"][0]['credential']).neutron()
            body = {
                "pool": {
                    "name": self.config.get("name"),
                    "lb_method": self.config.get("lb_method"),
                    "protocol": self.config.get("protocol"),
                    "subnet_id": self.config.get("subnet_id")
                }
            }
            lb_pool = neutron.create_lb_pool(body)['pool']
            self.context['pool'] = lb_pool
            LOG.debug("LbPool with id '%s'" % lb_pool['id'])
        except Exception as e:
            msg = "Can't create pool: %s" % e
            if logging.is_debug():
                LOG.Exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            neutron = osclients.Clients(
                self.context["users"][0]["credential"]).neutron()
            neutron.delete_pool(self.context['pool']['id'])
            LOG.debug("LbPool '%s' deleted" % self.context["pool"]["id"])
        except Exception as e:
            msg = "Can't delete pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)


@context.configure(name="create_lb_member", order=600)
class CreateLbMember(context.context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "member": {
                "type": "object"
            },
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
            "priority": {
                "type": "integer"
            },
            "weight": {
                "type": "integer"
            }
        }
    }

    def setup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "member": {
                    "name": self.config.get("name", "test-member"),
                    "protocol_port": self.config.get("protocol_port"),
                    "pool_id": self.config.get("pool_id"),
                    "priority": self.config.get("priority"),
                    "weight": self.config.get("weight")
                }
            }
            lb_member = neutron.create_lb_member(body)['member']
            self.context['member'] = lb_member
            LOG.debug("LbMember with id '%s'" % lb_member['id'])
        except Exception as e:
            msg = "Can't create member: %s" % e
            if logging.is_debug():
                LOG.Exception(msg)
            else:
                LOG.warning(msg)
    def cleanup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            neutron.delete_member(self.context['member']['id'])
            LOG.debug("LbMember '%s' deleted" % self.context["member"]["id"])
        except Exception as e:
            msg = "Can't delete member: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

@context.configure(name="create_lb_vip", order=700)
class CreateLbVip(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "vip": {
                "type": "object"
            },
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
            "status": {
                "type": "string"
            },
            "status_description": {
                "type": "string"
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
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "vip": {
                    "admin_state_up": self.config.get("admin_state_up", True),
                    "name": self.config.get("name", "test-vip"),
                    "pool_id": self.config.get("pool_id"),
                    "protocol": self.config.get("protocol"),
                    "protocol_port": self.config.get("protocol_port"),
                    "subnet_id": self.config.get("subnet_id")
                }
            }
            lb_vip = neutron.create_lb_vip(body)['vip']
            self.context['vip'] = lb_vip
            LOG.debug("LbVip with id '%s'" % lb_vip['id'])
        except Exception as e:
            msg = "Can't create vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.exception(msg)

    def cleanup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            neutron.delete_vip(self.context['vip']['id'])
            LOG.debug("LbVip '%s' deleted" % self.context["vip"]["id"])
        except Exception as e:
            msg = "Can't delete vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

@context.configure(name="create_lb_healthmonitor", order=700)
class CreateLbHealthmonitor(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "health_monitor": {
                "type": "object"
            },
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
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "healthmonitor": {
                    "admin_state_up": self.config.get("admin_state_up", True),
                    "delay": self.config.get("delay"),
                    "http_method": self.config.get("http_method"),
                    "max_retries": self.config.get("max_retries"),
                    "pool_id": self.config.get("pool_id"),
                    "timeout": self.config.get("timeout"),
                    "type": self.config.get("type"),
                    "url_path": self.config.get("usr_path")
                }
            }
            lb_healthmonitor = neutron.create_lb_healthmonitor(body)['healthmonitor']
            self.context['healthmonitor'] = lb_healthmonitor
            LOG.debug("LbHealthmonitor with id '%s'" % lb_healthmonitor['id'])
        except Exception as e:
            msg = "Can't create server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            neutron.delete_lb_healthmonitor(self.context['lb_healthmonitor']['id'])
            LOG.debug("LbHealthmonitor '%s' deleted" % self.context["lb_healthmonitor"]["id"])
        except Exception as e:
            msg = "Can't delete lb_healthmonitor: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

