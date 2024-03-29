# Imports
from cslib.execution import execline
from cslib.externalLibs.conUtils import setConTitle,clear
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
from cslib._crosshellGlobalTextSystem import removeAnsiSequences
from cslib import CrosshellDebErr,writeWelcome

# Create a pipeline object
CS_PipeLine = execline()

# Do on-start operations
if CS_Settings.getProperty("crsh","Console.ClearOnStart") == True and CS_Pargs.nocls != True:
    clear()
if CS_Settings.getProperty("crsh","Console.Welcome.ShowOnStart") == True and CS_Pargs.nowelc != True:
    writeWelcome(csSession)

# Main loop
while True:
    # Fix title
    title = CS_Persistance.getProperty("crsh","Title")
    if title == None:
        title = CS_Settings.getProperty("crsh","Console.DefTitle")
    setConTitle( title )
    # Get prefix and ask user for input
    _prefix = getPrefix(csSession,"> ")
    if CS_Pargs.cmd != None:
        CS_LastInput = CS_Pargs.cmd
    elif CS_Registry["sInputInstance"] != None:
        CS_LastInput = CS_Registry["sInputInstance"].prompt(_prefix)
    else:
        # Hide toad if sInput disabled
        if CS_Registry["toadInstance"].no_si_showToad == True:
            CS_Registry["toadInstance"].showToad()
        else:
            CS_Registry["toadInstance"].remNoSIToad()
        # Prompt
        CS_LastInput = input(_prefix)
    CS_LastOutput = None
    # Execute input
    if CS_LastInput != "":
        CS_Inpparse.execute_internally(globals())
        CS_Exec.execute_internally(globals())
    # Handle output
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
    # Exit post cli-cmd exec
    if CS_Pargs.cmd != None:
        # Clear input values
        CS_Pargs.cmd = None
        # Exit?
        if CS_Pargs.noexit == False:
            # clear using ansi to stop coloring terminal post crosshell
            if csSession.data["sta"] != True:
                print("\033[0m")
            # break loop to exit
            break