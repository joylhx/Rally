#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.task import atomic

@scenario.configure(name="Neutron.create_pool_and_delete")
class CreatePoolAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_pool")
    def _create_pool(self, body):
        client = self.clients("neutron")
        pool = client.get(self.context['pool'])
        client.create_pool(pool, body)

    @atomic.action_timer("delete_pool")
    def _delete_pool(self, pool):
        self.clients("neutron").delete_pool(self.context["pool"], ["id"])
        #self.clients("neutron").delete_pool(pool["id"])

    def run(self, pool):
        self._create_pool(pool)
        self._delete_pool(pool)


@scenario.configure(name="Neutron.create_member_and_delete")
class CreateMemberAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_member")
    def _create_member(self, body):
        client = self.clients("neutron")
        member = client.get(self.context['member'])
        client.create_member(member, body)

    @atomic.action_timer("delete_member")
    def _delete_member(self, member):
        self.clients("neutron").delete_member(self.context["member"], ["id"])

    def run(self, member):
        self._create_member(member)
        self._delete_member(member)

@scenario.configure(name="Neutron.create_vip_and_delete")
class CreateVipAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_vip")
    def _create_vip(self, body):
        client = self.clients("neutron")
        vip = client.get(self.context['vip'])
        client.create_vip(vip, body)

    @atomic.action_timer("delete_vip")
    def _delete_vip(self, vip):
        self.clients("neutron").delete_vip(self.context["vip"], ["id"])

    def run(self, vip):
        self._create_vip(vip)
        self._delete_vip(vip)

@scenario.configure(name="Neutron.create_healthmonitor_and_delete")
class CreateHealthmonitorAndDelete(scenario.OpenStackScenario):

    @atomic.action_timer("create_healthmonitor")
    def _create_healthmonitor(self, body):
        client = self.clients("neutron")
        healthmonitor = client.get(self.context['healthmonitor'])
        client.create_health_monitor(healthmonitor, body)

    @atomic.action_timer("delete_healthmonitor")
    def _delete_healthmonitor(self, healthmonitor):
        self.clients("neutron").delete_health_monitor(self.context["healthmonitor"], ["id"])

    def run(self, healthmonitor):
        self._create_health_monitor(healthmonitor)
        self._delete_health_monitor(healthmonitor)


@scenario.configure(name="Neutron.list_multiple")
class ListMultiple(scenario.OpenStackScenario):

    @atomic.action_timer("list_multiple")
    def _list_multiple(self, **kwargs):
        self.clients("neutron").list_pools(**kwargs)
        self.clients("neutron").list_members(**kwargs)
        self.clients("neutron").list_vips(**kwargs)
        self.clients("neutron").list_health_monitors(**kwargs)

    def run(self, **kwargs):
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

    def run(self, vip, **kwargs):
        self._create_vip()
        self._associate_floatingip_for_vip()
        self._delete_vip()




