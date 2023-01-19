#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.08.06
#
# Changelog:
#
# 2019.08.06 - SBerendsen - start
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
# Base class for inheritance usage of storages
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# Internal
from ...util import central_data_store
from ...util import settings
from ...util import number_output
from . import storage

# External
import datetime
import numpy as np


# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class BaseStorage(object):   # class to be extended for each node

    def __init__(self):
        self.__storages       = []
        self.__log_storages   = None
        self.__sw_storages    = None    # string de-duplicator for storage overview output
        self.__array_storages = []


    def load_storages(self, storages):
        for item in storages:
            obj = storage.Storage.loadFromFileData(item)
            self.add_storage(obj)


    def add_storage(self, storage):
        self.__storages.append(storage)


    def register_storages(self, prefix,
                          cds: central_data_store.CentralDataStore,
                          cfg: settings.Config):
        """
        Registers all the storages with the data tree & sets up local output.

        prefix - prefix of the output filename & -path for logging storage data
        """

        # register
        for store in self.__storages:
            store.register(self)

        # output
        self.__log_storages = cfg.get_log_storages
        if (len(self.__storages) > 0 and self.__log_storages()):
            header = []
            self.__array_storages = [None] * len(self.__storages)
            for store in self.__storages:
                header.append(store.get_node_name())
            self.__sw_storages = number_output.NumberOutput(
                prefix + '_storages.csv', len(self.__storages), header,
                cfg.log_storages, cds.get_single_file_storages(),
                self.get_full_node_id())


    def update_storage_values(self, current_tp: datetime.datetime):
        for store in self.__storages:
            store.update(current_tp)


    def log_storages(self, current_time: datetime.datetime,
                     last_time: datetime.datetime):
        if (len(self.__storages) > 0 and self.__log_storages()):

            for i, store in enumerate(self.__storages):
                self.__array_storages[i] = store.get_volume()

            self.__sw_storages.write_record(np.array(self.__array_storages),
                                            current_time, last_time)


    def close_storages(self, current_time: datetime.datetime):
        if (len(self.__storages) > 0 and self.__log_storages()):
            self.__sw_storages.close(current_time)


    def error_storage_no_node(self, str_class: str, parts: list):
        print(f'\nError: {str_class}._get_child_object:')
        print(f'{str_class} object with {parts[0]} does not exist')
        print(f'Search ID:  {".".join(str(x) for x in parts)}')
        self.print_node_id_list_storage()
        exit(255)


    def print_node_id_list_storage(self):
        print('\nAttached storages:')
        for store in self.__storages:
            print(f'   {store.get_node_id()}')


    def _get_ided_storage_object(self, obj_id):
        for store in self.__storages:
            if (store.get_node_id() == obj_id):
                return store

        return None


    def output_overview_storages(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview_storages: Level not set')
            exit(255)

        f.write("\n" + "  " * level + f"Num Storages:          {len(self.__storages)}")







# 2. Functions =================================================================


# 3. Main Exec =================================================================
