#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.05.16
#
# Changelog:
#
# 2019.05.16 - SBerendsen - start
#
# ------------------------------------------------------------------------------
#
# Copyright 2019, Sven Berendsen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ------------------------------------------------------------------------------
#
# ToDo:
#   - Make daemons able to have wants on the very first timestep
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# general
import datetime
import os

# internal
from . import agent
from . import room
from .util import base_parts
from .util import central_data_store
from .util import settings
from .util import string_output
from huum_io import consumer_unit as io_consumer_unit

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class ConsumerUnit(base_parts.BaseParts
                   ):  # class for each consumer unit / household

    _TARGETABLE_CHILD_OBJECTS = [
        '$room', '$agent', '$event', '$storage', '$passedtime', '$replace',
        '$replace_all_agents'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name: str):
        base_parts.BaseParts.__init__(self, name, 'cu')

        self.rooms = []
        self.agents = []
        self.unique_appliances = {
        }  # dictionary with appliance classes. The values: lists with appliances of class X
        self.appliance_classes = [
        ]  # list of appliance classes present in this consumer unit.
        self.__string_wants = ''

        self.sw_wants = None  # writing deduplicator: daemon: wants
        self.sw_lifecycle = None  # writing deduplicator: daemon: lifecycle
        self.sw_blocking = None  # writing deduplicator: daemon: blocking controls
        self.sw_appliances = None  # writing deduplicator: appliance info

    def load(self, cu_data: io_consumer_unit.IOConsumerUnit,
             cds: central_data_store.CentralDataStore):
        """
        Loads the model data from a IO-model object.
        """
        for item in cu_data.rooms:
            obj = room.Room(item.name)
            obj.load(item, cds)
            self.add_room(obj)

        for item in cu_data.agents:
            obj = agent.Agent.loadFromFileData(item, cds)
            self.add_agent(obj)

        self.load_common(cu_data, cds.get_model_start_time(),
                         cds.get_compute_interval_sec())

    def add_room(self, room: room.Room):
        self.rooms.append(room)

    def add_agent(self, agent: agent.Agent):
        self.agents.append(agent)

    def get_agents(self):
        return self.agents

    def get_num_agents_in_consumer_unit(self):
        return len(self.agents)

    def initialize(self, prefix: str, parent_obj,
                   cds: central_data_store.CentralDataStore,
                   cfg: settings.Config):
        """
        Setups the initial 'status' for everything

        prefix    - prefix of the output directory
        parent_id - id of the parent node in the dependency tree
        """

        # data structure housekeeping
        self.register_tree_node(parent_obj)
        self.base_register(prefix + '/cu_' + self.get_node_name(), cds, cfg)

        # Directory setups -----------------------------------------------------
        consumer_unit_prefix = prefix + '/' + self.get_node_name() + '/'
        if not (cfg.headless
                or cfg.logging_type == 'none' or cfg.log_as_single):
            os.makedirs(consumer_unit_prefix, exist_ok=True)

        # Appliances -----------------------------------------------------------

        # setup appliances info
        self.sw_appliances = string_output.StringOutput(
            consumer_unit_prefix + self.get_node_name() +
            '_appliances_control.csv', cfg.log_appliances)

        if not (self.sw_appliances.get_file() is None):
            self.sw_appliances.get_file().write('Time;')

        for chamber in self.rooms:
            chamber.initialize(self.sw_appliances.get_file(),
                               consumer_unit_prefix + self.get_node_name(),
                               self, cds, cfg)

            # get and integrate appliances & appliances-classes
            for app in chamber.get_appliance_list():
                if (app[0] in self.unique_appliances):
                    self.unique_appliances[
                        app[0]] = self.unique_appliances[app[0]] + [app[1]]
                else:
                    self.unique_appliances[app[0]] = [app[1]]
            self.appliance_classes = [*self.unique_appliances.keys()]

        if not (self.sw_appliances.get_file() is None):
            self.sw_appliances.get_file().write('\n')

        # Daemons --------------------------------------------------------------

        # setup daemon info
        self.sw_wants = string_output.StringOutput(
            consumer_unit_prefix + self.get_node_name() + '_persons_wants.csv',
            cfg.log_wants)

        self.sw_lifecycle = string_output.StringOutput(
            consumer_unit_prefix + self.get_node_name() +
            '_persons_lifecycle.csv', cfg.log_lifecycle)

        self.sw_blocking = string_output.StringOutput(
            consumer_unit_prefix + self.get_node_name() +
            '_persons_blocking.csv', cfg.log_blocking)

        if not (cfg.headless or cfg.logging_type == 'none'):
            if (cfg.log_lifecycle):
                self.sw_lifecycle.get_file().write('Time;')
            if (cfg.log_wants):
                self.sw_wants.get_file().write('Time;')
            if (cfg.log_blocking):
                self.sw_blocking.get_file().write('Time;')

        # do daemon init
        for daemon in self.agents:
            daemon.initialize(self.sw_lifecycle.get_file(),
                              self.sw_wants.get_file(),
                              self.sw_blocking.get_file(),
                              consumer_unit_prefix,
                              self.unique_appliances.keys(), self, cds, cfg)

    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()

        for daemon in self.agents:
            daemon.connect_uids()

        for chamber in self.rooms:
            chamber.connect_uids()

    def update_events(self, current_tp: datetime.datetime,
                      func_add_event_queue_item):
        self.check_event_starts('Probability',
                                func_add_event_queue_item,
                                current_tp=current_tp)
        for chamber in self.rooms:
            chamber.update_events(current_tp, func_add_event_queue_item)
        for daemon in self.agents:
            daemon.update_events(current_tp, func_add_event_queue_item)

    def update_storages(self, current_tp: datetime.datetime):
        self.update_storage_values(current_tp)
        for chamber in self.rooms:
            chamber.update_storages(current_tp)
        for daemon in self.agents:
            daemon.update_storages(current_tp)

    def update(self, cds: central_data_store.CentralDataStore,
               cfg: settings.Config, func_add_event_queue_item):
        """
        Updates the model for the timepoint
        """

        # updates for the room(s)
        for chamber in self.rooms:
            chamber.update(cds.get_current_model_time(),
                           cds.get_last_model_time())

        # Get what the deamons want --------------------------------------------
        self.__string_wants = ''
        for daemon in self.agents:
            impulses = daemon.update(self.appliance_classes, cds,
                                     func_add_event_queue_item)
            # print('\n', cds.get_current_model_time(), impulses)

            # checking for appliance usage
            impulse = None
            if impulses is not None:
                if (impulses.size() > 0):
                    # print('\nImpulses > 0')

                    for i in range(0, impulses.size()):
                        app = self.get_appliance(impulses.get_at_pos(i),
                                                 cds.get_current_model_time())

                        # print('   ', impulses.get_at_pos(i), busy)

                        if (app is not None):
                            impulse = impulses.get_at_pos(i)
                            daemon.set_busy_until(
                                app.use_appliance(daemon,
                                                  cds.get_current_model_time(),
                                                  func_add_event_queue_item),
                                impulse)
                            break

            # for write
            if not (cfg.headless or cfg.logging_type == 'none'
                    or not cfg.log_wants):
                if (impulse is not None):
                    self.__string_wants += impulse + ';'
                else:
                    self.__string_wants += 'None;'

    def record_status(self, cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):

        # rooms
        for chamber in self.rooms:
            chamber.record_status(cds, cfg)

        # daemons
        if not (cfg.headless or cfg.logging_type == 'none'):

            if (cfg.log_lifecycle):
                string_status = ''
            if (cfg.log_blocking):
                string_blocking = ''

            for daemon in self.agents:
                daemon.record_status(cds, cfg)

                # extra daemon info
                if (cfg.log_lifecycle):
                    string_status = daemon.write_status(string_status)
                if (cfg.log_blocking):
                    string_blocking = daemon.write_blocking(string_blocking)

            # write daemon status ----------------------------------------------

            # no checks necessary as if no output = goes directly to empty function
            if (cfg.log_lifecycle):
                self.sw_lifecycle.write(string_status,
                                        cds.get_current_model_time(),
                                        cds.get_last_model_time())
            self.sw_wants.write(self.__string_wants,
                                cds.get_current_model_time(),
                                cds.get_last_model_time())
            if (cfg.log_blocking):
                self.sw_blocking.write(string_blocking,
                                       cds.get_current_model_time(),
                                       cds.get_last_model_time())

            # Deal with storages, etc ------------------------------------------
            self.base_log(cds.get_current_model_time(),
                          cds.get_last_model_time())

    def close(self, current_tp: datetime.datetime):
        for daemon in self.agents:
            daemon.close(current_tp)

        for chamber in self.rooms:
            chamber.close(current_tp)

        self.sw_wants.close(current_tp)
        self.sw_lifecycle.close(current_tp)
        self.sw_blocking.close(current_tp)
        self.sw_appliances.close(current_tp)
        self.close_storages(current_tp)

    def get_appliance(self, app_name: str, current_time: datetime.datetime):
        """
        Gets the appliance for the given name.

        Returns:

        appliance - appliance object requested. Returns 'None' if appliance not found.
        """

        if (app_name in self.unique_appliances.keys()):
            for app in self.unique_appliances[app_name]:
                if not app.is_used(current_time):
                    return app

        return None

    def _get_child_object(self, parts):
        """
        Overriden part of the base_connection method.
        """
        # print('gco:', type(self), parts)
        id_part = parts[0].split('_')
        if (id_part[0] in self._TARGETABLE_CHILD_OBJECTS):

            # check for base-part objects --------------------------------------
            if (self._is_base_part_element(id_part[0])):
                return self._get_base_part_node_object(parts)

            # check for objects ------------------------------------------------
            if (id_part[0] == "$room"):
                for chamber in self.rooms:
                    if (chamber.get_node_id() == parts[0]):
                        return chamber._get_node_object(parts)

                # catch
                print('\nError: consumer_unit._get_child_object:')
                print(f'Room object with {parts[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                print('\nAttached rooms:')
                for chamber in self.rooms:
                    print(f'   {chamber.get_node_id()}')
                exit(255)

            # check for actions ------------------------------------------------
            elif (parts[0][0:9] == '$replace_'):
                if (parts[0][9:] == 'all_agents'):
                    return [self.get_agents]

                else:
                    print('\nError: consumer_unit._get_child_object:')
                    print('Unrecognised replace target: #' + parts[0][9:] +
                          '#')
                    print('Expression:                  #' + parts[0] + '#')
                    exit(255)

            else:
                print('\nError: consumer_unit._get_child_object:')
                print('Not yet implemented _TARGETABLE_CHILD_OBJECTS:',
                      id_part)
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                exit(255)

        else:
            return None

    def return_results(self):
        results = []
        for item in self.rooms:
            results.extend(item.return_results())

        return results

    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        f.write("\n\n" + "  " * level + "- Consumer Unit:")
        f.write("\n" + "  " * level + f"  Name: {self.get_node_name()}")

        f.write("\n\n" + "   " * level + "Rooms:")
        for chamber in self.rooms:
            chamber.output_overview(f, level + 2)

        f.write("\n\n" + "   " * level + "Agents:")
        for daemon in self.agents:
            daemon.output_overview(f, level + 2)

        f.write("\n\n" + "  " * level +
                f"  NumUniqueAppliances:   {len(self.unique_appliances)}")
        f.write("\n" + "  " * level +
                f"  UniqueAppliances:      {self.unique_appliances}")
        self.output_overview_base_parts(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
