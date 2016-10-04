

# This class describes exception raised by StructManager
class StructManagerException(BaseException):
    # Error values
    STRUCT_MANAGER_ERROR = 0
    INVALID_FORMAT_FILE = 1
    INVALID_JSON_FORMAT = 2
    INVALID_ENDIANITY_TYPE = 3
    INVALID_FIELD_FORMAT = 4
    BAD_TYPE = 5
    BAD_SIZE = 6
    BAD_RANGE = 7
    BAD_DEFAULT_VAL = 8
    BAD_BLACK_LIST_VAL = 9
    ITEM_DOES_NOT_EXIST = 10
    BAD_SET_VALUE = 11
    BAD_BYTEARRAY_SIZE = 12

    # Error dict
    ERRORS_DICT = {STRUCT_MANAGER_ERROR: ("Unknown error has occured",
                                          "Unknown StructManagerError"),
                   INVALID_FORMAT_FILE: ("Format file does not exist",
                                         "Invalid Format File"),
                   INVALID_JSON_FORMAT: ("Bad json format given - json format must be a dictionary "
                                         "containing fields key,\nwhereas field item is another dictionary"
                                         " containing field name as key and a dictionary with\n"
                                         "size, type, index keys as obligation, and possible values key, e.g:\n"
                                         "{\n\t%s:\n\t"
                                         "{\n\t\t%s:\n\t\t"
                                         "{\n\t\t\t%s: %d,\n\t\t\t"
                                         "%s: %d,\n\t\t\t"
                                         "%s: %s,\n\t\t\t"
                                         "%s: %s\n\t\t}\n\t}\n}" % ("\"fields\"", "\"some-field-name\"",
                                                                    "\"index\"", 0, "\"size\"", 4, "\"type\"",
                                                                    "\"ascii\"", "\"default-val\"", "4"),
                                         "BAD_JSON_FORMAT"),
                   INVALID_ENDIANITY_TYPE: ("Bad endianity type given, only \"little\" and \"big\" are allowed",
                                            "Bad endianity"),
                   INVALID_FIELD_FORMAT: ("Bad field format.\neach field must contain the following attributes:"
                                          "\n\"size\", \"type\", \"index\"."
                                          "\nand optional: \"default-val\", \"lower-range\" & \"lower-range\","
                                          " \"black-list\".",
                                          "Bad field format"),
                   BAD_TYPE: ("Bad type given", "Bad type"),
                   BAD_SIZE: ("Bad size given, field size must be suitable to type size", "Bad size"),
                   BAD_RANGE: ("Bad range given, range must contain both %s and %s, with possible numeric values" %
                               ("\"lower-range\"", "\"upper-range\""), "Bad range"),
                   BAD_DEFAULT_VAL: ("Bad default val given, must be a possible numeric value", "Bad default val"),
                   BAD_BLACK_LIST_VAL: ("Black list must be a list of possibe forbidden values", "Bad black list"),
                   ITEM_DOES_NOT_EXIST: ("Data member doesnt exist within struct", "Item doesnt exist"),
                   BAD_SET_VALUE: ("Cannot assign given value to some field", "Bad set value"),
                   BAD_BYTEARRAY_SIZE: ("Invalid byte array size", "Bad bytearray size")}

    def __init__(self,
                 exception_val=STRUCT_MANAGER_ERROR,
                 str_error=None):
        self.err_val = exception_val
        self.str_error = str_error
        pass

    def __str__(self):
        if self.str_error is not None:
            print self.str_error
        else:
            try:
                print self.ERRORS_DICT[self.err_val][0]
            except KeyError:
                print self.ERRORS_DICT[self.STRUCT_MANAGER_ERROR][0]

    @staticmethod
    def get_error(err_val):
        try:
            print StructManagerException.ERRORS_DICT[err_val][1]
        except KeyError:
            print StructManagerException.ERRORS_DICT[StructManagerException.STRUCT_MANAGER_ERROR][1]
