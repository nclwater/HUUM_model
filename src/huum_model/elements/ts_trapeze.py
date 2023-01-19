# 
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.11.06
#
# Changelog:
#
# 2019.11.06 - SBerendsen - start
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
# Provides a way to generate a trapeze formed time series graph from constituent parts
#
# ------------------------------------------------------------------------------
#
# ToDo:
#   - Not happy with how the TS / raw-TS arrays are handled currently across the code - refactor!
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import numpy as np

# internal


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class TSTrapeze():     # simple way of generating a trapezoid time series from parts

    def __init__(self, t_start=None, t_rise=None, t_fall=None, t_end=None, h=None):
        self.t_start = t_start  # [sec] time from zero to the start of the trapeze
        self.t_rise  = t_rise   # [sec] time from t_start to reaching 'h1'
        self.t_fall  = t_fall   # [sec] time from 'h1' to 'h2'
        self.t_end   = t_end    # [sec] time from 'h2' to end of trapezoid
        self.h_1     = h        # [cm] starting height
        self.h_2     = h        # [cm] ending height


    def check(self):
        flag   = True   # false == not ok
        string = ''     # accumulated string

        if (self.t_start >= self.t_rise):
            string += '\n- t_start >= t_rise'
            flag = False

        if (self.t_rise >= self.t_fall):
            string += '\n- t_rise >= t_fall'
            flag = False

        if (self.t_fall >= self.t_end):
            string += '\n- t_fall >= t_end'
            flag = False


        if not(flag):
            print('ts_trapeze: error in set data')
            print(string)
            print(self.to_info_string())
            exit(255)


    def to_info_string(self):
        string = ''
        string += '\n'
        string += '\nt_start: ' + self.t_start
        string += '\nt_rise:  ' + self.t_rise 
        string += '\nt_fall:  ' + self.t_fall 
        string += '\nt_end:   ' + self.t_end  
        string += '\nh_1:     ' + self.h_1    
        string += '\nh_2:     ' + self.h_2    

        return string


    def conv_to_arrays(self, override_array):

        arr_y = np.array([0.0, self.h_1, self.h_2, 0.0])
        arr_x = np.array([self.t_start, self.t_start + self.t_rise, self.t_start +
                          self.t_rise + self.t_fall, self.t_start + self.t_rise + self.t_fall + self.t_end])

        return arr_x, arr_y


    def set_variable_value(self, var, val):
        """
        Given the variable, sets a corresponding value
        """
        if (var == 'h1'):
            self.h_1 = val

        elif (var == 'h2'):
            self.h_2 = val

        elif (var == 'h'):
            self.h_1 = val
            self.h_2 = val

        elif (var == 't_start'):
            self.t_start = val

        elif (var == 't_rise'):
            self.t_rise = val

        elif (var == 't_fall'):
            self.t_fall = val

        elif (var == 't_end'):
            self.t_end = val
        
        else:
            print('\nError: ts_trapeze.set_variable_value:')
            print('Unknown variable target:', var)
            exit(255)


    def combine_trapeze(self, ts_trapeze):
        """
        Overwrites the entries in the 'main' ts_trapeze with content from the second one,
        if it has data.
        """
        if not(ts_trapeze.h_1 is None):
            self.h_1 = ts_trapeze.h_1

        if not(ts_trapeze.h_2 is None):
            self.h_2 = ts_trapeze.h_2

        if not(ts_trapeze.t_start is None):
            self.t_start = ts_trapeze.t_start

        if not(ts_trapeze.t_rise is None):
            self.t_rise = ts_trapeze.t_rise

        if not(ts_trapeze.t_fall is None):
            self.t_fall = ts_trapeze.t_fall

        if not(ts_trapeze.t_end is None):
            self.t_end = ts_trapeze.t_end



# 2. Functions =================================================================


# 3. Main Exec =================================================================







