import re

from cslib.fuzzy import fuzzy_substring_search


def extractComments(json_or_yaml_string=str) -> (str,dict):
    if json_or_yaml_string != None:
        split = json_or_yaml_string.split("\n")
        newsplit = []
        extractedLines = {}
        split2 = []
        for elem in split:
            if elem.strip(" ") != "":
                split2.append(elem)
        split = split2
        for i,line in enumerate(split):
            strip = line.strip(" ")
            if strip.startswith("#") or strip.startswith("//"):
                extractedLines[i] = line
            else:
                newsplit.append(line)
        new = '\n'.join(newsplit)
        return new,extractedLines
    else:
        return json_or_yaml_string,None

def injectComments(json_or_yaml_string,extractedLines) -> str:
    if json_or_yaml_string != None and extractedLines != None and extractedLines != {}:
        split = json_or_yaml_string.split("\n")
        for i,line in extractedLines.items():
            split = injectStringAtIndex(split,i,line)
        return '\n'.join(split)
    else:
        return json_or_yaml_string

def injectStringAtIndex_dict(dictToInjectTo=dict, index=int, string=str) -> dict:
    # Create a list to store the dictionary items as (index, value) tuples
    items = list(dictToInjectTo.items())
    # Insert the new key-value pair at the specified index
    items.insert(index, (index, string))
    # Iterate over the remaining items and increment their keys
    for i in range(index + 1, len(items)):
        old_key, value = items[i]
        new_key = old_key + 1
        items[i] = (new_key, value)
    # Convert the modified list of items back to a dictionary
    modified_dict = dict(items)
    return modified_dict

def injectStringAtIndex_list(listToInjectTo=list, index=int, string=str) -> list:
    return listToInjectTo[:index] + [string] + listToInjectTo[index:]

def extractComments_newlineSupport(json_or_yaml_string=str) -> (str,dict):
    if json_or_yaml_string != None:
        split = json_or_yaml_string.split("\n")
        newsplit = []
        extractedLines = {}
        for i,elem in enumerate(split):
            if elem == "":
                split[i] = "§newline§"
        for i,line in enumerate(split):
            strip = line.strip(" ")
            if strip.startswith("#") or strip.startswith("//"):
                extractedLines[i] = line
            elif strip == "§newline§":
                extractedLines[i] = "\n"
            else:
                newsplit.append(line)
        new = '\n'.join(newsplit)
        return new,extractedLines
    else:
        return json_or_yaml_string,None

def injectComments_newlineSupport(json_or_yaml_string,extractedLines) -> str:
    if json_or_yaml_string != None and extractedLines != None and extractedLines != {}:
        split = json_or_yaml_string.split("\n")
        for i,line in extractedLines.items():
            split = injectStringAtIndex(split,i,line)
        newstring = ""
        for elem in split:
            if elem != "\n":
                newstring += "\n" + elem
            else:
                newstring += elem
        return newstring.strip("\n")
    else:
        return json_or_yaml_string

def _stripJsonComments(jsonString):
    commentPattern = r'(\/\/[^\n]*|\/\*[\s\S]*?\*\/)'
    jsonWithoutComments = re.sub(commentPattern, '', jsonString)
    return jsonWithoutComments

def is_substring_enclosed_by_double_quotes(s: str, substring: str) -> bool:
    inside_quotes = False
    substring_length = len(substring)
    quote_char = '"'
    for i in range(len(s) - substring_length + 1):
        if s[i:i + substring_length] == substring:
            if inside_quotes:
                return True  # Found the substring enclosed by quotes
        if s[i] == quote_char:
            inside_quotes = not inside_quotes  # Toggle the flag when encountering quotes
    return False

def is_substring_enclosed_by_single_quotes(s: str, substring: str) -> bool:
    inside_quotes = False
    substring_length = len(substring)
    quote_char = "'"
    for i in range(len(s) - substring_length + 1):
        if s[i:i + substring_length] == substring:
            if inside_quotes:
                return True  # Found the substring enclosed by quotes
        if s[i] == quote_char:
            inside_quotes = not inside_quotes  # Toggle the flag when encountering quotes
    return False

def is_substring_enclosed_by_any_qoutes(s: str, substring: str) -> bool:
    return is_substring_enclosed_by_double_quotes(s, substring) or is_substring_enclosed_by_single_quotes(s, substring)

def first_substring_occurrence(s: str, substring1: str, substring2: str) -> str:
    index1 = s.find(substring1)
    index2 = s.find(substring2)
    if index1 == -1 and index2 == -1:
        return None  # Neither substring found
    elif index1 == -1:
        return substring2  # Only substring2 found
    elif index2 == -1:
        return substring1  # Only substring1 found
    else:
        return substring1 if index1 < index2 else substring2  # Return the substring with the smaller index

