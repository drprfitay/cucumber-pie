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

a["last_field"] = 200

print a["last_field"]

