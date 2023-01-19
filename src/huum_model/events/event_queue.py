#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.07.06
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
# Deals with the organising the event queue
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# general
import datetime
import os

# internal
from . import event_queue_item
from ..util import central_data_store
from ..util import settings

# 1. Global vars ===============================================================
_num_executed_events = 0


# 1.1 Classes ------------------------------------------------------------------
class EventQueue():  # class to be extended for each node

    def __init__(self):

        self.__event_queue = [
        ]  # queue of event effects not the event themselves


    def setup_event_queue(self, model_name: str, cfg: settings.Config):
        directory = cfg.output_prefix + '/' + model_name + '/'
        if (cfg.headless or cfg.logging_type == 'none' or not cfg.log_events):
            self.__f_event_log = None
        else:
            os.makedirs(directory, exist_ok=True)
            self.__f_event_log = open(directory + 'Event_Effects.log', 'w')
            self.__f_event_log.write('Event log for run started on ' +
                                     str(datetime.datetime.now()) + '\n')


    def close_event_queue(self):
        if not (self.__f_event_log is None):
            self.__f_event_log.close()


    def add_event_queue_item(self, effect, time_start=None):
        """
        Redo using kwargs
        """
        self.__event_queue.append(
            event_queue_item.EventQueueItem(effect, time_start))


    def remove_event_queue_item(self, event):
        self.__event_queue.remove(event)


    def work_event_queue(self, cds: central_data_store.CentralDataStore):
        """
        ToDo: Improve the execution order (as in 'del' before 'add' and similar)
        """
        while (len(self.__event_queue) > 0):
            work_queue = self.__event_queue
            self.__event_queue = []
            if not (self.__f_event_log is None):
                self.__f_event_log.write(
                    '\nEvents at sim-time ' +
                    cds.get_current_model_time().isoformat(' ') + '\n')
                self.__f_event_log.write('Queue Items present: ' +
                                         str(len(work_queue)) + '\n')

            cnt = len(work_queue)
            for item in work_queue:
                global _num_executed_events
                _num_executed_events = _num_executed_events + 1
                if not (self.__f_event_log is None):
                    self.__f_event_log.write(
                        str(cnt) + ': ' + str(item.effect) + '\n')
                item.effect.execute(cds, time_start=item.val)
                cnt -= 1


    def output_overview_event_queue(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(
                f'{self.get_node_name()}.output_overview_event_queue: Level not set'
            )
            exit(255)

        f.write("\n" + "  " * level +
                f"Num Executed Events:   {_num_executed_events}")
        f.write("\n" + "  " * level +
                f"Num Event Queue Items: {len(self.__event_queue)}")
        if (len(self.__event_queue) > 0):
            f.write("\n" + "  " * level + "Event Queue Items:")
            for item in self.__event_queue:
                item.output_overview(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
