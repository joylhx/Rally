#!/usr/bin/python

import json

from rally.common import logging
from rally.plugins.openstack import scenario
from plugins.scenarios.trove import utils


"""Scenarios for Trove configurations."""


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveConfigurations.list_configurations")
class ListConfigurations(utils.TroveScenario):
    def run(self):
        """List all configurations.

        Measure the "trove configuration-list" command performance.
        """
        self._list_configurations()


@scenario.configure(name="TroveConfigurations.create_and"
                    "_delete_configuration")
class CreateAndDeleteConfiguration(utils.TroveScenario):
    def run(self, values, datastore, datastore_version, name=None):
        """Create a configuration with the given config, and then delete it.

        :param values: the value dict to create a trove configuration
        :param datastore: datastore of trove configuration to create
        :param datastore_version: datastore version of trove configuration to
               create
        :param name: name of configuration, if not given, generate a random one
        """
        values = json.dumps(values)
        configuration = self._create_configuration(
            values, name=name,
            datastore=datastore, datastore_version=datastore_version)
        self._delete_configuration(configuration)


@scenario.configure(name="TroveConfigurations.create_attach_and_"
                    "detach_configuration")
class CreateAttachAndDetachConfiguration(utils.TroveScenario):
    def run(self, values, datastore, datastore_version, name=None):
        """Create a configuration with the given config, and then attach it
        to an instance. The instance was created in context.

        :param values: the value dict to create a trove configuration
        :param datastore: datastore of trove configuration to create
        :param datastore_version: datastore version of trove configuration to
               create
        :param name: name of configuration, if not given, generate a random one
        """
        values = json.dumps(values)
        configuration = self._create_configuration(
            values, name=name,
            datastore=datastore, datastore_version=datastore_version)
        instance_id = self.context["instance"]["id"]
        self._attach_configuration(instance_id, configuration)
        self._detach_configuration(instance_id)

        self._delete_configuration(configuration)


@scenario.configure(name="TroveConfigurations.create_and_edit_configuration")
class CreateAndEditConfiguration(utils.TroveScenario):
    def run(self, values, datastore, datastore_version, name=None, **kwargs):
        """Create configuration and edit, do not cover the old one, ant then
        check the values.

        :param values: the value dict to create a trove configuration
        :param datastore: datastore of trove configuration to create
        :param datastore_version: datastore version of trove configuration to
               create
        :param name: name of configuration, if not given, generate a random one
        :param kwargs: update_values to update a configuration
        """
        create_values = json.dumps(values)
        if "update_values" in kwargs.keys() and kwargs["update_values"].keys():
            update_values = json.dumps(kwargs["update_values"])
        else:
            raise Exception("Can't update configuration: "
                            "update_values must be specify.")
        cfg = self._create_configuration(create_values,
                                         name=name,
                                         datastore=datastore,
                                         datastore_version=datastore_version)

        # edit configuration
        self._edit_configuration(cfg, update_values)
        edited_cfg = self._get_configuration(cfg)

        # check if correct
        if set(kwargs["update_values"].keys()) <= set(edited_cfg.values.keys()):
            for k in kwargs["update_values"].keys():
                if edited_cfg.values[k] == kwargs["update_values"][k]:
                    pass
                else:
                    raise Exception("Edit configuration failed, values not "
                                    "match, now the values are: %s"
                                    % edited_cfg.values)
        else:
            raise Exception("Edit configuration failed, key not match, "
                            "now the valuses are: %s"
                            % edited_cfg.values)
