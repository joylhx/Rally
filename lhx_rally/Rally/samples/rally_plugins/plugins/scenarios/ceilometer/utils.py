#!/usr/bin/python

from rally.plugins.openstack import scenario


class CeilometerScenario(scenario.OpenStackScenario):
    """Base class for Ceilometer scenarios with basic atomic actions."""

    def _list_samples(self, meter_name, query, limit):
        return self.clients("ceilometer").samples.list(meter_name=meter_name,
                                                       q=query, limit=limit)
