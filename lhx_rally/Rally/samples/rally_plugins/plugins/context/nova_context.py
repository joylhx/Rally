#!/usr/bin/env python
# encoding: utf-8

from rally.common import logging
from rally import consts
from rally import osclients
from rally.task import context, utils

LOG = logging.getLogger(__name__)


@context.configure(name="create_floatingip", order=999)
class CreateFloatIP(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "external_net": {"type": "string"}
        }
    }

    def setup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            body = {
                "floatingip": {
                    "floating_network_id": self.config['external_net']
                }
            }
            floating_ip = neutron.create_floatingip(body)['floatingip']
            self.context['floatingip'] = floating_ip
            LOG.debug("FloatingIP with id '%s'" % floating_ip['id'])
        except Exception as e:
            msg = "Can't create server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
            neutron.delete_floatingip(self.context['floatingip']['id'])
            LOG.debug("Floatingip '%s' deleted" % self.context["floatingip"]["id"])
        except Exception as e:
            msg = "Can't delete floatingip: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

@context.configure(name="create_server", order=1000)
class CreateServerContext(context.Context):

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "additionalProperties": False,
        "properties": {
            "name": {
                "type": "string",
            },
            "flavor": {
                "type": "string",
            },
            "nics": {
                "type": "array",
                "items": {
                    "properties": {"net-id": {"type": "string"}}
                }
            },
            "block_device": {
                "type": "array",
                "properties": {
                    "boot_index": {"type": "string"},
                    "uuid": {"type": "string"},
                    "source_type": {"type": "string"},
                    "volume_size": {"type": "string"},
                    "destination_type": {"type": "string"},
                    "delete_on_termination": {"type": "boolean"}
                }
            },
            "meta":{
                "type":"object",
                "properties": {
                    "reset_password": {"type":"string"}
                }
            },
            "userdata":{
                "type":"string",
            }


        }
    }

    def setup(self):
        try:
            client = osclients.Clients(self.context['users'][0]['credential']).nova()
            server = client.servers.create(
                name=self.config.get('name', 'test'),
                image=None,
                userdata=self.config.get('userdata'),
                #meta=self.config['meta'],
                flavor=client.flavors.get(self.config.get('flavor', 2)),
                block_device_mapping_v2=list(self.config['block_device']),
                nics=list(self.config['nics']))
            self.context['server'] = server
            utils.wait_for_status(
                server, update_resource=client.servers.get,
                ready_statuses=['ACTIVE'], timeout=180, check_interval=5)

            server = client.servers.get(server.id)
            if self.context.get('floatingip'):
                neutron = osclients.Clients(self.context['users'][0]['credential']).neutron()
                for port in neutron.list_ports()['ports']:
                    for ips in port['fixed_ips']:
                        if ips['ip_address'] == server.networks.values()[0][0]:
                            break
                    else:
                        continue
                    break

                neutron.update_floatingip(self.context['floatingip']['id'], {"floatingip": {"port_id": port['id']}})

            self.context['server'] = server.to_dict()
            LOG.debug("Server with id '%s'" % server.id)
        except Exception as e:
            msg = "Can't create server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)

    def cleanup(self):
        try:
            manager = osclients.Clients(self.context['users'][0]['credential']).nova().servers
            server = manager.get(self.context['server']['id'])
            server.force_delete()
            try:
                utils.wait_for_delete(server, manager.get)
            except BaseException:
                pass
            LOG.debug("Server '%s' deleted" % self.context["server"]["id"])
        except Exception as e:
            msg = "Can't delete server: %s" % e
            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning(msg)
