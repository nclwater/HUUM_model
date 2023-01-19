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
# Base class for lifestyle habits
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import datetime

# internal
from ..events import base_event
from ..elements import alternatives
from ..util import base_data
from ..elements import conditionals
from ..elements import probability_type

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Habit(base_data.BaseData,
            base_event.BaseEvent):  # class for building the lifecycle

    _TARGETABLE_CHILD_OBJECTS = [
        '$event'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self,
                 name: str,
                 habit_status: str,
                 next_type,
                 probability_type,
                 min_duration=-1):

        base_data.BaseData.__init__(self, name, 'lifestylehabit')
        base_event.BaseEvent.__init__(self)

        self.habit_status     = habit_status.lower()
        self.next_type        = next_type
        self.probability_type = probability_type
        if (min_duration is
                None):  # minimum duration of previous habit stage in [sec]
            self.min_duration = -1
        else:
            self.min_duration = min_duration


    @classmethod
    def fromFileData(cls, file_data, time_step: int):

        # generate future alternatives
        possibilities = alternatives.Alternatives(file_data.next_default)
        for alt in file_data.next:
            cond = conditionals.Condition.fromString(alt.condition)
            possibilities.add_alternative(alt.target, cond, alt.target)

        # generate lifestyle habit
        prob = probability_type.ProbabilityType.fromFileData(
            file_data.probability, cls)
        cls = Habit(file_data.name,
                    file_data.habit_status,
                    possibilities,
                    prob,
                    min_duration=file_data.min_duration)

        # add anything else
        cls.load_events(file_data.events, time_step)

        return cls


    def register(self, parent_obj):
        self.register_tree_node(parent_obj)
        self.register_events()


    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()


    def get_activation_tp(self, min_duration, current_tp: datetime.datetime,
                          current_day: datetime.datetime):
        """
        Returns the next activation timepoint.

        min_duration - minimum duration for habit
        """

        # prep minimum length
        minimum_extend = current_tp + datetime.timedelta(
            seconds=min_duration) - current_day

        # default given interval
        if (self.min_duration > 0):
            time_target = max(
                minimum_extend,
                self.probability_type.get_activation_tp()) + current_day
        else:
            time_target = self.probability_type.get_activation_tp(
            ) + current_day

        # sanity check that next TP isn't in the past
        if (current_tp > time_target):
            time_target = time_target + datetime.timedelta(days=1)

        return time_target


# 2. Functions =================================================================


# 3. Main Exec =================================================================
