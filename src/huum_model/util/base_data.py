#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2019.06.02
#
# Changelog:
#
# 2019.06.02 - SBerendsen - start
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
# Offers the basic needed data structures for most 'main' objects
#
# ------------------------------------------------------------------------------
#


# 0. Imports ===================================================================
from ..graph import base_connection

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------
# class to be extended for each node
class BaseData(base_connection.BaseConnection):

    def __init__(self, name: str, node_type: str):
        base_connection.BaseConnection.__init__(self, name, node_type)



# 2. Functions =================================================================


# 3. Main Exec =================================================================
