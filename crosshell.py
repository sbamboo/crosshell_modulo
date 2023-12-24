import os
import sys

# Get startfilepath
startfp = os.path.abspath(__file__)

# Define the path of the main script
CSMAINFILEPATH = os.path.join(os.path.dirname(startfp), 'core', 'main.py')

# Prepare the formatted startfilepath string
CSSTARTFILEPATHstring = "@startfile:{}".format(startfp)

# Insert the startfilepath at the beginning of sys.argv
sys.argv.pop(0)
sys.argv.insert(0, CSSTARTFILEPATHstring)

# Execute the main script without waiting for user input
try:
    os.system(f"{sys.executable} {CSMAINFILEPATH} {' '.join(sys.argv)}")
except KeyboardInterrupt:
    print("\n\n[Crosshell]: Ended by keyboard iterupt. Bya <3")
# The subprocess will run without waiting for user input and will close when the main script finishes.