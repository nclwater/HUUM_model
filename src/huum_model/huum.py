#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
#
# Changelog:
#
# 2020.02.10 - SBerendsen - start
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
# Main HUUM method to work from
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# internal
from huum_io import model_io

from . import model
from .util import settings

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
class HUUM(object):

    def __init__(self):

        self.model = None


    def load(self, fn: str):

        # load data
        model_data = model_io.IOModelHUUM.load(fn)

        # convert settings
        config = settings.Config.fromFileData(model_data.settings)

        # setup model
        self.model = model.Model(config.name, config)

        # load data
        self.model.load(model_data.model)


    def load_from_memory(self, model_data: model_io.IOModelHUUM):

        # config stuff
        config = settings.Config.fromFileData(model_data.settings)
        self.model = model.Model(config.name, config)

        # transfer data
        self.model.load(model_data.model)


    def run(self,
            msg: bool = True,
            dir_output: str = None,
            quiet: bool = False,
            output_filter: str = None):

        self.model.initialize(dir_output=dir_output,
                              output_filter=output_filter)
        self.model.run(quiet=quiet)


    def return_results(self):
        if (self.model.cfg.headless):
            return self.model.return_results()

        else:
            print('\nError: huum.return_results:')
            print('Not yet supported for non-headless runs')
            exit(255)


    def output_overview(self, fn: str):
        """
        Outputs the number of elements within the model
        """
        f = open(fn, 'w')

        f.write('%YAML 1.2\n---\n\n')

        self.model.output_overview(f, level=0)

        f.close()


# 2. Functions =================================================================

# 3. Main Exec =================================================================
