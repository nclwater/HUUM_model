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
# Data structure with the needed settings
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# general
import datetime
import dateutil.parser

# internal
from huum_io import settings as io_settings

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class Config:  # holds config data

    def __init__(self,
                 startDate: datetime.datetime,
                 endDate: datetime.datetime,
                 prefix: str,
                 t_step_min: int = 1,
                 t_step_max: int = 1,
                 headless: bool = False,
                 logging_type: str = "complex",
                 log_as_single: bool = False,
                 log_events: bool = False,
                 log_passed_time: bool = False,
                 log_storages: bool = False,
                 log_appliances: bool = False,
                 log_activation: bool = False,
                 log_blocking: bool = False,
                 log_lifecycle: bool = False,
                 log_wants: bool = False,
                 log_probability: bool = False,
                 log_TS_outputs: bool = True,
                 seed: str = None,
                 name: str = None):

        # required data
        self.datum_start = startDate
        self.datum_end = endDate
        self.output_prefix = prefix

        # optional data
        self.name = name
        self.t_step_min = t_step_min
        self.t_step_max = t_step_max
        self.seed = seed

        # logging stuff
        self.headless = headless
        self.logging_type = logging_type.lower()
        self.log_as_single = log_as_single

        self.log_events = log_events
        self.log_passed_time = log_passed_time
        self.log_storages = log_storages
        self.log_appliances = log_appliances
        self.log_activation = log_activation
        self.log_blocking = log_blocking
        self.log_lifecycle = log_lifecycle
        self.log_wants = log_wants
        self.log_probability = log_probability
        self.log_TS_outputs = log_TS_outputs

        # derived data
        self.nr_timesteps = datetime.timedelta.total_seconds(endDate -
                                                             startDate)

        if (t_step_max != t_step_min):
            print('\nsettings.Config: Error:')
            print(
                'No variable timestep currently support, min&max need to be equal\n'
            )
            exit(255)
        else:
            self.t_step = t_step_max

    @classmethod
    def fromFileData(config, settings_data: io_settings):
        """
        Converting a loaded settings file data to a settings object.
        """

        assert type(settings_data.time_start) is str, (
            f'Wrong type for start time data: {type(settings_data.time_start)}, expects _str_'
        )
        assert type(settings_data.time_end) is str, (
            f'Wrong type for end time data: {type(settings_data.time_end)}, expects _str_'
        )

        t_start = dateutil.parser.isoparse(settings_data.time_start)
        t_end = dateutil.parser.isoparse(settings_data.time_end)

        cls = Config(t_start,
                     t_end,
                     settings_data.dir_output,
                     name=settings_data.title,
                     headless=settings_data.headless,
                     logging_type=settings_data.logging_type,
                     log_as_single=settings_data.log_as_single,
                     log_events=settings_data.log_events,
                     log_passed_time=settings_data.log_passedTime,
                     log_storages=settings_data.log_storage,
                     log_appliances=settings_data.log_appliances,
                     log_activation=settings_data.log_activation,
                     log_blocking=settings_data.log_blocking,
                     log_lifecycle=settings_data.log_lifecycle,
                     log_wants=settings_data.log_wants,
                     log_probability=settings_data.log_probability,
                     log_TS_outputs=settings_data.log_TS_outputs,
                     t_step_min=settings_data.t_step_min,
                     t_step_max=settings_data.t_step_max,
                     seed=settings_data.seed)

        # TODO Checks for all settings
        # FIXME Only fail once everything has been checked...

        assert type(
            cls.name
        ) == str, 'Project title is not a string, maybe starts with a number?'

        return cls

    def get_headless(self):
        return self.headless

    def get_log_as_single(self):
        return self.log_as_single

    def get_logging_type(self):
        return self.logging_type

    def get_log_passed_time(self):
        return self.log_passed_time

    def get_log_storages(self):
        return self.log_storages


# 2. Functions =================================================================

# 3. Main Exec =================================================================
