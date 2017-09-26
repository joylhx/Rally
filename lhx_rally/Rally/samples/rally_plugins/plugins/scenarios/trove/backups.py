#!/usr/bin/python
# Trove Scenarios for EayunStack 3.0.0
# Scenarios for Trove backups

from rally.common import logging
from rally.plugins.openstack import scenario
from plugins.scenarios.trove import utils


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveBackups.list_backups")
class ListBackups(utils.TroveScenario):
    def run(self):
        """Get a list for all backups.
        Measure the "trove backup-list" command performance.
        """
        self._list_backups()


@scenario.configure(name="TroveBackups.create_and_delete_backup")
class CreateAndDeleteBackup(utils.TroveScenario):
    def run(self, name=None, **kwargs):
        """Create a backup of the instance, while the instance was
        created in context. And then delete the backkup.

        :param name: the name of backup to create
        :param kwargs: optional additional arguments for backup creation
        """
        backup = self._create_backup(self.context["instance"]["id"],
                                     name=name, **kwargs)

        self._delete_backup(backup)


@scenario.configure(name="TroveBackups.create_and_show_backup")
class CreateAndShowBackup(utils.TroveScenario):
    def run(self, name=None, **kwargs):
        """Create a backup of the instance, while the instance was
        created in context. And then get the details for the backkup.

        :param name: the name of backup to create
        :param kwargs: optional additional arguments for backup creation
        """
        backup = self._create_backup(self.context["instance"]["id"],
                                     name=name, **kwargs)
        self._get_backup(backup)
        self._delete_backup(backup)


@scenario.configure(name="TroveBackups.create_incremental_backup")
class CreateIncrementalBackup(utils.TroveScenario):
    def run(self, name=None, **kwargs):
        """Create an incremental backup, while the parent backup was
        created  in context.

        :param name: the name of backup to create
        :param kwargs: optional additional arguments for backup creation
        """
        instance_id = self.context["instance"]["id"]
        if "incremental" in kwargs.keys():
            if kwargs["incremental"] is not True:
                raise Exception("'incremental' must set to True.")
            else:
                pass
        else:
            kwargs["incremental"] = True
        backup = self._create_backup(instance_id,
                                     name=name, **kwargs)
        self._delete_backup(backup)


@scenario.configure(name="TroveBackups.create_incremental_backup"
                         "_and_delete_parent")
class CreateIncrementalBackupAndDeleteParent(utils.TroveScenario):
    def run(self, name=None, **kwargs):
        """Create a backup for instance as parent and create an incremental
        backup from the parent, and then delete the parent backup, check if
        children backups are delete with it.

        :param name: the name of backup to create
        :param kwargs: optional additional arguments for backup creation
        """
        instance_id = self.context["instance"]["id"]
        if "child_backups_counts" not in kwargs.keys():
            child_counts = 1
        else:
            child_counts = kwargs["child_backups_counts"]
            del kwargs["child_backups_counts"]
        if "incremental" in kwargs.keys():
            if kwargs["incremental"] is not True:
                raise Exception("'incremental' must set to True.")
            else:
                parent_bck = self._create_backup(instance_id,
                                                 name=name, **kwargs)
        else:
            kwargs["incremental"] = True
            parent_bck = self._create_backup(instance_id,
                                             name=name, **kwargs)
        child_bcks = []
        for i in range(0, child_counts):
            child_bcks.append(self._create_backup(instance_id,
                                                  name=name, **kwargs))
        self._delete_backup(parent_bck)
        for child_bck in child_bcks:
            try:
                from troveclient.exceptions import NotFound
                self._get_backup(child_bck)
                raise Exception("Child backup %s is not deleted" % child_bck)
            except NotFound:
                msg = ("Child backup %s is deleted, check OK" % child_bck)
                LOG.debug(msg)


@scenario.configure(name="TroveBackups.create_incremental_backup_and_delete")
class CreateIncrementalBackupAndDelete(utils.TroveScenario):
    def run(self, name=None, **kwargs):
        """Create a backup for instance as parent and create an incremental
        backup from the parent, delete the children backups first, and then
        delete the parent backup.

        :param name: the name of backup to create
        :param kwargs: optional additional arguments for backup creation
        """
        instance_id = self.context["instance"]["id"]
        if "child_backups_counts" not in kwargs.keys():
            child_counts = 1
        instance_id = self.context["instance"]["id"]
        if "incremental" in kwargs.keys():
            if kwargs["incremental"] is not True:
                raise Exception("'incremental' must set to True.")
            else:
                parent_bck = self._create_backup(instance_id,
                                                 name=name, **kwargs)
        else:
            kwargs["incremental"] = True
            parent_bck = self._create_backup(instance_id,
                                             name=name, **kwargs)
        child_bcks = []
        for i in range(0, child_counts):
            child_bcks.append(self._create_backup(instance_id,
                                                  name=name, **kwargs))
        for child_bck in child_bcks:
            self._delete_backup(child_bck)
            LOG.debug("Child backup [%s: %s] is deleted"
                      % (child_bck.name, child_bck.id))
        self._delete_backup(parent_bck)
        LOG.debug("Parent backup [%s: %s] is deleted"
                  % (parent_bck.name, parent_bck.id))
