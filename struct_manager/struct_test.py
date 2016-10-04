from structmanager import *


a = StructManager("example_struct")

b = 5
b = 6

for pair in a.struct_fields.items():
    print "\n~~~~~~~~~~~~~~~~~~~"
    print pair[0]
    print pair[1]
    print "~~~~~~~~~~~~~~~~~~~"

print a.struct_size

a["another_field"] = [ord('a') + i for i in range(0, 5)]

a["some_field"] = [32, 34]
a["last_field"] = 198

print a.serialize()

