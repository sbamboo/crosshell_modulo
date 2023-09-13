# [CStags]
# readerReturnVars = True
# [TagEnd]


write-host "Hello from powershell!`n"
write-host "Lets write out a crosshell variable:"
write-host "CSScriptRoot: $CSScriptRoot"

write-host "`nLets test legacy-naming:"
write-host "NewVar:(CS_BaseDir): $CS_BaseDir"
write-host "OldVar(csbasedir): $csbasedir"
write-host "OldVar(basedir): $basedir"

& $pwshsup_varexprt "csbasedir"