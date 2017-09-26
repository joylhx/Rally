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


@context.configure(name="databases", namespace="openstack", order=1000)
class CreateDatabaseContext(context.Context):
    """Create database for trove instance."""
    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "databases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }

    @logging.log_task_wrapper(LOG.info, _("Enter context: `Databases`"))
    def setup(self):
        """This method is called before the task start."""
        if name  not in self.config["databases"].keys():
            self.config["databases"]["name"] = None
        try:
            for iter_, (user, tenant_id) in enumerate(rutils.iterate_per_tenants(
                    self.context["users"])):
                LOG.debug("Creating instances for user tenant %s "
                          % (user["tenant_id"]))
                tmp_context = {"user": user,
                               "tenant": self.context["tenants"][tenant_id],
                               "task": self.context["task"],
                               "owner_id": self.context["owner_id"],
                               "iteration": iter_}
                trove_scenario = trove_utils.TroveScenario(tmp_context)
                LOG.debug("Calling _create_database for instance %s"
                          % (self.context["instance"]["name"]))
                database = trove_scenario._create_database(
                    self.context["instance"]["id"],
                    self.config["databases"])
                LOG.debug("Adding created database %s to context" % database.name)
                self.context["database"] = database
        except Exception as e:
            msg = ("Can't create context database for instance: %s" % e.message)
            raise Exception(msg)
            # if logging.is_debug():
            #     LOG.exception(msg)
            # else:
            #     LOG.warning(msg)

    @logging.log_task_wrapper(LOG.info, _("Exit context: `Databases`"))
    def cleanup(self):
        try:
            trove = osclients.Clients(
                self.context["admin"]["credential"]).trove()
            trove.databases.delete(self.context["instance"]["id"], self.context["database"])
            LOG.debug("Database %s deleted" % self.context["database"]["name"])
        except Exception as e:
            msg = "Can't delete context database: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
