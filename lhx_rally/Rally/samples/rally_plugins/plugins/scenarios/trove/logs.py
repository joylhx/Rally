#!/bin/python

from rally.common import logging
from rally.plugins.openstack import scenario
from plugins.scenarios.trove import utils


"""Scenarios for Trove logs."""


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveLogs.list_logs")
class ListLogs(utils.TroveScenario):
    def run(self):
        """Get a list of all guest logs."""
        self._list_logs(self.context["instance"]["id"])


@scenario.configure(name="TroveLogs.show_log")
class ShowLog(utils.TroveScenario):
    def run(self, log_name):
        """Show details of a given log, the instance was created in
        context.

        :param log_name: the name of log to show
        """
        log = self._show_log(self.context["instance"]["id"], log_name)
        LOG.debug("Showoing log successfully, the log's informations are: %s"
                  % log._info)


@scenario.configure(name="TroveLogs.enable_and_disable_log")
class EnableAndDisableLog(utils.TroveScenario):
    def run(self, log_name):
        """Enable a log of instance, check if enabled successfully, and then
        disable it, check again. The instance was created in context.

        :param log_name: the name of log to enable and disable
        """
        instance_id = self.context["instance"]["id"]
        enabled_log = self._enable_log(instance_id, log_name)
        # check if enabled:
        if enabled_log.status != "Ready":
            raise Exception("Log is not enabled, the status is: %s"
                            % enabled_log.status)

        disabled_log = self._disable_log(instance_id, log_name)
        # check if disabled:
        if disabled_log.status != "Disabled":
            raise Exception("Log is not disabled, the status is: %s"
                            % disabled_log.status)


@scenario.configure(name="TroveLogs.publish_and_discard_log")
class PublishAndDiscardLog(utils.TroveScenario):
    def run(self, log_name, **kwargs):
        """Publish the given log and check if published, and then discard it
        and check if discarded.

        :param log_name: the name of log to publish and discard
        :param kwargs: publish_args to specify
        """
        instance_id = self.context["instance"]["id"]
        if kwargs:
            disable = kwargs["publish_args"]["disable"] \
                if "disable" in kwargs.keys() else None
            discard = kwargs["publish_args"]["discard"] \
                if "discard" in kwargs.keys() else None
        self._publish_log(instance_id, log_name,
                          disable=disable, discard=discard)
        published_log = self._show_log(instance_id, log_name)
        # check if published:
        if discard and published_log.container == "None":
            raise Exception("Publish failed.")

        discarded_log = self._discard_log(instance_id, log_name)
        # check if discarded:
        if discarded_log.container != "None":
            LOG.warning("Container is: %s" % discarded_log.container)
            raise Exception("Discard failed.")


@scenario.configure(name="TroveLogs.publish_and_disable_log")
class PublishAndDisableLog(utils.TroveScenario):
    def run(self, log_name, **kwargs):
        """Publish the given log and check if published, and then disable it
        and check if disabled.

        :param log_name: the name of log to publish and discard
        :param kwargs: publish_args and disable_args to specify
        """
        instance_id = self.context["instance"]["id"]
        disable = None
        publish_discard = None
        disable_discard = None
        if "publish_args" in kwargs.keys():
            if ("discard" in kwargs["publish_args"].keys()
                    and kwargs["publish_args"]["discard"] is True):
                raise Exception("Instance has no logs to discard, "
                                "please set discard to false.")
            elif "discard" in kwargs["publish_args"].keys():
                publish_discard = kwargs["publish_args"]["discard"]
        if "disable_args" in kwargs.keys():
            if "discard" in kwargs["disable_args"].keys():
                disable_discard = kwargs["disable_args"]["discard"]

        self._publish_log(instance_id, log_name,
                          disable=disable, discard=publish_discard)
        published_log = self._show_log(instance_id, log_name)
        # check if published:
        if publish_discard and published_log.container == "None":
            raise Exception("Publish failed.")

        disabled_log = self._disable_log(instance_id,
                                         log_name,
                                         discard=disable_discard)
        # check:
        if disable_discard and disabled_log.container != "None":
            LOG.warning("Container is: %s" % disabled_log.container)
            raise Exception("Log was not discarded, container is: %s"
                            % disabled_log.container)
        if disabled_log.status not in ["Disabled", "Partial"]:
            LOG.warning("Log disable failed.")
            raise Exception("Log disable failed, status is: %s"
                            % disabled_log.status)
