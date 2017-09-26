#!/bin/python

from rally.common.i18n import _
from rally.common import logging
from rally.common import utils as rutils
from rally import consts
from rally import osclients
from rally.task import context
from plugins.scenarios.trove import utils as trove_utils

LOG = logging.getLogger(__name__)


@context.configure(name="backup", namespace="openstack", order=1000)
class CreateBackupContext(context.Context):
    """Create backup for trove instance."""
    CONFIG_SCHEMA = {
        "type":  "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "incremental": {"type": "boolean"},
            "backup_per_instance": {
                "type": "integer",
                "minimum": 1
            }
        }
    }

    DEFAULT_CONFIG = {
        "backups_per_instance": 1
    }

    @logging.log_task_wrapper(LOG.info, _("Enter context: `Backups`"))
    def setup(self):
        """This method is called before the task start."""
        kwargs = {}
        try:
            for iter_, (user, tenant_id) in enumerate(
                    rutils.iterate_per_tenants(self.context["users"])):
                LOG.debug("Creating context backup for user tenant %s "
                          % (user["tenant_id"]))
                tmp_context = {"user": user,
                               "tenant": self.context["tenants"][tenant_id],
                               "task": self.context["task"],
                               "owner_id": self.context["owner_id"],
                               "iteration": iter_}
                trove_scenario = trove_utils.TroveScenario(tmp_context)

                backup = trove_scenario._create_backup(
                    self.context["instance"]["id"], **kwargs)
                LOG.debug("Adding created backup %s to context" % backup.name)
                self.context["backup"] = backup.to_dict()
        except Exception as e:
            msg = "Can't create context backup: %s" % e.message
            raise Exception(msg)

    @logging.log_task_wrapper(LOG.info, _("Exit context: `Backups`"))
    def cleanup(self):
        """This method is called after the task finish."""
        try:
            trove = osclients.Clients(
                self.context["admin"]["credential"]).trove()
            trove.backups.delete(self.context["backup"]["id"])
            LOG.debug("Backup %s deleted" % self.context["backup"]["name"])
        except Exception as e:
            msg = "Can't delete context backup: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
