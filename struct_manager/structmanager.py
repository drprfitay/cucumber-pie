from struct import pack, unpack
from struct_manager_exception import *
import json


# StructManager handles helps managing structs
# by some json format tempate and allows handling byte arrays
# every function within this class may raise StructManagerException
class StructManager(object):
    # constructs a struct manager object and loads
    # a struct template into it
    # template_file - json file describing struct format
    def __init__(self, template_file):
        json_format = None

        # Read format file
        try:
            format_file = file(template_file, "r")
            json_format = format_file.read()
            format_file.close()
        except IOError:
            raise StructManagerException(exception_val=StructManagerException.INVALID_FORMAT_FILE)

        struct_dict = json.loads(json_format)

        self.x = encode_unicode_dict(struct_dict)


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
        pass

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


# Converts a unicode string to ascii
# item - unicode string
def unicode_to_ascii(item):
    if isinstance(item, unicode):
        return item.encode("ascii")
    return item


# Encodes a dictionary from unicode dict to ascii
# unicode_dict - dict that needs encoding
def encode_unicode_dict(unicode_dict):
    if not isinstance(unicode_dict, dict):
        return unicode_dict

    dict_list = []

    for pair in unicode_dict.items():
        new_pair = []
        for tuple_obj in pair:
            if isinstance(tuple_obj, dict):
                new_pair.append(encode_unicode_dict(tuple_obj))
            else:
                new_pair.append(unicode_to_ascii(tuple_obj))
        dict_list.append(new_pair)

    return dict(dict_list)
