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
# Holds the controls for each room.
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# General
import datetime

# Internal
from . import appliance
from .util import base_parts
from .util import central_data_store
from .util import settings
from huum_io import room as io_room


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Room(base_parts.BaseParts):  # class for each consumer unit / household

    _TARGETABLE_CHILD_OBJECTS = [
        '$room', '$appliance', '$event', '$storage', '$passedtime'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name: str):
        super().__init__(name, 'room')

        self.appliances = []


    def load(self, room_data: io_room.IORoom,
             data_store: central_data_store.CentralDataStore):
        """
        Loads the room data from a IO-model object.
        """
        for item in room_data.appliances:
            obj = appliance.Appliance(item.name,
                                      item.appliance_class,
                                      item.block_length,
                                      no_external_block=item.block_user)
            obj.load(item, data_store)
            self.add_appliance(obj)

        # load common stuff
        self.load_common(room_data, data_store.get_model_start_time(),
                         data_store.get_compute_interval_sec())


    def initialize(self, file: str, directory: str, parent_obj,
                   cds: central_data_store.CentralDataStore,
                   cfg: settings.Config):

        # data structure housekeeping
        self.register_tree_node(parent_obj)
        self.base_register(directory + '/room_' + self.get_node_name(), cds,
                           cfg)

        # output preperations
        for device in self.appliances:
            if not (file is None):
                file.write(device.get_node_name() + '_blocked_until;' +
                           device.get_node_name() + '_blocked_by;')
            device.initialize(directory, self, cds, cfg)


    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()

        for device in self.appliances:
            device.connect_uids()


    def update_events(self, current_tp: datetime.datetime,
                      func_add_event_queue_item):
        self.check_event_starts('Probability',
                                func_add_event_queue_item,
                                current_tp=current_tp)
        for device in self.appliances:
            device.update_events(current_tp, func_add_event_queue_item)


    def update_storages(self, current_tp: datetime.datetime):
        self.update_storage_values(current_tp)
        for device in self.appliances:
            device.update_storages(current_tp)


    def update(self, current_tp: datetime.datetime,
               last_tp: datetime.datetime):
        for device in self.appliances:
            device.update(current_tp, last_tp)


    def record_status(self, cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):

        for device in self.appliances:
            device.record_status(cds, cfg)

        self.base_log(cds.get_current_model_time(), cds.get_last_model_time())


    def close(self, current_tp: datetime.datetime):
        for device in self.appliances:
            device.close(current_tp)

        self.close_storages(current_tp)


    def add_appliance(self, appliance: appliance.Appliance):
        self.appliances.append(appliance)


    def get_appliance_list(self):
        listing = []
        for device in self.appliances:
            listing += [[device.get_class_name(), device]]

        return listing


    def get_appliance(self, name: str):
        """
        Gets the appliance with the given name.

        Returns:

        app - appliance object
        """
        app = None
        for item in self.appliances:
            if (name == item.get_node_name()):
                return item

        return app


    def _get_child_object(self, parts):
        """
        Overriden part of the base_connection method.
        """
        # print('gco:', type(self), parts)
        # check for objects
        id_part = parts[0].split('_')
        if (id_part[0] in self._TARGETABLE_CHILD_OBJECTS):
            if (id_part[0] == "$appliance"):
                for device in self.appliances:
                    if(device.get_node_id() == parts[0]):
                        return device._get_node_object(parts)

                # catch
                print('\nError: room._get_child_object:')
                print(f'Appliance object with {parts[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                print('Attached appliances:')
                for device in self.appliances:
                    print(device.get_node_id())
                exit(255)

            else:
                print('\nError: room._get_child_object:')
                print('Not yet implemented _TARGETABLE_CHILD_OBJECTS:', id_part)
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                exit(255)

            return None


    def return_results(self):
        results = []
        for item in self.appliances:
            results.append(item.return_results())

        return results


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        f.write("\n\n" + "  " * level + "- Room:")
        f.write("\n" + "  " * level + f"  Name: {self.get_node_name()}")

        f.write("\n\n" + "  " * level + "  Appliances:")
        for device in self.appliances:
            device.output_overview(f, level + 2)

        self.output_overview_base_parts(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
