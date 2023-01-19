#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.05.30
#
# Changelog:
#
# 2019.05.30 - SBerendsen - start
# 2019.06.03 - SBerendsen - added stuff for internal tree structure
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
# Provides the central data store for commonly accessed data
#
# ToDo
#   - the 'tree movement' functions need to be replaced by graph specific versions
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# internal
from . import date_parser

# external
import datetime
# import dateutil

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class CentralDataStore:  # central data store structure
    def __init__(self,
                 t_start: datetime.datetime,
                 t_end: datetime.datetime,
                 time_step: int = 1,
                 log_passed_time: bool = False,
                 log_storages: bool = False):

        self.__model_start_time        = t_start
        self.__model_end_time          = t_end
        self.__current_model_time      = datetime.datetime.today()            # dummy value
        self.__current_model_day       = datetime.datetime.today()            # dummy value
        self.__current_model_dayOfWeek = datetime.datetime.today().weekday()  # dummy value
        self.__last_model_time         = t_end
        self.__compute_interval        = datetime.timedelta(seconds=time_step)

        # log info
        self.__log_passed_time         = log_passed_time
        self.__log_storages            = log_storages

        self.__single_file_output      = None

    # Time stuff ---------------------------------------------------------------
    def set_current_model_time(self, time):

        self.__model_start_time = time
        self.__last_model_time = self.__current_model_time
        self.__current_model_time = time
        self.__current_model_day = datetime.datetime(time.year, time.month,
                                                     time.day)
        self.__current_model_dayOfWeek = time.weekday()


    def get_model_start_time(self):
        return self.__model_start_time


    def get_model_end_time(self):
        return self.__model_end_time


    def get_current_model_time(self):
        return self.__current_model_time


    def get_current_model_day(self):
        return self.__current_model_day


    def get_current_model_dayOfWeek(self):
        return self.__current_model_dayOfWeek


    def get_last_model_time(self):
        return self.__last_model_time


    def get_compute_interval(self):
        return self.__compute_interval


    def get_compute_interval_sec(self):
        return self.__compute_interval.total_seconds()


    def parse_time_strings(self, string):
        """
        Parses and works on 

        Inputs:
        
        string
            To be parsed/evaluated string. Either in form ISOtime or of the variable
            forms $Model_Start or $Model_End which inserts the corresponding value.
        """
        if (string == '$Model_Start'):
            obj = self.get_model_start_time()

        elif (string == '$Model_End'):
            obj = self.get_model_end_time()

        else:
            # obj = dateutil.parser.isoparse(string)
            obj = date_parser.parse_isodatetime(string)

        return obj

    # Logging stuff ------------------------------------------------------------

    def set_single_file_ts(self, file_link):
        self.__single_file_output = file_link


    def get_single_file_ts(self):
        return self.__single_file_output


    def get_single_file_storages(self):
        return None


    def get_single_file_passed_time(self):
        return None


    def get_single_file_probabilities(self):
        return None


    def get_log_passed_time(self):
        return self.__log_passed_time


    def get_log_storages(self):
        return self.__log_storages


# 2. Functions =================================================================

# 3. Main Exec =================================================================
