#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context
from time import sleep

LOG = logging.getLogger(__name__)

@context.configure(name="pool_context", order=803)
class LbPoolContext(context.Context):

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



@context.configure(name="member_context", order=804)
class LbMemberContext(context.Context):

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
            },
            "priority": {
                "type": "integer"
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
                    "admin_state_up": self.config.get("admin_state_up", True),
                    "priority": self.config.get("priority")
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


@context.configure(name="vip_context", order=805)
class LbVipContext(context.Context):

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
            LOG.debug("LbVip '%s' delete successful." % self.context["vip"])
        except Exception as e:
            msg = "Can't delete vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

        sleep(10)

@context.configure(name="healthmonitor_context", order=806)
class LbHealthmonitorContext(context.Context):

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
            LOG.debug("LbHealthmonitor with id '%s' create successful." % self.context["health_monitor"])
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
            LOG.debug("LbHealthmonitor '%s' delete successful." % self.context["health_monitor"])
        except Exception as e:
            msg = "Can't delete lb_healthmonitor: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

@context.configure(name="l7rule_context", order=810)
class LbL7ruleContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "tenant_id": {
                "type": "string"
            },
            "type": {
                "type": "string"
            },
            "compare_value": {
                "type": "string"
            },
            "compare_type": {
                "type": "string"
            },
            "key": {
                "type": "string"
            },
            "value": {
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
                "l7rule": {
                    "type": self.config.get('type', 'backendServerId'),
                    "key": self.config.get('key'),
                    "value": self.config.get('value'),
                    "compare_type": self.config.get('compare_type'),
                    "compare_value": self.config.get('compare_value')
                }
            }
            self.context['l7rule'] = client.create_l7rule(body=body)["l7rule"]["id"]
            LOG.debug("Lbl7rule with id '%s' create successful." % self.context['l7rule'])
        except Exception as e:
            msg = "Can't create l7rule: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_l7rule(self.context['l7rule'])
            LOG.debug("Lbl7rule '%s' delete successful." % self.context['l7rule'])
        except Exception as e:
            msg = "Can't delete l7rule: %s" % e
            if logging.is_debug():
                LOG.exceptiom(msg)
            else:
                LOG.warning(msg)

@context.configure(name="l7policy_context", order=811)
class LbL7policyContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "tenant_id": {
                "type": "string"
            },
            "pool_id": {
                "type": "string"
            },
            "priority": {
                "type": "integer"
            },
            "action": {
                "type": "string"
            },
            "key": {
                "type": "string"
            },
            "value": {
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
                "l7policy": {
                    "priority": self.config.get("priority"),
                    "action": self.config.get("action"),
                    "key": self.config.get("key"),
                    "value": self.config.get("value")
                }
            }
            self.context['l7policy'] = client.create_l7policy(body=body)['l7policy']['id']
            LOG.debug("Lbl7policy with id '%s' create successful." % self.context['l7policy'])
        except Exception as e:
            msg = "Can't create l7policy: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).neutron()
            client.delete_l7policy(self.context['l7policy'])
            LOG.debug("Lbl7policy '%s' delete successful." % self.context['l7policy'])
        except Exception as e:
            msg = "Can't delete l7policy: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

