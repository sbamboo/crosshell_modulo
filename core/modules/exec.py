# Imports
from cslib import CrosshellDebErr,fromPath
from cslib.datafiles import _fileHandler

# Entries to include in the cmdletScope (Excluding variables added by exec)
entries = _fileHandler("json","get",csSession.data["gef"])

# Execute
try:
    CS_LastOutput = CS_PipeLine.execute(csSession,globals(),entries)
except CrosshellDebErr as e:
    if csSession.data["set"].getProperty("crsh","Execution.OnlyAllowCmdlets") == True:
        CS_LastOutput = e
    else:
        # Do something with the expression
        #CS_LastOutput = CS_LastInput
        CS_LastOutput = e