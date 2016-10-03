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
        pass

    # gets the value of some data member
    # item - data member name
    def __getitem__(self, item):
        pass

    # gets the bytes of some data member
    # data_member - the name of the data member
    def get_data_member_bytes(self, data_member_name):
        pass

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

            added_field[self.SIZE_ATTR] = field[self.SIZE_ATTR]
            added_field[self.TYPE_ATTR] = field[self.TYPE_ATTR]
            added_field[self.ENDIANITY_ATTR] = struct_endianity
            struct_size += field[self.SIZE_ATTR]
            fields[field_name] = added_field

        self.struct_size = struct_size
        self.struct_fields = fields
        self.endianity = struct_endianity

    # serializes struct into a byte array
    def serialize(self):
        pass

    # deserializes struct into some byte_array
    def desrialize(self, byte_array):
        pass

    # sets the default endianity of the struct
    # endianity - type of endianity, little or big
    def set_endianity(self, endianity):
        pass

    # sets the default endianity of a specific
    # data member within the struct
    # data_member - data member name
    # endianity - type of endianity, little or big
    def set_data_member_endianity(self, data_member, endianity):
        pass


# Encodes a dictionary from unicode dict to ascii
# unicode_dict - dict that needs encoding
def encode_unicode_dict(unicode_dict):
    if not isinstance(unicode_dict, dict):
        return unicode_dict

    dict_list = []

    for pair in unicode_dict.items():
        new_pair = map(lambda item: encode_unicode_dict(item) if isinstance(item, dict) else
                       item.encode("ascii") if isinstance(item, unicode) else item, pair)

        dict_list.append(new_pair)

    return dict(dict_list)
