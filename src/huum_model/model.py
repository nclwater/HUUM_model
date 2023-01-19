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
import gc
import os
import shutil
from tqdm import tqdm

# internal
from . import holding
from .events import base_event
from .events import event_queue
from .graph import base_connection
from .translators.passed_time import base_passed_time
from .translators.storage import base_storage
from .util import central_data_store
from .util import rnd_wrapper
from .util import settings
from .util import string_output
from .util import number_output
from huum_io import model

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Model(base_connection.BaseConnection, base_event.BaseEvent,
            event_queue.EventQueue, base_storage.BaseStorage,
            base_passed_time.BasePassedTime
            ):  # holds the info for a whole model

    _TARGETABLE_CHILD_OBJECTS = [
        '$holding', '$event', '$storage', '$passedtime'
    ]  # which child objects are targetable. Needs to be set in each class extensions

    def __init__(self, name: str, cfg: settings.Config):

        # data stuff
        self.holdings        = []
        self.cfg             = cfg
        self.__simtime       = None
        self._single_file_ts = None

        # cleanup output folder
        if not (cfg.headless):
            shutil.rmtree(self.cfg.output_prefix + '/' + name,
                          ignore_errors=True)

        # get timestep (replace!)
        if (self.cfg.t_step_min != self.cfg.t_step_max):
            print('\nModel.__init__: Error')
            print('Currently a variable timestep is not allowed')
            exit(255)
        else:
            time_step = self.cfg.t_step_min

        # model item setup
        base_connection.BaseConnection.__init__(self, 'root', 'model')
        base_event.BaseEvent.__init__(self)
        event_queue.EventQueue.__init__(self)
        base_storage.BaseStorage.__init__(self)
        base_passed_time.BasePassedTime.__init__(self)
        self.cds = central_data_store.CentralDataStore(
            t_start=self.cfg.datum_start,
            t_end=self.cfg.datum_end,
            time_step=time_step,
            log_passed_time=cfg.log_passed_time,
            log_storages=cfg.log_storages)

        # setups which can already be done now
        self.cds.set_current_model_time(self.cfg.datum_start)


    def load(self, model_data: model.IOModel):
        """
        Loads the model data from a IO-model object.
        """
        for item in model_data.holdings:
            obj = holding.Holding(item.id)
            obj.load(item, self.cds)
            self.add_holding(obj)

        self.load_events(model_data.events, self.cfg.datum_start)
        self.load_storages(model_data.storages)
        self.load_timed_storages(model_data.timed_storages,
                                 self.cds.get_model_start_time())


    def add_holding(self, holding: holding.Holding):
        self.holdings.append(holding)


    def initialize(self, dir_output: str = None, output_filter: str = None):
        """
        Setups the initial 'status' for everything.
        """

        # deal with optional argument(s) ---------------------------------------
        if not (dir_output is None):
            self.cfg.output_prefix = dir_output + self.cfg.name

        if (self.cfg.seed is not None):
            rnd_wrapper.rnd_set_seed(self.cfg.seed)

        if not (output_filter is None):
            self.cfg.logging_type = output_filter

        # secondary data setup -------------------------------------------------

        # settings for not-yet-implemented single file outputs
        if (self.cfg.get_log_as_single()):
            self.cfg.log_events      = False
            self.cfg.log_passed_time = False
            self.cfg.log_storages    = False
            self.cfg.log_appliances  = False
            self.cfg.log_blocking    = False
            self.cfg.log_lifecycle   = False
            self.cfg.log_wants       = False
            self.cfg.log_probability = False
            self.cfg.log_TS_outputs  = True

        string_output.setup_class_vars(self.cfg.get_headless,
                                       self.cfg.get_logging_type,
                                       self.cfg.get_log_as_single)
        number_output.setup_class_vars(self.cfg.get_headless,
                                       self.cfg.get_logging_type,
                                       self.cfg.get_log_as_single)

        # setups for output
        if (self.cfg.log_TS_outputs and self.cfg.log_as_single):
            if (self.cfg.headless or self.cfg.logging_type == 'none'):
                self.cds.set_single_file_ts(None)

            else:
                os.makedirs(self.cfg.output_prefix + '/', exist_ok=True)
                self._single_file_ts = open(self.cfg.output_prefix + '/single_ts.csv', 'w')
                self.cds.set_single_file_ts(self._single_file_ts)
                self._single_file_ts.write('Time;')

        # main data setup ------------------------------------------------------
        self.__simtime = datetime.datetime.now()

        # data structure housekeeping ------------------------------------------
        self.set_root_node()
        self.setup_event_queue(self.get_node_name(), self.cfg)
        self.register_events()
        self.register_storages(self.cfg.output_prefix + '/main_model_',
                               self.cds, self.cfg)

        for hold in self.holdings:
            if not (self.cfg.headless or self.cfg.logging_type == 'none'):
                os.makedirs(self.cfg.output_prefix + '/', exist_ok=True)
            hold.initialize(
                self.cfg.output_prefix + '/' + self.get_node_name() + '/',
                self, self.cds, self.cfg)

        # connect the UID to callbacks -----------------------------------------
        self.connect_events()
        for hold in self.holdings:
            hold.connect_uids()

        # logging
        if (self.cfg.log_as_single and not self.cfg.headless):
            if (self.cfg.log_TS_outputs and not self.cfg.headless):
                self.cds.get_single_file_ts().write('\n')
        self.__internal_record()

        # see whether some memory can be freed
        gc.collect()


    def run(self, quiet: bool = False):
        """
        Runs the model
        """

        self.__simtime = datetime.datetime.now()

        # loop until ending timepoint
        if (quiet):
            while True:

                self.__internal_run()

                # end, if appropiate
                if (self.cds.get_current_model_time() >= self.cfg.datum_end):
                    break

        # loop until ending timepoint (progress bar edition)
        else:
            half_day_ticks = 43200 / max(self.cfg.t_step_min,
                                         self.cfg.t_step_max)
            total_ticks    = int(
                (self.cfg.datum_end - self.cfg.datum_start).total_seconds() /
                self.cfg.t_step_min) + 1
            tick_interval = int(total_ticks / max(20, total_ticks / half_day_ticks))
            counter       = 0
            with tqdm(total=total_ticks) as pbar:
                while True:
                    self.__internal_run()

                    # Update progress bar
                    counter += 1
                    if (counter % tick_interval == 0):
                        pbar.update(tick_interval)

                    # end, if appropiate
                    if (self.cds.get_current_model_time() >=
                            self.cfg.datum_end):
                        break

        # cleanups
        self.close_event_queue()
        self.close_storages(self.cds.get_current_model_time())
        for hold in self.holdings:
            hold.close(self.cds.get_current_model_time())

        if (self.cfg.log_as_single):
            if (self.cfg.log_TS_outputs and not self.cfg.headless):
                self.cds.get_single_file_ts().close()



    def __internal_run(self):
        """
        To save making changes in two places due to the progress bar.
        """

        # set new current time
        self.cds.set_current_model_time(self.cds.get_current_model_time() +
                                        self.cds.get_compute_interval())

        # execute events
        self.work_event_queue(self.cds)

        # check for general events
        self.check_event_starts('Probability',
                                self.add_event_queue_item,
                                current_tp=self.cds.get_current_model_time())
        for hold in self.holdings:
            hold.update_events(self.cds.get_current_model_time(),
                               self.add_event_queue_item)

        # update each storage
        self.update_storage_values(self.cds.get_current_model_time())
        for hold in self.holdings:
            hold.update_storages(self.cds.get_current_model_time())

        # work the model itself
        for hold in self.holdings:
            hold.update(self.cds, self.cfg, self.add_event_queue_item)

        # logging
        self.__internal_record()


    def __internal_record(self):
        """
        Records the model's status.
        """

        if (self.cfg.log_as_single):
            if (self.cfg.log_TS_outputs and not self.cfg.headless):
                self.cds.get_single_file_ts().write(
                    self.cds.get_current_model_time().isoformat(' ') + ';')

        # work the model itself
        for hold in self.holdings:
            hold.record_status(self.cds, self.cfg)

        self.log_storages(self.cds.get_current_model_time(),
                          self.cds.get_last_model_time())
        self.log_passed_times(self.cds.get_current_model_time(),
                              self.cds.get_last_model_time())

        if (self.cfg.log_as_single):
            if (self.cfg.log_TS_outputs and not self.cfg.headless):
                self.cds.get_single_file_ts().write('\n')


    def return_results(self):
        """
        ToDo
            - Implement finer control over what is returned
        """
        results = []
        for item in self.holdings:
            results.extend(item.return_results())

        return results


    def _timespan_comp(self, what: str):
        time_diff = datetime.datetime.now() - self.__simtime
        print('Time taken to', what, 'was', time_diff.total_seconds(),
              'seconds')


    def output_overview(self, f, level: int = -1):
        """
        Outputs the number of elements within the model
        """

        if (level < 0):
            print(f'{self.get_node_name()}.output_overview: Level not set')
            exit(255)

        f.write("\n" + "  " * level + "Model:")
        f.write("\n" + "  " * level + f"Name: {self.get_node_name()}")

        f.write("\n" + "  " * level + "Holdings:")
        for hold in self.holdings:
            hold.output_overview(f, level + 1)

        f.write('\n')
        self.output_overview_events(f, level)
        self.output_overview_event_queue(f, level)
        self.output_overview_storages(f, level)
        self.output_overview_passed_time(f, level)


# 2. Functions =================================================================

# 3. Main Exec =================================================================
