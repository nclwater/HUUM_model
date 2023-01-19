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
# Offers wrapper for random number generator, for ease of replacement and logging.
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================

# external
import random

# 1. Global vars ===============================================================


# ------------------------------------------------------------------------------
# logfile = open('rnd.log', 'w')


# 2. Functions =================================================================
def rnd_set_seed(seed):
    random.seed(seed)
    # global logfile
    # logfile = open('rnd.log', 'w')
    # logfile.write(f'Seed: {seed}\n\n')
    # now = datetime.now()
    # logfile.write(f"Time: {now.isoformat(' ')}")


def rnd_get_gauss_dist(mu, sigma):
    # val = random.normalvariate(mu, sigma)
    # logfile.write(f'NOR: {val}\n')
    val = random.gauss(mu, sigma)
    # logfile.write(f'GAU: {val}\n')
    return val


def rnd_get_uniform_dist(a, b):
    val = random.uniform(a, b)
    # logfile.write(f'UNI: {val}\n')
    return val


def rnd_get_random_number():
    val = random.random()
    # logfile.write(f'RND: {val}\n')
    return val


# 3. Main Exec =================================================================
