#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.07
#
# Changelog:
#
# 2019.06.07 - SBerendsen - start
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
# Description & generation of the usage pattern (read: time series)
#
# ToDo:
# - make it be able to be on-the-fly generated
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import numpy as np
import datetime

# internal
from ..util import spaced_array as spaced_array

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class UsagePattern(spaced_array.SpacedArray):  # class for holding information related to usage patterns
    def __init__(self, name: str, data_type: str, usage_length: int,
                 val_x: np.array, val_y: np.array, time_step: int):
        """
        name         - name of the usage pattern. Duplicates allowed if data_type different
        data_type    - specific output datatype
        usage_length - for how long this pattern blocks the daemon from doing anything [0>: non-blocking]
        val          - a tuple of two data-arrays: x-coords and y-coords of to-be-interpolated usage curve
        time_step    - length of internal, fixed timestep
        """
        self.name         = name.lower()
        self.data_type    = data_type
        self.usage_length = datetime.timedelta(seconds=usage_length)

        spaced_array.SpacedArray.__init__(self, val_x, val_y, time_step,
                                          'single')


    @classmethod
    def loadFromFileData(cls, file_data, time_step: int):
        cls = UsagePattern(file_data.name, file_data.demand_type,
                           file_data.usage_length, file_data.usage_t,
                           file_data.usage_value, time_step)
        return cls


    def get_usage_length(self):
        return self.usage_length


# 2. Functions =================================================================

# 3. Main Exec =================================================================
