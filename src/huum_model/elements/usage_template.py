#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.21
#
# Changelog:
#
# 2019.06.21 - SBerendsen - start
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
# Base class for generating flexible usage habits for run-time
#
# ToDo:
#   - sensible rename .name -> .appliance and .uniqueID -> .name
#   - see whether it can be combined with usage_habit.py
#
# ------------------------------------------------------------------------------
#



# 0. Imports ===================================================================
import numpy as np

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class UsageTemplate:
    def __init__(self,
                 name: str,
                 uniqueID: str,
                 only_valid: str,
                 typus: str,
                 habit_length: int,
                 arr_x: np.array,
                 arr_y: np.array,
                 habit_type: str = 'add',
                 time_buffer: int = 0):
        self.name             = name.lower()        # name of the appliance, which is target
        self.uniqueID         = uniqueID.lower()    # unique-id for this habit instance. Used for distinguishing between the different
        # effects affecting one appliance
        # if it is only the name, it is the 'base' usage level
        # if it $name.<something>, it has been created by some kind of event.
        if not(only_valid is None):                 # which lifestyle_habit.status it is valid for
            self.only_valid   = only_valid.lower()
        else:
            self.only_valid   = None
        self.typus            = typus               # which type of template it is:
        #       - Cyclical_Global: repeats the same pattern from start of the simulation
        #       - Cyclical:        repeats the pattern from the start of the lifestyle habit time
        #       - Start:           sets the pattern to the start of the lifestyle habit time
        #       - End:             sets the pattern to the end of the lifestyle habit time
        self.habit_length = habit_length  # Length of usage pattern (for zero padding at the end)
        self.habit_type   = habit_type    # type of probability computation, supported are 'add'itive and 'mult'iplicative
        self.arr_x        = arr_x         # Numpy data array for the x-values (it is assumed that the arrays start at 0-0)
        self.arr_y        = arr_y         # Numpy data array for the y-values (it is assumed that the arrays start at 0-0)
        self.time_buffer  = time_buffer   # how much _padding_ should be between activation time & template active (useful for functions)

    @classmethod
    def fromFileData(cls, file_data):

        cls = UsageTemplate(file_data.name,
                            file_data.appliance,
                            file_data.valid_when,
                            file_data.template_type,
                            file_data.duration,
                            file_data.probability_t,
                            file_data.probability_value,
                            habit_type=file_data.computation_type,
                            time_buffer=int(file_data.buffer))

        return cls


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview: Level not set')
            exit(255)

        f.write("\n\n" + "  " * level + "- Usage Habit Template:")
        f.write("\n" + "  " * level + f"  Appliance:   {self.name}")
        f.write("\n" + "  " * level + f"  TemplateId:  {self.uniqueID}")
        f.write("\n" + "  " * level + f"  OnlyValid:   {self.only_valid}")
        f.write("\n" + "  " * level + f"  Typus:       {self.typus}")
        f.write("\n" + "  " * level + f"  HabitType:   {self.habit_type}")
        f.write("\n" + "  " * level + f"  Buffer:      {self.time_buffer}")
        f.write("\n" + "  " * level + f"  HabitLength: {self.habit_length}")
        f.write("\n" + "  " * level + f"  Arr_X:       {self.arr_x}")
        f.write("\n" + "  " * level + f"  Arr_Y:       {self.arr_y}")



# 2. Functions =================================================================


# 3. Main Exec =================================================================
