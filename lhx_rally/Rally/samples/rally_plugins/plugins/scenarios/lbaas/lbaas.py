#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.common import logging
import utils


LOG = logging.getLogger(__name__)

@scenario.configure(name="Lbaas.create_different_protocol_pools")
class CreateDifferentProtocolPools(utils.LbaasScenario):
    """Create lb pool."""
    def run(self, **kwargs):
        pools = self._create_pool(kwargs)
        self._delete_pool(pools)

@scenario.configure(name="Lbaas.create_member_and_delete")
class CreateMembersAndDelete(utils.LbaasScenario):
    """Create active and backup member."""
    def run(self, **kwargs):
        members = self._create_member(kwargs)
        self._delete_member(members)

@scenario.configure(name="Lbaas.create_vip_and_delete")
class CreateVipAndDelete(utils.LbaasScenario):
    """Create lb vip and delete."""
    def run(self, **kwargs):
        vip = self._create_vip(kwargs)
        self._delete_vip(vip)

@scenario.configure(name="Lbaas.create_healthmonitor_and_delete")
class CreateHealthmonitorAndDelete(utils.LbaasScenario):

    def run(self, **kwargs):
        self._create_health_monitor(kwargs)
        self._delete_health_monitor(kwargs)


@scenario.configure(name="Lbaas.list_multiple")
class ListMultiple(utils.LbaasScenario):
    """List lb-pools,lb-members,lb-vips,lb-healthmonitors."""
    def run(self):
        self._list_multiple()

@scenario.configure(name="Lbaas.associate_floatingip_for_vip")
class AssociateFloatingipForVip(utils.LbaasScenario):
    """Associate a floatingip for vip"""
    def run(self, **kwargs):
        vip = self._create_vip(kwargs)
        self._associate_floatingip_for_vip()
        self._delete_vip(vip)

@scenario.configure(name="Lbaas.create_and_delete_l7rule")
class CreateAndDeleteL7rule(utils.LbaasScenario):
    """Create and delete l7rule."""
    def run(self, **kwargs):
        l7rule = self._create_l7_rule(kwargs)
        self._delete_l7_rule(l7rule)

@scenario.configure(name="Lbaas.create_and_delete_l7policy")
class CreateAndDeleteL7policy(utils.LbaasScenario):
    """Create and delete l7policy."""
    def run(self, **kwargs):
        l7policy = self._create_l7_policy(kwargs)
        self._delete_l7_policy(l7policy)

@scenario.configure(name="Lbaas.associate_and_disassociate_l7rule_l7policy")
class AssociateAndDisassociateL7ruleL7policy(utils.LbaasScenario):
    """L7rule and L7policy associate/disassociate."""
    def run(self):
        self._associate_rule_and_policy(self.context['l7rule'], self.context['l7policy'])
        self._disassociate_rule_and_policy(self.context['l7rule'], self.context['l7policy'])

@scenario.configure(name="Lbaas.one_rule_to_many_policies")
class OneRuleToManyPolicies(utils.LbaasScenario):
    """One l7rule to many l7policies.
    The same to mean: Associate one l7rule to different l7policy.
    """
    def run(self, policy_count=3, **kwargs):
        l7policies = []
        for i in range(policy_count):
            l7policy = self._create_l7_policy(kwargs)
            l7policies.append(self._associate_rule_and_policy(self.context['l7rule'], l7policy))        
        
        self._disassociate_rule_and_policy(self.context['l7rule'], l7policy)
        self._delete_l7_policy(l7policy)


@scenario.configure(name="Lbaas.one_policy_has_many_rules")
class OnePolicyHasManyRules(utils.LbaasScenario):
    """Create many l7rule, and associate it to one l7policy."""
    def run(self, rule_count=3, **kwargs):
        l7rules = []
        for i in range(rule_count):
            l7rule = self._create_l7_rule(kwargs)
            l7rules.append(self._associate_rule_and_policy(self.context['l7policy'], l7rule))
        self._disassociate_rule_and_policy(self.context['l7policy'], l7rule)
        self._delete_l7_rule(l7rule)





