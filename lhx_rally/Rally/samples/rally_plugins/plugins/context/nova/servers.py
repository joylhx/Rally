#!/usr/bin/python
# Nova server context for EayunStack 3.0.0 plugins

from rally.common.i18n import _
from rally.common import logging
from rally.common import utils as rutils
from rally.common import validation
from rally import osclients
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack import types
from rally.task import context
from rally.task import utils as t_utils


LOG = logging.getLogger(__name__)


@validation.add("required_platform", platform="openstack", users=True)
@context.configure(name="nova_servers", order=430)
class ServerGenerator(context.Context):
    """Context class for adding temporary servers for benchmarks.

    Servers are added for each tenant.
    """

    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "image": {
                "description": "Name of image to boot server(s) from.",
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            },
            "flavor": {
                "description": "Name of flavor to boot server(s) with.",
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            },
            "servers_per_tenant": {
                "description": "Number of servers to boot in each Tenant.",
                "type": "integer",
                "minimum": 1
            },
            "auto_assign_nic": {
                "description": "True if NICs should be assigned.",
                "type": "boolean",
            },
            "nics": {
                "type": "array",
                "description": "List of networks to attach to server.",
                "items": {"oneOf": [
                    {"type": "object",
                     "properties": {"net-id": {"type": "string"}},
                     "description": "Network ID in a format like OpenStack API"
                                    " expects to see."},
                    {"type": "string", "description": "Network ID."}]},
                "minItems": 1
            },
            "force_delete": {
                "type": "boolean",
                "descriptions": "Force delete server if set to True."
            }
        },
        "required": ["image", "flavor"],
        "additionalProperties": False
    }

    DEFAULT_CONFIG = {
        "servers_per_tenant": 5,
        "auto_assign_nic": False,
        "force_delete": False
    }

    @logging.log_task_wrapper(LOG.info, _("Enter context: `Servers`"))
    def setup(self):
        image = self.config["image"]
        flavor = self.config["flavor"]
        auto_nic = self.config["auto_assign_nic"]
        servers_per_tenant = self.config["servers_per_tenant"]
        kwargs = {}
        if self.config.get("nics"):
            if isinstance(self.config["nics"][0], dict):
                # it is a format that Nova API expects
                kwargs["nics"] = self.config["nics"]
            else:
                kwargs["nics"] = [{"net-id": nic}
                                  for nic in self.config["nics"]]

        clients = osclients.Clients(self.context["users"][0]["credential"])
        image_id = types.GlanceImage.transform(clients=clients,
                                               resource_config=image)
        flavor_id = types.Flavor.transform(clients=clients,
                                           resource_config=flavor)

        for iter_, (user, tenant_id) in enumerate(rutils.iterate_per_tenants(
                self.context["users"])):
            LOG.debug("Booting servers for user tenant %s "
                      % (user["tenant_id"]))
            tmp_context = {"user": user,
                           "tenant": self.context["tenants"][tenant_id],
                           "task": self.context["task"],
                           "owner_id": self.context["owner_id"],
                           "iteration": iter_}
            nova_scenario = nova_utils.NovaScenario(tmp_context)

            LOG.debug("Calling _boot_servers with image_id=%(image_id)s "
                      "flavor_id=%(flavor_id)s "
                      "servers_per_tenant=%(servers_per_tenant)s"
                      % {"image_id": image_id,
                         "flavor_id": flavor_id,
                         "servers_per_tenant": servers_per_tenant})

            servers = nova_scenario._boot_servers(image_id, flavor_id,
                                                  requests=servers_per_tenant,
                                                  auto_assign_nic=auto_nic,
                                                  **kwargs)

            current_servers = [server.id for server in servers]

            LOG.debug("Adding booted servers %s to context"
                      % current_servers)

            self.context["tenants"][tenant_id][
                "servers"] = current_servers

    @logging.log_task_wrapper(LOG.info, _("Exit context: `Servers`"))
    def cleanup(self):
        try:
            nova = osclients.Clients(
                self.context["admin"]["credential"]).nova()
            tenant_id = self.context["users"][0]["tenant_id"]
            for server in self.context["tenants"][tenant_id]["servers"]:
                server = nova.servers.get(server)
                if self.config["force_delete"]:
                    server.force_delete()
                else:
                    server.delete()
                t_utils.wait_for_status(
                    server,
                    ready_statuses=["deleted"],
                    check_deletion=True,
                    update_resource=t_utils.get_from_manager(),
                    timeout=300,
                    check_interval=1
                )
                LOG.debug("Context server [%s: %s] is deleted"
                          % (server.name, server.id))
        except Exception as e:
            msg = "Can't delete context server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
