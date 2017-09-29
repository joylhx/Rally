#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.common import logging
import utils


LOG = logging.getLogger(__name__)

@scenario.configure(name="Lbaas.create_different_protocol_pools")
class CreateDifferentProtocolPools(utils.LbaasScenario):
    """Create different protocol lb pools and delete them.
    param name: The name of pool.
    param lb_method: The pool stategy include ROUND_ROBIN, LEAST_CONNECTIONS, SOURCE_IP
    param protocol: Pool protocol include HTTP,TCP,HTTPS
    param subnet_id: The subnet where the pool is located.
    """
    def run(self, **kwargs):
        pools = self._create_pool(kwargs)
        self._delete_pool(pools)

@scenario.configure(name="Lbaas.create_member_and_delete")
class CreateMembersAndDelete(utils.LbaasScenario):
    """Create active/backup member, and then delete it.
    param pool_id: The member of the pool.
    param address: The member's ip address.
    param protocol_port: The member's protocol_port.
    param priority: The member's priority, use it to distinguish active or backup member.
    """
    def run(self, **kwargs):
        member = self._create_member(kwargs)
        self._delete_member(member)

@scenario.configure(name="Lbaas.create_vip_and_delete")
class CreateVipAndDelete(utils.LbaasScenario):
    """Create lb vip and delete it.
    param name: The name of vip.
    param protocol: The protocol for balanceing, including HTTP,TCP,HTTPS.
    param protocol_port: TCP port on which to listen for client traffic that is associated with the vip address.
    param pool_id: Pool id or name this vip belongs to.
    param subnet_id: The subnet on which to allocate the vip address.
    param session_persistence: The vip of session_persistence including APP_COOKIE,HTTP_COOKIE.
    """
    def run(self, **kwargs):
        vip = self._create_vip(kwargs)
        self._delete_vip(vip)

@scenario.configure(name="Lbaas.create_healthmonitor_and_delete")
class CreateHealthmonitorAndDelete(utils.LbaasScenario):
    """Create and delete healthmonitor.
    param http_method: The http method used for requests by the monitor of type http.
    param delay: The time in seconds between sending probes to members.
    param max_retries: Number od permissible connection failures before changing the member status to inactive.
    param timeout: Maximum number of seconds for a monitor.
    param type: One of the predefined health monitor types.
    """
    def run(self, **kwargs):
        self._create_healthmonitor(kwargs)
        self._delete_healthmonitor(kwargs)


@scenario.configure(name="Lbaas.list_multiple")
class ListMultiple(utils.LbaasScenario):
    """List lb-pools,lb-members,lb-vips,lb-healthmonitors, lb-l7rule, lb-l7policy."""
    def run(self):
        self._list_multiple()

@scenario.configure(name="Lbaas.associate_floatingip_for_vip")
class AssociateFloatingipForVip(utils.LbaasScenario):
    """Associate a floatingip for vip"""
    def run(self, **kwargs):
        vip = self._create_vip(kwargs)
        self._associate_floatingip_for_vip(vip)
        self._delete_vip(vip)

@scenario.configure(name="Lbaas.create_and_delete_l7rule")
class CreateAndDeleteL7rule(utils.LbaasScenario):
    """Create and delete l7rule.
    param type: The type of l7rule.
    param key: The keyword for l7rule type.
    param value: The value of l7rule type.
    param compare_type: The compare type of l7rule type.
    param compare_value: The compare value of l7rule compare-type value.
    """
    def run(self, **kwargs):
        l7rule = self._create_l7_rule(kwargs)
        self._delete_l7_rule(l7rule)

@scenario.configure(name="Lbaas.create_and_delete_l7policy")
class CreateAndDeleteL7policy(utils.LbaasScenario):
    """Create and delete l7policy.
    param priority: The priority for l7policy.
    param pool_id: The l7policy of pool that belong.
    param action: Exec action on the l7policy if l7rule match.
    param key: The key of the l7policy action keyword.
    param value: The value of the l7policy action values.
    """
    def run(self, **kwargs):
        l7policy = self._create_l7_policy(kwargs)
        self._delete_l7_policy(l7policy)

@scenario.configure(name="Lbaas.associate_and_disassociate_l7rule_l7policy")
class AssociateAndDisassociateL7ruleL7policy(utils.LbaasScenario):
    """L7rule and L7policy associate/disassociate."""
    def run(self):
        self._associate_rule_and_policy(self.context['l7rule'], self.context['l7policy'])
        self._disassociate_rule_and_policy(self.context['l7rule'], self.context['l7policy'])

@scenario.configure(name="Lbaas.update_the_l7rule")
class UpdateTheL7rule(utils.LbaasScenario):
    """Update the l7rule."""
    def run(self, **kwargs):
        self._update_l7_rule(kwargs)

@scenario.configure(name="Lbaas.update_the_l7policy")
class UpdateL7policy(utils.LbaasScenario):
    """Update the l7policy."""
    def run(self, **kwargs):
        self._update_l7_policy(kwargs)

