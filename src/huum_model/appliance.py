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
# 2019.06.05 - SBerendsen - now remembers who it is used by
# 2019.10.03 - SBerendsen - added option to not block the user
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
# Anything related to single appliances.
#
# ToDo
# - make the probability time series be generated on the fly
# - make the block length depend on the usage pattern being applied
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# general
import datetime
import numpy as np

# internal
from . import agent
from .elements import usage_pattern
from .events import event_effect
from .util import base_parts
from .util import central_data_store
from .util import settings
from .util import number_output

from huum_io import appliance as io_appliance

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Appliance(base_parts.BaseParts):  # holds all relevant appliance info

    _TARGETABLE_CHILD_OBJECTS = [
        '$appliance', '$event', '$storage', '$passedtime', '$replace',
        '$replace_user'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self,
                 name: str,
                 app_class: str,
                 block_length: int,
                 no_external_block: bool = False):
        super().__init__(name, 'appliance')

        self.appliance_class        = app_class.lower()     # what appliance "class" this one belongs to
        self.block_length_appliance = block_length          # for how long the usage blocks the user in [sec]
        self.block_length_patterns  = 0

        # usage stuff
        # if currently is being used, until when the appliance is blocked
        self.blocked_until = None
        self.blocked_by    = None  # who currently uses it
        self.usage_pattern = []

        # info output
        # set of all the different usage pattern types
        self.list_ts_type  = set([])
        self.sw_ts_output  = None               # output: timeseries
        self.sw_activation = None               # output: write activation times to file
        self.__array_usage = None               # fixed size list to hold demand values for output
        self._is_activated = np.array([0.0])    # switch whether this appliance was actived this timestep

        # debug vars
        self.__num_last    = 0


    def load(self, appliance_data: io_appliance.IOAppliance,
             cds: central_data_store.CentralDataStore):
        """
        Loads the appliance data from a IO-model object.
        """
        for item in appliance_data.usage_patterns:
            obj = usage_pattern.UsagePattern.loadFromFileData(
                item, cds.get_compute_interval_sec())
            self.add_usage_pattern(obj)

        # load common stuff
        self.load_common(appliance_data, cds.get_model_start_time(),
                         cds.get_compute_interval_sec())


    def get_class_name(self):
        return self.appliance_class


    def get_user_as_list(self):
        """
        Returns the user, when applicable.
        """
        return [self.blocked_by]


    def add_usage_pattern(self,
                          pattern: usage_pattern.UsagePattern,
                          start_time: datetime.datetime = None):
        if (start_time is not None):
            pattern.start_time = start_time

        self.usage_pattern.append(pattern)
        self.list_ts_type.add(pattern.data_type)


    def initialize(self, directory: str, parent_obj,
                   cds: central_data_store.CentralDataStore,
                   cfg: settings.Config):

        # data structure housekeeping
        self.register_tree_node(parent_obj)
        self.base_register(directory + '_appliance_' + self.get_node_name(),
                           cds, cfg)

        # adjust blocking length to be at least as long as any usage habit
        longest = datetime.timedelta(seconds=0)
        for pattern in self.usage_pattern:
            longest = max(longest, pattern.get_usage_length())
        self.block_length_appliance = datetime.timedelta(
            seconds=self.block_length_appliance)
        self.block_length_patterns = longest

        # setup TS-output file
        if (len(self.list_ts_type) > 0):

            # setup ts output
            self.sw_ts_output = number_output.NumberOutput(
                directory + '_' + self.get_node_name() + '_outputTS.csv',
                len(self.list_ts_type), self.list_ts_type, cfg.log_TS_outputs,
                cds.get_single_file_ts(), self.get_full_node_id())

            # setup output list size
            self.__array_usage = [0.0] * len(self.list_ts_type)

        else:
            print('\nappliance.Appliance: Warning')
            print(f'Appliance {self.get_node_name()} has no output ts types setup')

        # setup activation output
        self.sw_activation = number_output.NumberOutput(
            directory + '_' + self.get_node_name() + '_applianceActivation.csv',
            1, ['Appliance_Activation'], cfg.log_activation,
            cds.get_single_file_ts(), self.get_full_node_id())

    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()


    def update_events(self, current_tp: datetime.datetime,
                      func_add_event_queue_item):
        self.check_event_starts('Probability',
                                func_add_event_queue_item,
                                current_tp=current_tp)


    def update_storages(self, current_tp: datetime.datetime):
        self.update_storage_values(current_tp)


    def update(self, current_tp: datetime.datetime,
               last_tp: datetime.datetime):

        for pattern in self.usage_pattern:
            pattern.update(current_tp)


    def record_status(self, cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):
        # debug
        if (len(self.usage_pattern) != self.__num_last):
            self.__num_last = len(self.usage_pattern)

        # usage values
        if (len(self.list_ts_type) > 0):

            for i, item in enumerate(self.list_ts_type):
                val = 0.0
                for usage in self.usage_pattern:
                    if (item == usage.data_type):
                        val += usage.get_value()

                self.__array_usage[i] = val

            self.sw_ts_output.write_record(np.array(self.__array_usage),
                                           cds.get_current_model_time(),
                                           cds.get_last_model_time())

        self.sw_activation.write_record(self._is_activated,
                                        cds.get_current_model_time(),
                                        cds.get_last_model_time())
        self._is_activated[0] = 0.0

        # control status
        if (self.blocked_until is not None):
            string = self.blocked_until.isoformat(
                ' ') + ';' + self.blocked_by.get_node_name()
        else:
            string = 'None;None'


        # common logging
        self.base_log(cds.get_current_model_time(), cds.get_last_model_time())

        return string


    def close(self, current_tp: datetime.datetime):
        if (len(self.list_ts_type) > 0):
            self.sw_ts_output.close(current_tp)
        self.sw_activation.close(current_tp)
        self.close_storages(current_tp)


    def is_used(self, current_tp: datetime.datetime):
        """
        Checks whether the appliance is currently usable.

        Returns:

        flag - if not used, return 'None'. Otherwise until when it is being used
        """
        if (self.blocked_until is not None):
            if (self.blocked_until < current_tp):
                self.blocked_until = None
                self.blocked_by    = None

        return self.blocked_until


    def use_appliance(self, daemon: agent.Agent,
                      current_tp: datetime.datetime,
                      func_add_event_queue_item):
        """
        Sets the appliance to being used.

        use_id - id of the agent using this appliance currently
        ts     - adjustable time series data

        Returns:

        usage_length - until when the daemon cannot do anything else.
        """
        self.blocked_until = current_tp + self.block_length_patterns
        self.blocked_by    = daemon
        agent_block_length = current_tp + self.block_length_appliance

        for pattern in self.usage_pattern:
            pattern.activate(current_tp, current_tp + pattern.get_timespan())

        # run possible post events
        self.check_event_starts('Activate',
                                func_add_event_queue_item,
                                current_tp,
                                time_start=self.blocked_until)

        # setup for activation write
        self._is_activated[0] = 1.0

        # return until when the agent is blocked
        return agent_block_length


    def exec_event(self,
                   action: list,
                   effect: event_effect.EventEffect,
                   **kwargs: dict):
        """
        Object implementation override.

        If the action is to delete something, ending the 'check for delete' with an
        underscore, it deletes anything with contains the string. Anything else, it
        only goes for the target given.

        action  - what should be done. Input is already disaggregated into components
        effects - the effects obj  
        val     - extra value passing

        Optional args for this:

        current_tp
            Current timepoint.
        """

        # usage patterns .......................................................
        if (action[0] == 'usage_pattern'):

            if (action[1] == 'add'):
                self.add_usage_pattern(effect, start_time=kwargs["current_tp"])

            elif (action[1] == 'del'):
                pattern_list = [
                    elem for elem in self.usage_pattern if elem.name != effect
                ]
                self.usage_pattern = pattern_list.copy()

            else:
                print('appliance.exec_event: Unsupported action: #' +
                      str(action) + '#')
                print('Object type:', type(self).__name__)
                exit(255)

        # events ...............................................................
        elif (action[0] == 'event'):
            if (action[1] == 'activate'):
                counter = 0
                for event in self.get_events():
                    if (event.get_node_name() == action[2]):
                        counter += 1
                        event.set_active(True)

                # sanity check
                if (counter == 0):
                    print('Event #' + action[2] + '# for appliance ' +
                          self.get_id() + ' does not exist')
                    print('Object type:', type(self).__name__)
                    exit(255)
                elif (counter > 1):
                    print('More than one occurrance of event with that name')
                    print('Event #' + action[2] + '# for appliance ' +
                          self.get_id() + ' exists more than once')
                    print('Object type:', type(self).__name__)
                    exit(255)

            else:
                print('appliance.exec_event: Unsupported action: #' +
                      str(action) + '#')
                print('Object type:', type(self).__name__)
                exit(255)

        # Catch all ........................................................
        else:
            print('appliance.exec_event: Unsupported action-target: #' +
                  str(action) + '#')
            print('Object type:', type(self).__name__)
            exit(255)


    def _get_child_object(self, parts):
        """
        Overriden part of the base_connection method.
        """
        # print('gco:', type(self), parts)
        # check for objects
        id_part = parts[0].split('_')
        if (id_part[0] in self._TARGETABLE_CHILD_OBJECTS):

            # check for base-part objects --------------------------------------
            if (self._is_base_part_element(id_part[0])):
                return self._get_base_part_node_object(parts)

            # check for actions ------------------------------------------------
            elif (parts[0][0:9] == '$replace_'):
                if (parts[0][9:] == 'user'):
                    return [self.get_user_as_list]

                else:
                    print('\nError: appliance.eval_uid_part:')
                    print('Unrecognised replace target: #' + parts[0][9:] + '#')
                    print('Expression:                  #' + parts[0] + '#')
                    exit(255)

            else:
                print('\nError: appliance._get_child_object:')
                print('Not yet implemented _TARGETABLE_CHILD_OBJECTS:', id_part[0])
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                exit(255)
        else:
            return None


    def return_results(self):
        return self.sw_ts_output.get_results(self.get_full_node_id())


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        f.write("\n\n" + "  " * level + "- Appliance:")
        f.write("\n" + "  " * level + f"  Name: {self.get_node_name()}")

        f.write("\n" + "  " * level + f"  Num Usage Patterns: {len(self.usage_pattern)}")

        self.output_overview_base_parts(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
