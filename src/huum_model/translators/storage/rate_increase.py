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
# Class for providing the settings for the change in volume for any storages
#
# ToDo:
#   - checks
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================
from ...elements.timed_effects import base_timed_effect

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Rate(base_timed_effect.BaseTimedEffect):
    def __init__(self,
                 name,
                 typus=None,
                 time_start=None,
                 time_end=None,
                 const_val=None,
                 target=None,
                 mult=None,
                 list_increases=None):

        # superclass
        base_timed_effect.BaseTimedEffect.__init__(self,
                                                   time_start=time_start,
                                                   time_end=time_end)

        self._name  = name.lower()
        self._typus = typus.lower()  # currently supported: 'constant', 'target', 'target_function'

        # for typus == constant
        self._const_val = const_val

        # for typus == target
        if not (target is None):
            self._target = target.lower(
            )  # worked on later. Currently supported: num_people_in_consumer_unit,
        else:
            self._target = None
        
        self._num  = None            # set later, if the target resolves to a number
        self._func = None            # set later, if the target given is a number ("target_function")
        self._mult = mult            # multiplier
        self._dict = list_increases  # needs


    @classmethod
    def loadFromFileData(cls, file_data):

        if (file_data.type == 'constant'):
            cls = Rate(file_data.name,
                       typus=file_data.type,
                       const_val=file_data.const_val)

        else:
            print('rate.Rate.loadFromFileData: Error:')
            print('Unsupported rate type:', file_data.type)
            exit(255)

        return cls


    def initialize(self, obj_parent):
        """
        Replace by using UID.
        """
        if (self._typus == 'target'):
            if (self._target is None):
                print('\nrate type given as _target_, but no target defined\n')
                print('rate: #' + self._name + '#\n')
                exit(255)

            elif (self._target == 'num_people_in_consumer_unit'):
                id_parent = obj_parent.get_id()
                id_consumer_unit = obj_parent.tree.get_consumer_unit_part(
                    id_parent)
                obj       = obj_parent.tree.get_node(id_consumer_unit)
                self._num = obj.get_num_agents_in_consumer_unit()

            else:
                print('\nUnknown target type: #' + self._target + '#\n')
                print('rate: #' + self._name + '#\n')
                exit(255)

        elif (self._typus == 'target_function'):
            if (self._target is None):
                print('\nrate type given as _target_, but no target defined\n')
                print('rate: #' + self._name + '#\n')
                exit(255)

            elif (self._target == 'num_people_in_consumer_unit'):
                id_parent        = obj_parent.get_id()
                id_consumer_unit = obj_parent.tree.get_consumer_unit_part(
                    id_parent)
                obj = obj_parent.tree.get_node(id_consumer_unit)
                self._func = obj.get_num_agents_in_consumer_unit

            elif (self._target == 'agent_status'):
                id_parent = obj_parent.get_id()
                if (not obj_parent.tree.is_agent_part_string(id_parent)):
                    print(
                        'rate_increase.initialize: Parent_id does is not from agent'
                    )
                    print('Id: ' + id_parent)
                    exit(255)
                obj = obj_parent.tree.get_node(
                    obj_parent.tree.get_agent_part(id_parent))
                self._func = obj.get_status

            else:
                print('\nUnknown target_function: #' + self._target + '#\n')
                print('rate: #' + self._name + '#\n')
                exit(255)


    def get_val(self):
        if (self._typus == 'constant'):
            return self._const_val

        elif (self._typus == 'target'):
            return self._num * self._mult

        elif (self._typus == 'target_function'):
            if (self._target == 'agent_status'):
                status = self._func()
                return self._dict[status]
            else:
                return self._func() * self._mult

        else:
            print('rate_increase.get_val: Unsupported typus: ' + self._typus)
            exit(255)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
