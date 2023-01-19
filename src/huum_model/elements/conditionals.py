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
# Provides dealing with a conditional tests
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import sys
import time

# internal
from ..util import central_data_store

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Condition:  # data structure to deal with a condition
    
    def __init__(self, variable, operator, value):
        """
        variable - what to check for
        operator - comparison operator
        value    - what value to compare to
        model    - link to main model
        """
        self.variable = variable.lower()
        self.operator = operator.lower()
        self.value    = value

        # do variable specific stuff
        if (self.variable == '$weekday'):
            if (self.operator == '=='):
                self.value = time.strptime(value, '%A').tm_wday
            else:
                print('\nCondition.__init__: Error: Variable: ', self.variable,
                      ' unsupported operator: ', self.operator)
                sys.exit(255)

        else:
            print('\nCondition.__init__: Error: Unknown Variable: ',
                  self.variable)
            sys.exit(255)


    @classmethod
    def fromString(cls, condition_data):
        cls = Condition(condition_data.what, condition_data.type,
                        condition_data.value)
        return cls

        
    def evaluate(self, cds: central_data_store.CentralDataStore):
        """
        Evaluates whether the condition is true
        """
        if (self.variable == '$weekday'):
            if (self.value == cds.get_current_model_dayOfWeek()):
                return True
        
        elif(self.variable != ''):
            print('\nError: conditionals.evaluate:')
            print(f'Unsupported variable type: {self.variable}')
            print()
            exit(255)

        return False


# 2. Functions =================================================================

# 3. Main Exec =================================================================
