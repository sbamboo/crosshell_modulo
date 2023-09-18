from cslib.externalLibs.conUtils import pause

if sargv != "":
    if CS_IsCaptured == True:
        buffer_cwrite_adv(sargv)
    else:
        print(sargv)
pause()