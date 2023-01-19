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
# Base to class to add event related stuff.
#
# ------------------------------------------------------------------------------
#



# 0. Imports ===================================================================

# general
import datetime

# internal
from . import event
from ..util import rnd_wrapper


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class BaseEvent(object):   # class to be extended for each node

    def __init__(self):
        self.__events = []


    def load_events(self, events, time_step: int):
        for item in events:
            obj = event.Event.loadFromFileData(item, time_step)
            self.add_event(obj)


    def get_events(self):
        return self.__events


    def add_event(self, event):
        self.__events.append(event)


    def _get_named_event_object(self, name):
        for occurance in self.__events:
            if (occurance.get_node_name() == name):
                return occurance

        return None


    def exec_event(self, action, effect, **kwargs):
        """
        Object implementation override.
        Supposed to fail by default to indicate which classes should override.

        action  - what should be done. Input is already disaggregated into components
        effects - the effects obj  
        """
        print("Error: exec_event not overridden in extending class - fix!")
        print('Class:', self.get_node_type())
        exit(255)


    def register_events(self):
        for happening in self.__events:
            happening.register(self)


    def connect_events(self):
        for happening in self.__events:
            happening.connect()


    def check_event_starts(self,
                           event_type,
                           func_add_event_queue,
                           current_tp: datetime.datetime,
                           time_start=None):
        """
        Goes through all events and checks probability wise, whether they should be
        activated.

        event_type - what kind of event it is
        time_start - (refactor to using __**kwargs__) start time to be passed on
        """
        for happening in self.__events:
            if (happening.get_probability(event_type, current_tp) >=
                    rnd_wrapper.rnd_get_random_number()):
                happening.activate(func_add_event_queue, time_start=time_start)


    def output_overview_events(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview_events: Level not set')
            exit(255)

        f.write("\n" + "  " * level + f"Num Events:            {len(self.__events)}")



# 2. Functions =================================================================


# 3. Main Exec =================================================================