def getContext(extractLineData,default="bottom-connecting"):
    """Returns in format: tuple(<contextName>, <lineIndex>, <contextIndex>, <contextStr>)
    
    newline:
        The line is on a newline.
        `
        \n
        `

    same-line-at-end:
        The comment is on the same line as the reference, but at the end of the line.
        `
        hello: world # comment
        `

    only-comment:
        The comment is the only thing in the doc.
        `
        # comment
        `

    first-line-comment:
        The comment is on the first line of the doc.
        `
        # comment
        hello: world
        `

    last-line-comment:
        The comment is on the last line of the doc.
        `
        hello: world
        # comment
        `

    no-context:
        There is no context.
        `
        ..\n..
        # comment
        ..\n..
        `

    bottom-connecting:
        The comment is related to the line below it.
        `
        ..\n..
        # comment
        world: hello
        `

    top-connecting:
        The comment is related to the line above it.
        `
        hello: world
        # comment
        ..\n..
        `

    """
    line_ind = extractLineData["comment"][0]
    if extractLineData["type"] == "reff":
        top_ind = extractLineData["reff_top"][0]
        dow_ind = extractLineData["reff_dow"][0]
    else:
        top_ind = extractLineData["comment"][0]
        dow_ind = extractLineData["comment"][0]
    if extractLineData["isNewline"] == True:
        if top_ind == line_ind and dow_ind == line_ind:
            return ("newline-top",line_ind,top_ind,extractLineData["reff_top"][1])
        elif top_ind == line_ind:
            return ("newline-bot",line_ind,dow_ind,extractLineData["reff_dow"][1])
        elif dow_ind == line_ind:
            return ("newline-top",line_ind,top_ind,extractLineData["reff_top"][1])
    else:
        if extractLineData["type"] == "reff-before":
            return ("same-line-at-end",line_ind,line_ind,extractLineData["reff"][1])
        else:
            if extractLineData["reff_top"][1] == extractLineData["comment"][1] and extractLineData["reff_dow"][1] == extractLineData["comment"][1]:
                return ("only-comment",line_ind,line_ind,extractLineData["comment"][1])
            elif extractLineData["reff_top"][1] == extractLineData["comment"][1]:
                return ("first-line-comment",line_ind,dow_ind,extractLineData["comment"][1])
            elif extractLineData["reff_dow"][1] == extractLineData["comment"][1]:
                return ("last-line-comment",line_ind,top_ind,dow_ind,extractLineData["comment"][1])
            else:
                if extractLineData["reff_top"][1] in ["§newline§","\u00a7newline\u00a7"] and extractLineData["reff_dow"][1] in ["§newline§","\u00a7newline\u00a7"]:
                    return ("no-context",line_ind,-1,extractLineData["comment"][1])
                elif extractLineData["reff_top"][1] in ["§newline§","\u00a7newline\u00a7"]:
                    return ("bottom-connecting",line_ind,dow_ind,extractLineData["reff_dow"][1])
                elif extractLineData["reff_dow"][1] in ["§newline§","\u00a7newline\u00a7"]:
                    return ("top-connecting",line_ind,top_ind,extractLineData["reff_top"][1])
                else:
                    return (default,line_ind,dow_ind,"")

def _isConfigColor(string,cmntType="#"):
    if cmntType == None:
        if "#" in string:
            cmntType = "#"
        else:
            cmntType = "//"
    if string.split(cmntType)[0].strip(" ").endswith("fg:") or string.split(cmntType)[0].strip(" ").endswith("bg:"):
        return True
    else:
        return False

def _isAllowed(string,cmntType=None):
    if is_substring_enclosed_by_any_qoutes(string,cmntType) or _isConfigColor(string,"#"):
        return False
    else:
        return True

