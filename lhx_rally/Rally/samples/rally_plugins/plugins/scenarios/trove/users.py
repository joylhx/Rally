#!/bin/python

from rally.common import logging
from rally.plugins.openstack import scenario
from plugins.scenarios.trove import utils


"""Scenarios for Trove users."""


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveUsers.list_users")
class ListUsers(utils.TroveScenario):
    def run(self):
        """Get a list of all Users from the instance's Database.
        The instance was created in context.
        """
        self._list_users(self.context["instance"]["id"])


@scenario.configure(name="TroveUsers.create_and_delete_user")
class CreateAndDeleteUser(utils.TroveScenario):
    def run(self, users):
        """Create users for trove instance, and then delete the user.
        The instance was created in context.

        :param users: a list of users to create. "name", "password",
               "database" can be specify, if not, generate a random one.
        """
        if "name" in users[0].keys():
            if users[0]["name"] is None:
                LOG.warning("'name' didn't specify, generate "
                            "random name to run")
                users[0]["name"] = self.generate_random_name()
            elif users[0]["password"] is None:
                LOG.warning("'password didn't specify, generate "
                            "random password to run")
                users[0]["password"] = self.generate_random_name()
        else:
            LOG.warning("users didn't specify, generate random name "
                        "and password to run")
            users[0]["name"] = self.generate_random_name()
            users[0]["passowrd"] = self.generate_random_name()
        self._create_user(self.context["instance"]["id"], users)
        self._delete_user(self.context["instance"]["id"], users[0]["name"])
