

# This class describes exception raised by StructManager
class StructManagerException(BaseException):
    # Error values
    STRUCT_MANAGER_ERROR = 0
    INVALID_FORMAT_FILE = 1
    INVALID_JSON_FORMAT = 2

    # Error dict
    ERRORS_DICT = {STRUCT_MANAGER_ERROR: ("Unknown error has occured",
                                          "Unknown StructManagerError"),
                   INVALID_FORMAT_FILE: ("Format file does not exist",
                                         "Invalid Format File"),
                   INVALID_JSON_FORMAT: ("Bad json format given - json format must be a dictionary "
                                         "containing fields key, whereas field item is another dictionary"
                                         "containing field name as key and a dictionary with "
                                         "size, type, index keys as obligation, and possible values key, e.g:\n"
                                         "{%s:\n\t"
                                         "{%s:\n\t\t"
                                         "{%s: %d,\n\t\t"
                                         "%s: %d\n\t\t,"
                                         "%s: %s\n\t\t,"
                                         "%s: %s}\n\t}\n}" % ("fieds", "some-field-name",
                                                              "index", 0, "size", 4, "type", "ascii",
                                                              "default-val", "4"), "BAD_JSON_FORMAT")}

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
