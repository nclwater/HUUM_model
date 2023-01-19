#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2020.07.09
#
# Changelog:
#
# 2020.07.09 - SBerendsen - start
#
# ------------------------------------------------------------------------------
#
# Copyright 2020, Sven Berendsen
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
# (replacement for the dateutil package) turns a datetime-string into a datetime object.
#
# ToDo
#   - Implement more date formats
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================
import datetime
# import re

# 1. Global vars ===============================================================


# 1.1 Classes ------------------------------------------------------------------

# 2. Functions =================================================================

def parse_isodatetime(timestamp: str):
    """
    Parses and iso formatted string.

    Taken from 

    ToDo
        - insert error checking
        - get the version from https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object
          working with blanks.
    """

    # quick checks
    flag = True

    if (timestamp[4:5] != '-'):
        flag = False

    if (timestamp[7:8] != '-'):
        print('case2')
        flag = False

    if (timestamp[10:11] != ' '):
        print('case3')
        flag = False

    if (timestamp[13:14] != ':'):
        print('case4')
        flag = False

    if not (flag):
        print('Error: date_parser.parse_isodatetime:')
        print('Unrecognised/Unsupported datetime string:', timestamp)
        exit()

    # try conversions
    try:
        year = int(timestamp[0:4])
    except ValueError:
        # Handle the exception
        print('Error: date_parser.parse_isodatetime:')
        print("Year isn't an integer", timestamp[0:4])
        exit()

    try:
        month = int(timestamp[5:7])
    except ValueError:
        # Handle the exception
        print('Error: date_parser.parse_isodatetime:')
        print("Month isn't an integer", timestamp[5:7])
        exit()

    try:
        day = int(timestamp[8:10])
    except ValueError:
        # Handle the exception
        print('Error: date_parser.parse_isodatetime:')
        print("Day isn't an integer", timestamp[8:10])
        exit()

    try:
        hour = int(timestamp[11:13])
    except ValueError:
        # Handle the exception
        print('Error: date_parser.parse_isodatetime:')
        print("Hour isn't an integer", timestamp[11:13])
        exit()

    try:
        minute = int(timestamp[14:16])
    except ValueError:
        # Handle the exception
        print('Error: date_parser.parse_isodatetime:')
        print("Minutes isn't an integer", timestamp[14:16])
        exit()

    output_datetime = datetime.datetime(year, month, day, hour, minute)


    # # This regex removes all colons and all
    # # dashes EXCEPT for the dash indicating + or - utc offset for the timezone
    # conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', timestamp)

    # # Split on the offset to remove it. Use a capture group to keep the delimiter
    # split_timestamp = re.split(r"[+|-]",conformed_timestamp)
    # main_timestamp = split_timestamp[0]
    # if len(split_timestamp) == 3:
    #     sign = split_timestamp[1]
    #     offset = split_timestamp[2]
    # else:
    #     sign = None
    #     offset = None

    # # Generate the datetime object without the offset at UTC time
    # output_datetime = datetime.datetime.strptime(main_timestamp +"Z", "%Y%m%dT%H%M%S.%fZ" )
    # if offset:
    #     # Create timedelta based on offset
    #     offset_delta = datetime.timedelta(hours=int(sign+offset[:-2]), minutes=int(sign+offset[-2:]))

    #     # Offset datetime with timedelta
    #     output_datetime = output_datetime + offset_delta

    return output_datetime


# 3. Main Exec =================================================================
