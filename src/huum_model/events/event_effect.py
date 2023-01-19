#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.05
#
# Changelog:
#
# 2019.06.05 - SBerendsen - start
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
# Event object.
#
# ------------------------------------------------------------------------------
#



# 0. Imports ===================================================================

# internal
from ..elements import probability_type
from ..elements import usage_pattern
from ..elements import usage_template
from ..util import central_data_store


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class EventEffect(object):   # class to hold event effect and target data

    def __init__(self, target: str, action_type: str, effect):

        self.__target      = target.lower()         # target of action, get transformet into the target id
        self.__target_func = None                   # holds the targeting function
        self.__action_type = action_type.lower()    # what kind of action should be done
        self.__effect      = effect                 # object with the action itself


    @classmethod
    def loadFromFileData(cls, file_data, parent_id: str, time_step: int):

        # generate the effect object according to type
        if (file_data.effect_type == 'Target'):
            effect_data = file_data.effect_data

        elif (file_data.effect_type == 'Event_Usage_Habit_Template'):
            effect_data = usage_template.UsageTemplate.fromFileData(
                file_data.effect_data)

        elif (file_data.effect_type == 'Usage_Pattern'):
            effect_data = usage_pattern.UsagePattern.loadFromFileData(
                file_data.effect_data, time_step)

        elif (file_data.effect_type == 'Probability'):
            effect_data = probability_type.ProbabilityType.fromFileData(
                file_data.effect_data, parent_id)

        elif (file_data.effect_type == 'None'):
            effect_data = None

        else:
            print('\nevent_effect.EventEffect.loadFromFileData: Error:')
            print('Unknown/Unsupported effect type:', file_data.effect_type)
            print(file_data)
            exit()

        # now generate the object
        cls = EventEffect(file_data.target, file_data.action, effect_data)

        return cls


    def __str__(self):
        string = 'Event Effect Target: ' + self.__target + ' with action ' + \
            self.__action_type + '\nand effect-type ' + \
            str(type(self.__effect))
        return string


    def check(self, name):
        """
        Checks for target validity and action type possibility (both incomplete)
        """

        # check supported action type(s)
        if (self.__action_type == 'add.probability'):
            pass

        else:
            print('\nError: While checking event effect: Unsupported action:' +
                  self.__action_type)
            print('Event:' + name + 'Target:' + self.__target)
            exit(255)


    def get_target(self):
        return self.__target


    def connect(self, parent_obj):
        self.__target_func = parent_obj.get_uid_target_obj(self.__target)


    def execute(self,
                cds: central_data_store.CentralDataStore,
                time_start=None):
        """
        Executes the event effects.
        """
        # if (type(self.__target_obj) is str):
        #     print('something')
        #     exit()
        for target in self.__target_func:

            assert callable(target), (
                '\nError: event_effect.execute: Given item is not a function'
                f'\nTarget-UID:  {self.__target}'
                f'\nTarget:      {str(target)}'
                f'\nTarget list: {" ".join(str(x) for x in self.__target_func)}'
            )

            assert isinstance(target(), list), (
                '\nError: event_effect.execute: Given item is not iterable'
                f'\nTarget-UID:  {self.__target}'
                f'\nTarget:      {str(target)}'
                f'\nTarget list: {" ".join(str(x) for x in self.__target_func)}\n'
            )

            for item in target():
                item.exec_event(self.__action_type.split('.'),
                                self.__effect,
                                current_tp=cds.get_current_model_time(),
                                time_start=time_start,
                                timestep=cds.get_compute_interval_sec())


# 2. Functions =================================================================


# 3. Main Exec =================================================================
