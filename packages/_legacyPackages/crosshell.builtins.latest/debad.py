import os
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
from cslib.execution import exclude_codeblocks

inp = sargv

inclInp = False
if inp.startswith("deb:"):
    inclInp = True
    inp = inp.replace("deb:","")

if inp.strip().startswith("{"):
    inp = inp.replace("{","",1)
elif inp.strip().endswith("}"):
    inp = inp[::-1].replace("}","",1)[::-1]

oinp = inp

inp = inp.replace("{sp}"," ")

lines = []

plines = inp.split("\n")

for line in plines:
    if "\\n" in line:
        lines.extend( line.split("\\n") )
    else:
        lines.append(line)

cathead_col = csSession.data["set"].getProperty("crsh_pkg_debad","Formatting.cathead")
catfill_col = csSession.data["set"].getProperty("crsh_pkg_debad","Formatting.catfill")
catedge_col = csSession.data["set"].getProperty("crsh_pkg_debad","Formatting.catedge")
subtitl_col = csSession.data["set"].getProperty("crsh_pkg_debad","Formatting.subtitl")
subinfo_col = csSession.data["set"].getProperty("crsh_pkg_debad","Formatting.subinfo")

def replBase(s) -> str:
    s = s.replace("{tab}","    ")
    s = s.replace("{sp1}"," "*1)
    s = s.replace("{sp2}"," "*2)
    s = s.replace("{sp3}"," "*3)
    return s

subtitles = {}

for i,line in enumerate(lines):
    if line.startswith("cat@"):
        line = line.replace("cat@","")
        lines[i] = cathead_col.replace("%", replBase(line) )
    elif line.startswith("cate@"):
        line = line.replace("cate@","")
        lines[i] = catedge_col.replace("%", replBase(line) )
    elif line.startswith("catf@"):
        line = line.replace("catf@","")
        lines[i] = catfill_col.replace("%", replBase(line) )
    elif "sub@" in line:
        delim = ":"
        if not line.startswith("sub@"):
            parts = line.split("sub@")
            delim = parts[0]
            line  = parts[1]
            if '"' in delim:
                delim = delim.replace('"',"")
            elif "'" in delim:
                delim = delim.replace("'","")
        if not delim in line:
            line = line.replace("sub@","")
            lines[i] = replBase( subinfo_col.replace("%", line ).replace("{delim}","") )
        else:
            parts = line.split(delim)
            title = replBase(subtitl_col.replace("%", parts[0] ))
            subtitles[i] = title.replace("{delim}","")
            parts.pop(0)
            lines[i] = replBase( title.replace("{delim}",delim) + subinfo_col.replace("%", delim.join(parts) ) )
    if "{fill}" in lines[i]:
        st = lines[i].replace("{fill}","")
        st,_ = exclude_codeblocks(st)
        st = st.replace("!cs.codeblock!","")
        a = int(os.get_terminal_size()[0] - len(st))
        lines[i] = lines[i].replace( "{fill}", str(" "*a))

longestsub = 0
for stitle in subtitles.values():
    if len(stitle) > longestsub:
        longestsub = len(stitle)

longest = 0
for line in lines:
    if len(line) > longest:
        st,_ = exclude_codeblocks(line)
        st = st.replace("!cs.codeblock!","")
        a = int(longest - len(st))
        longest = len(st)

for i,line in enumerate(lines):
    if i in subtitles.keys():
        a = int(longestsub - len(subtitles[i]))
    else:
        a = 0
    lines[i] = line.replace("{auto}",str(" "*a))

    if "{edge}" in line:
        st = line.replace("{edge}","")
        st,_ = exclude_codeblocks(st)
        st = st.replace("!cs.codeblock!","")
        a = int(longest - len(st))
        lines[i] = lines[i].replace("{edge}",str(" "*a))

nlines = []
for line in lines:
    if not line.strip() == "}":
        nlines.append(line)

text = '\n'.join(nlines)

text = text.replace("{strnl}","\\n")

if inclInp:
    oinp = "{f.darkmagenta}\nDebug> Input: {f.darkgray}" + oinp + "{r}" + "\n" 
    text = oinp + "\n" + text

toformat,excludes = exclude_nonToFormat(text)
formatted = csSession.data["txt"].parse(toformat)
text = include_nonToFormat(formatted,excludes)
print(text)