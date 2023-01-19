#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.03
#
# Changelog:
#
# 2019.06.03 - SBerendsen - start
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
# Base class for usage habits
#
# ToDo:
#   - setup for alternatives (i.e. getting drinking water from tab in bath or kitchen)
#   - setup for reset from given startpoint
#   - setup for cyclical behaviour (e.g. during the night, it is much more likely that one goes to the toilet at 4h, 8h...)
#   - if not given, get model start & end time from the given model link
#   - sensible rename .name -> .appliance and .uniqueID -> .name
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# Internal
from ...graph import base_connection
from ...util import central_data_store

# External
import datetime
import numpy as np

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class UsageHabit(base_connection.BaseConnection
                 ):  # class for each type of usage habit - probability

    _TARGETABLE_CHILD_OBJECTS = [
        '$event'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self,
                 name,
                 appliance,
                 start_time,
                 end_time,
                 habit_type='add',
                 only_valid=None):

        base_connection.BaseConnection.__init__(self, name, 'usagehabit')
        if (
            only_valid is not None
        ):  # which lifestyle_habit.status it is valid for (also checks for a part match
            self.only_valid = only_valid.lower(
            )  # from the start of status string, i.e. status:'active_weekend' with this one
        else:  # being 'active' would match, but not the other way around)
            self.only_valid = None

        self.appliance  = appliance.lower()     # name of target appliance
        self.start_time = start_time            # probability from when onwards it affects the appliance
        self.end_time   = end_time              # probability until when it affects the appliance
        self.habit_type = habit_type.lower()    # what kind of habit it is 'add'itive or 'mult'iplicative
        self.data       = None                  # probability time series. One tick=1sec (global assumption),
        # goes from t_start to t_end

        self._data_type = None                  # data type of this usage habit
        self._func      = None                  # function for data type 'function'
        self._val_const = None                  # constant value given

        # set stuff which can be set
        if (habit_type == 'add'):
            self.no_change_val = 0.0

        elif (habit_type == 'mult'):
            self.no_change_val = 1.0

        else:
            print('\nclass Habit: __init__:')
            print('Unsupported habit_type:', habit_type)
            exit(255)


    @classmethod
    def fromFileData(cls, file_data, agent_id,
                     cds: central_data_store.CentralDataStore):

        t_start = cds.parse_time_strings(file_data.valid_t_start)
        t_end   = cds.parse_time_strings(file_data.valid_t_end)

        cls = UsageHabit(file_data.name,
                         file_data.appliance,
                         t_start,
                         t_end,
                         file_data.computation_type,
                         only_valid=file_data.valid_when)

        if (file_data.data_type == 'Constant'):
            cls.gen_data(file_data.data_type, file_data.data_value, -1)

        elif (file_data.data_type == 'Function'):
            cls.gen_data(file_data.data_type, file_data.data_function, -1)

        else:
            print('\nusage_habit.UsageHabit.fromFileData: Error')
            print('Unsupported data_type:', file_data.data_type)
            exit(255)

        return cls


    def gen_data(self, data_type, val, time_step: int):
        """
        Generates the data array from the given data.

        data_type - what data setting should be done. Currently supported:
                    # constant: constant value all across
                    # linear:   linear interpolation between the given datapoints
                    # function: the target is a function
        val       - value to set the data stuff to. Form depends on data_type:
                    # constant: single value
                    # linear:   a list with two arrays
                    # function: a string with the target text which then gets evaluated/associated
        time_step - size of timestep in seconds

        ToDo
            - refactor into different classes using a class factory
        """

        # setup and init data
        self._data_type = data_type.lower()
        if (self._data_type == 'constant'):
            self._val_const = float(val)

        elif (self._data_type == 'linear'):
            # get needed array size
            interval   = self.end_time - self.start_time
            array_size = int(interval.total_seconds()) / time_step
            x          = np.arange(0, array_size * time_step, time_step)
            self.data  = np.interp(x, val[0], val[1])

        elif (self._data_type == 'function'):
            self.data = val

        else:
            print('\nusage_habit.gen_data: Error:')
            print(' Illegal/unrecognised given data type: #' + self._data_type + '#')
            exit(255)


    def register(self, parent_obj):
        """
        For setting the unique-id, which is _not_ being registered into the access tree
        """
        self.register_tree_node(parent_obj)


    def connect_uids(self):
        """
        Overridden function implementation.
        """
        if (self._data_type == 'function'):
            uid_obj = self.get_uid_target_obj(self.data)

            # tests
            assert isinstance(uid_obj, list), (
                '\nError: usage_habit.connect_uids: UID target is not a list'
                f'\nCurrent ID:   {self.get_full_node_id()}'
                f'\nQuery string: {self.data}')

            for item in uid_obj:
                assert callable(item), (
                    '\nError: usage_habit.connect_uids: Returned UID target is no callback'
                    f'\nCurrent ID:   {self.get_full_node_id()}'
                    f'\nQuery string: {self.data}'
                    f'\nItem:         {str(item)}'
                    f'\nList:         {" ".join(str(x) for x in uid_obj)}')

            assert (len(uid_obj) == 1), (
                '\nError: usage_habit.connect_uids: More than one target returned'
                f'\nCurrent ID:   {self.get_full_node_id()}'
                f'\nQuery string: {self.data}')

            self._func = uid_obj[0]


    def get_probability(self, current_tp: datetime.datetime, time_step: int):
        """
        Gets the current probability

        Returns:

        probability - current probability. Returns 'None' if it is too early and NaN if it is too late.
        """

        # default value if not yet active (t_start > current_time)
        if (self.start_time > current_tp):
            return self.no_change_val

        elif (self.end_time < current_tp):
            print('usage_habit.get_probability:')
            print(
                "This shouldn't be happening, non-cleaned time limited habit present."
            )
            exit(255)

        elif (self._data_type == 'constant'):
            return self._val_const

        elif (self._data_type == 'linear'):
            # compute time difference in sec
            diff       = current_tp - self.start_time
            diff_entry = diff.total_seconds() / float(time_step)

            if (diff_entry >= self.data.size):
                return self.no_change_val
            else:
                return float(self.data[int(diff_entry)])

        elif (self._data_type == 'function'):
            return self._func(self.only_valid)

        else:
            print('Error: UsageHabit.get_probability')
            print('Unsupported data_type:', self._data_type)
            exit(255)


    def is_valid(self, current_tp: datetime.datetime):
        # checks whether the usage habit is still valid
        if (self.end_time < current_tp):
            return False
        else:
            return True


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(
                f'{self.get_node_name()}.output_overview: Level not set'
            )
            exit(255)

        f.write("\n\n" + "  " * level + "- Usage Habit:")
        f.write("\n" + "  " * level + f"  Appliance:   {self.appliance}")
        f.write("\n" + "  " * level + f"  OnlyValid:   {self.only_valid}")
        f.write("\n" + "  " * level + f"  StartTime:   {self.start_time}")
        f.write("\n" + "  " * level + f"  EndTime:     {self.end_time}")
        f.write("\n" + "  " * level + f"  HabitType:   {self.habit_type}")
        f.write("\n" + "  " * level + f"  ValNoChange: {self.no_change_val}")
        f.write("\n" + "  " * level + f"  DataType:    {self._data_type}")

        if (self._data_type == 'constant'):
            f.write("\n" + "  " * level + f"  ValConst:    {self._val_const}")

        elif (self._data_type == 'linear'):
            f.write("\n" + "  " * level + f"  Data:        {self.data}")

        elif (self._data_type == 'function'):
            f.write("\n" + "  " * level + f"  Data:        {self.data}")

        else:
            print('\nusage_habit.gen_data: Error:')
            print(' Illegal/unrecognised given data type: #' +
                  self._data_type + '#')
            exit(255)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
