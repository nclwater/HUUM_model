#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2020.07.02
#
# Changelog:
#
# 2020.07.02 - SBerendsen - start
#
# ------------------------------------------------------------------------------
#
# Copyright 2020, Sven Berendsen
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
# Module for transforming and holding linear data into internal useable order.
#
# ------------------------------------------------------------------------------
#
# ToDo
#   - Setup for non-uniform timestep
#   - implement other ways for interpolation / resampling (currently it is the modeller's responsibility)
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import datetime
import numpy as np


# internal


# 1. Global vars ===============================================================
__ALLOWED_REPEAT_TYPES = ['single', 'cyclical']


# 1.1 Classes ------------------------------------------------------------------
class SpacedArray:   # holds config data
    def __init__(self,
                 arr_x: np.array,
                 arr_y: np.array,
                 time_step: int,
                 repeat_type: str,
                 repeat_length: int = -1):

        # settings
        self.__repeat_type     = repeat_type    # whether and how it should repeat

        # runtime data
        self.__t_start         = None           # start time, for dealing with starting zeros
        self.__n               = -1             # internal position counter
        self.__t_end           = None           # until when it is supposed to run (hard-end)

        if (self.__repeat_type == 'single'):           # how long in between repeats
            self.__repeat_interval = -1

        elif (self.__repeat_type == 'cyclical'):
            self.__repeat_interval = datetime.datetime(seconds=repeat_length)

        else:
            print('spaced_array.SpacedArray: Error:')
            print('Unsupported repeat_type:', repeat_type)
            exit(255)

        # generate array
        arr_size     = 1 + (arr_x[-1] // time_step)
        time_span    = time_step * arr_size     # length of the timespan the array is active for
        get_x_arr    = np.arange(0, arr_size * time_step, time_step)
        self.__array = np.interp(get_x_arr, arr_x, arr_y)

        # other data
        self.__time_span = datetime.timedelta(seconds=time_span)


    def get_timespan(self):
        return self.__time_span


    def get_timespan_sec(self):
        return self.__time_span.total_seconds()


    def checks(self):
        pass


    def activate(self, t_start: datetime.datetime, set_end: datetime.datetime):
        self.__t_start = t_start
        self.__n       = -1
        self.__t_end   = set_end


    def update(self, t_current: datetime.datetime):
        if (self.__t_start is None):
            pass

        elif (t_current > self.__t_end):
            if (self.__repeat_type == 'cyclical'):
                self.__t_start = self.__t_start + self.__repeat_interval
                self.__t_end   = self.__t_start + self.__time_span
                self.__n       = -1
            else:
                self.deactivate()

        elif (t_current >= self.__t_start):
            self.__n = self.__n + 1


    def get_value(self):
        """
        Todo
            Rebuild so that the first check isn't necessary.
        """
        if (self.__n >= len(self.__array)):
            return 0.0

        elif (self.__n >= 0):
            return self.__array[self.__n]

        else:
            return 0.0


    def deactivate(self):
        self.__t_start = None
        self.__t_end   = None
        self.__n       = -1






# 2. Functions =================================================================


# 3. Main Exec =================================================================
