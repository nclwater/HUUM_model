#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.10.28
#
# Changelog:
#
# 2019.10.28 - SBerendsen - start, based on storage stuff
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
# Base class for passed_time objects
#
# ------------------------------------------------------------------------------
#
# Todo:
#   - refactor this and *storage* for code-deduplication
#   - refarctor to use Pandas / timedelta for the conversion translator
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# internal
from ...events import base_event
from ...util import base_data
from ...util import date_parser
from ...util import table_1d

# external
import datetime
# import dateutil.parser


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class PassedTime(base_event.BaseEvent, base_data.BaseData):   # class to be extended for each node

    _TARGETABLE_CHILD_OBJECTS = [
        '$get', '$get_value_function'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name, start_tp: datetime.datetime, initial_time=None):

        base_data.BaseData.__init__(self, name, 'passedtime')
        base_event.BaseEvent.__init__(self)


        # set
        self.__translators     = {}                 # translator object to get from time-since-date to probability (type:table_1d)
        # always needs entry 'default'

        if (type(initial_time) == str):             # initial date & time to work from
            if (initial_time == '$model_t_start'):
                self.__date = start_tp
            else:
                try:
                    # self.__date = dateutil.parser.isoparse(initial_time)
                    self.__date = date_parser.parse_isodatetime(initial_time)
                except ValueError:
                    print('DateUtil could not get datetime from #' + initial_time + '#')
                    print('Expects a format of YYYY-MM-DD hh:mm')
                    exit()

                except Exception as error:
                    print('passed_time.PassedTime.init: Error:')
                    print('dateutil parser failed whily parsing #' + initial_time + '#')
                    print('Expects a format of YYYY-MM-DD hh:mm')
                    print('With error: ' + str(error))
                    exit()
        else:
            self.__date = initial_time


    @classmethod
    def loadFromFileData(cls, file_data, start_tp: datetime.datetime):
        cls = PassedTime(file_data.name,
                         start_tp,
                         initial_time=file_data.start_t)
        for item in file_data.translators:
            obj = table_1d.Table1d.loadFromFileData(item)
            cls.add_translator(item.active_for, obj)

        return cls


    def add_translator(self, key, translator):
        self.__translators[key] = translator


    def register(self, parent_obj, start_tp: datetime.datetime):
        self.register_tree_node(parent_obj)

        if (self.__date is None):
            self.__date = start_tp


    def check(self, current_tp: datetime.datetime):
        if ('default' not in self.__translators):
            print('\nError: passed_time.check:')
            print('\nKey _default_ not found in translator dictionary')
            exit(255)


    def get_timespan(self, current_tp: datetime.datetime):
        return current_tp - self.__date


    def get_timespan_seconds(self, current_tp: datetime.datetime):
        delta = current_tp - self.__date
        return delta.total_seconds()


    def get_val(self, current_tp: datetime.datetime, input_target='default'):

        delta = current_tp - self.__date

        if (input_target in self.__translators):
            return self.__translators[input_target].get_value(delta.total_seconds())
        else:
            return self.__translators['default'].get_value(delta.total_seconds())


    def set_time(self, current_tp: datetime.datetime, datum=None):
        if (datum is None):
            self.__date = current_tp
        else:
            self.__date = datum


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
                print('\nError: passed_time.eval_uid_part:')
                print('Unrecognised get target: #' + parts[0][5:] + '#')
                print('Expression:              #' + parts + '#')
                exit(255)
        else:
            print('\nError: passed_time.eval_uid_part:')
            print('Unrecognised action: in expression: #' + parts + '#')
            exit(255)


    def exec_event(self, action, effect, **kwargs):
        """
        Object implementation override

        action  - what should be done. Input is already disaggregated into components
        effects - the effects obj  

        Optional args for this:

        current_tp
            Current timepoint.
        time_start
            Start time
        """

        # storage ............................................................
        if (action[0] == 'passed_time'):
            if (action[1] == 'empty'):
                self.set_time(kwargs["current_tp"], effect)

            else:
                print('passed_time.exec_event: Unsupported action-type: #' +
                      str(action) + '# for target:passed_time')
                print('Passed_Time object name:', self.get_name())
                print('Passed_Time object UUID:', self.get_id())
                print('Effect:                 ', str(effect))
                print('time_start:             ', str(kwargs["time_start"]))
                exit(255)


        # Catch all ............................................................
        else:
            print('passed_time.exec_event: Unsupported action-target: #' +
                  str(action) + '#')
            print('Passed_Time object name:', self.get_name())
            print('Passed_Time object UUID:', self.get_id())
            print('Effect:                 ', str(effect))
            print('time_start:             ', str(kwargs["time_start"]))
            exit(255)



# 2. Functions =================================================================


# 3. Main Exec =================================================================
