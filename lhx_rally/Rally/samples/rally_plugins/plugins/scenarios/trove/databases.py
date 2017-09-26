#!/bin/python
# Trove tasks for EayunStack 3.0.0
# Scenarios for Trove databases

from rally.common import logging
from rally.plugins.openstack import scenario
from plugins.scenarios.trove import utils


LOG = logging.getLogger(__name__)


@scenario.configure(name="TroveDatabases.list_databases")
class ListDatabases(utils.TroveScenario):
    def run(self):
        """List databases of the given instance, while the instance was
        created in context.

        Measure the "trove database-list" commands performance.
        """
        self._list_databases(self.context["instance"]["id"])

@scenario.configure(name="TroveDatabases.create_and_delete_database")
class CreateAndDeleteDatabase(utils.TroveScenario):
    def run(self, databases):
        """Create new databases within the specified instance, while the
        instance was created in context, and then delete the database.

        :param databases: the databases to create, specified the name for
               databases, if not given, generate a random one to test.
        """
        # TODO: multiple databases ?
        if "name" not in databases[0].keys():
            databases[0]["name"] = self.generate_random_name()
        self._create_database(self.context["instance"]["id"],
                              databases)
        self._delete_database(self.context["instance"]["id"],
                              databases[0]["name"])
