# [CStags]
# pwsh.passCSvars = True
# pwsh.returnCSVars = True
# pwsh.legacyNames = True
# pwsh.allowFuncCalls = True
# [TagEnd]

write-host "Hello from powershell!`n"
write-host "Lets write out a crosshell variable:"
write-host "CSScriptRoot: $CSScriptRoot"

write-host "`nLets test legacy-naming:"
write-host "NewVar:(CS_BaseDir): $CS_BaseDir"
write-host "OldVar(csbasedir): $csbasedir"
write-host "OldVar(basedir): $basedir"

write-host "`nLets print the welcome message by calling welcome:"
& $pwshsup_funcCall "welcome"

write-host "`nGood now lets return out some variables"

pause

& $pwshsup_varexprt "csbasedir"