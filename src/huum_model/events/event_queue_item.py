#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.07.08
#
# Changelog:
#
# 2019.06.08 - SBerendsen - start
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
# Item for holding event_queue effects which are to be executed
#
# ToDo:
#   - redo using kwargs
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class EventQueueItem(object):  # class to be extended for each node
    
    def __init__(self, effect, val):

        self.effect = effect
        self.val = val


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print('Event_Queue_Item.output_overview: Level not set')
            exit(255)

        f.write("\n" + "  " * level + "- EventQueueItem:")
        f.write("\n" + "  " * level + "  {self.effect}")
        f.write("\n" + "  " * level + "  {self.val}")


# 2. Functions =================================================================

# 3. Main Exec =================================================================
