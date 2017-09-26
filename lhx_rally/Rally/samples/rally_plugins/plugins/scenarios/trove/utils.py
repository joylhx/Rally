#!/usr/bin/python

"""These are the all utils for Trove"""

from oslo_config import cfg

from rally.common import logging
from rally.plugins.openstack import scenario
from rally.task import atomic
from rally.task import utils

CONF = cfg.CONF
LOG = logging.getLogger(__file__)


class TroveScenario(scenario.OpenStackScenario):
    """Base class for Trove scenario with basic atomic actions."""

    @atomic.action_timer("trove.list_instances")
    def _list_instances(self):
        """Return user instances list."""
        LOG.debug("Listing instances...")
        return self.clients("trove").instances.list()

    @atomic.action_timer("trove.create_instance")
    def _create_instance(self, flavor, datastore, datastore_version,
                         nics, volume, name=None, **kwargs):
        """Create an instance."""
        if name:
            instance_name = name
        else:
            instance_name = self.generate_random_name()

        LOG.debug("Creating Instance with name %s" % instance_name)
        instance = self.clients("trove").instances.create(
            instance_name,
            flavor, datastore=datastore, datastore_version=datastore_version,
            nics=nics, volume=volume, **kwargs)
        self.sleep_between(10)
        instance = utils.wait_for_status(
            instance,
            ready_statuses=["ACTIVE"],
            update_resource=utils.get_from_manager(),
            timeout=300,
            check_interval=1
        )
        return instance

    @atomic.action_timer("trove.get_instance")
    def _get_instance(self, instance):
        """Return the given instance info."""
        if isinstance(instance, unicode):
            LOG.debug("Geting instance information: %s" % instance)
        else:
            LOG.debug("Geting instance information: [%s: %s]"
                      % (instance.name, instance.id))
        return self.clients("trove").instances.get(instance)

    def _delete_instance(self, instance):
        """Delete the given instance."""
        from rally.exceptions import GetResourceFailure
        if isinstance(instance, unicode):
            instance = self.clients("trove").instances.get(instance)
        else:
            pass
        try:
            LOG.debug("Deleting instance: [%s: %s]"
                      % (instance.name, instance.id))
            atomic_name = ("trove.delete_instance")
            with atomic.ActionTimer(self, atomic_name):
                instance.delete()
                utils.wait_for_status(
                    instance,
                    ready_statuses=["deleted"],
                    check_deletion=True,
                    update_resource=utils.get_from_manager(),
                    timeout=120,
                    check_interval=1
                )
        except GetResourceFailure as e:
            msg = ("Delete error, try again: %s" % e.message)
            LOG.warning(msg)
            from troveclient.exceptions import NotFound
            try:
                self.clients("trove").instances.get(instance)
            except NotFound:
                msg = ("Delete successfully.")
                LOG.debug(msg)
            except Exception as e:
                raise e

    @atomic.action_timer("trove.force_delete_instance")
    def _force_delete_instance(self, instance):
        """Force Delete an BUILD or ERROR status instance."""
        LOG.debug("Force deleting instance: %s" % instance)
        # TODO: check deleted.
        # atomic_name = ("trove.force_delete_instance")
        # with atomic.ActionTimer(self, atomic_name):
        instance.force_delete()
        # utils.wait_for_status(
        #     instance,
        #     ready_statuses=["deleted"],
        #     check_deletion=True,
        #     update_resource=utils.get_from_manager(),
        #     timeout=120,
        #     check_interval=1
        # )

    @atomic.action_timer("trove.restart_instance")
    def _restart_instance(self, instance):
        """Restart the given instance."""
        if isinstance(instance, unicode):
            instance = self.clients("trove").instances.get(instance)
        else:
            pass
        LOG.debug("Restart instance: [%s: %s]"
                  % (instance.name, instance.id))
        instance.restart()
        restarted_instance = utils.wait_for_status(
            instance,
            ready_statuses=["ACTIVE"],
            update_resource=utils.get_from_manager(),
            timeout=120,
            check_interval=1
        )
        return restarted_instance

    @atomic.action_timer("trove.detachh_replica")
    def _detach_replica(self, instance):
        """Detach replica instance itself."""
        if isinstance(instance, unicode):
            instance = self.clients("trove").instances.get(instance)
        else:
            pass
        LOG.debug("Detach replica: [%s: %s]" % (instance.name, instance.id))
        instance.detach_replica()
        detached_instance = utils.wait_for_status(
            instance,
            ready_statuses=["ACTIVE"],
            update_resource=utils.get_from_manager(),
            timeout=300,
            check_interval=1
        )
        return detached_instance

    @atomic.action_timer("trove.create_backup")
    def _create_backup(self, instance, name=None, **kwargs):
        """Create a backup for instance."""
        if isinstance(instance, unicode):
            LOG.debug("Create backup for instance: %s" % instance)
        else:
            LOG.debug("Create backup for instance: [%s: %s]"
                      % (instance.name, instance.id))
        if name:
            backup_name = name
        else:
            backup_name = self.generate_random_name()
        LOG.debug("Backup with name=%(name)s instance=%(instance)s "
                  "kwargs=%(kwargs)s will be created."
                  % {"name": backup_name,
                     "instance": instance,
                     "kwargs": kwargs})
        backup = self.clients("trove").backups.create(backup_name,
                                                      instance, **kwargs)
        backup = utils.wait_for_status(
            backup,
            ready_statuses=["COMPLETED"],
            update_resource=utils.get_from_manager(),
            timeout=600,
            check_interval=5
        )
        return backup

    @atomic.action_timer("trove.delete_backup")
    def _delete_backup(self, backup):
        """Delete the given backup."""
        if isinstance(backup, unicode):
            backup = self.clients("trove").backups.get(backup)
        else:
            pass
        LOG.debug("Deleting backup: [%s: %s]" % (backup.name, backup.id))
        self.clients("trove").backups.delete(backup)
        utils.wait_for_status(
            backup,
            ready_statuses=["deleted"],
            check_deletion=True,
            update_resource=utils.get_from_manager(),
            timeout=120,
            check_interval=1
        )

    @atomic.action_timer("trove.list_backups")
    def _list_backups(self):
        """List all backups for tenant."""
        LOG.debug("Listing backups...")
        return self.clients("trove").backups.list()

    @atomic.action_timer("trove.get_backup")
    def _get_backup(self, backup):
        """Get the given backup."""
        LOG.debug("Geting backup...")
        return self.clients("trove").backups.get(backup)

    @atomic.action_timer("trove.list_databases")
    def _list_databases(self, instance):
        """List all databases for instance."""
        LOG.debug("Listing databases...")
        return self.clients("trove").databases.list(instance)

    @atomic.action_timer("trove.create_database")
    def _create_database(self, instance, databases):
        """Create database for instance."""
        if isinstance(instance, unicode):
            LOG.debug("Create database for instance: %s" % instance)
        else:
            LOG.debug("Create database for instance: [%s: %s]"
                      % (instance.name, instance.id))
        return self.clients("trove").databases.create(instance, databases)

    @atomic.action_timer("trove.delete_database")
    def _delete_database(self, instance, dbname):
        """Delete database."""
        LOG.debug("Deleting database %s of instance %s" % (dbname, instance))
        self.clients("trove").databases.delete(instance, dbname)

    @atomic.action_timer("trove.list_configurations")
    def _list_configurations(self):
        """List configurations."""
        LOG.debug("List configurations...")
        return self.clients("trove").configurations.list()

    @atomic.action_timer("trove.create_configuration")
    def _create_configuration(self, values, name=None,
                              datastore=None, datastore_version=None):
        """Create configuration."""
        LOG.debug("Creating configuration %s" % name)
        if name:
            name = name
        else:
            name = "cfg_%s" % self.generate_random_name()
        return self.clients("trove").configurations.create(
            name, values,
            datastore=datastore, datastore_version=datastore_version)

    @atomic.action_timer("trove.delete_configuration")
    def _delete_configuration(self, configuration):
        """Delete the given configuration."""
        if isinstance(configuration, unicode):
            LOG.debug("delete configuration: %s" % configuration)
        else:
            LOG.debug("Delete configuration: [%s: %s]"
                      % (configuration.name, configuration.id))
        self.clients("trove").configurations.delete(configuration)

    @atomic.action_timer("trove.edit_configuration")
    def _edit_configuration(self, configuration, values):
        """Edit the given configuration."""
        if isinstance(configuration, unicode):
            LOG.debug("Edit configuration %s with new values: %s"
                      % (configuration, values))
        else:
            LOG.debug("Edit configuration [%s: %s] with new values: %s"
                      % (configuration.name, configuration.id, values))
        return self.clients("trove").configurations.edit(configuration, values)

    def _get_configuration(self, configuration):
        """Get the details of the given configuraiton."""
        if isinstance(configuration, unicode):
            LOG.debug("Get the details of configuration %s" % configuration)
        else:
            LOG.debug("Get the details of configuration [%s: %s]"
                      % (configuration.name, configuration.id))
        return self.clients("trove").configurations.get(configuration)

    @atomic.action_timer("trove.attach_configuration")
    def _attach_configuration(self, instance, configuration):
        """Edit instance to attach configuration."""
        # TODO: check if attached
        LOG.debug("Attach configuration %s to instance %s"
                  % (configuration, instance))
        self.clients("trove").instances.edit(
            instance, configuration=configuration)

    @atomic.action_timer("trove.detach_configuration")
    def _detach_configuration(self, instance):
        """Edit instance to detach configuration."""
        # TODO: check if detached
        LOG.debug("Detach configuration from %s"
                  % instance)
        self.clients("trove").instances.edit(
            instance, remove_configuration=True)

    @atomic.action_timer("trove.list_users")
    def _list_users(self, instance):
        """List users for instance."""
        LOG.debug("List users...")
        return self.clients("trove").users.list(instance)

    @atomic.action_timer("trove.create_user")
    def _create_user(self, instance, users):
        """Create user for instance."""
        if isinstance(instance, unicode):
            LOG.debug("Create user %s for instance %s"
                      % (users[0]["name"], instance))
        else:
            LOG.debug("Create user %s of instance [%s: %s]"
                      % (users[0]["name"], instance.name, instance.id))
        return self.clients("trove").users.create(instance, users)

    @atomic.action_timer("trove.delete_user")
    def _delete_user(self, instance, username, hostname=None):
        """Delete the given user."""
        if isinstance(instance, unicode):
            LOG.debug("Delete user %s for instance %s"
                      % (username, instance))
        else:
            LOG.debug("Delete user %s of instance [%s: %s]"
                      % (username, instance.name, instance.id))
        self.clients("trove").users.delete(instance, username,
                                           hostname=hostname)

    @atomic.action_timer("trove.list_logs")
    def _list_logs(self, instance):
        """List the logs of instance."""
        if isinstance(instance, unicode):
            LOG.debug("list logs of instance %s" % instance)
        else:
            LOG.debug("List logs of instance [%s: %s]"
                      % (instance.name, instance.id))
        return self.clients("trove").instances.log_list(instance)

    @atomic.action_timer("trove.show_log")
    def _show_log(self, instance, log_name):
        """Show the log of given instance with log name."""
        if isinstance(instance, unicode):
            LOG.debug("Show the %s log instance %s"
                      % (log_name, instance))
        else:
            LOG.debug("Show the %s log of instance [%s: %s]"
                      % (log_name, instance.name, instance.id))
        return self.clients("trove").instances.log_show(instance, log_name)

    @atomic.action_timer("trove.enable_log")
    def _enable_log(self, instance, log_name):
        """Enable the given log of instance with log name."""
        if isinstance(instance, unicode):
            LOG.debug("Eable the %s log instance %s"
                      % (log_name, instance))
        else:
            LOG.debug("Eable the %s log of instance [%s: %s]"
                      % (log_name, instance.name, instance.id))
        return self.clients("trove").instances.log_enable(instance, log_name)

    @atomic.action_timer("trove.disable_log")
    def _disable_log(self, instance, log_name, discard=None):
        """Disable the given log of instance with log name."""
        if isinstance(instance, unicode):
            LOG.debug("Disable the %s log instance %s"
                      % (log_name, instance))
        else:
            LOG.debug("Disable the %s log of instance [%s: %s]"
                      % (log_name, instance.name, instance.id))
        return self.clients("trove").instances.log_disable(instance,
                                                           log_name,
                                                           discard=discard)

    @atomic.action_timer("trove.publish_log")
    def _publish_log(self, instance, log_name, disable=None, discard=None):
        """Publish the given log of instance with log name."""
        if isinstance(instance, unicode):
            LOG.debug("Publish the %s log instance %s"
                      % (log_name, instance))
        else:
            LOG.debug("Publish the %s log of instance [%s: %s]"
                      % (log_name, instance.name, instance.id))
        return self.clients("trove").instances.log_publish(instance,
                                                           log_name,
                                                           disable=disable,
                                                           discard=discard)

    @atomic.action_timer("trove.discard_log")
    def _discard_log(self, instance, log_name):
        """Discard the given log of instance with log name."""
        if isinstance(instance, unicode):
            LOG.debug("Discard the %s log instance %s"
                      % (log_name, instance))
        else:
            LOG.debug("Discard the %s log of instance [%s: %s]"
                      % (log_name, instance.name, instance.id))
        return self.clients("trove").instances.log_discard(instance,
                                                           log_name)
