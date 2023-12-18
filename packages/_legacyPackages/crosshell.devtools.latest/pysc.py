try:
    _ = CS_Text
except:
    print("Devtools must be run with runAsInternal enabled!")
    exit()

sargv = sargv.replace("\\%1","§1").replace("\\%2","§2").replace("\\%3","§3").replace("\\%4","§4").replace("\\%5","§5") # esc-placeholders -> placeholder-placeholders
sargv = sargv.replace("%1","(").replace("%2",")").replace("%3",";").replace("%4","'").replace("%5",'"') # placeholder -> char
sargv = sargv.replace("§1","%1").replace("§2","%2").replace("§3","%3").replace("§4","%4").replace("§5","%5") # placeholder-placeholders -> n-esc-placeholders
exec(sargv)