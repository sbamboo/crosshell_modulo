def buildPrefix(char=str,vars=dict,space=True):
    # get vars
    stripAnsi=vars["stripAnsi"]
    # setup
    format = "{f.magenta}"
    reset = "{r}"
    # handle vars
    if stripAnsi == True:
        format = ""
        reset = ""
    # build
    string = f"{format}{char}{reset}"
    if space == True:
        string += " "
    # return
    return string