#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.10.28
#
# Changelog:
#
# 2019.10.28 - SBerendsen - start, based on passed_time stuff
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
# Base class for inheritance of passed_time objects
#
# ------------------------------------------------------------------------------
#
# Todo:
#   - refactor this and *passed_time* for code-deduplication
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# Internal
from ...util import central_data_store
from ...util import settings
from ...util import number_output
from . import passed_time

# External
import datetime
import numpy as np


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class BasePassedTime(object):   # class to be extended for each node

    def __init__(self):
        self.__passed_time       = []
        self.__log_passed_time   = None
        self.__sw_passed_time    = None     # string de-duplicator for passed_time overview output
        self.__array_passed_time = []


    def load_timed_storages(self, data_pt, start_tp: datetime.datetime):
        for item in data_pt:
            obj = passed_time.PassedTime.loadFromFileData(item, start_tp)
            self.add_passed_time(obj)


    def add_passed_time(self, passed_time):
        self.__passed_time.append(passed_time)


    def error_passed_time_no_node(self, str_class: str, parts: list):
        print(f'\nError: {str_class}._get_child_object:')
        print(f'{str_class} object with {parts[0]} does not exist')
        print(f'Search ID:  {".".join(str(x) for x in parts)}')
        self.print_node_id_list_passed_time()
        exit(255)


    def print_node_id_list_passed_time(self):
        print('\nAttached passed_time_storages:')
        for passed_time_storage in self.__passed_time:
            print(f'   {passed_time_storage.get_node_id()}')


    def _get_ided_passed_time_object(self, obj_id):
        for passedTime_storage in self.__passed_time:
            if (passedTime_storage.get_node_id() == obj_id):
                return passedTime_storage

        return None


    def register_passed_times(self, prefix: str, log_passed_time: bool,
                              start_tp: datetime.datetime,
                              cfg: settings.Config,
                              cds: central_data_store.CentralDataStore):
        """
        Registers all the passed_time-objects with the data tree & sets up local output.

        prefix - prefix of the output filename & -path for logging passed_time data
        """

        # register
        for passed_time_storage in self.__passed_time:
            passed_time_storage.register(self, start_tp)

        # output
        self.__log_passed_time = cfg.get_log_passed_time
        if (len(self.__passed_time) > 0 and self.__log_passed_time()):
            header = []
            self.__array_passed_time = [None] * len(self.__passed_time)
            for passed_time_storage in self.__passed_time:
                header.append(passed_time_storage.get_node_name())

            self.__sw_passed_time = number_output.NumberOutput(
                prefix + '_passed_times.csv', len(self.__passed_time), header,
                cfg.log_probability, cds.get_single_file_probabilities(),
                self.get_full_node_id())


    def log_passed_times(self, current_time: datetime.datetime,
                         last_time: datetime.datetime):
        if (len(self.__passed_time) > 0 and self.__log_passed_time()):

            for i, passed_time_storage in enumerate(self.__passed_time):
                self.__array_passed_time[
                    i] = passed_time_storage.get_timespan_seconds(current_time)

            self.__sw_passed_time.write_record(
                np.array(self.__array_passed_time), current_time, last_time)


    def close_passed_times(self, current_time: datetime.datetime):
        if (len(self.__passed_time) > 0 and self.__log_passed_time()):
            self.__sw_passed_time.close(current_time)


    def output_overview_passed_time(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview_passed_time: Level not set')
            exit(255)

        f.write("\n" + "  " * level + f"Num Passed Time:       {len(self.__passed_time)}")


# 2. Functions =================================================================


# 3. Main Exec =================================================================
