#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.08.20
#
# Changelog:
#
# 2019.08.20 - SBerendsen - start
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
# Base class for dealing with timed effects
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class BaseTimedEffect:  # class for each type of usage habit - probability
    
    def __init__(self, time_start=None, time_end=None):
        self._time_start = time_start
        self._time_end   = time_end


    def is_valid(self, current_time):
        """
        Checks if the object is still valid. 

        current_time - time to check against

        Returns 'True' when yes, 'False' otherwise.
        """
        valid = True
        if (self._time_end is not None):
            if (self._time_end < current_time):
                valid = False

        return valid


    def is_active(self, current_time):
        active = True
        if (self._time_end is not None):
            if (self._time_end < current_time):
                active = False
        if (self._time_start is not None):
            if (self._time_start > current_time):
                active = False

        return active


# 2. Functions =================================================================

# 3. Main Exec =================================================================
