###############################################
#              structmanager
# 
# Author: DrPrItay
#
# Description: This python model wrapps struct 
# usage and allows creating some struct by 
# a predefined json, also gives access to
# data members of the struct and manipulation
# of those as described within the json format 
# previously
#
###############################################

from struct import pack, unpack
from struct_manager_exception import *
import json


# StructManager handles helps managing structs
# by some json format tempate and allows handling byte arrays
# every function within this class may raise StructManagerException
class StructManager(object):
    FIELDS_ATTR = "fields"
    ENDIANITY_ATTR = "endianity"
    TYPE_ATTR = "type"
    SIZE_ATTR = "size"
    INDEX_ATTR = "index"
    RANGE_ATTR = "range"
    CURRENT_VAL_ATTR = "current_value"
    DEFAULT_ATTR = "default-value"
    UPPER_ATTR = "upper-range"
    LOWER_ATTR = "lower-range"
    BLACK_LIST_ATTR = "black-list-values"
    possible_types = {"byte": ('B', 1), "word": ('H', 2), "dword": ('I', 4), "qword": ('Q', 8)}
    possible_endianity = {"big": ">", "little": "<"}

    # constructs a struct manager object and loads
    # a struct template into it
    # template_file - json file describing struct format
    def __init__(self, template_file):
        self.endianity = None
        self.struct_fields = None
        self.struct_size = None
        self.load_template(template_file)

    # sets the value of some data member within the struct
    # key - data member name
    # value - data member value
    def __setitem__(self, key, value):
        # sanity check
        if key not in self.struct_fields:
            raise StructManagerException(exception_val=StructManagerException.ITEM_DOES_NOT_EXIST)

        value_list = []

        # if not an array
        if not isinstance(value, list):
            value_list = [value]
        else:
            value_list = value

        # validate value, if invalid exception should be raised
        self.__validate(key, value_list)

        self.struct_fields[key][self.CURRENT_VAL_ATTR] = value_list

    # gets the value of some data member
    # item - data member name
    def __getitem__(self, item):
        # sanity check
        if item not in self.struct_fields:
            raise StructManagerException(exception_val=StructManagerException.ITEM_DOES_NOT_EXIST)

        return self.struct_fields[item][self.CURRENT_VAL_ATTR]

    # gets the bytes of some data member
    # data_member - the name of the data member
    def get_data_member_bytes(self, data_member_name):
        # sanity check
        if data_member_name not in self.struct_fields:
            raise StructManagerException(exception_val=StructManagerException.ITEM_DOES_NOT_EXIST)

        type_format = self.possible_types[self.struct_fields[data_member_name][self.TYPE_ATTR]][0]
        type_size = self.possible_types[self.struct_fields[data_member_name][self.TYPE_ATTR]][1]
        field_size = self.struct_fields[data_member_name][self.SIZE_ATTR]
        field_endianity = self.possible_endianity[self.struct_fields[data_member_name][self.ENDIANITY_ATTR]]

        return pack(field_endianity + str(field_size / type_size) + type_format, 
                    *self.struct_fields[data_member_name][self.CURRENT_VAL_ATTR])

    # reloads struct with a new template
    # template_file - json file describing struct format
    def load_template(self, template_file):
        json_format = None
        struct_endianity = "little"
        struct_size = 0
        fields = {}

        # Read format file
        try:
            format_file = file(template_file, "r")
            json_format = format_file.read()
            format_file.close()
        except IOError:
            raise StructManagerException(exception_val=StructManagerException.INVALID_FORMAT_FILE)

        struct_dict = encode_unicode_dict(json.loads(json_format))

        if not isinstance(struct_dict, dict):
            raise StructManagerException(exception_val=StructManagerException.INVALID_JSON_FORMAT)

        # Format validation check
        if self.FIELDS_ATTR not in struct_dict or not isinstance(struct_dict[self.FIELDS_ATTR], dict):
            raise StructManagerException(exception_val=StructManagerException.INVALID_JSON_FORMAT)

        # Checking for valid endianity type
        if self.ENDIANITY_ATTR in struct_dict:
            if struct_dict[self.ENDIANITY_ATTR] not in self.possible_endianity:
                raise StructManagerException(exception_val=StructManagerException.INVALID_ENDIANITY_TYPE)
            else:
                struct_endianity = struct_dict[self.ENDIANITY_ATTR]

        # Go through all fields within dict and validate
        for field_name in struct_dict[self.FIELDS_ATTR].keys():
            field = struct_dict[self.FIELDS_ATTR][field_name]
            added_field = {}

            # Checking that a field type, size was given
            if (self.TYPE_ATTR not in field or self.SIZE_ATTR not in field
                    or self.INDEX_ATTR not in field):
                raise StructManagerException(exception_val=StructManagerException.INVALID_FIELD_FORMAT)

            # Checking that given field type exists
            if field[self.TYPE_ATTR] not in self.possible_types:
                raise StructManagerException(exception_val=StructManagerException.BAD_TYPE,
                                             str_error="Bad type, only possible types are:\n%s" %
                                                       ", ".join([key for key in self.possible_types.keys()]))
            # Checking that valid size given
            if field[self.SIZE_ATTR] % self.possible_types[field[self.TYPE_ATTR]][1] != 0:
                raise StructManagerException(exception_val=StructManagerException.BAD_SIZE)

            # Checking if range wasnt stated
            if not (self.UPPER_ATTR in field or self.LOWER_ATTR in field):
                added_field[self.RANGE_ATTR] = None
            # Range was stated
            else:
                if (self.UPPER_ATTR in field) is not (self.LOWER_ATTR in field):
                    raise StructManagerException(exception_val=StructManagerException.INVALID_FORMAT_FILE)

                if (not isinstance(field[self.LOWER_ATTR], int) or
                        not isinstance(field[self.UPPER_ATTR], int) or
                        field[self.LOWER_ATTR] > field[self.UPPER_ATTR] or
                        field[self.LOWER_ATTR] < 0 or
                        field[self.UPPER_ATTR] >= 2 ** (8 * self.possible_types[field[self.TYPE_ATTR]][1])):
                    raise StructManagerException(exception_val=StructManagerException.BAD_RANGE)

                added_field[self.RANGE_ATTR] = (field[self.LOWER_ATTR], field[self.UPPER_ATTR])

            # Default attr wasnt stated
            if self.DEFAULT_ATTR not in field:
                added_field[self.DEFAULT_ATTR] = None
            # Default range was stated
            else:
                if (not isinstance(field[self.DEFAULT_ATTR], int) or
                        field[self.DEFAULT_ATTR] not in
                        range(0, 2 ** (8 * self.possible_types[field[self.TYPE_ATTR]][1]))):
                    print type(field[self.DEFAULT_ATTR])
                    print field[self.DEFAULT_ATTR]
                    print field_name
                    raise StructManagerException(exception_val=StructManagerException.BAD_DEFAULT_VAL)
                added_field[self.DEFAULT_ATTR] = field[self.DEFAULT_ATTR]

            # Black list attr not given
            if self.BLACK_LIST_ATTR not in field:
                added_field[self.BLACK_LIST_ATTR] = None
            # Black list given
            else:
                # If whether black list item isn't a list, or one of the black list objects are not numeric
                # or not in possible values range
                if (not isinstance(field[self.BLACK_LIST_ATTR], list) or
                        len(filter(lambda list_item: True if (not isinstance(list_item, int) or
                                    list_item not in range(0, 2 ** (8 * self.possible_types[field[self.TYPE_ATTR]][1])))
                                    else False, field[self.BLACK_LIST_ATTR])) > 0):
                    raise StructManagerException(exception_val=StructManagerException.BAD_BLACK_LIST_VAL)

                added_field[self.BLACK_LIST_ATTR] = field[self.BLACK_LIST_ATTR]

            added_field[self.INDEX_ATTR] = field[self.INDEX_ATTR]
            added_field[self.SIZE_ATTR] = field[self.SIZE_ATTR]
            added_field[self.TYPE_ATTR] = field[self.TYPE_ATTR]
            added_field[self.ENDIANITY_ATTR] = struct_endianity
            added_field[self.CURRENT_VAL_ATTR] = [0 for i in range(0, field[self.SIZE_ATTR] /
                                                            self.possible_types[field[self.TYPE_ATTR]][1])]

            struct_size += field[self.SIZE_ATTR]
            fields[field_name] = added_field

        self.struct_size = struct_size
        self.struct_fields = fields
        self.endianity = struct_endianity

    # serializes struct into a byte array
    def serialize(self):
        sorted_field_names = self.struct_fields.items()
        sorted_field_names.sort(key=lambda tup: tup[1][self.INDEX_ATTR])
        sorted_field_names = [pair[0] for pair in sorted_field_names]

        return "".join([self.get_data_member_bytes(field_name) for field_name in sorted_field_names])

    # deserializes struct into some byte_array
    def deserialize(self, byte_array):
        # sanity check
        if len(byte_array) != self.struct_size:
            raise StructManagerException(exception_val=StructManagerException.BAD_BYTEARRAY_SIZE)

        sorted_fields = self.struct_fields.items()
        sorted_fields.sort(key=lambda tup: tup[1][self.INDEX_ATTR]) 
        byte_array_ptr = 0

        # Deserialize each field
        for data_member_name, data_member_dict in sorted_fields:
            type_format = self.possible_types[data_member_dict[self.TYPE_ATTR]][0]
            type_size = self.possible_types[data_member_dict[self.TYPE_ATTR]][1]
            field_size = data_member_dict[self.SIZE_ATTR]
            field_endianity = self.possible_endianity[data_member_dict[self.ENDIANITY_ATTR]]

            # Deserialize field from bytearray using bytearray ptr
            data_member_values = map(lambda x: x, 
                                     unpack(field_endianity + str(field_size / type_size) + type_format, 
                                            byte_array[byte_array_ptr: byte_array_ptr + field_size]))

            self.__validate(data_member_name, data_member_values)

            # Forward ptr and set val
            byte_array_ptr += field_size
            self[data_member_name] = data_member_values

    # sets the default endianity of the struct
    # endianity - type of endianity, little or big
    def set_endianity(self, endianity):
        # Set endianity of all fields, if invalid endianity set_data_member_endianity would raise 
        # an error
        for field in self.struct_fields.keys():
            self.set_data_member_endianity(field, endianity)

        # if reached this, no error was raised hence endianity is valid
        self.struct_endianity = endianity

    # sets the default endianity of a specific
    # data member within the struct
    # data_member - data member name
    # endianity - type of endianity, little or big
    def set_data_member_endianity(self, data_member, endianity):
        # sanity check
        if data_member not in self.struct_fields:
            raise StructManagerException(exception_val=StructManagerException.ITEM_DOES_NOT_EXIST)

        if endianity not in self.possible_endianity:
            raise StructManagerException(exception_val=StructManagerException.INVALID_ENDIANITY_TYPE)        

        self.struct_fields[data_member][self.ENDIANITY_ATTR] = endianity

    # validates if some value could be placed into some field
    # field_name - name of the required struct field
    # value - field value (if array this should be a list)
    def __validate(self, field_name, value_list):

        item_range = self.struct_fields[field_name][self.RANGE_ATTR]
        black_list = self.struct_fields[field_name][self.BLACK_LIST_ATTR]
        default_val = self.struct_fields[field_name][self.DEFAULT_ATTR]
        field_type = self.struct_fields[field_name][self.TYPE_ATTR]
        field_size = self.struct_fields[field_name][self.SIZE_ATTR]
        type_size = self.possible_types[field_type][1]

        # number of list items is equal to needed array size
        if len(value_list) != (field_size / type_size):
            raise StructManagerException(exception_val=StructManagerException.BAD_SET_VALUE,
                                         str_error="Cannot assign value to %s, data member is an array in the "
                                                   "size of %d, and %d values were given" %
                                                   (field_name, field_size / type_size, len(value_list)))
        # Go through all values given to dm (possibley each dm is an array)
        for item_value in value_list:
            # If a default value was set, dm or each dm cell (if an array) must be equal to
            # default value
            if default_val is not None:
                if item_value != default_val:
                    raise StructManagerException(exception_val=StructManagerException.BAD_SET_VALUE,
                                                 str_error="Cannot assign value to %s, as data member must have a" \
                                                 " default value of %d" % (field_name, default_val))
                else:
                    continue
            # no default value was set
            else:
                # item is within possible range
                if item_range is None:
                    if item_value not in range(0, 2 ** (8 * type_size)):
                        raise StructManagerException(exception_val=StructManagerException.BAD_SET_VALUE,
                                                     str_error="Cannot assign value to %s, value must be in range of"
                                                     " %d to %d" % (field_name, 0, 2 ** (8 * type_size)))
                # item is within set range
                else:
                    if item_value not in range(item_range[0], item_range[1]):
                        raise StructManagerException(exception_val=StructManagerException.BAD_SET_VALUE,
                                                     str_error="Cannot assign value to %s, value must be in range of"
                                                     " %d to %d" % (field_name, item_range[0], item_range[1]))
                # item isnt within black list
                if black_list is not None and item_value in black_list:
                    raise StructManagerException(exception_val=StructManagerException.BAD_SET_VALUE,
                                                 str_error="Cannot assign value to %s, value must not be within black"
                                                 "list of values which is: %s" % (field_name, ", ".join(
                                                    map(lambda n: str(n), black_list))))


# Encodes a dictionary from unicode dict to ascii
# unicode_dict - dict that needs encoding
def encode_unicode_dict(unicode_dict):
    if not isinstance(unicode_dict, dict):
        return unicode_dict

    dict_list = []

    # go through all pairs within dict
    for pair in unicode_dict.items():
        new_pair = map(lambda item: encode_unicode_dict(item) if isinstance(item, dict) else
                       item.encode("ascii") if isinstance(item, unicode) else item, pair)

        dict_list.append(new_pair)

    return dict(dict_list)
