#!/usr/bin/python
# Trove instances tasks for EayunStack 3.0.0
# Scenarios for Trove instance.

from rally.common import logging
from rally.plugins.openstack import scenario
from rally.task import utils as task_utils
import utils


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveInstances.list_instances")
class ListInstances(utils.TroveScenario):
    def run(self):
        """List all instances of tenants.
        Measure the "trove list" command performance.
        """
        self._list_instances()


@scenario.configure(name="TroveInstances.create_and_delete_instance")
class CreateAndDeleteInstance(utils.TroveScenario):
    def run(self, flavor, datastore, datastore_version,
            nics, volume, name=None, **kwargs):
        """Create instance and delete it.

        :param flavor: flavor to be used to create an instance
        :param name: name of instance, if not given, generate a random one
        :param datastore: datastore of trove instance to create
        :param datastore_version: datastore version of trove instance to create
        :param nics: the nics information to create an instance
        :param: volume: the size of volume to be created
        :param: kwargs: optional additional arguments for instance creation
        """
        instance = self._create_instance(
            flavor, datastore, datastore_version,
            nics, volume, name=name, **kwargs)

        self._delete_instance(instance)


@scenario.configure(name="TroveInstances.create_and_delete_replica_instance")
class CreateAndDeleteReplicaInstance(utils.TroveScenario):
    def run(self, flavor, datastore, datastore_version,
            nics, volume, name=None, **kwargs):
        """Create a replica of an existing instance,
        the existing instance will be created in context.

        :param flavor: flavor to be used to create an replica instance
        :param name: name of replica instance, if not given,
               generate a random one
        :param datastore: datastore of replica instance to create
        :param datastore_version: datastore version of replica instance
               to create
        :param nics: the nics information to create a replica instance
        :param volume: the size of volume to be created
        :param kwargs: optional additional arguments for replica instance
               creation
        """
        kwargs["replica_of"] = self.context["instance"]["id"]
        replica_instance = self._create_instance(flavor, datastore,
                                                 datastore_version,
                                                 nics, volume, name=name,
                                                 **kwargs)
        self._delete_instance(replica_instance)


@scenario.configure(name="TroveInstances.restart_and_get_instance")
class RestartAndGetInstance(utils.TroveScenario):
    def run(self):
        """Restart an instance and get the details of instance.

        The instance will be created in context.
        """
        instance = self.context["instance"]["id"]
        restarted_instance = self._restart_instance(instance)
        self._get_instance(restarted_instance)


@scenario.configure(name="TroveInstances.force_delete_building_instance")
class ForceDeleteBuildingInstance(utils.TroveScenario):
    def run(self, flavor, datastore, datastore_version,
            nics, volume, name=None, **kwargs):
        """When an instance is building, force delete it.

        :param flavor: flavor to be used to create an instance
        :param name: name of instance, if not given, generate a random one
        :param datastore: datastore of instance to create
        :param datastore_version: datastore version of instance to create
        :param nics: the nics information to create a instance
        :param: volume: the size of volume to be created
        :param: kwargs: optional additional arguments for instance creation
        """
        if name is not None:
            instance_name = name
        else:
            instance_name = self.generate_random_name()
        LOG.debug("Creating instnace with name %s" % instance_name)
        instance = self.clients("trove").instances.create(
            instance_name, flavor,
            datastore=datastore, datastore_version=datastore_version,
            nics=nics, volume=volume, **kwargs)
        self.sleep_between(1)
        instance = task_utils.wait_for_status(
            instance,
            ready_statuses=["BUILD"],
            update_resource=task_utils.get_from_manager(),
            timeout=30,
            check_interval=1
        )
        self._force_delete_instance(instance)


@scenario.configure(name="TroveInstances.create_replica_and_detach")
class CreateReplicaAndDetach(utils.TroveScenario):
    def run(self, flavor, datastore, datastore_version,
            nics, volume, name=None, **kwargs):
        """Create a replica instance and detach it.

        The source instance will be created in context.

        :param flavor: flavor to be used to create an instance
        :param name: name of instance, if not given, generate a random one
        :param datastore: datastore of instance to create
        :param datastore_version: datastore version of instance to create
        :param nics: the nics information to create a instance
        :param: volume: the size of volume to be created
        :param: kwargs: optional additional arguments for instance creation
        """
        src_instance = self.context["instance"]["id"]
        kwargs["replica_of"] = src_instance
        replica = self._create_instance(
            flavor, datastore, datastore_version,
            nics, volume, name=name, **kwargs)
        self._detach_replica(replica)
        self._delete_instance(replica)


@scenario.configure(name="TroveInstances.create_instance_from_backup")
class CreateInstanceFromBackup(utils.TroveScenario):
    def run(self, flavor, datastore, datastore_version,
            nics, volume, name=None, **kwargs):
        """Create an instance from backup.

        The backup  will be created in context.

        :param flavor: flavor to be used to create an instance
        :param name: name of instance, if not given, generate a random one
        :param datastore: datastore of instance to create
        :param datastore_version: datastore version of instance to create
        :param nics: the nics information to create a instance
        :param: volume: the size of volume to be created
        :param: kwargs: optional additional arguments for instance creation
        """
        kwargs["restorePoint"] = {"backupRef": self.context["backup"]["id"]}
        instance = self._create_instance(
            flavor, datastore, datastore_version,
            nics, volume, name=name, **kwargs)
        LOG.debug("Instance with name %s was created" % name)

        self._delete_instance(instance)
