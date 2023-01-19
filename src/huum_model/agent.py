#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.05.16
#
# Changelog:
#
# 2019.05.16 - SBerendsen - start
# 2019.06.24 - SBerendsen - Different 'attachment points' for usage habits
# 2019.08.19 - SBerendsen - combined both usage habit lists into one ...
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
# ToDo:
#   - usage habit combination which is different from just adding
#   - usage habit with variable duration, etc
#   - usage habit tied to usage type instead to appliance
#   - usage habit chain
#   - lifecycle alternatives: allow each alternative to have an associated switch points
#   - refacture usage habit handling so that no new object needs to be created
#   - remove empty generation of probability record if no wants exist
#   - check "cyclical" and "cyclical_global" usage habit activations
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# general
import datetime
import sys

import numpy as np

# internal
from huum_io import agent as io_agent
from .elements import lifecycle
from .elements import ts_trapeze
from .elements import usage_template
from .elements.timed_effects import usage_habit
from .events import event_effect
from .util import base_parts
from .util import central_data_store
from .util import fifo_queue
from .util import number_output
from .util import rnd_wrapper
from .util import settings

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Agent(base_parts.BaseParts):  # class for each consumer unit / household

    _TARGETABLE_CHILD_OBJECTS = [
        '$event', '$storage', '$passedtime', '$lifestylehabit', '$usagehabit'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name: str):
        super().__init__(name, 'agent')

        # Living status --------------------------------------------------------
        self.lifestyle_habits              = {}
        self.life_style_habits_num_keys    = 0      # number of different keys

        # list for translating habit keys to numbers
        self.life_style_habits_list_keys   = {}
        self.life_style_habits_num_status  = 0      # number of different names

        # list for translating habit names to numbers
        self.life_style_habits_list_status = {}
        self.current_type                  = None
        self.status                        = None
        self.next_status_change            = None

        # Usage stuff ----------------------------------------------------------

        # list of usage habits (including those from events)
        self.usage_habits_add       = []    # usage habits for addition
        self.usage_habits_mult      = []    # usage habits for multiplication
        self.usage_habits_templates = []    # templates for specific usage behaviors
        self.sw_probability         = None  # probability record

        # Wait until -----------------------------------------------------------
        self.wait_for_what          = None  # For which appliance the daemon is waiting to be free
        self.wait_until             = None  # Until when the daemon has to wait
        self.wait_ts                = None  # adjusted time series data

        # Busy setting ---------------------------------------------------------
        self.busy_until             = None  # If the daemon is doing something, until when it blocks
        self.busy_with              = None  # what the agent is currently busy with

        # Action Queue ---------------------------------------------------------
        self.action_queue           = fifo_queue.FifoList()  # future action queue

        # extra information for habit output-ts --------------------------------
        self.__timeseries_formers   = []    # dict of things to adjusted for variable output TS
        # each entry contains a triplet of data: [<target>, <var>, <val>] with
        # target = targeted appliance; var = which variable of ts_trapeze should
        # be replaced and val = the probability_type object from which to take
        # the value

        # Holding results ------------------------------------------------------
        self.__probabilities        = []    # probabilities for current timestep


    @classmethod
    def loadFromFileData(cls, agent_data: io_agent.IOAgent,
                         cds: central_data_store.CentralDataStore):
        """
        Loads the agent data from a IO-model object.
        """

        cls = Agent(agent_data.id)

        # lifecycle related stuff
        for item in agent_data.lifecycle:
            obj = lifecycle.Habit.fromFileData(item, cds.get_compute_interval_sec())
            cls.add_lifestyle_habit(obj)

        # load usage habits
        for item in agent_data.usage_habits:
            obj = usage_habit.UsageHabit.fromFileData(item, cls.get_node_id, cds)
            cls.add_usage_habit(obj)

        # load usage habit templates
        for item in agent_data.habit_templates:
            obj = usage_template.UsageTemplate.fromFileData(item)
            cls.add_usage_habit_template(obj)

        # load common stuff
        cls.load_common(agent_data, cds.get_model_start_time(),
                        cds.get_compute_interval_sec())

        return cls


    def add_lifestyle_habit(self, habit: lifecycle.Habit):

        # sanity check
        if (habit.get_node_name() in self.life_style_habits_list_keys.keys()):
            print("Agent.add_lifestyle_habit: Error")
            print('Given key already exists', habit.get_node_name())
            exit(255)

        else:
            self.lifestyle_habits[habit.get_node_name()] = habit

        # add to overview list
        self.life_style_habits_num_keys += 1
        self.life_style_habits_list_keys[habit.get_node_name()] = self.life_style_habits_num_keys
        if not (habit.habit_status in
                self.life_style_habits_list_status.keys()):
            self.life_style_habits_num_status += 1
            self.life_style_habits_list_status[
                habit.habit_status] = self.life_style_habits_num_status


    def add_usage_habit(self,
                        habit: usage_habit.UsageHabit,
                        during_runtime=False):

        if (habit.habit_type == 'add'):
            self.usage_habits_add.append(habit)
            if (during_runtime):
                self.usage_habits_add[-1].register(self)
                self.usage_habits_add[-1].connect_uids()

        elif (habit.habit_type == 'mult'):
            self.usage_habits_mult.append(habit)
            if (during_runtime):
                self.usage_habits_mult[-1].register(self)
                self.usage_habits_mult[-1].connect_uids()

        else:
            print('\nagent.add_usage_habit:')
            print('Given usage habit has an unsupported no_change_val:',
                  habit.no_change_val)
            print('Habit:', habit.name)
            exit(255)


    def add_usage_habit_template(self, habit: usage_template.UsageTemplate):
        self.usage_habits_templates.append(habit)


    def add_usage_habit_from_template(self, name: str, uniqueID: str,
                                      start_tp: datetime.datetime,
                                      end_tp: datetime.datetime,
                                      habit_type: str, only_valid: str,
                                      arr_x: np.array, arr_y: np.array,
                                      time_step: int):
        """
        ToDo
            - refactor to take directly the template object
        """

        #
        habit_template = usage_habit.UsageHabit(name, uniqueID, start_tp,
                                                end_tp, habit_type, only_valid)
        habit_template.gen_data('linear', [arr_x, arr_y], time_step)
        self.add_usage_habit(habit_template)


    def add_timeseries_former(self, target: str, var, val):
        self.__timeseries_formers.append([target, var, val])


    def get_status(self):
        return self.status


    def initialize(self, file_lifestyle: str, file_wants: str,
                   file_blocking: str, directory: str, list_appliances: list,
                   parent_obj, cds: central_data_store.CentralDataStore,
                   cfg: settings.Config):
        """
        Setups the initial 'status' for everything

        file_lifestyle  - file to write lifestyle info to
        file_wants      - file to write wants info to
        file_blocking   - file to write blocking info to
        directory       - directory to write the info into
        list_appliances - list of appliances present within the consumer unit
        parent_obj      - link to parent object
        """

        # data structure housekeeping
        self.register_tree_node(parent_obj)
        self.base_register(directory + '/agent_' + self.get_node_name(), cds,
                           cfg)

        for habit in self.usage_habits_add:
            habit.register(self)

        for habit in self.usage_habits_mult:
            habit.register(self)

        for lifestyle_habit_key in self.lifestyle_habits:
            self.lifestyle_habits[lifestyle_habit_key].register(self)

        # --- Do initial output into overview(s) and lifestyle habits ----------
        if not (file_blocking is None):
            file_blocking.write(self.get_node_name() + '_wait_what;' +
                                self.get_node_name() + '_wait_until;' +
                                self.get_node_name() + '_busy_until;')

        if not (file_wants is None):
            file_wants.write(self.get_node_name() + ';')

        if not (file_lifestyle is None):
            file_lifestyle.write(self.get_node_name() + '_activity;' +
                                 self.get_node_name() + '_status;')


        # set initial status
        active_habit            = self.lifestyle_habits['initial']
        self.current_type       = 'initial'
        self.status             = active_habit.habit_status
        self.next_type          = active_habit.next_type.choose_alternative(cds)
        self.next_status_change = active_habit.get_activation_tp(
            active_habit.min_duration, cds.get_current_model_time(),
            cds.get_current_model_day())

        # setup usage habits as needed
        self.activate_usage_habits(cds)

        # write status legend
        if (not (cfg.headless or cfg.logging_type == 'none')) and cfg.log_lifecycle:
            f = open(
                directory + '/' + 'LegendInfo_' + self.get_node_name() +
                '_status.csv', 'w')
            f.write('Id;Status;\n')
            for key, value in self.life_style_habits_list_status.items():
                f.write(str(key) + ';' + str(value) + ';\n')
            f.close()
            f = open(
                directory + '/' + 'LegendInfo_' + self.get_node_name() +
                '_keys.csv', 'w')
            f.write('Id;Keys;\n')
            for key, value in self.life_style_habits_list_keys.items():
                f.write(str(key) + ';' + str(value) + ';\n')
            f.close()

        # --- Setup the own records output -------------------------------------

        # Probability record....................................................
        self.sw_probability = number_output.NumberOutput(
            directory + '/' + self.get_node_name() + '_probability_record.csv',
            len(list_appliances), list_appliances, cfg.log_probability,
            cds.get_single_file_probabilities(), self.get_full_node_id())

        # set initial probabilities to zero to avoid a mess with registering or not
        # => initial probabilities might be wrong
        self.__probabilities  = [0.0] * len(list_appliances)


    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()

        for habit in self.usage_habits_add:
            habit.connect_uids()

        for habit in self.usage_habits_mult:
            habit.connect_uids()

        for life_status in self.lifestyle_habits.values():
            life_status.connect_uids()


    def write_status(self, string: str):
        # try:
        #     string_type = self.life_style_habits_list_keys[self.current_type]
        # except KeyError:
        #     print('from self.life_style_habits_list_keys', self.current_type)
        #     exit(255)

        # try:
        #     string_status = self.life_style_habits_list_status[self.status]
        # except KeyError:
        #     print('from self.life_style_habits_list_status', self.status)
        #     print('stati:')
        #     for item in self.life_style_habits_list_status:
        #         print(item)
        #     exit(255)

        return (string +
                str(self.life_style_habits_list_keys[self.current_type]) +
                ';' + str(self.life_style_habits_list_status[self.status]) +
                ';')


    def write_blocking(self, string: str):
        string = ''

        if (self.wait_for_what is not None):
            string += self.wait_for_what + ';'
        else:
            string += 'None;'

        if (self.wait_until is not None):
            string += self.wait_until.isoformat(' ') + ';'
        else:
            string += 'None;'

        if (self.busy_until is not None):
            string += self.busy_until.isoformat(' ') + ';'
        else:
            string += 'None;'

        return string


    def update_events(self, current_tp: datetime.datetime,
                      func_add_event_queue_item):
        self.check_event_starts('Probability',
                                func_add_event_queue_item,
                                current_tp=current_tp)


    def update_storages(self, current_tp: datetime.datetime):
        self.update_storage_values(current_tp)


    def update(self, list_appliances: list,
               cds: central_data_store.CentralDataStore, func_add_event_queue):
        """
        Updates the model:daemon for the current timepoint

        Input
            list_appliances - list of appliances present
            current_tp      - current simulated timepoint
            last_tp         - last simulated timepoint

        Output
            impulse         - which appliance the daemon 'wants' to use
            ts              - ts_trapeze object to 
        """

        # main status ..........................................................
        if (self.next_status_change <= cds.get_current_model_time()):
            active_habit            = self.lifestyle_habits[self.next_type]
            self.current_type       = self.next_type
            self.status             = active_habit.habit_status
            self.next_type          = active_habit.next_type.choose_alternative(cds)
            next_habit              = self.lifestyle_habits[self.next_type]
            self.next_status_change = next_habit.get_activation_tp(
                active_habit.min_duration, cds.get_current_model_time(),
                cds.get_current_model_day())

            self.activate_usage_habits(cds)
            active_habit.check_event_starts('Activate', func_add_event_queue,
                                            cds.get_current_model_time())

        # cleanup of overdue habits ............................................
        habit_list = [
            elem for elem in self.usage_habits_add
            if elem.is_valid(cds.get_current_model_time()) is True
        ]
        if (len(habit_list) is not len(
                self.usage_habits_add)):  # saves unnecessary memory copying
            self.usage_habits_add = habit_list.copy()

        habit_list = [
            elem for elem in self.usage_habits_mult
            if elem.is_valid(cds.get_current_model_time()) is True
        ]
        if (len(habit_list) is not len(
                self.usage_habits_mult)):  # saves unnecessary memory copying
            self.usage_habits_mult = habit_list.copy()


        # usage probability (and output) .......................................
        for i, device in enumerate(list_appliances):

            if not (self.busy_with == device
                    or self.action_queue.is_in(device)):

                rand = rnd_wrapper.rnd_get_random_number()
                val = self.get_probability(device,
                                           cds.get_current_model_time(),
                                           cds.get_compute_interval_sec())
                if (val > rand):
                    self.action_queue.append(device)
                    self.__probabilities[i] = val

            else:
                self.__probabilities[i] = 0.0

        # if self.action_queue.size() > 0:
        #     print('Queue:', self.action_queue.size(),
        #           cds.get_current_model_time(), self.busy_with,
        #           self.busy_until, self.action_queue._data)

        # override by deferred appliance usage or being busy
        # blocks any other 'wants' or actions
        if self.busy_until is None:
            return self.action_queue

        else:

            if (self.busy_until < cds.get_current_model_time()):
                self.busy_until = None
                self.busy_with = None
                return self.action_queue
            else:
                return None


    def record_status(self, cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):

        self.sw_probability.write_record(np.array(self.__probabilities),
                                         cds.get_current_model_time(),
                                         cds.get_last_model_time())

        self.base_log(cds.get_current_model_time(), cds.get_last_model_time())


    def close(self, current_tp: datetime.datetime):
        """
        Finalizes anything still left open
        """
        self.sw_probability.close(current_tp)
        self.close_storages(current_tp)


    def get_probability(self, appliance_name: str,
                        current_tp: datetime.datetime, time_step: int):
        """
        Returns the current probability. First searches through the 'basic' ones, then
        the rest.

        appliance - name of appliance being looked at

        Returns:

        probability - the probability of that appliance being used
        """

        # search for multiplication
        probability_mult = 1.0
        for habit in self.usage_habits_mult:
            if (appliance_name == habit.appliance):
                if (habit.only_valid is None
                        or self.__check_status_part(habit.only_valid)):
                    val = habit.get_probability(current_tp, time_step)
                    probability_mult *= val  # careful, numbers can get big really fast...

        # stop if unnecessary to continue
        if (probability_mult == 0.0):
            return probability_mult

        # search for addition
        probability_add = 0.0
        for habit in self.usage_habits_add:
            if (appliance_name == habit.appliance):
                if (habit.only_valid is None
                        or self.__check_status_part(habit.only_valid)):
                    val = habit.get_probability(current_tp, time_step)
                    if (val != 0.0):
                        probability_add += val

        return probability_add * probability_mult


    def set_wait_until(self, date_time: datetime.datetime, impulse: str, ts):
        """
        Sets until when the daemon has to wait for an appliance to be free.

        date_time - TP, from which the appliance is useable again.
        impulse   - what appliance to wait for
        ts        - variable ts data
        """
        self.wait_until = date_time
        self.wait_for_what = impulse
        self.wait_ts = ts


    def set_busy_until(self, busy_until: datetime.datetime, busy_with: str):
        """
        Sets until when the daemon cannot do anything else.

        date_time - TP, until when the daemon is busy
        """
        self.busy_until = busy_until
        self.busy_with  = busy_with
        self.action_queue.remove_item(busy_with)


    def activate_usage_habits(self, cds: central_data_store.CentralDataStore):
        """
        Check which usage habit templates should be active and sets them up.
        """
        # remove the existing ones
        self.usage_habits_add = [
            item for item in self.usage_habits_add
            if item.is_valid(cds.get_current_model_time())
        ]
        self.usage_habits_mult = [
            item for item in self.usage_habits_mult
            if item.is_valid(cds.get_current_model_time())
        ]

        # setup the new ones
        for habit in self.usage_habits_templates:
            self.activate_usage_habit(habit, cds.get_current_model_time(),
                                      cds.get_model_start_time(),
                                      cds.get_compute_interval_sec())


    def activate_usage_habit(self, habit: usage_template.UsageTemplate,
                             current_tp: datetime.datetime,
                             start_tp: datetime.datetime, time_step: int):
        """
        Turns a habit template into an active habit.
        """
        if (self.__check_status_part(habit.only_valid)
                or habit.only_valid is None):

            if habit.typus == 'Cyclical_Global':
                diff_seconds = current_tp - start_tp
                start_time = current_tp - datetime.timedelta(seconds=(
                    diff_seconds.total_seconds() % habit.habit_length))

                while True:
                    end_time = min(
                        start_time +
                        datetime.timedelta(seconds=habit.habit_length),
                        self.next_status_change)
                    self.add_usage_habit_from_template(
                        habit.name, habit.uniqueID, start_time, end_time,
                        habit.habit_type, habit.only_valid, habit.arr_x,
                        habit.arr_y, time_step)
                    start_time = end_time

                    if end_time >= self.next_status_change:
                        break

            elif habit.typus == 'Cyclical':
                start_time = current_tp

                while True:
                    end_time = min(
                        start_time +
                        datetime.timedelta(seconds=habit.habit_length),
                        self.next_status_change)
                    self.add_usage_habit_from_template(
                        habit.name, habit.uniqueID, start_time, end_time,
                        habit.habit_type, habit.only_valid, habit.arr_x,
                        habit.arr_y, time_step)
                    start_time = end_time

                    if end_time >= self.next_status_change:
                        break

            elif habit.typus == 'Start':
                start_time = current_tp + datetime.timedelta(
                    seconds=habit.time_buffer)
                end_time = min(
                    current_tp + datetime.timedelta(seconds=habit.time_buffer +
                                                    habit.habit_length),
                    self.next_status_change)
                # print('Activating Start Time:', current_tp, start_tp, self.next_status_change, start_time, end_time)
                self.add_usage_habit_from_template(habit.name, habit.uniqueID,
                                                   start_time, end_time,
                                                   habit.habit_type,
                                                   habit.only_valid,
                                                   habit.arr_x, habit.arr_y,
                                                   time_step)

            elif habit.typus == 'End':
                start_time = self.next_status_change + datetime.timedelta(
                    seconds=habit.time_buffer - habit.habit_length)
                end_time = self.next_status_change - datetime.timedelta(
                    seconds=habit.time_buffer)
                # print('Activating End Time:  ', current_tp, start_tp, self.next_status_change, start_time, end_time)
                self.add_usage_habit_from_template(habit.name, habit.uniqueID,
                                                   start_time, end_time,
                                                   habit.habit_type,
                                                   habit.only_valid,
                                                   habit.arr_x, habit.arr_y,
                                                   time_step)

            else:
                print(
                    'Agent:activate_usage_habits: Unrecognised template type: '
                    + habit.typus)
                sys.exit(255)


    def exec_event(self,
                   action: list,
                   effect: event_effect.EventEffect,
                   **kwargs: dict):
        """
        Object implementation override.

        If the action is to delete something, ending the 'check for delete' with an
        underscore, it deletes anything with contains the string. Anything else, it
        only goes for the target given.

        action
            what should be done. Input is already disaggregated into components
        effect
            the effects obj

        Optional args for this:

        current_tp
            Current timepoint.
        time_start
            Start time
        timestep
            [int, sec] Current model timestep. Only works for static one.
        """

        # check for non-final item
        sub_parts = action[0].split("_")
        if (sub_parts[0] in self._TARGETABLE_CHILD_OBJECTS):

            # common parts
            if (self._is_base_part_element(sub_parts[0])):
                flag = self._get_base_part_down_node(action, effect, **kwargs)

            if (flag is False):
                # specific parts (currently catch all)
                print('\nAgent.exec_event: Error:')
                print('Action on _TARGETABLE_CHILD_OBJECTS not yet implemented.')
                print('Child Object:', print(sub_parts[0]))
                print('Whole Action:', print('.'.join(action)))
                exit(255)

        # probability ..........................................................
        elif (action[0] == 'probability'):
            if (action[1] == 'add'):
                self.add_usage_habit_from_template(
                    effect.name, effect.uniqueID, kwargs["time_start"],
                    kwargs["time_start"] +
                    datetime.timedelta(seconds=effect.habit_length),
                    effect.habit_type, effect.only_valid, effect.arr_x,
                    effect.arr_y, kwargs["timestep"])

            elif (action[1] == 'del'):

                # deal with addition habits
                if (effect[-1:] == '_'):
                    pattern_list = [
                        elem for elem in self.usage_habits_add
                        if elem.get_node_id()[0:len(effect)] is not effect
                    ]
                else:  # above implies: not general del
                    pattern_list = [
                        elem for elem in self.usage_habits_add
                        if elem.get_node_id() is not effect
                    ]

                self.usage_habits_add = pattern_list.copy()

                # deal with multiplication habits
                if (effect[-1:] == '_'):
                    pattern_list = [
                        elem for elem in self.usage_habits_mult
                        if elem.get_node_id()[0:len(effect)] is not effect
                    ]
                else:  # above implies: not general del
                    pattern_list = [
                        elem for elem in self.usage_habits_mult
                        if elem.get_node_id() is not effect
                    ]

                self.usage_habits_mult = pattern_list.copy()

            else:
                print('\nagent.exec_event: Unsupported action-type: #' +
                      str(action) + '#')
                print('Object type:', type(self).__name__, '\n')
                exit(255)

        # events ...............................................................
        elif (action[0] == 'event'):
            if (action[1] == 'activate'):
                counter = 0
                for event in self.get_events():
                    if (event.get_node_name() == action[2]):
                        counter += 1
                        event.set_active(True)

                # sanity check
                if (counter == 0):
                    print('\nEvent #' + action[2] + '# for agent ' +
                          self.get_id() + ' does not exist')
                    print('Object type:', type(self).__name__, '\n')
                    exit(255)
                elif (counter > 1):
                    print('\nMore than one occurrance of event with that name')
                    print('Event #' + action[2] + '# for agent ' +
                          self.get_id() + ' exists more than once')
                    print('Object type:', type(self).__name__, '\n')
                    exit(255)

            elif (action[1] == 'deactivate'):
                counter = 0
                for event in self.get_events():
                    if (event.get_node_name() == action[2]):
                        counter += 1
                        event.set_active(False)

                # sanity check
                if (counter == 0):
                    print('\nEvent #' + action[2] + '# for agent ' +
                          self.get_id() + ' does not exist')
                    print('Object type:', type(self).__name__)
                    exit(255)
                elif (counter > 1):
                    print('\nMore than one occurrance of event with that name')
                    print('Event #' + action[2] + '# for agent ' +
                          self.get_id() + ' exists more than once', '\n')
                    exit(255)

            else:
                print('\nagent.exec_event: Unsupported action-type: #' +
                      str(action) + '#')
                print('Object type:', type(self).__name__, '\n')
                exit(255)

        # Catch all ............................................................
        else:
            print('\nagent.exec_event: Unsupported action-target: #' +
                  str(action) + '#', '\n')
            exit(255)


    def __check_status_part(self, check_against):
        if (self.status[0:len(check_against)] == check_against):
            return True
        else:
            return False


    def __get_var_ts_data(self, appliance):
        """
        Generates the overload ts_trapeze data for a given appliance
        """
        output = None
        flag_output_setup = False

        for former in self.__timeseries_formers:
            if (former[0] == appliance):
                if (not flag_output_setup):
                    output = ts_trapeze.TSTrapeze()
                    flag_output_setup = True

                output.set_variable_value(former[1],
                                          former[2].get_probability_value())

        return output


    def _get_child_object(self, parts):
        """
        Overriden part of the base_connection method.
        """
        # print('gco:', type(self), parts)
        id_part = parts[0].split('_')
        if (id_part[0] in self._TARGETABLE_CHILD_OBJECTS):

            # check for base-part objects --------------------------------------
            if (self._is_base_part_element(id_part[0])):
                return self._get_base_part_node_object(parts)

            else:
                print('\nError: agent._get_child_object:')
                print('Not yet implemented _TARGETABLE_CHILD_OBJECTS:', id_part)
                print(f'Search ID:  {".".join(str(x) for x in parts)}')
                exit(255)

        else:
            return None


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        f.write("\n\n" + "  " * level + "- Agent:")
        f.write("\n" + "  " * level + f"  Name:                            {self.get_node_name()}")

        f.write("\n" + "  " * level + f"  Num Lifestyle Habits:            {len(self.lifestyle_habits)}")
        f.write("\n" + "  " * level + f"  Num Lifestyle Habits List Stati: {len(self.life_style_habits_list_status)}")

        if (len(self.usage_habits_add) > 0):
            f.write("\n\n" + "  " * level + f"  Num Usage Habits Add:            {len(self.usage_habits_add)}")
            f.write("\n" + "  " * level + "  Usage Habits Add:")
            for item in self.usage_habits_add:
                item.output_overview(f, level + 2)

        if (len(self.usage_habits_mult) > 0):
            f.write("\n\n" + "  " * level + f"  Num Usage Habits Mult:           {len(self.usage_habits_mult)}")
            f.write("\n" + "  " * level + "  Usage Habits Mult:")
            for item in self.usage_habits_mult:
                item.output_overview(f, level + 2)

        if (len(self.usage_habits_templates) > 0):
            f.write("\n\n" + "  " * level + f"  Num Usage Habit Templates:       {len(self.usage_habits_templates)}")
            f.write("\n" + "  " * level + "  Usage Habits Templates:")
            for item in self.usage_habits_templates:
                item.output_overview(f, level + 2)

        f.write("\n\n" + "  " * level + f"  Num Time Series Former:          {len(self.__timeseries_formers)}")
        f.write("\n" + "  " * level + f"  Num Probabilities:               {len(self.__probabilities)}")
        f.write("\n" + "  " * level + f"  Probabilities:                   {self.__probabilities}")

        f.write("\n" + "  " * level + f"  Current Habit:                   {self.current_type}")
        f.write("\n" + "  " * level + f"  Current Habit Status:            {self.status}")

        self.output_overview_base_parts(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
