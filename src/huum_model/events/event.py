#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.04
#
# Changelog:
#
# 2019.06.04 - SBerendsen - start
# 2019.07.31 - SBerendsen - added an active/deactive status switch
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
#
# ToDo
#   - figure out how to set the exec timepoint
#   - make probability more flexible (a la usage habits)
#   - make unique-id more flexible and unique
#   - make dealing with the when the check is run, simpler (indicator primes?)
#   - allow removal over longer term effects
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# Internal
from ..util import base_data
from ..elements import probability_type as prob_type
from . import event_effect

# External
import datetime

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Event(base_data.BaseData):  # class to hold event relevant data

    _TARGETABLE_CHILD_OBJECTS = [
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self,
                 name,
                 event_type,
                 probability=None,
                 switch=False,
                 active=True):

        # main part
        base_data.BaseData.__init__(self, name, 'event')

        self.__event_type  = event_type   # how the event is being run (on/off _Switch_, _Probability_)

        self.__probability = probability  # event_type == 'probability': execution probability to get activated
        self.__switch      = switch       # event_type == 'switch': initial switch status (on/off = true/false)

        self.__active      = active       # whether the event is active or not

        self.__effects     = []


    @classmethod
    def loadFromFileData(cls, file_data, time_step: int):

        cls = Event(file_data.name,
                    file_data.type,
                    probability=None,
                    switch=file_data.switch,
                    active=file_data.active)

        # deal with probabilty
        if (file_data.probability is not None):
            prob = prob_type.ProbabilityType.fromFileData(
                file_data.probability, cls)
            cls._set_probability(prob)

        for item in file_data.effects:
            obj = event_effect.EventEffect.loadFromFileData(item, cls, time_step)
            cls.add_effect(obj)

        return cls


    def _set_probability(self, prob):
        self.__probability = prob


    def add_effect(self, effect):
        self.__effects.append(effect)


    def get_event_type(self):
        return self.__event_type


    def register(self, parent_obj):
        """
        Adds the event to the tree

        root - object id the event is rooted to.
        """
        self.register_tree_node(parent_obj)


    def connect(self):
        """
        Resolves the internal UID to a function callback.
        """
        for effect in self.__effects:
            effect.connect(self)


    def check(self):
        if (self.__event_type == 'Probability'):
            pass
        elif (self.__event_type == 'Switch'):
            pass
        elif (self.__event_type == 'Activate'):
            pass
        else:
            print('EventSetup: Event ' + self.get_node_name() +
                  ' has unsupported event type ' + self.__event_type)
            exit(255)


    def get_probability(self, event_type: str, current_tp: datetime.datetime):
        prob = 0.0

        # exit, if inactive
        if not (self.__active):
            return prob

        # exit if wrong event type
        if (event_type != self.__event_type):
            return prob

        if (event_type == 'Activate'):
            return 1.0

        # test for a true/false switch
        if (self.__event_type == 'Switch'):
            if (self.__switch):
                prob = 1.0

        # probability type
        elif (self.__event_type == 'Probability'):
            prob = self.__probability.get_probability_value(current_tp)

        else:
            print('get_probability: unsupported event type: ' + event_type +
                  ' for event: ' + self.get_full_node_id())
            exit(255)

        return prob


    def activate(self, func_add_event_queue_item, time_start=None):

        for effect in self.__effects:
            func_add_event_queue_item(effect, time_start=time_start)

        return


    def exec_event(self,
                   action,
                   effect,
                   **kwargs):
        """
        Object implementation override.

        If the action is to delete something, ending the 'check for delete' with an
        underscore, it deletes anything with contains the string. Anything else, it
        only goes for the target given.

        action     - what should be done. Input is already disaggregated into components
        effect     - the effects obj  
        """

        if (action[0] == 'event'):
            if (action[1] == 'activate'):
                self.set_active(True)

            elif (action[1] == 'deactivate'):
                self.set_active(False)

            else:
                print('event.exec_event: Unsupported action-type: #' +
                      str(action) + '#')
                print('Object type:', type(self).__name__)
                exit(255)

        # Catch all ............................................................
        else:
            print('event.exec_event: Unsupported target-type: #' +
                  str(action) + '#')
            print('Object type:', type(self).__name__)
            exit(255)


    def set_active(self, status=True):
        """
        Sets the event's active/de-activated status.

        status - specific status (true/false)
        """
        self.__active = status


# 2. Functions =================================================================

# 3. Main Exec =================================================================
