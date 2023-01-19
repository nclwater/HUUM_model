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
# Provides a data structure to deal with choosing between alternatives output
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================
from ..util import central_data_store

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Alternatives:  # class for dealing with when there is a list to choose from
    
    def __init__(self, default):
        """
        Setup

        default - the default return value
        """
        self.default      = default.lower()
        self.Alternatives = []


    def add_alternative(self, name, condition, value):
        """
        Adds an alternative

        name      - name of alternative
        condition - what to test against
        value     - return value, if it passes
        """
        self.Alternatives.append([name, condition, value])

        
    def choose_alternative(self, cds: central_data_store.CentralDataStore):
        """
        Returns the chosen alternative
        """
        for choice in self.Alternatives:
            if (choice[1].evaluate(cds)):
                return choice[2].lower()

        return self.default.lower()


# 2. Functions =================================================================

# 3. Main Exec =================================================================
