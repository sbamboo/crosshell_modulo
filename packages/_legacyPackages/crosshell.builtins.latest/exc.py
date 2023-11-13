# region CROSSHELL HINTS
from types import FunctionType
sargv: str
CS_LastInput: str
CS_LastOutput: str
CS_PipeLine: object
CS_Inpparse: object
CS_Exec: object
csSession: object
exclude_nonToFormat: FunctionType
include_nonToFormat: FunctionType
removeAnsiSequences: FunctionType
CrosshellDebErr: object
CrosshellExit: object
# endregion CROSSHELL HINTS


# Get content
from cslib.externalLibs.filesys import filesys as fs
raw_content = sargv
lines = raw_content.split("\n")

# Save prev
old_CS_LastInput = CS_LastInput
old_CS_LastOutput = CS_LastOutput 
old_CS_PipeLine = CS_PipeLine

# Create pipeline
from cslib.execution import execline
CS_PipeLine = execline()

# Execute for each line
try:
    for line in lines:
        # Set input
        CS_LastInput = line
        # Clear outputs
        CS_LastOutput = None
        # Execute input
        if CS_LastInput != "":
            CS_Inpparse.execute_internally(globals())
            CS_Exec.execute_internally(globals())
        # Handle and print output
        if CS_LastOutput != None and CS_LastOutput != "":
            if type(CS_LastOutput) == str:
                # Global Text System
                formatMode = csSession.data["set"].getProperty("crsh","Console.FormatOutMode")
                if formatMode == False: formatMode = "off"
                formatMode = formatMode.lower()
                if formatMode != "off":
                    toformat,excludes = exclude_nonToFormat(CS_LastOutput)
                    formatted = csSession.data["txt"].parse(toformat)
                    final = include_nonToFormat(formatted,excludes)
                    if formatMode == "strip":
                        final = removeAnsiSequences(final)
                else: final = CS_LastOutput
                print(final)
            elif type(CS_LastOutput) == CrosshellDebErr:
                print(CS_LastOutput)
except CrosshellExit as e:
    print(e)