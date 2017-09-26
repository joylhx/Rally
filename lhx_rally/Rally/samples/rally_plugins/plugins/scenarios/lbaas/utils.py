#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally.plugins.openstack import scenario
from rally.task import atomic
#from rally.task import utils

LOG = logging.getLogger(__file__)

class LbaasScenario(scenario.OpenStackScenario):
    """Base class for Lbass scenrio with basic atomic actions."""
    @atomic.action_timer("lbaas.create_pool")
    def _create_pool(self, body):
        try:
            #body = {
            #    "pool": {
            #        "name": "rally_pool"
            #        "subnet_id": self.context.["user_subnet"]
            #    }
            #}
            pools = {}
            pools = self.clients("neutron").create_pool(body)["pool"]["id"]
            LOG.debug("LbPool '%s' has create." % pools)
        except Exception as e:
            msg = "Can't create pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return pools

    @atomic.action_timer("lbaas.delete_pool")
    def _delete_pool(self, pools):
        try:
            self.clients("neutron").delete_pool(pools)
            LOG.debug("LbPool '%s' has delete." % pools)
        except Exception as e:
            msg = "Can't delete pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbass.create_member")
    def _create_member(self, body):
        try:
            members = {}
            members = self.clients("neutron").create_member(body)["member"]["id"]
            LOG.debug("Lbmember '%s' has create." % members)
        except Exception as e:
            msg = "Can't create Lbmember: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return members

    @atomic.action_timer("lbaas.delete_member")
    def _delete_member(self, members):
        try:
            self.clients("neutron").delete_member(members)
            LOG.debug("Lbmember '%s' has delete." % members)
        except Exception as e:
            msg = "Can't delete member: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.create_vip")
    def _create_vip(self, body):
        try:
            client = self.clients("neutron")
            vips = client.create_vip(body)["vip"]["id"]
            LOG.debug("LbVip '%s' has create." % vips)
        except Exception as e:
            msg = "Can't create vip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return vips

    @atomic.action_timer("lbaas.delete_vip")
    def _delete_vip(self, vips):
        try:
            self.clients("neutron").delete_vip(vips)
            LOG.debug("LbVip '%s' has delete." % vips)
        except Exception as e:
            msg = "Can't delete vip: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.create_healthmonitor")
    def _create_healthmonitor(self, body):
        try:
            client = self.clients("neutron")
            healthmonitor = client.create_health_monitor(body)
            LOG.debug("LbHealthmonitor '%s' has create." % healthmonitor)
        except Exception as e:
            msg = "Can't create healthmonitor: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
            return healthmonitor

    @atomic.action_timer("lbaas.delete_healthmonitor")
    def _delete_healthmonitor(self, healthmonitor):
        try:
            self.clients("neutron").delete_health_monitor(healthmonitor)
            LOG.debug("LbHealthmonitor '%s' has been deleted." % healthmonitor)
        except Exception as e:
            msg = "Can't delete healthmonitor: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.list_multiple")
    def _list_multiple(self):
        self.clients("neutron").list_pools()
        self.clients("neutron").list_members()
        self.clients("neutron").list_vips()
        self.clients("neutron").list_health_monitors()

    @atomic.action_timer("lbaas.associate_floatingip_for_vip")
    def _associate_floatingip_for_vip(self, vip, **kwargs):
        client = self.clients("neutron")
        list_vip = client.get(vip["id"])
        if self.context.get('floatingip'):
            neutron = client.Clients(self.context['users'][0]['credential']).neutron()
            for port in neutron.list_ports()['ports']:
                for ips in port['fixed_ips']:
                    if ips['ip_address'] == list_vip.networks.values()[0][0]:
                        break
                    else:
                        continue
                    break

            neutron.update_floatingip(self.context['floatingip']['id'], {"floatingip": {"port_id": port['id']}})

    @atomic.action_timer("lbaas.create_l7_policy")
    def _create_l7_policy(self, body):
        try:
            l7policies = {}
            l7policies = self.clients("neutron").create_l7policy(body)["l7policy"]["id"]
            LOG.debug("L7policy '%s' has been created." % l7policies)
        except Exception as e:
            msg = "Can't create l7policy: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return l7policies

    @atomic.action_timer("lbaas.delete_l7_policy")
    def _delete_l7_policy(self, l7policy):
        try:
            self.clients("neutron").delete_l7policy(l7policy)
            LOG.debug("L7policy '%s' has been deleted." % l7policy)
        except Exception as e:
            msg = "Can't delete l7policy: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.list_l7_policies")
    def _list_l7_policies(self):
        self.clients("neutron").list_l7policies()

    @atomic.action_timer("lbaas.show_l7_policy")
    def _show_l7_policy(self, l7policy):
        self.clients("neutron").show_l7policy(l7policy)

    @atomic.action_timer("lbaas.update_l7_policy")
    def _update_l7_policy(self, l7policy):
        self.clients("neutron").update_l7policy(l7policy)

    @atomic.action_timer("lbaas.create_l7_rule")
    def _create_l7_rule(self, body):
        try:
            l7rule = {}
            l7rule = self.clients("neutron").create_l7rule(body)["l7rule"]["id"]
            LOG.debug("L7rule '%s' has been created." % l7rule )
        except Exception as e:
            msg = "Can't create l7rule: '%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return l7rule

    @atomic.action_timer("lbaas.delete_l7_rule")
    def _delete_l7_rule(self, l7rule):
        try:
            self.clients("neutron").delete_l7rule(l7rule)
            LOG.debug("L7rule '%s' has been deleted." % l7rule)
        except Exception as e:
            msg = "Can't delete l7rule:'%s'" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.list_l7_rules")
    def _list_l7_rules(self):
        self.clients("neutron").list_l7rules()

    @atomic.action_timer("lbaas.show_l7_rule")
    def _show_l7_rule(self, l7rule):
        self.clients("neutron").show_l7rule(l7rule)

    @atomic.action_timer("lbaas.update_l7_rule")
    def _update_l7_rule(self, l7rule):
        self.clients("neutron").update_l7rule(l7rule)

    @atomic.action_timer("lbaas.associate_rule_and_policy")
    def _associate_rule_and_policy(self, l7rule, l7policy):
        try:
            self.clients("neutron").associate_l7rule(l7rule, l7policy)
            LOG.debug("Associate l7rule and policy successfully!")
        except Exception as e:
            msg = "Can't assocaite l7rule: '%s' and policy." % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    @atomic.action_timer("lbaas.disassociate_rule_and_policy")
    def _disassociate_rule_and_policy(self, l7rule, l7policy):
        try:
            self.clients("neutron").disassociate_l7rule(l7rule, l7policy)
            LOG.debug("Disassociate l7rule and policy successfully!")
        except Exception as e:
            msg = "Can't disassociate l7rule: '%s' and policy." % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)




