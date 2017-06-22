#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic
from rally.common import logging


LOG = logging.getLogger(__name__)

@scenario.configure(name="Neutron.create_different_protocol_pools")
class CreatePoolsAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_pool")
    def _create_pool(self, body):
        try:
            pools = self.clients("neutron").create_pool(body)["pool"]["id"]
            LOG.debug("LbPool '%s' has create." % pools)
        except Exception as e:
            msg = "Can't create pool: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return pools

    @atomic.action_timer("delete_pool")
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

    def run(self, **kwargs):
        pools = self._create_pool(kwargs)
        self._delete_pool(pools)


@scenario.configure(name="Neutron.create_member_and_delete")
class CreateMembersAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_member")
    def _create_member(self, body):
        try:
            import pdb;pdb.set_trace()
            members = self.clients("neutron").create_member(body)["member"]["id"]
            LOG.debug("Lbmember '%s' has create." % members)
        except Exception as e:
            msg = "Can't create Lbmember: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
        return members

    @atomic.action_timer("delete_member")
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

    def run(self, **kwargs):
        members= self._create_member(kwargs)
        self._delete_member(members)

@scenario.configure(name="Neutron.create_vip_and_delete")
class CreateVipAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_vip")
    def _create_vip(self, body):
        client = self.clients("neutron")
        client.create_vip(body)


    def run(self, **kwargs):
        self._create_vip(kwargs)

@scenario.configure(name="Neutron.create_healthmonitor_and_delete")
class CreateHealthmonitorAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_healthmonitor")
    def _create_healthmonitor(self, body):
        client = self.clients("neutron")
        client.create_health_monitor(body)

    @atomic.action_timer("delete_healthmonitor")
    def _delete_healthmonitor(self):
        self.clients("neutron").delete_health_monitor(self.context["healthmonitor"], ["id"])

    def run(self, **kwargs):
        self._create_health_monitor(kwargs)
        self._delete_health_monitor(kwargs)


@scenario.configure(name="Neutron.list_multiple")
class ListMultiple(scenario.OpenStackScenario):

    @atomic.action_timer("list_multiple")
    def _list_multiple(self):
        self.clients("neutron").list_pools()
        self.clients("neutron").list_members()
        self.clients("neutron").list_vips()
        self.clients("neutron").list_health_monitors()

    def run(self):
        self._list_multiple()

@scenario.configure(name="Neutron.associate_floatingip_for_vip")
class AssociateFloatingipForVip(scenario.OpenStackScenario):

    @atomic.action_timer("associate_floatingip_for_vip")
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

    def run(self, **kwargs):
        self._create_vip()
        self._associate_floatingip_for_vip()
        self._delete_vip()




