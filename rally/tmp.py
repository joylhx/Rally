#!/usr/bin/env python
# encoding: utf-8

class Network():
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "nics": {
                "type": "array",
                "properties": {
                    "net-id": {
                        "type": "string"
                    }
                }
            }
        }
    }

    def setup(self):
        #get body
        for iter_, (user, tenant_id) in enumerate(rutils.iterate_per_tenants(self.context["users"])):
            LOG.debug("Create network for user tenant %s " % (user["tenant_id"]))
            tmp_context = {"user": user,
                           "tenant": self.context["tenant"][tenant_id],
                           "task": self.context["task"],
                           "iteration": iter_}
            network_id = self.contexr['tenants'][tenant_id]['network']['id']
            neutron_scenario = neutron_utils.NeutronScenario(tmp_context)
            self.context['tenants'][tenant_id]["network"]
