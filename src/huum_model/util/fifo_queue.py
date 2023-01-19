#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2020.09.01
#
# Changelog:
#
# 2020.09.01 - SBerendsen - start
#
# ------------------------------------------------------------------------------
#
# Copyright 2021, Sven Berendsen
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
# Implements a FIFO queue, but not using the queue class so that it can be checked
# what is already present in the queue.
# Taken from: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch17s15.html
# but adjusted with extra features.
#
# ToDo
#   - Perf testing
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class FifoList:

    def __init__(self):
        self._data = []

    def size(self):
        return len(self._data)

    def append(self, string: str):
        self._data.append(string)

    def append_if_not_in(self, string: str):
        if not self.is_in(string):
            self._data.append(string)

    def pop(self):
        return self._data.pop(0)

    def pop_item(self, string: str):
        """ Pops the item given by string - does not check whether it is present!"""
        pos = self._data.index(string)
        return self._data.pop(pos)

    def remove_item(self, string: str):
        self._data.remove(string)

    def is_in(self, string: str):
        return string in self._data

    def get_at_pos(self, pos: int):
        return self._data[pos]

# 2. Functions =================================================================


# 3. Main Exec =================================================================
