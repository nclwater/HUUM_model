#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.10
#
# Changelog:
#
# 2019.06.10 - SBerendsen - start
# 2020.04.26 - SBerendsen - Replaced branches by callbacks for easier testing
# 2020.07.28 - SBerendsen - extracted into separate file and renamed
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
# De-duplicates string lines for CSV-output
#
# ------------------------------------------------------------------------------
#
# ToDo
#   - rework using a numbered scale
#   - refactor to lessen duplicate code
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# external
import datetime
import os

# 1. Global vars ===============================================================
_filter_types = ['none', 'all', 'simple', 'complex']


# 1.1 Classes ------------------------------------------------------------------
class StringOutput:  # class to de-duplicate string output (datetime different, but removes identical content)

    # class variables (shared settings - both should be function callbacks)
    _headless    = None
    _filter_type = None
    _single_file = False

    # class object specific stuff
    def __init__(self, filename: str, should_log: bool):

        # setup variables
        self._file = None

        self._write_func      = None        # function call back to the actually used write function
        self._fn              = filename
        self._last_string     = ""
        self._last_tp_written = datetime.datetime(year=1, month=1, day=1)

        # do the work
        if (self._headless() or StringOutput._filter_type() == 'none'
                or not should_log):
            self._file       = None
            self._write_func = self._write_nothing

        else:
            directory = os.path.dirname(self._fn)
            if not os.path.exists(directory):
                os.makedirs(directory)
            self._file = open(self._fn, 'w')

            if (StringOutput._filter_type() == 'all'):
                self._write_func = self._write_full

            elif (StringOutput._filter_type() in ['simple', 'complex']):
                self._write_func = self._write_simple_filter


    def get_file(self):
        return self._file


    def direct_write(self, string: str):
        """
        Writes a value directly to file, if output is enabled.
        """
        if not (self._file is None):
            self._file.write(string)


    def write(self, string: str, current_tp: datetime.datetime,
              last_tp: datetime.datetime):
        self._write_func(string, current_tp, last_tp)


    def close(self, current_tp: datetime.datetime):

        # check to see whether a last write is needed
        if (self._headless() or self._filter_type() == 'none'
                or self._file is None):
            pass

        else:
            if (self._last_tp_written != current_tp):
                self._file.write(current_tp.isoformat(' ') + ';')
                self._file.write(self._last_string + '\n')

            self._file.close()


    def _write_full(self, string: str, current_tp: datetime.datetime,
                    last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries.
        """
        # write new status
        self._file.write(current_tp.isoformat(' ') + ';')
        self._file.write(string + '\n')
        self._last_tp_written = current_tp


    def _write_simple_filter(self, string: str, current_tp: datetime.datetime,
                             last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries.
        """
        if not (self._headless()):
            if (string != self._last_string):

                # write last status. if needed, to get the form correct
                if (last_tp > self._last_tp_written
                        and self._last_string is not None):
                    self._file.write(last_tp.isoformat(' ') + ';')
                    self._file.write(self._last_string + '\n')

                # write new status
                self._file.write(current_tp.isoformat(' ') + ';')
                self._file.write(string + '\n')
                self._last_string     = string
                self._last_tp_written = current_tp


    def _write_nothing(self, string: str, current_tp: datetime.datetime,
                       last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries.
        """
        pass


# 2. Functions =================================================================


def setup_class_vars(headless: bool, output_filter: str, single_file: bool):
    StringOutput._headless    = headless
    StringOutput._filter_type = output_filter
    StringOutput._single_file = single_file

    if not (StringOutput._filter_type() in _filter_types):
        print('\nError: string_output.initialise:')
        print(f'Given filter type #{StringOutput._filter_type()}# is not supported')
        print('Supported types:', _filter_types)
        exit(255)


# 3. Main Exec =================================================================
