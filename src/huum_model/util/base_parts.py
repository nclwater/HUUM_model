#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
#
# Changelog:
#
# 2019.06.30 - SBerendsen - start
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
# Base to class for others to extend so that event pathing can work.
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# Internal
from ..events import base_event
from ..events import event_effect
from ..graph import base_connection
from ..translators.passed_time import base_passed_time
from ..translators.storage import base_storage
from . import central_data_store
from . import settings

# External
import datetime


# 1. Global vars ===============================================================
_BASE_PARTS_NODE_OBJECTS = [
    '$event', '$storage', '$passedtime'
]  # which child objects provided by base_parts are targetable.


# 1.1 Classes ------------------------------------------------------------------
# class to be extended for each node
class BaseParts(base_event.BaseEvent, base_connection.BaseConnection, base_storage.BaseStorage, base_passed_time.BasePassedTime):

    def __init__(self, name: str, node_type: str):
        base_connection.BaseConnection.__init__(self, name, node_type)
        base_event.BaseEvent.__init__(self)
        base_storage.BaseStorage.__init__(self)
        base_passed_time.BasePassedTime.__init__(self)


    def load_common(self, item, start_tp: datetime.datetime, time_step: int):
        """
        Loads the common attachable objects (events & all translators)
        """
        self.load_events(item.events, time_step)
        self.load_storages(item.storages)
        self.load_timed_storages(item.timed_storages, start_tp)


    def get_common_items(self):
        """
        Returns the all events and storages for central registration.
        """
        return self._storages, self._events


    def _is_base_part_element(self, element_id):
        if (element_id in _BASE_PARTS_NODE_OBJECTS):
            return True
        else:
            return False


    def _get_base_part_node_object(self, parts):
        # check for objects
        id_part = parts[0].split('_')
        if (id_part[0] == "$event"):
            # print('\nbasepart_node 1')
            obj        = self._get_named_event_object("_".join(id_part[1:]))
            return_obj = obj._get_node_object(parts[1:])

            # catch
            if (return_obj is None):
                print('\nError: base_parts._get_base_part_node_object:')
                print(f'Event object with {parts[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                exit(255)
            else:
                return return_obj

        elif (id_part[0] == "$passedtime"):
            # print('\nbasepart_node 2')
            obj        = self._get_ided_passed_time_object(parts[0])
            return_obj = obj._get_node_object(parts[1:])

            # catch
            if (return_obj is None):
                print('\nError: base_parts._get_base_part_node_object:')
                print(f'passedTime object with {parts[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                self.print_node_id_list_passed_time()
                exit(255)
            else:
                return return_obj

        elif (id_part[0] == "$storage"):
            # print('\nbasepart_node 3')
            obj        = self._get_ided_storage_object(parts[0])
            return_obj = obj._get_node_object(parts[1:])

            # catch
            if (return_obj is None):
                print('\nError: base_parts._get_base_part_node_object:')
                print(f'storage object with {parts[0]} does not exist')
                print(f'Search ID:        {".".join(str(x) for x in parts)}')
                print(f'\nStorage Object: {str(obj)}')
                self.print_node_id_list_storage()
                print('')
                exit(255)
            else:
                return return_obj

        else:
            print('\nError: base_parts._get_base_part_node_object:')
            print('Not yet implemented __BASE_PARTS_NODE_OBJECTS:', id_part)
            print(f'Search ID:  {".".join(str(x) for x in parts)}')
            exit(255)


    def _get_base_part_down_node(self,
                                 action: list,
                                 effect: event_effect.EventEffect,
                                 **kwargs: dict):
        """
        Like _get_base_part_node_object, but no object return and only goes down.

        ToDo
            Check whether it can be refactored to be one method.
        """

        # check for objects
        id_part = action[0].split('_')
        if (id_part[0] == "$event"):
            # print('\nbasepart_node 1')
            obj = self._get_named_event_object("_".join(id_part[1:]))

            # catch
            if (obj is None):
                print('\nError: base_parts._get_base_part_down_node:')
                print(f'Event object with {action[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in action)}')
                exit(255)
            else:
                obj.exec_event(action[1:], effect, **kwargs)
                return True


        elif (id_part[0] == "$passedtime"):
            # print('\nbasepart_node 2')
            obj = self._get_ided_passed_time_object(action[0])

            # catch
            if (obj is None):
                print('\nError: base_parts._get_base_part_down_node:')
                print(f'passedTime object with {action[0]} does not exist')
                print(f'Search ID:  {".".join(str(x) for x in action)}')
                self.print_node_id_list_passed_time()
                exit(255)
            else:
                obj.exec_event(action[1:], effect, **kwargs)
                return True


        elif (id_part[0] == "$storage"):
            # print('\nbasepart_node 3')
            obj = self._get_ided_storage_object(action[0])

            # catch
            if (obj is None):
                print('\nError: base_parts._get_base_part_down_node:')
                print(f'storage object with {action[0]} does not exist')
                print(f'Search ID:        {".".join(str(x) for x in action)}')
                print(f'\nStorage Object: {str(obj)}')
                self.print_node_id_list_storage()
                print('')
                exit(255)
            else:
                obj.exec_event(action[1:], effect, **kwargs)
                return True


        else:
            print('\nError: base_parts._get_base_part_down_node:')
            print('Not yet implemented __BASE_PARTS_NODE_OBJECTS:', id_part)
            print(f'Search ID:  {".".join(str(x) for x in action)}')
            exit(255)


    def base_register(self, prefix_storage,
                      cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):
        self.register_events()
        self.register_storages(prefix_storage, cds, cfg)
        self.register_passed_times(prefix_storage, cds.get_log_passed_time(),
                                   cds.get_model_start_time(), cfg, cds)


    def base_log(self, current_time: datetime.datetime,
                 last_time: datetime.datetime):
        self.log_storages(current_time, last_time)
        self.log_passed_times(current_time, last_time)


    def return_results(self):
        print('\nError: return_results not implemented')
        print('Id:', self._id)
        exit(255)


    def output_overview_base_parts(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview_base_parts: Level not set')
            exit(255)

        f.write('\n')
        self.output_overview_events(f, level)
        self.output_overview_storages(f, level)
        self.output_overview_passed_time(f, level)


# 2. Functions =================================================================


# 3. Main Exec =================================================================
