toad = csSession.registry["toadInstance"]
sInput = csSession.registry["sInputInstance"]

import re

def swapp_ansi_ground(ansicode=str):
    _swapp_mapping = {
        "0": "0",
        "30": "40",
        "31": "41",
        "32": "42",
        "33": "43",
        "34": "44",
        "35": "45",
        "36": "46",
        "37": "47",
        "90": "100",
        "91": "101",
        "92": "102",
        "93": "103",
        "94": "104",
        "95": "105",
        "96": "106",
        "97": "107",
    }
    swapp_mapping = _swapp_mapping.copy()
    for key,value in _swapp_mapping.items():
        swapp_mapping[value] = key
    # Find
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Define a regular expression pattern to match ANSI escape codes
    matches = ansi_escape_pattern.finditer(ansicode)                           # Use re.finditer to find all matches in the input string
    # Replace
    for match in matches:
        code = str(match.group())
        ocode = code
        if "38;2" in code or "48;2" in code:
            # replace rgb
            code = code.replace("48;2","§rgb-swapp§")
            code = code.replace("38;2","48;2")
            code = code.replace("§rgb-swapp§","38;2")
        else:
            if len(code) == 8 or len(code) == 9:
                code = swapp_mapping[code]
        ansicode = ansicode.replace(ocode,code,1)
    return ansicode


timed = False
if "-t" in argv:
    tindex = argv.index("-t")
    try:
        timed = argv[tindex+1]
        argv.pop(tindex)
    except: pass
    argv.pop(tindex)

# invert formatting
sargv = swapp_ansi_ground(sargv)
#sargv = sargv.replace("\033","esc")

# timed
if timed != False:
    toad.timedMsgNu(' '.join(argv),float(timed))
# no-timed
else:
    toad.setOnetime(f"{sargv}")

toad.updNoSIToad()