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
import numpy as np
import pandas as pd
import os

# 1. Global vars ===============================================================
_filter_types = ['none', 'all', 'simple', 'complex']


# ------------------------------------------------------------------------------
class NumberOutput:  # removes identical content lines as well as lines with constant increases

    # class variables (shared settings - both should be function callbacks)
    _headless = None
    _filter_type = None
    _single_file = False

    # class object specific stuff
    def __init__(self, filename: str, nr_entries: int, column_names: list,
                 should_log: bool, file_single_output, source_id: str):

        # header
        if (NumberOutput._single_file()):
            self._header = []
        else:
            self._header = ['Time']
        self._header.extend(column_names)

        # deal with the output target
        self._filename = filename

        # internal data stuff
        self.last_array = np.full(nr_entries, np.NaN)
        self.last_array_delta = np.full(nr_entries, np.NaN)
        self.last_array_size = len(column_names)
        self.set_array = False
        self.set_array_delta = False
        self.last_tp_written = datetime.datetime(year=1, month=1, day=1)

        # headless or not
        if (NumberOutput._headless() or NumberOutput._filter_type() == 'none'
                or not should_log):
            self._file = None
            self._dict = None
            self._df = None

        elif (NumberOutput._single_file()):
            self._file = file_single_output
            if not (self._file is None):
                header = ''
                for item in self._header:
                    header += f'{source_id}#{item};'
                self._file.write(header)

        else:
            directory = os.path.dirname(self._filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            self._file = open(self._filename, 'w')
            header = ''
            for item in self._header:
                header += item + ';'
            self._file.write(header + '\n')

        # function linking
        if (NumberOutput._filter_type() == 'none' or not should_log):
            self._write_func = self._write_nothing

        elif (NumberOutput._headless()):
            if (NumberOutput._filter_type() == 'all'):
                self._write_func = self._write_full_headless

            elif (NumberOutput._filter_type() == 'simple'):
                self._write_func = self._write_simple_filter_headless

            elif (NumberOutput._filter_type() == 'complex'):
                self._write_func = self._write_complex_filter_headless

        elif (NumberOutput._single_file()):
            if (self._file is None):
                self._write_func = self._write_nothing
            else:
                self._write_func = self._write_single_file

        else:
            if (NumberOutput._filter_type() == 'all'):
                self._write_func = self._write_full

            elif (NumberOutput._filter_type() == 'simple'):
                self._write_func = self._write_simple_filter

            elif (NumberOutput._filter_type() == 'complex'):
                self._write_func = self._write_complex_filter

    def write_record(self, string: str, current_tp: datetime.datetime,
                     last_tp: datetime.datetime):
        self._write_func(string, current_tp, last_tp)

    def get_results(self, prefix=''):
        if (NumberOutput._headless()):

            if prefix != '':
                cols = [f'{prefix}_{x}' for x in self._header]

            else:
                cols = self._header

            self._df = pd.DataFrame.from_dict(self._dict,
                                              orient='index',
                                              columns=cols)
            self._df.index = pd.to_datetime(self._df.index)
            return self._df
        else:
            print('\nError: number_output.get_results:')
            print("Run wasn't headless")
            exit(255)

    def close(self, current_tp: datetime.datetime):
        # check to see whether a last write is needed
        if (self.last_tp_written != current_tp
                and not NumberOutput._filter_type() == 'none'):
            if (NumberOutput._headless() and not (self._dict is None)):
                self._dict[current_tp.isoformat(' ')] = self.last_array

            else:
                if not (self._file is None):
                    if not (self._single_file()):
                        self._file.write(current_tp.isoformat(' ') + ';')
                        self._file.write(';'.join(
                            [str(x) for x in self.last_array]))
                        self._file.write(';\n')

        if not (self._file is None or self._single_file()):
            self._file.close()

    def _write_nothing(self, np_array: np.array, current_tp: datetime.datetime,
                       last_tp: datetime.datetime):
        """
        Dummy "write to file" to test perf impact of logic.

        array  - data array to output to file
        """
        pass

    def _write_full(self, np_array: np.array, current_tp: datetime.datetime,
                    last_tp: datetime.datetime):
        """
        Remembers the output

        array  - data array to output to file
        """
        if not (self.set_array):

            self._file.write(current_tp.isoformat(' ') + ';')
            self._file.write(';'.join([str(x) for x in np_array]) + ';\n')

            self.set_array = True

        else:
            self._file.write(last_tp.isoformat(' ') + ';')
            self._file.write(';'.join([str(x)
                                       for x in self.last_array]) + ';\n')

    def _write_full_headless(self, np_array: np.array,
                             current_tp: datetime.datetime,
                             last_tp: datetime.datetime):
        """
        Remembers the output

        array  - data array to output to file
        """
        if not (self.set_array):
            self._dict = {}
            self.set_array = True

        self._dict[current_tp.isoformat(' ')] = np_array

    def _write_simple_filter(self, np_array: np.array,
                             current_tp: datetime.datetime,
                             last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries

        array  - data array to output to file
        """

        # sanity check
        # if (len(array) != len(self.last_array)):
        #     print('\nnumber_output:write')
        #     print('Size of given array and set array are different')
        #     print('\nGiven:', len(array))
        #     print(array)
        #     print('Set:  ', len(self.last_array))
        #     print(self.last_array)
        #     print('Header:')
        #     print(self._header)
        #     exit(255)

        # decide what to do
        if not (self.set_array):

            self._file.write(current_tp.isoformat(' ') + ';')
            self._file.write(';'.join([str(x) for x in np_array]) + ';\n')

            self.last_array = np_array
            self.set_array = True
            self.last_tp_written = current_tp

        else:
            if not (np.allclose(
                    self.last_array, np_array, rtol=0.0, atol=1e-15)):

                self._file.write(last_tp.isoformat(' ') + ';')
                self._file.write(';'.join([str(x)
                                           for x in self.last_array]) + ';\n')

                self.last_tp_written = current_tp

            self.last_array = np_array

    def _write_simple_filter_headless(self, np_array: np.array,
                                      current_tp: datetime.datetime,
                                      last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries

        array  - data array to output to file
        """

        # sanity check
        # if (len(array) != len(self.last_array)):
        #     print('\nnumber_output:write')
        #     print('Size of given array and set array are different')
        #     print('\nGiven:', len(array))
        #     print(array)
        #     print('Set:  ', len(self.last_array))
        #     print(self.last_array)
        #     print('Header:')
        #     print(self._header)
        #     exit(255)

        # decide what to do
        if not (self.set_array):

            self.last_array = np_array
            self.set_array = True
            self.last_tp_written = current_tp

            self._dict = {}
            self._dict[current_tp.isoformat(' ')] = np_array

        else:
            if not (np.allclose(
                    self.last_array, np_array, rtol=0.0, atol=1e-15)):

                self._dict[current_tp.isoformat(' ')] = np_array

                self.last_tp_written = current_tp

            self.last_array = np_array

    def _write_complex_filter(self, np_array: np.array,
                              current_tp: datetime.datetime,
                              last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries

        array  - data array to output to file
        """

        # sanity check
        # if (len(array) != len(self.last_array)):
        #     print('\nnumber_output:write')
        #     print('Size of given array and set array are different')
        #     print('\nGiven:', len(array))
        #     print(array)
        #     print('Set:  ', len(self.last_array))
        #     print(self.last_array)
        #     print('Header:')
        #     print(self._header)
        #     exit(255)

        # decide what to do
        if (not self.set_array and not self.set_array_delta):

            self._file.write(current_tp.isoformat(' ') + ';')
            self._file.write(';'.join([str(x) for x in np_array]) + ';\n')

            self.last_array = np_array
            self.set_array = True
            self.last_tp_written = current_tp

        elif (self.set_array and not self.set_array_delta):
            self.last_array_delta = np_array - self.last_array
            self.set_array_delta = True

            # only output for distinct lines (only backwards check, forward is still todo)
            if (not np.allclose(np_array, self.last_array, 1e-05, 1e-08)):
                self.last_array = np_array
                self.last_tp_written = current_tp

        elif (self.set_array and self.set_array_delta):
            delta = np_array - self.last_array

            if (not np.allclose(
                    delta, self.last_array_delta, rtol=0.0, atol=1e-15)):

                self._file.write(last_tp.isoformat(' ') + ';')
                self._file.write(';'.join([str(x)
                                           for x in self.last_array]) + ';\n')

                self.last_tp_written = current_tp

            self.last_array = np_array
            self.last_array_delta = delta

        else:
            print('number_output_Float.write:')
            print('Unmanaged case for output setting:')
            print('set_output:', self.set_array)
            print('set_delta: ', self.set_array_delta)
            exit(255)

    def _write_complex_filter_headless(self, np_array: np.array,
                                       current_tp: datetime.datetime,
                                       last_tp: datetime.datetime):
        """
        Writes the string to file while removing lines with duplicate entries

        array  - data array to output to file
        """

        # sanity check
        # if (len(array) != len(self.last_array)):
        #     print('\nnumber_output:write')
        #     print('Size of given array and set array are different')
        #     print('\nGiven:', len(array))
        #     print(array)
        #     print('Set:  ', len(self.last_array))
        #     print(self.last_array)
        #     print('Header:')
        #     print(self._header)
        #     exit(255)

        # decide what to do
        if (not self.set_array and not self.set_array_delta):

            self._dict = {}
            self._dict[current_tp.isoformat(' ')] = np_array

            self.last_array = np_array
            self.set_array = True
            self.last_tp_written = current_tp

        elif (self.set_array and not self.set_array_delta):
            self.last_array_delta = np_array - self.last_array
            self.set_array_delta = True

            # only output for distinct lines (only backwards check, forward is still todo)
            if (not np.allclose(np_array, self.last_array, 1e-05, 1e-08)):
                self.last_array = np_array
                self.last_tp_written = current_tp

        elif (self.set_array and self.set_array_delta):
            delta = np_array - self.last_array

            if (not np.allclose(
                    delta, self.last_array_delta, rtol=0.0, atol=1e-15)):

                self._dict[current_tp.isoformat(' ')] = np_array

                self.last_tp_written = current_tp

            self.last_array = np_array
            self.last_array_delta = delta

        else:
            print('number_output_Float.write:')
            print('Unmanaged case for output setting:')
            print('set_output:', self.set_array)
            print('set_delta: ', self.set_array_delta)
            exit(255)

    def _write_single_file(self, np_array: np.array,
                           current_tp: datetime.datetime,
                           last_tp: datetime.datetime):
        """
        Writes the string to file, adjusted for single file output.

        array  - data array to output to file
        """
        self._file.write(';'.join([str(x) for x in np_array]) + ';')


# 2. Functions =================================================================


def setup_class_vars(headless: bool, output_filter: str, single_file: bool):
    NumberOutput._headless = headless
    NumberOutput._filter_type = output_filter
    NumberOutput._single_file = single_file

    if not (NumberOutput._filter_type() in _filter_types):
        print('\nError: number_output.initialise:')
        print(
            f'Given filter type #{NumberOutput._filter_type()}# is not supported'
        )
        print('Supported types:', _filter_types)
        exit(255)


# 3. Main Exec =================================================================
