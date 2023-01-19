#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.05.17
#
# Changelog:
#
# 2019.05.17 - SBerendsen - start
# 2019.10.29 - SBerendsen - added ability to link to functions
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
# Class to encapsulate all the different probability types and still give sensible
# returns
#
# ------------------------------------------------------------------------------
#
# Todo:
#   - Refactor so that the ugliness in dealing with functions & targets vanishes
#   - The general variables used here are 'bad' -> refactor
#
# ------------------------------------------------------------------------------
#



# 0. Imports ===================================================================

# external
import datetime
import sys

# internal
from ..util import rnd_wrapper


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class ProbabilityType:     # class to wrap all supported probabilities
    def __init__(self, typus, a=None, b=None, c=None):
        self.__type = typus  # see get_activation_tp for more infor
        self.__a    = a      # a, b & c depend on whats typus is set
        self.__b    = b
        self.__c    = c
        self.__func = None


    @classmethod
    def fromFileData(cls, file_data, parent_obj):

        if (file_data.type == 'Constant'):
            cls = ProbabilityType(file_data.type, file_data.constant)

        elif (file_data.type == 'Uniform'):
            cls = ProbabilityType(file_data.type, file_data.range_from, file_data.range_to)

        elif (file_data.type == 'Function'):
            cls = ProbabilityType(file_data.type, file_data.function, parent_obj)

        elif (file_data.type == 'Gauss'):
            cls = ProbabilityType(file_data.type, file_data.mu, file_data.sigma)

        else:
            print('\nProbabilityType.fromFileData: Error:')
            print('Unsupported probability type: ' + str(cls.type))
            print(file_data)
            exit(255)

        return cls


    def get_activation_tp(self):
        if (self.__type == 'Constant'):     # a is in seconds since the start of the day
            return datetime.timedelta(seconds=self.__a)

        elif (self.__type == 'Uniform'):    # propability uniformly distributed between a and b
            return datetime.timedelta(seconds=rnd_wrapper.rnd_get_uniform_dist(self.__a, self.__b))

        elif (self.__type == 'Gauss'):    # propability uniformly distributed between a and b
            return datetime.timedelta(seconds=rnd_wrapper.rnd_get_gauss_dist(self.__a, self.__b))

        elif (self.__type == 'Function'):   # a is the link to the model, b is the target_id
            # and c is the UID of the parent object
            if (self.__func is None):
                self.__func = self.__a.tree.get_uid_target_obj(self.__b.lower(), self.__c().lower())[0]
            return datetime.timedelta(seconds=self.__func())

        else:
            print('\nError: Probability_Type.get_activation_tp:')
            print('Unknown/unsupported probability type: _' + self.__type + '_\n')
            sys.exit(255)


    def get_probability_value(self, current_tp: datetime.datetime):
        if (self.__type == 'Constant'):
            return self.__a

        elif (self.__type == 'Uniform'):
            return rnd_wrapper.rnd_get_uniform_dist(self.__a, self.__b)

        elif (self.__type == 'Gauss'):
            return rnd_wrapper.rnd_get_gauss_dist(self.__a, self.__b)

        elif (self.__type == 'Function'):

            if (self.__func is None):
                returned_obj = self.__b.get_uid_target_obj(self.__a)
                if (len(returned_obj) != 1):
                    print('\nError: probability_type.get_probability_value:')
                    print('Target for functions returns more than one object')
                    print(f'Target: {self.__a.lower()}')
                    exit(255)
                self.__func = returned_obj[0]

            return self.__func(current_tp)

        else:
            print('\nError: Probability_Type.get_probability_value:')
            print('Unknown/unsupported probability type: _' + self.__type + '_\n')
            sys.exit(255)



# 2. Functions =================================================================


# 3. Main Exec =================================================================
