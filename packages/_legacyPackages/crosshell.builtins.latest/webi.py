# [Imports]
from cslib import autopipImport
import webbrowser
import re
requests   = autopipImport("requests")

# [Settings]
channel = "modulo"

# [Get argv]
argus = sargv.strip(" ")

# [Arguments]

_id = ""
_open = False
_list = False

if "-o" in argus or "-open" in argus:
    argus = argus.replace("-open","")
    argus = argus.replace("-o","")
    argus = argus.strip()
    _open = True

if "-list" in argus:
    argus = argus.replace("-list","")
    argus = argus.strip()
    _list = True

if "-id" in argus:
    _id = argus.replace("-id","")
    _id = _id.strip()
else:
    _id = argus

# [Code]

# list
if _list == True:
    id_linkbase = "https://sbamboo.github.io/"
    id_link1 = "websa/crosshell/webi.html"
    url = id_linkbase + id_link1 + "?list=True" + f"&channel={channel}"
    c = "id_shorteners = "
    try:
        rawlist = (((requests.get(url)).text).split(c)[1].split("\n")[0]).replace('"','')
    except IndexError:
        print(f"\033[31mNo atricle returned for keyword '{_id}', use 'webi -list' to list out avaliable articles.\033[0m")
        exit()
    rawlist = rawlist.replace(" ","")
    webiItems = rawlist.split(",")
    print("Avaliable shortener ids: ")
    for item in webiItems:
        print(f"\033[33m{item}\033[0m")

# id
if _id != "" and _id != None:
    id_linkbase = "https://sbamboo.github.io/"
    id_link1 = "websa/crosshell/webi.html"
    url = id_linkbase + id_link1 + f"?id={_id}&giveurl=True" + f"&channel={channel}"
    c = "urllocation_" + _id + " = "
    try:
        newlink = (((requests.get(url)).text).split(c)[1].split("\n")[0]).replace('"','')
    except IndexError:
        print(f"\033[31mNo atricle returned for keyword '{_id}', use 'webi -list' to list out avaliable articles.\033[0m")
        exit()
    print("\033[90mSource: "+url+"\033[0m")
    url = id_linkbase + newlink
    if url == id_linkbase:
        print(f"\033[31mId '{_id}' not found online. Try 'webi -list'\033[0m")
    else:
        if _open == True:
            webbrowser.open(url)
        else:
            content = (requests.get(url)).text
            pattern = r'<h1>.*</h1>|<p>.*</p>|<i>.*</i>|<br>|<h3>.*</h3>|<b>.*</b>'
            matches = re.finditer(pattern,content)
            for m in matches:
                s = m.group()
                s = s.replace("<i>","\033[3m")
                s = s.replace("</i>","\033[23m")
                s = s.replace("<b>","\033[1m")
                s = s.replace("</b>","\033[22m")
                s = s.replace("<h3>","\033[1m")
                s = s.replace("</h3>","\033[22m")
                s = s.replace("<h1>","\033[1mArticle: ")
                s = s.replace("</h1>","\033[22m")
                s = s.replace("<p>","")
                s = s.replace("</p>","")
                s = s.replace("<br>","")
                print(s)