def extractComments_v2(json_or_yaml=str, discard_newline=True) -> (str,dict):
    type_ = "json" if json_or_yaml.strip(" ").startswith("{") else "yaml"
    if type_ == "json": raise Exception("JSON not supported yet.")
    if json_or_yaml == None:
        return json_or_yaml,None
    dataDict = {
        "type": type_,
        "cmnts": {}
    }
    split = json_or_yaml.split("\n")
    newsplit = []
    extractedLines = []
    for i,elem in enumerate(split):
        if discard_newline != True:
            if elem == "":
                split[i] = "§newline§"
    for i,line in enumerate(split):
        strip = line.strip(" ")
        if strip.startswith("#"):
            reff_top = (i-1,split[i-1]) if i-1 >= 0 else (i,line)
            reff_dow = (i+1,split[i+1]) if i+1 <= len(split)-1 else (i,line)
            data = {
                "type": "reff",
                "comment": (i,line),
                "reff_top": reff_top,
                "reff_dow": reff_dow,
                "isNewline": False,
                "cmntType": "#"
            }
            extractedLines.append(data)
        elif strip.startswith("//"):
            reff_top = (i-1,split[i-1]) if i-1 >= 0 else (i,line)
            reff_dow = (i+1,split[i+1]) if i+1 <= len(split)-1 else (i,line)
            data = {
                "type": "reff",
                "comment": (i,line),
                "reff_top": reff_top,
                "reff_dow": reff_dow,
                "isNewline": False,
                "cmntType": "//"
            }
            extractedLines.append(data)
        elif strip == "§newline§":
            reff_top = (i-1,split[i-1]) if i-1 >= 0 else (i,line)
            reff_dow = (i+1,split[i+1]) if i+1 <= len(split)-1 else (i,line)
            data = {
                "type": "reff",
                "comment": (i,line),
                "reff_top": reff_top,
                "reff_dow": reff_dow,
                "isNewline": True,
                "cmntType": None
            }
            extractedLines.append(data)
        elif "#" in line or "//" in line:
            if _isAllowed(line, "#"):
                if _isAllowed(line, "//"):
                    # find first of # and //
                    first = first_substring_occurrence(line, "#", "//")
                    # split at first of # and //
                    before = None
                    after = None
                    cmntType = None
                    if first == "#":
                        data = line.split("#")
                        before = data[0]
                        after = "#" + data[1]
                        cmntType = "#"
                    else:
                        data = line.split("//")
                        before = data[0]
                        after = "//" + data[1]
                        cmntType = "//"
                    # add to extractedLines and newsplit
                    extractedLines.append({
                        "type": "reff-before",
                        "comment": (i,after),
                        "reff": (i,before),
                        "isNewline": False,
                        "cmntType": cmntType
                    })
                    newsplit.append(before)
                else:
                    # split by first #
                    before = None
                    after = None
                    data = line.split("#")
                    before = data[0]
                    after = "#" + data[1]
                    # add to extractedLines and newsplit
                    extractedLines.append({
                        "type": "reff-before",
                        "comment": (i,after),
                        "reff": (i,before),
                        "isNewline": False,
                        "cmntType": "#"
                    })
                    newsplit.append(before)
            elif _isAllowed(line, "//"):
                print(_isAllowed(line, "//"))
                if _isAllowed(line, "#"):
                    # find first of # and //
                    first = first_substring_occurrence(line, "#", "//")
                    # split at first of # and //
                    before = None
                    after = None
                    cmntType = None
                    if first == "#":
                        data = line.split("#")
                        before = data[0]
                        after = "#" + data[1]
                        cmntType = "#"
                    else:
                        data = line.split("//")
                        before = data[0]
                        after = "//" + data[1]
                        cmntType = "//"
                    # add to extractedLines and newsplit
                    extractedLines.append({
                        "type": "reff-before",
                        "comment": (i,after),
                        "reff": (i,before),
                        "isNewline": False,
                        "cmntType": cmntType
                    })
                    newsplit.append(before)
                else:
                    # split by first //
                    before = None
                    after = None
                    data = line.split("//")
                    before = data[0]
                    after = "//" + data[1]
                    # add to extractedLines and newsplit
                    extractedLines.append({
                        "type": "reff-before",
                        "comment": (i,after),
                        "reff": (i,before),
                        "isNewline": False,
                        "cmntType": "//"
                    })
                    newsplit.append(before)
            else:
                newsplit.append(line)
        else:
            newsplit.append(line)
    for i,d in enumerate(extractedLines):
        extractedLines[i]["context"] = getContext(d)
    return '\n'.join(newsplit),extractedLines

