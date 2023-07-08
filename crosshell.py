import os
import sys

# Get startfilepath
startfp = os.path.abspath(__file__)

# Define the path of the main script
CSMAINFILEPATH = f"{os.path.dirname(startfp)}{os.sep}core{os.sep}main.py"

# Prepare the formatted startfilepath string
CSSTARTFILEPATHstring = "@startfile:{}".format(startfp)

# Insert the startfilepath at the beginning of sys.argv
sys.argv.pop(0)
sys.argv.insert(0, CSSTARTFILEPATHstring)

# Execute the main script
import subprocess
subprocess.Popen([sys.executable, CSMAINFILEPATH, *sys.argv])
#exec(open(CSMAINFILEPATH).read())
