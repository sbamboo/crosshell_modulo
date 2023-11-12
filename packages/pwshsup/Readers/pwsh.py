import os
import ast

from cslib.execution import execute_string

def main(session,cmddata=dict,args=list,encoding=str,defencoding=str,isCaptured=bool,globalValues=dict):
    ps1file = cmddata["path"]
    args = args
    encoding = encoding
    sendVars = False
    passbackVars = False
    legacyNames = False
    allowFuncCalls = False
    if cmddata.get("extras") != None:
        _true = ["true","True",True]
        _sendVars = cmddata["extras"].get("pwsh.passCSvars")
        _passbackVars = cmddata["extras"].get("pwsh.returnCSVars")
        _legacyNames = cmddata["extras"].get("pwsh.legacyNames")
        _allowFuncCalls = cmddata["extras"].get("pwsh.allowFuncCalls")
        if _sendVars in _true: sendVars = True
        if _passbackVars in _true: passbackVars = True
        if _legacyNames in _true: legacyNames = True
        if _allowFuncCalls in _true: allowFuncCalls = True
    pwshPath = "pwsh"
    sendBackVars = {}
    # Get .pwsh folder
    supportFolder = os.path.join(os.path.abspath(os.path.dirname(cs_readerPath)),".pwsh")
    # Std execute
    if sendVars == False:
        command = f"{pwshPath} {ps1file} {' '.join(args)}"
        if cs_lph_isAllowed(command) == True:
            os.system(command)
        else:
            session.deb.perror("lng:cs.cmdletexec.longpath.nonallowed",raiseEx=True)
    # Send variables:
    else:
        # Add some variables
        if passbackVars == True:
            globalValues["pwshsup_varexprt"] = f"{supportFolder}{os.sep}pwsh_exportVariables.ps1"
        if allowFuncCalls == True:
            globalValues["pwshsup_funcCall"] = f"{supportFolder}{os.sep}pwsh_functionCaller.ps1"
        # Lets init a vars str
        vars = str()
        # Iterage over globals
        for key,value in globalValues.items():
            # Remove function and object elements
            if not "<function" in str(value) and not "<module" in str(value) and not "__" in str(value) and not " object at " in str(value) and not str(value) == "":
                # Handle double slash
                if "\\\\" in str(value):
                    value = str(value).replace("\\\\","\\")
                # Add
                vars += f"{key}§{value}§¤§"
        # Strip placeholder from end of string
        vars.rstrip("§¤§")
        # Strip spaces from vars
        vars = vars.replace(" ","{s}")
        # Handle qoutes
        vars = vars.replace('"',"{q}")
        # Setup some filepaths
        runtime = f"{supportFolder}{os.sep}runtime.ps1"
        exitFile = f"{supportFolder}{os.sep}exit.empty"
        passbackFile = f"{supportFolder}{os.sep}passback.vars"
        funcCallFile = f"{supportFolder}{os.sep}passback.calls"
        # If an exitfile exists remove it
        if os.path.exists(exitFile) == True:
            os.remove(exitFile)
        # Run the runtime script
        rtcommand = f'{pwshPath} {runtime} {ps1file} "{vars}" {passbackVars} {legacyNames} {allowFuncCalls}'
        os.system(rtcommand)
        # Handle passbacks if enabled
        if passbackVars == True:
            # While loop to wait for passbackfiles
            while True:
                # If allowFuncCalls check for functionCalls
                if os.path.exists(funcCallFile) == True:
                    # Try getting the content
                    try:
                        content = open(funcCallFile,'r',encoding=defencoding).read()
                        content = content.rstrip("\n")
                    except:
                        content = ""
                    # Remove the file
                    os.remove(funcCallFile)
                    # Handle decode atempt
                    if "{%1%}" in content or "{%2%}" in content:
                        content = content.replace("{%2%}",'"')
                        content = content.replace("{%1%}","'")
                    # Send call to be executed in crosshell
                    execute_string(content,session,capture=False,globalVals=globalValues)
                # If a variablePassbackFilee exists break the loop (Since they are post-exec)
                if os.path.exists(passbackFile) == True:
                    break
            # Handle passback file
            try:
                content = open(passbackFile,'r',encoding=defencoding).read()
            except:
                content = None
            if os.path.exists(passbackFile):
                os.remove(passbackFile)
            if content != None:
                # Parse out the runtimes passback string
                passBacks = content.split("§¤§")
                # Remove empty last element
                if passBacks[-1] == "": passBacks.pop(-1)
                # Iterate through out the variables and parse out name and value
                for var in passBacks:
                    if var != "" and var != "\n":
                        name = var.split("§")[0]
                        value = var.replace(f"{name}§", "")
                        # If the name starts with a ! dont eval the value and just add it
                        if name[0] == "!":
                            name = name.lstrip("!")
                            sendBackVars[name] = value.strip("'")
                        # If no !, literal_eval the input and then add it
                        else:
                            # Check if value is string and if so add "" to help literal_eval
                            if str(value)[0] != "[" and str(value)[0] != '"': value = '"' + str(value) + '"'
                            # Eval
                            value2 = ast.literal_eval(value)
                            sendBackVars[name] = value2
        # If a exit.empty file exists remove it
        if os.path.exists(exitFile):
            os.remove(exitFile)
        # return sendback if exists
        if sendBackVars != None:
            return sendBackVars
