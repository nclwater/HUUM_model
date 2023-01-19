#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.08.06
#
# Changelog:
#
# 2019.08.06 - SBerendsen - start
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
# Base class for storages
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# Internal
from ...events import base_event
from ...util import base_data
from ...util import table_1d
from ...translators.storage import rate_increase
from ...elements import probability_type

# External
import datetime

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Storage(base_event.BaseEvent, base_data.BaseData):   # class to be extended for each node

    _TARGETABLE_CHILD_OBJECTS = [
        '$get_value_function', '$get'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name, initial_volume=0.0):
        base_data.BaseData.__init__(self, name, 'storage')
        base_event.BaseEvent.__init__(self)

        # set
        self.__translators = {}                 # translator object to get from volume to probability (type:table_1d)
        # always needs entry 'default'
        self.__volume      = initial_volume     # initial fill

        # internal vars
        self.__rates      = []               # list of active volume increase rates


    @classmethod
    def loadFromFileData(cls, file_data):
        cls = Storage(file_data.name, initial_volume=file_data.initial_volume)

        # translators
        for item in file_data.translators:
            obj = table_1d.Table1d.loadFromFileData(item)
            cls.add_translator(item.active_for, obj)

        # rates
        for item in file_data.rates:
            obj = rate_increase.Rate.loadFromFileData(item)
            cls.add_rate(obj)

        return cls


    def add_rate(self, rate):
        self.__rates.append(rate)


    def add_translator(self, key, translator):
        self.__translators[key] = translator


    def register(self, parent_obj):
        self.register_tree_node(parent_obj)


    def check(self):
        if ('default' not in self.__translators):
            print('\nError: storage.check:')
            print('\nKey _default_ not found in translator dictionary')
            exit(255)


    def update(self, current_tp: datetime.datetime):

        # first remove the ones which are out of (time) bounds
        rate_list = [elem for elem in self.__rates if elem.is_valid(current_tp)]
        if (len(rate_list) != len(self.__rates)):     # saves unnecessary memory copying
            self.__rates = rate_list.copy()

        # get actual update value
        increase = 0.0
        for rate in self.__rates:
            val = rate.get_val()
            increase += val

        self.__volume += increase


    def get_volume(self):
        return self.__volume


    def get_val(self, input='default'):
        if (input in self.__translators):
            return self.__translators[input].get_value(self.__volume)
        else:
            return self.__translators['default'].get_value(self.__volume)


    def empty_volume(self, amount=None):
        if (amount is None):
            self.__volume = 0.0
        else:
            self.__volume += amount


    def _get_child_object(self, parts):
        """
        Overriden part of the base_connection method.
        """
        # print('gco:', type(self), parts)
        # check for actions
        if (parts[0][0:5] == '$get_'):
            if (parts[0][5:] == 'value_function'):
                return [self.get_val]

            else:
                print('\nError: storage.eval_uid_part:')
                print('Unrecognised get target: #' + parts[0][5:] + '#')
                print('Expression:              #' + parts + '#')
                exit(255)
        else:
            print('\nError: storage.eval_uid_part:')
            print('Unrecognised action: in expression: #' + parts + '#')
            exit(255)


    def exec_event(self,
                   action,
                   effect,
                   **kwargs):
        """
        Object implementation override

        action  - what should be done. Input is already disaggregated into components
        effects - the effects obj  

        Optional args for this:

        current_tp
            Current timepoint.
        """

        # storage ............................................................
        if (action[0] == 'storage'):
            if (action[1] == 'empty'):
                self.empty_volume()

            elif (action[1] == 'add_volume'):
                if (isinstance(effect, probability_type.ProbabilityType)):
                    self.__volume += effect.get_probability_value(
                        kwargs["current_tp"])
                elif isinstance(effect, int):
                    self.__volume += effect

            elif (action[1] == 'set_random'):
                self.__volume = effect.get_probability_value(
                    kwargs["current_tp"])

            else:
                print('storage.exec_event:')
                print('Unsupported action-type: #' + str(action) + '# for target:storage')
                print('Object type:', type(self).__name__)
                exit(255)


        # Catch all ............................................................
        else:
            print('storage.exec_event:')
            print('Unsupported action-target: #' + str(action) + '#')
            print('Object type:', type(self).__name__)
            exit(255)



# 2. Functions =================================================================


# 3. Main Exec =================================================================
