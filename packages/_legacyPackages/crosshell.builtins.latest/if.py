if len(argv) < 2:
    print(csSession.deb.get("If called with invalid input, please provide both a condition and codeblock!","exception"))
    exit()

def strCB(s):
    if s.startswith("{"):
        s = s.replace("{","",1)
    if s.endswith("}"):
        s = s[::-1].replace("}","",1)[::-1]
    return s

statement = argv[0]
codeblock = ' '.join(argv[1:])

print(f"Conditional Statement: {statement}")
print(f"Executional Codeblock: {codeblock}")

from cslib.externalLibs.filesys import filesys as fs
from cslib.execution import execline

# Save prev
old_CS_LastInput = CS_LastInput
old_CS_LastOutput = CS_LastOutput
old_CS_PipeLine = CS_PipeLine

def execStr(s):
    raw_content = s
    lines = raw_content.split("\n")

    # Create pipeline
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
                    return final
                elif type(CS_LastOutput) == CrosshellDebErr:
                    return CS_LastOutput
    except CrosshellExit as e:
        return e

execStr(statement)