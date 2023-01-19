#
# ------------------------------------------------------------------------------
# HUUM - Household Utilities Usage Model (Prototype)
# Demonstrator for the full model
# ------------------------------------------------------------------------------
#
# Author: Sven Berendsen
# Date:   2020.03.16
#
# Changelog:
#
# 2020.03.16 - SBerendsen - start
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
# Base class to deal with connections and their assorted
#
# ToDo
#   - fix _get_node_object so that it can deal with the first part of child objects as well
#
# ------------------------------------------------------------------------------
#

# 0. Imports ===================================================================

# 1. Global vars ===============================================================
_TARGETABLE_OBJECTS = [
    '$model', '$holding', '$cu', '$room', '$agent', '$appliance', '$event',
    '$storage', '$passedtime', '$lifestylehabit', '$usagehabit'
]  # all possible object types


# 1.1 Classes ------------------------------------------------------------------
class BaseConnection(object):  # class to be extended for each node

    def __init__(self, name: str, node_type: str):

        _TARGETABLE_CHILD_OBJECTS = [
        ]  # which child objects are targetable. Needs to be set in each class extensions

        # checks
        # node_type check
        if not (f'${node_type}' in _TARGETABLE_OBJECTS):
            print(
                'Error: BaseConnection.register_tree_node: Unsupported node type'
            )
            print('Node_name:', name)
            print('Node_type:', f'${node_type}')
            print('Supported:', _TARGETABLE_OBJECTS)
            exit(255)

        # set during init
        self.__name      = name.lower()
        self.__node_type = f'${node_type}'                      # type of local node [$<node_type>]
        self.__id        = f'{self.__node_type}_{self.__name}'  # full, local id [<type>_name]

        # set later
        self.__full_id     = None  # full id [as list of "full_id"s]
        self.__node_level  = None  # which is the local node level (top-level == 1)
        self.__parent_node = None  # parent node object


    def get_node_name(self):
        return self.__name


    def get_node_type(self):
        return self.__node_type


    def get_node_id(self):
        return self.__id


    def get_node_level(self):
        return self.__node_level


    def get_full_node_id(self):
        return self.__full_id


    def get_self(self):
        """
        Specifically for return UID target & target resolution.
        """
        return [self]


    def set_root_node(self):
        """
        Needs to be run first, before any other registering is being done.
        """

        self.__full_id    = self.__id
        self.__node_level = 0


    def register_tree_node(self, parent_node):
        """
        Registers the node.
        """

        # set stuff
        self.__parent_node = parent_node
        self.__node_level  = parent_node.get_node_level() + 1
        self.__full_id     = f'{parent_node.get_full_node_id()}.{self.__id}'

    
    def connect_uids(self):
        """
        Function to be overriden with local appropiate implementation.

        Connects the set UID with callbacks to the appropiate functions.
        """
        print('\nError: BaseConnection.connect_uids: Not yet implemented')
        print(f'Current ID: {self.__full_id}')
        exit(255)


    def get_uid_target_obj(self, uid: str):
        """
        Returns the UID target(s) objects.
        """
        # print('\n\nUID-start ----------------------------------------------------------------------')
        # split them
        parts = uid.lower().split('.')

        # get the objects
        objects = self._get_node_object(parts)

        # sanity checks
        assert objects is not None, (
            '\nError: get_uid_target_obj: Target not found (object empty)'
            f'\nCurrent ID: {self.__full_id}'
            f'\nSearch ID:  {uid}')

        assert isinstance(objects, list), (
            '\nError: get_uid_target_obj: Not returning a list'
            f'\nCurrent ID: {self.__full_id}'
            f'\nSearch ID:  {uid}')

        for item in objects:
            assert callable(item), (
                '\nError: get_uid_target_obj: Returned item is no callback'
                f'\nCurrent ID: {self.__full_id}'
                f'\nSearch ID:  {uid}'
                f'\nItem:       {str(item)}'
                f'\nList:       {" ".join(str(x) for x in objects)}')

        return objects


    def _get_node_object(self, parts: list):
        """
        Get the targeted object(s).
        """
        
        # # debug
        # if not hasattr(self, '_TARGETABLE_CHILD_OBJECTS'):
        #     print('Error: base_connection._get_node_object:')
        #     print('_TARGETABLE_CHILD_OBJECTS not implemented for this class')
        #     print(type(self))
        #     exit(255)

        # print('\n\nLooking for parts:', parts)
        # print(type(self))


        # first check if empty - if so, arrived at the wanted object
        if (len(parts) == 0):
            # print('\ncase 0')
            # print(type(self), parts)
            return [self.get_self]

        # get first part (positioned here as the "is empty" version is already caught)
        id_part = parts[0].split('_')

        # check whether it is the local node
        if (parts == self.__full_id):
            # print('\ncase 1')
            # print(type(self), parts)
            return [self.get_self]

        # deal with keyword "object type"
        elif (parts[0] == self.__node_type):
            # print('\ncase 2')
            # print(type(self), parts)
            return self.__get_local_object(parts[1:])

        # deal with 'local name'
        elif (parts[0] == self.__id):
            # print('\ncase 3')
            # print(type(self), parts)
            return self.__get_local_object(parts[1:])

        # deal with keyword "$self"
        elif (parts[0] == '$self'):
            # print('\ncase 4')
            # print(type(self), parts)
            if (len(parts) == 1):
                return [self.get_self]
            else:
                return self.__get_local_object(parts[1:])

        # check whether it is a child object
        elif (id_part[0] in self._TARGETABLE_CHILD_OBJECTS):
            # print('\ncase 5')
            # print(type(self), parts)
            return self.__get_local_object(parts)

        # catch-all
        else:
            # print('\ncase 6')
            # print(type(self), parts)
            # print(id_part[0])
            # print((parts[0] in self._TARGETABLE_CHILD_OBJECTS))
            # print(parts[0], self._TARGETABLE_CHILD_OBJECTS)
            # print(self.__node_level > 0)
            if (self.__node_level > 0):
                return self.__parent_node._get_node_object(parts)
            else:
                return None


    def __get_local_object(self, parts):
        """
        Wrapper method to allow for easier self checks (and avoid duplicate programming).
        """

        # case: end of line
        if (len(parts) == 0):
            return [self.get_self]

        # everything else
        return self._get_child_object(parts)


    def _get_child_object(self, parts):
        """
        To be overriden for each extending class. Should only call the "_get_node_object" function.
        """
        print('\nError: BaseConnection._get_child_object: Not yet implemented')
        print(f'Current ID: {self.__full_id}')
        print(f'Search ID:  {".".join(str(x) for x in parts)}')
        print('gco:', type(self), parts)
        exit(255)


# 3. Main Exec =================================================================