def injectComments_v2(lines,extractedLines, attemptFuzzy=False, samelineSpacer="", discard_newline=True) -> str:
    print(lines,"\n\n",len(lines))
    raise Exception("STOP")
    for eline in extractedLines:
        try:
            contextName = eline["context"][0]
            lineIndex = eline["context"][1]
            contextIndex = eline["context"][2]
            reffLine = eline["context"][3]
            comment = eline["comment"][1]
        except Exception as e:
            print(e,"\n\n",eline)
        # attempt to find index
        foundInd = None
        for i,l in enumerate(lines):
            if eline["cmntType"] != None and eline["cmntType"] in l:
                p = l.split( eline["cmntType"] )[0].strip()
            else: p = ""
            if l == reffLine:
                foundInd = i
                break
            elif reffLine in p:
                foundInd = i
                break

            else:
                if not is_substring_enclosed_by_any_qoutes(l,": "):
                    key = reffLine.split(": ")[0].strip()
                    if key in l:
                        foundInd = i
                        break
                elif attemptFuzzy == True and p != "":
                    foundInd = fuzzy_substring_search(p,lines)
                    break
        # Newline-top
        if contextName == "newline-top" and discard_newline == False:
            if foundInd != None:
                ind = foundInd-1
                if ind >= 0:
                    lines = injectStringAtIndex_list(lines,ind,comment)    
                else:
                    lines = injectStringAtIndex_list(lines,lineIndex,comment)
            else:
                lines = injectStringAtIndex_list(lines,lineIndex,comment)
        # Newline-bot
        elif contextName == "newline-bot" and discard_newline == False:
            if foundInd != None:
                ind = foundInd+1
                if ind <= len(lines)-1:
                    lines = injectStringAtIndex_list(lines,ind,comment)    
                else:
                    lines = injectStringAtIndex_list(lines,lineIndex,comment)
            else:
                lines = injectStringAtIndex_list(lines,lineIndex,comment)
        # Same-line-at-end
        elif contextName == "same-line-at-end":
            if foundInd != None:
                lines[foundInd] = str(lines[foundInd]) + str(samelineSpacer) + str(comment)
            else:
                #if eline["reff_top"][0] == lineIndex and eline["reff_dow"][0] == lineIndex:
                #    lines[lineIndex] = str(lines[lineIndex]) + str(samelineSpacer) + str(comment)
                #elif eline["reff_top"][0] == lineIndex:
                #    ind = eline["reff_dow"][0]+1
                #    if ind <= len(lines)-1:
                #        lines[ind] = str(lines[ind]) + str(samelineSpacer) + str(comment)
                #    else:
                #        lines[lineIndex] = str(lines[lineIndex]) + str(samelineSpacer) + str(comment)
                #elif eline["reff_dow"][0] == lineIndex:
                #    ind = eline["reff_top"][0]-1
                #    if ind >= 0:
                #        lines[ind] = str(lines[ind]) + str(samelineSpacer) + str(comment)
                #    else:
                #        lines[lineIndex] = str(lines[lineIndex]) + str(samelineSpacer) + str(comment)
                #else:
                #    lines[lineIndex] = str(lines[lineIndex]) + str(samelineSpacer) + str(comment)
                lines[lineIndex] = str(lines[lineIndex]) + str(samelineSpacer) + str(comment)
        # Only-comment
        elif contextName == "only-comment":
            midInd = len(lines)//2
            try:
                lines[midInt] = comment
            except:
                lines.append(comment)
        # First-line-comment
        elif contextName == "first-line-comment":
            lines = injectStringAtIndex_list(lines,0,comment)
        # Last-line-comment
        elif contextName == "last-line-comment":
            lines.append(comment)
        # No-context
        elif contextName == "no-context":
            try:
                lines[lineIndex] = comment
            except:
                lines.append(comment)
        # Bottom-connecting
        elif contextName == "bottom-connecting":
            if foundInd != None:
                ind = foundInd-1
                if ind >= 0:
                    lines = injectStringAtIndex_list(lines,ind,comment)    
                else:
                    lines = injectStringAtIndex_list(lines,lineIndex,comment)
            else:
                lines = injectStringAtIndex_list(lines,lineIndex,comment)
        # Top-connecting
        elif contextName == "top-connecting":
            if foundInd != None:
                ind = foundInd+1
                if ind <= len(lines)-1:
                    lines = injectStringAtIndex_list(lines,ind,comment)    
                else:
                    lines = injectStringAtIndex_list(lines,lineIndex,comment)
            else:
                lines = injectStringAtIndex_list(lines,lineIndex,comment)
    return '\n'.join(lines).replace("§newline§\n","\n").replace("\u00a7newline\u00a7\n","\n")

def finBet(c, sd, ed):
    pattern = re.compile(re.escape(sd) + r'((?:[^' + re.escape(sd+ed) + r']*' + re.escape(sd) + r'[^' + re.escape(sd+ed) + r']*' + re.escape(ed) + r')*[^' + re.escape(sd+ed) + r']*?)' + re.escape(ed))
    match = pattern.search(c)
    if match:
        return match.group(0)
    else:
        return None

def finBetWl(c, sd, ed, stackPlaceholder="§STACK:%§",startOnIndex=0):
    matches = []
    def replace(match):
        nonlocal matches, stackPlaceholder, startOnIndex
        matches.append(match.group(0))
        return stackPlaceholder.replace("%",str(len(matches)-1+startOnIndex))
    pattern = re.compile(re.escape(sd) + r'((?:[^' + re.escape(sd+ed) + r']*' + re.escape(sd) + r'[^' + re.escape(sd+ed) + r']*' + re.escape(ed) + r')*[^' + re.escape(sd+ed) + r']*?)' + re.escape(ed))
    modified_text = pattern.sub(replace, c)
    return modified_text, matches