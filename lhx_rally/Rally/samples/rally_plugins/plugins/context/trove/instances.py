#!/bin/python

from rally.common.i18n import _
from rally.common import logging
from rally.common import utils as rutils
from rally import consts
from rally import osclients
from rally.task import context
from rally.plugins.openstack.cleanup import manager as resource_manager
from plugins.scenarios.trove import utils as trove_utils

LOG = logging.getLogger(__name__)


@context.configure(name="instance", namespace="openstack", order=1000)
class CreateInstanceContext(context.Context):
    """Create trove instance.

    Instances are added for each tenants.
    """

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "flavor": {
                "type": "string",
            },
            "name": {"type": "string"},
            "datastore": {
                "type": "string",
            },
            "datastore_version": {
                "type": "string",
            },
            "volume": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "size": {
                        "type": "integer",
                        "minimun": 1
                    }
                }
            },
            "nics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "net-id": {"type": "string"},
                    }
                }
            }
        }
    }

    @logging.log_task_wrapper(LOG.info, _("Enter context: `Instances`"))
    def setup(self):
        """This method is called before the task start."""
        # TODO: add instances_per_tenants to create multiple instances
        kwargs = {}
        try:
            flavor = self.config["flavor"]
            datastore = self.config["datastore"]
            datastore_version = self.config["datastore_version"]
            nics = self.config["nics"]
            volume = self.config["volume"]
            name = self.config.get("name", None)

            for iter_, (user, tenant_id) in enumerate(
                    rutils.iterate_per_tenants(self.context["users"])):
                LOG.debug("Creating instances for user tenant %s "
                          % (user["tenant_id"]))
                tmp_context = {"user": user,
                               "tenant": self.context["tenants"][tenant_id],
                               "task": self.context["task"],
                               "owner_id": self.context["owner_id"],
                               "iteration": iter_}
                trove_scenario = trove_utils.TroveScenario(tmp_context)

                LOG.debug("Calling _create_instance with flavor=%(flavor)s "
                          "datastore=%(datastore)s "
                          "datastore_version=%(datastore_version)s "
                          "nics=%(nics)s "
                          "volume=%(volume)s "
                          % {"flavor": flavor,
                             "datastore": datastore,
                             "datastore_version": datastore_version,
                             "nics": nics,
                             "volume": volume})

                instance = trove_scenario._create_instance(flavor, datastore,
                                                           datastore_version,
                                                           nics, volume,
                                                           name=name,
                                                           **kwargs)

                LOG.debug("Adding created instance %s to context"
                          % instance.name)
                self.context["instance"] = instance.to_dict()
        except Exception as e:
            msg = "Can't create context for trove instance: %s" % e.message
            raise Exception(msg)

    @logging.log_task_wrapper(LOG.info, _("Exit context: `Instances`"))
    def cleanup(self):
        """This method is called after the task finish."""
        try:
            trove = osclients.Clients(
                self.context["admin"]["credential"]).trove()
            trove.instances.delete(self.context["instance"]["id"])
            LOG.debug("Instance %s deleted request is sent"
                      % self.context["instance"]["name"])
        except Exception as e:
            msg = "Can't delete context instance: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
