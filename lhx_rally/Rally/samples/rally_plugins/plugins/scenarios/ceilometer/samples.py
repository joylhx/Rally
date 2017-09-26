#!/usr/bin/python
# Ceilometer scenarios for EayunStack 3.0.1

from time import sleep
from rally.plugins.openstack import scenario
from plugins.scenarios.ceilometer import utils
from rally.task import atomic
from rally.common import logging


LOG = logging.getLogger(__file__)

"""Scenarios for Ceilometer Samples API."""


@scenario.configure(name="CeilometerSamples.list_samples_with_meter_name")
class ListSamplesWithMeterName(utils.CeilometerScenario):
    def run(self, meter_infos, limit=None, interval=60):
        query_by_server = [
            "cpu_util",
            "memory.usage"
        ]
        query_by_port = [
            "network.es.port.incoming.bytes",
            "network.es.port.incoming.packets",
            "network.es.port.incoming.internal.bytes",
            "network.es.port.incoming.internal.packets",
            "network.es.port.incoming.external.bytes",
            "network.es.port.incoming.external.packets",
            "network.es.port.outgoing.bytes",
            "network.es.port.outgoing.packets",
            "network.es.port.outgoing.internal.bytes",
            "network.es.port.outgoing.internal.packets",
            "network.es.port.outgoing.external.bytes",
            "network.es.port.outgoing.external.packets"
        ]
        atomic_name = ("ceilometer.sleep")
        with atomic.ActionTimer(self, atomic_name):
            LOG.debug("Sleep %ss to wait ceilometer." % interval)
            sleep(interval)
        for meter_info in meter_infos:
            meter_name = meter_info["meter_name"]
            query = meter_info["query"]
            server_id = self.context["tenant"]["servers"][0]
            if meter_name in query_by_server:
                query[0]["value"] = server_id
            elif meter_name in query_by_port:
                port_id = self.clients("neutron").list_ports(
                    device_id=server_id)["ports"][0]["id"]
                query[0]["value"] = port_id
            atomic_name = ("ceilometer.%s" % meter_name)
            with atomic.ActionTimer(self, atomic_name):
                samples = self._list_samples(meter_name, query, limit)
            if samples:
                LOG.debug("Sample %s check PASS." % meter_name)
            else:
                raise Exception("Sample %s returns empty, please check."
                                % meter_name)
