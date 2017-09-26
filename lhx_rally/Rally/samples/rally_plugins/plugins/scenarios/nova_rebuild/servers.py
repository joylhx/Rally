#!/usr/bin/env python
# encoding: utf-8

from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.cinder import utils as cinder_utils
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
import time


"""Scenario for Nova rebuild servers."""

@scenario.configure(name="NovaServers.rebuild_shutoff_server")
class RebuildShutoffServer(nova_utils.NovaScenario, cinder_utils.CinderScenario):

    def run(self, from_image, to_image, flavor, force_delete=True, min_sleep=0, max_sleep=0, **kwargs):
        """Rebuild a server when it is shutoff."""
        server = self._boot_server(from_image, flavor, **kwargs)
        self._stop_server(server)
        self.sleep_between(min_sleep=0, max_sleep=0)

        self._rebuild_server(server, to_image)
        self.sleep_between(min_sleep, max_sleep)
        time.sleep(100)

        self._delete_server(server, force=force_delete)

@scenario.configure(name="NovaServers.rebuild_server_and_attached_volume")
class RebuildServerAndAttachedVolume(nova_utils.NovaScenario, cinder_utils.CinderBasic):

    def run(self, flavor, from_image, to_image, force_delete=True, volume_size=1, min_sleep=0, max_sleep=0, to_delete=True, create_volume_kwargs=None, **kwargs):
        """When server attached a volume, rebuild the server."""
        create_volume_kwargs = create_volume_kwargs or {}

        server = self._boot_server(from_image, flavor, **kwargs)
        volume = self.cinder.create_volume(volume_size, **create_volume_kwargs)

        attachment = self._attach_volume(server, volume)
        self.sleep_between(min_sleep, max_sleep)

        self._rebuild_server(server, to_image)
        if to_delete:
            self._detach_volume(server, volume, attachment)
            self.cinder.delete_volume(volume)
            self._delete_server(server, force=force_delete)


@scenario.configure(name="NovaServers.rebuild_server_and_attached_multiple_volumes")
class RebuildServerAndAttachedMultipleVolumes(nova_utils.NovaScenario, cinder_utils.CinderBasic):
    def run(self, from_image, to_image, flavor, min_sleep=0, max_sleep=0, force_delete=True,
            volume_size=2, volume_count=3, to_delete=True, create_volume_kwargs=None, **kwargs):
        """When server attached multiple volumes, rebuild the server."""
        create_volume_kwargs = create_volume_kwargs or {}
        server = self._boot_server(from_image, flavor, **kwargs)

        attachments = []
        for i in range(volume_count):
            volume = self.cinder.create_volume(volume_size, **create_volume_kwargs)
            attachments.append(self._attach_volume(server, volume))

        self._rebuild_server(server, to_image)
        self.sleep_between(min_sleep, max_sleep)

        if to_delete:
            self._delete_server(server, force=force_delete)
            time.sleep(150)
            self.cinder.delete_volume(volume)



@scenario.configure(name="NovaServers.rebuild_server_and_associated_floatingip")
class RebuildServerAndAssociatedFloatingip(nova_utils.NovaScenario, neutron_utils.NeutronScenario):

    def run(self, to_image,  min_sleep=0, max_sleep=0, force_delete=True):
        """Rebuild a server when it associated floatingip."""

        manager = self.clients("nova").servers
        server = manager.get(self.context['server']['id'])
        self._rebuild_server(server, to_image)

        self.sleep_between(min_sleep, max_sleep)
        #self._dissociate_floating_ip(server, address)
        self._delete_server(server, force=force_delete)

@scenario.configure(name="NovaServers.rebuild_server_and_live_migration")
class RebuildServerAndLiveMigration(nova_utils.NovaScenario, cinder_utils.CinderScenario):

    def run(self, from_image, to_image, flavor, block_migration=False, disk_over_commit=True, force_delete=True, min_sleep=0, max_sleep=0, **kwargs):
        """Rebuild a server then live migrate."""

        server = self._boot_server(from_image, flavor, **kwargs)
        self._rebuild_server(server, to_image)
        self.sleep_between(min_sleep, max_sleep)

        new_host = self._find_host_to_migrate(server)
        self._live_migrate(server, new_host, block_migration, disk_over_commit)

        self.sleep_between(min_sleep, max_sleep)
        self._delete_server(server, force=force_delete)


@scenario.configure(name="NovaServers.rebuild_server_and_migrate")
class RebuildServerAndMigrate(nova_utils.NovaScenario, cinder_utils.CinderScenario):
    def run(self, from_image, to_image, flavor, force_delete=True, min_sleep=0, max_sleep=0, **kwargs):
        """Rebuild a server then migrate."""

        server = self._boot_server(from_image, flavor, **kwargs)
        self._rebuild_server(server, to_image)

        self.sleep_between(min_sleep, max_sleep)

        self._migrate(server)
        confirm = kwargs.get("confirm", True)
        if confirm:
            self._resize_confirm(server, status="ACTIVE")
        else:
            self._resize_revert(server, status="ACTIVE")
        self._delete_server(server, force=force_delete)


