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
#
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# general
import datetime
import os

# internal
from . import consumer_unit
from .util import base_parts
from .util import central_data_store
from .util import settings
from huum_io import holding as io_holding

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Holding(base_parts.BaseParts):  # holds the info for a whole property

    _TARGETABLE_CHILD_OBJECTS = [
        '$cu', '$event', '$storage', '$passedtime'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name: str):
        super().__init__(name, 'holding')

        self.consumer_units = []

    def load(self, holding_data: io_holding.IOHolding,
             cds: central_data_store.CentralDataStore):
        """
        Loads the model data from a IO-model object.
        """
        for item in holding_data.cu:
            obj = consumer_unit.ConsumerUnit(item.id)
            obj.load(item, cds)
            self.add_consumer_unit(obj)

        # load common stuff
        self.load_common(holding_data, cds.get_model_start_time(),
                         cds.get_compute_interval_sec())

    def add_consumer_unit(self, consumer_unit: consumer_unit.ConsumerUnit):
        self.consumer_units.append(consumer_unit)

    def initialize(self, prefix: str, parent_obj,
                   cds: central_data_store.CentralDataStore,
                   cfg: settings.Config):
        """
        Setups the initial 'status' for everything

        prefix    - prefix of the output directory
        parent_id - id of the parent node in the dependency tree
        """

        # data structure housekeeping ------------------------------------------
        self.register_tree_node(parent_obj)
        self.base_register(prefix + '/holding_' + self.get_node_name(), cds,
                           cfg)

        for cu in self.consumer_units:
            if not (cfg.headless
                    or cfg.logging_type == 'none' or cfg.log_as_single):
                os.makedirs(prefix + '/', exist_ok=True)
            cu.initialize(prefix + '/' + self.get_node_name() + '/', self, cds,
                          cfg)

    def connect_uids(self):
        """
        Overridden function implementation.
        """
        self.connect_events()
        for cu in self.consumer_units:
            cu.connect_uids()

    def update_events(self, current_tp: datetime.datetime,
                      func_add_event_queue_item):
        self.check_event_starts('Probability',
                                func_add_event_queue_item,
                                current_tp=current_tp)
        for cu in self.consumer_units:
            cu.update_events(current_tp, func_add_event_queue_item)

    def update_storages(self, current_tp: datetime.datetime):
        self.update_storage_values(current_tp)
        for cu in self.consumer_units:
            cu.update_storages(current_tp)

    def update(self, cds: central_data_store.CentralDataStore,
               cfg: settings.Config, func_add_event_queue):
        """
        Updates the model for the timepoint
        """
        for cu in self.consumer_units:
            cu.update(cds, cfg, func_add_event_queue)

    def record_status(self, cds: central_data_store.CentralDataStore,
                      cfg: settings.Config):

        for cu in self.consumer_units:
            cu.record_status(cds, cfg)

        self.base_log(cds.get_current_model_time(), cds.get_last_model_time())

    def close(self, current_tp: datetime.datetime):
        for cu in self.consumer_units:
            cu.close(current_tp)
        self.close_storages(current_tp)

    def return_results(self):
        results = []
        for item in self.consumer_units:
            results.extend(item.return_results())

        return results

    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        f.write("\n\n" + "  " * level + "- Holding:")
        f.write("\n" + "  " * level + f"  Name: {self.get_node_name()}")

        f.write("\n\n" + "   " * level + " Consumer Units:")
        for cu in self.consumer_units:
            cu.output_overview(f, level + 1)

        self.output_overview_base_parts(f, level + 1)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
