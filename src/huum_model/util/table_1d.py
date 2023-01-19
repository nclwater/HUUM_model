#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.08.22
#
# Changelog:
#
# 2019.08.22 - SBerendsen - start
# 2020.02.11 - SBerendsen - changed default handling of above/below values
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
# Provides the tools and methods to use a 1d, 2column table
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================
import numpy as np

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Table1d:  # class for dealing with when there is a list to choose from
    def __init__(self,
                 arr_x,
                 arr_y,
                 return_above='last',
                 return_below='first'):
        """
        Setup

        arr_x - array with the x-values (sorted ascending)
        arr_y - array with the y-values
        return_above - what to return if index > x_max (def:None; 'last':last value)
        return_below - what to return if index < x_min (def:None; 'first':first value)
        """
        self._arr_x        = arr_x
        self._arr_y        = arr_y
        self._return_above = _decode_return(return_above, arr_y)
        self._return_below = _decode_return(return_below, arr_y)


    @classmethod
    def loadFromFileData(cls, file_data):

        cls = Table1d(file_data.table_x,
                      file_data.table_y,
                      return_above=file_data.return_above,
                      return_below=file_data.return_below)

        return cls

    def get_value(self, x):
        if (self._arr_x[0] > x):
            return self._return_below

        elif (self._arr_x[-1] < x):
            return self._return_above

        elif (self._arr_x[-1] == x):
            return self._arr_y[-1]

        else:
            pos = np.searchsorted(self._arr_x, float(x), side='right')
            rat = (x - self._arr_x[pos - 1]) / (self._arr_x[pos] -
                                                self._arr_x[pos - 1])
            return self._arr_y[pos - 1] + rat * (self._arr_y[pos] -
                                                 self._arr_y[pos - 1])


# 2. Functions =================================================================
def _decode_return(return_type, arr_y):
    if (return_type is None or return_type == 'None'):
        return None
    elif (return_type == 'last'):
        return arr_y[-1]
    elif (return_type == 'first'):
        return arr_y[0]
    else:
        print('Table_1d:_decode_return: Unsupported return type: #' +
              str(return_type) + '#')
        exit()


# 3. Main Exec =================================================================
