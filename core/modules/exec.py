from cslib import CrosshellDebErr

entries = [
    "csSession",
    "fprint",
    "csLoadPackageData"
]

try:
    CS_LastOutput = CS_PipeLine.execute(csSession,globals(),entries)
except CrosshellDebErr as e:
    if csSession.data["set"].getProperty("crsh","Execution.OnlyAllowCmdlets") == True:
        CS_LastOutput = e
    else:
        # Do something with the expression
        CS_LastOutput = CS_LastInput