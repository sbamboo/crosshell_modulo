if csSession.data["set"].getProperty("crsh","Execution.PrintComments") == True:
    if sargv.startswith(" "):
        sargv = sargv.strip(" ")
    print("{!90m}"+sargv+"{r}")