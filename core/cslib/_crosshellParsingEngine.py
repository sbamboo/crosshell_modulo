
import json
import re
from .externalLibs.filesys import filesys

'''
CSlib: Crosshell parsing engine
'''
# Getting the dataType of a string:
def evaluateDataType(toEval):
    if toEval.startswith("[") and toEval.endswith("]"):
        return "list"
    elif toEval.startswith('"') and toEval.endswith('"'):
        return "string"
    elif toEval.isdigit():
        return "int"
    else:
        try:
            json.loads(toEval)
            return "json"
        except ValueError:
            return "string" # Fallback to string

# Check if simple-math-expression
def is_simple_math_expression(expression):
    # Check st-opr
    operators = ["+","-","*","/","//","^","**"]
    if expression[0] in operators or expression[0:1] in operators:
        return False
    # Build a regular expression pattern to match digits, arithmetic operators, parentheses
    pattern = r"^[0-9\.\+\-\*\/\(\)\^\.\s]*$"
    # Use the search function to check if the expression matches the pattern
    try:
        match = re.search(pattern, expression)
    except: pass
    return match is not None

# CrosshellParsingEngine
def crosshellParsingEngine(stringToParse) -> str:
    '''CSPA: CrosshellParsingEngine version 1.0
       Takes string, parses complexSyntax and returns simpleSyntax
       Needs the 'set', 'get', 'append' and 'subtract' cmdlets
    '''
    # [Functions]
    # Function to parse shortVariableAsignSyntax aswell as equalsPipe operations
    def parseInputString(inputString):
        if "=|" in inputString:
            parts = inputString.split("=|")
            variable = parts[0].strip()
            variable = variable.strip("$")
            commands = [command.strip() for command in parts[1].split("|")]
            pipeCommand = " | ".join(commands)
            return f"{pipeCommand} | set {variable}"
        elif "+=" in inputString:
                parts = inputString.split("+=")
                variable = parts[0].strip()
                variable = variable.strip("$")
                parts.pop(0)
                value = ("=".join(parts)).strip("=").strip()
                if "$" in value: value = value.replace("$", "%variableOperator%")
                return f"append {variable} {value}"
        elif "-=" in inputString:
                parts = inputString.split("-=")
                variable = parts[0].strip()
                variable = variable.strip("$")
                parts.pop(0)
                value = ("=".join(parts)).strip("=").strip()
                if "$" in value: value = value.replace("$", "%variableOperator%")
                return f"subtract {variable} {value}"
        elif "=" in inputString:
            if "$" in inputString:
                parts = inputString.split("=")
                variable = parts[0].strip()
                variable = variable.strip("$")
                parts.pop(0)
                value = ("=".join(parts)).strip("=").strip()
                if "$" in value: value = value.replace("$", "%variableOperator%")
                if value == "":
                    return f"get {variable}"  # Handle the case where the value is empty
                data_type = evaluateDataType(value)

                if data_type == "list":
                    return f"set {variable} '{value}'"
                elif data_type == "string":
                    if value.startswith('"') and value.endswith('"'):
                        return f"set {variable} {value}"
                    else:
                        return f"set {variable} \"{value}\""
                elif data_type == "int":
                    return f"set {variable} {value}"
                elif data_type == "json":
                    return f"set {variable} {value}"
            else: return inputString
        else:
            if "$" in inputString:
                variable = inputString.strip("$").strip()
                return f"get {variable}"  # Handle the case where only the variable is provided
            else:
                return inputString
        return ""
    # Function to handle reorderPipeArguments:
    def parseReorderPipes(inputString):
        if "§" in inputString:
            final = ""
            reorderParts = inputString.split("§")
            inputString = inputString.replace("§", "")
            for part in reorderParts:
                part = part.strip()
                # move part to end
                inputString = inputString.replace(part,"",1)
                final = part + inputString
                inputString = inputString.lstrip()
                inputString = inputString + " | " + part
            inputString = inputString.lstrip("|").strip()
            return final
        else:
            return inputString # No reorderPipes so just return
    # Function to handle comments
    def handleComments(string):
        if string.strip(" ").startswith("#"):
            string = "comment " + string.lstrip("#")
        return string
    # Parse "<str>" -> p "<str>"
    def printQoute(string):
        if string.strip(" ").startswith('"'):
            # Find all substrings inside innermost double slashes
            matches = re.findall(r'\"(.*?)\"', string)
            # Replace all innermost double slashes with placeholder
            for match in matches:
                string = string.replace(match,f'p "{match}"',1)
                string = string.replace('"',"",1)
                string = string[::-1].replace('"',"",1)[::-1]
        return string
    # Parse "<mexpr>" -> scalc "mexpr"
    def scalcMexpr(string):
        string2 = string.replace("ans","")
        if string2.strip(" ") == "":
            return string
        if is_simple_math_expression(string2.strip(" ")):
            string = f'scalc "{string.strip(" ")}"'
        return string
    # Function to reparse pipe elements
    def reparsePipeElements(pipeString):
        split = pipeString.split("|")
        handledString = ""
        for s in split:
            s = s.strip()
            s = parseInputString(s)
            s = handleComments(s)
            s = scalcMexpr(s)
            s = printQoute(s)
            handledString += s + " | "
        handledString = handledString.rstrip("| ")
        return handledString
    # Function to replace placeholders
    def reReplacePlaceholders(_string):
        return _string.replace("%variableOperator%","$")
    # [Parse]
    if "|" not in stringToParse and "§" not in stringToParse:
        stringToParse = parseInputString(stringToParse)
    stringToParse = parseReorderPipes(stringToParse)
    stringToParse = reparsePipeElements(stringToParse)
    stringToParse = reReplacePlaceholders(stringToParse)
    return stringToParse

def pathtagManager_parse(string,toParse=dict) -> str:
    '''CSlib.CSPE: Function to parse only a given set of tags, once!'''
    for tagName,tagValue in toParse.items():
        tagString = '{' + tagName + '}'
        string = string.replace(tagString,tagValue)
    return string

def pathtagmanager_parseDict(_dict,toParse=dict) -> dict:
    for key,val in _dict.items():
        if type(val) == str:
            _dict[key] = pathtagManager_parse(val,toParse)
        else:
            _dict[key] = pathtagmanager_parseDict(val,toParse)
    return _dict

class pathtagManager():
    '''CSlib.CSPE: Pathtagmanager class'''
    def __init__(self,defaultPathtags=dict):
        self.defPathtags = defaultPathtags
        self.pathtags = self.defPathtags.copy()
    def addTag(self,tag,value):
        self.pathtags[tag] = value
    def remTag(self,tag):
        if self.pathtags.get(tag) != None:
            self.pathtags.pop(tag)
    def getTag(self,tag):
        return self.pathtags[tag]
    def getTags(self):
        return self.pathtags
    def updateTag(self,tagDict=dict):
        self.pathtags.update(tagDict)
    def eval(self,string,extraPathTags=None) -> str:
        toParse = self.pathtags.copy()
        if extraPathTags != None:
            if type(extraPathTags) != dict:
                raise Exception("If defined, extraPathTags must be of type dict!")
            toParse.update(extraPathTags)
        return pathtagManager_parse(string,toParse)
    def ensureAl(self):
        for _,tagValue in self.pathtags.items():
            if filesys.notExist(tagValue) == True:
                    filesys.ensureDirPath(tagValue)


# Parenthesis
def _get_innermost_parenthesis(string):
    '''CSlib.CSPE: Function to get the innermost parenthesis.'''
    match = re.search(r'\([^()]*\)', string)
    if match:
        return match.group()
    else:
        return ""

def _parse_parenthesis(sinput) -> list:
    '''CSlib.CSPE: Function to order parenthesis by order (Note! dosen't strip or split by any other rule).'''
    text = "(" + sinput + ")"
    colist = []
    while re.search(r'\([^()]*\)', text):
        innermost_parenthesis = _get_innermost_parenthesis(text)
        content = innermost_parenthesis.replace("(","")
        content = content.replace(")","")
        colist.append(content)
        text = text.replace(innermost_parenthesis,"§delim§")
    newColist = []
    for co in colist:
        newColist.extend(co.split("§delim§"))
    colist = []
    for co in newColist:
        if co != "":
            colist.append(co)
    return colist

def _parse_p_order_with_split(p_order=list) -> str:
    '''CSlib.CSPE: Function to semi separate a parenthesis list.'''
    semiorder_str = ""
    for i,elem in enumerate(p_order):
        # Fix broken-pipe-starts
        if elem != "| ":
            elem = elem.strip()
            # I honestly don't know why these where here, so ehm hope they aren't needed
            #if elem.startswith("||"):
            #    elem = elem.replace("||","")
            #    elem = elem.strip()
            if not elem.endswith("||"):
                _next = None
                try:
                    _next = p_order[i+1]
                except: pass
                if _next == None or _next.strip(" ").startswith("|") != True:
                    elem = elem + "||"
            semiorder_str += elem
    # This also fixes broken-pipe-ends
    semiorder_str = semiorder_str.rstrip("||")
    return semiorder_str

def orderParse_parenthesis(sInput) -> str:
    '''CSlib.CSPE: Function to parse parenthesis in order to a semicolon-sepparated list.'''
    return _parse_p_order_with_split( _parse_parenthesis(sInput) )


def split_string_by_spaces(input_string) -> list:
    '''CSlib.CSPE: Function to split a string by spaces not inside qoutes.'''
    substrings = []
    current_substring = []
    inside_quotes = False
    quote_char = None
    for char in input_string:
        if char == ' ' and not inside_quotes:
            # If we encounter a space and we're not inside quotes, consider it as a delimiter
            if current_substring:
                substrings.append(''.join(current_substring))
                current_substring = []
        elif char in ('"', "'"):
            # Toggle the inside_quotes flag and set the quote_char when encountering a quote
            inside_quotes = not inside_quotes
            if inside_quotes:
                quote_char = char
            else:
                quote_char = None
        else:
            # Add the character to the current substring
            current_substring.append(char)
    # Add the last substring if it exists
    if current_substring:
        substrings.append(''.join(current_substring))
    return substrings

def splitByDelimiters_re(inputString, delimiters):
    '''CSlib.CSPE: Split a string by multiple delimiters.
    Split the input string by any of the specified delimiters.

    Args:
    input_string (str): The string to be split.
    delimiters (list): A list of delimiter strings.

    Returns:
    list: A list of substrings obtained by splitting the input string by any of the delimiters.
    '''
    # Combine all delimiters into a single regular expression pattern
    delimiterPattern = '|'.join(map(re.escape, delimiters))
    
    # Use the re.split() function to split the string by the combined delimiter pattern
    substrings = re.split(delimiterPattern, inputString)
    
    return substrings

def splitByDelimiters(inputString, delimiters):
    '''CSlib.CSPE: Split a string by multiple delimiters.
    Split the input string by any of the specified delimiters.

    Args:
    input_string (str): The string to be split.
    delimiters (list): A list of delimiter strings.

    Returns:
    list: A list of substrings obtained by splitting the input string by any of the delimiters.
    '''
    substrings = [inputString]
    for delimiter in delimiters:
        newSubstrings = []
        for substring in substrings:
            newSubstrings.extend(substring.split(delimiter))
        substrings = newSubstrings
    return substrings

def splitSafe_parse(text,delims=["||"]):
    '''CSlib.CSPE: Safely parse splits.'''
    segments = splitByDelimiters(text, delims)
    for i,segment in enumerate(segments):
        segments[i] = crosshellParsingEngine(segment)
    _str = "||".join(segments)
    return _str.strip("||")

def useOnlyDoublePipeSplit(text) -> str:
    '''CSlib.CSPE: Function to replace ; with ||.'''
    result = []
    inside_braces = False
    if text != None:
        for char in text:
            if char == '{':
                inside_braces = True
            elif char == '}':
                inside_braces = False
            if char == ';' and not inside_braces:
                result.append('||')
            else:
                result.append(char)
        return ''.join(result)
    else:
        return text


def exclude_nonToFormat(input_string):
    # Find all substrings inside innermost double slashes
    pattern = r'//([^/]+)//'
    matches = re.findall(pattern, input_string)

    if not matches:
        # If no innermost double slashes found, return the input string as is
        return (input_string, [])

    # Replace all innermost double slashes with §cs.toNotFormat§
    replaced_string = re.sub(pattern, '§cs.toNotFormat§', input_string)

    return (replaced_string, matches)


def include_nonToFormat(input_string, substrings):
    for substring in substrings:
        # Remove // from the beginning and end of the substring
        clean_substring = substring.strip('/')
        # Replace "§cs.toNotFormat§" with the cleaned substring
        input_string = input_string.replace("§cs.toNotFormat§", clean_substring, 1)
    return input_string

def find_qoutedSubstrings(string,pattern,placeholder):
    # Find all substrings inside innermost double slashes
    matches = re.findall(pattern, string)
    if not matches:
        # If no innermost double slashes found, return the input string as is
        return (string, [])
    # Replace all innermost double slashes with placeholder
    replaced_string = re.sub(pattern, placeholder, string)
    return (replaced_string, matches)

def fix_qoutedSubStrings(matches,toReplace,replaceWidth):
    for i,match in enumerate(matches):
        matches[i] = '"' + match.replace(toReplace,replaceWidth) + '"'
    return matches

def include_substrings(input_string, substrings, placeholder):
    for substring in substrings:
        # Replace "§cs.qoutedString§" with the substring
        input_string = input_string.replace(placeholder, substring, 1)
    return input_string

def placeholdAnyQouted(string,pattern,placeholder,toReplace,replaceWith) -> str:
    s2,x = find_qoutedSubstrings(string,pattern,placeholder)
    x = fix_qoutedSubStrings(x,toReplace,replaceWith)
    s3 = include_substrings(s2, x,placeholder)
    return s3

def placeholdAnyQoutedX(string,replaceWith):
    placeholder = "§copied§"
    newstr = placeholdAnyQouted(
        string=      string,
        pattern=     r'\"(.*?)\"',
        placeholder= "§cs.qoutedSubString§",
        toReplace=   replaceWith,
        replaceWith= placeholder
    )
    return newstr,placeholder

def findVariables(string):
    pattern = r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    variables = re.findall(pattern, string)
    return variables

def fixDoubleGet(string,csSession):
    split = string.split("||")
    for i,p in enumerate(split):
        if p.startswith("get get "):
            th = split_string_by_spaces(p.replace("get get ","",1))[0]
            cmdletNames = []
            for key,cmdlet in csSession.registry["cmdlets"].items():
                cmdletNames.extend(key)
                if cmdlet.get("aliases") != None:
                    cmdletNames.extend(cmdlet["aliases"])
            if th in cmdletNames:
                p = p.replace("get get ","",1)
                var = findVariables(p)[0]
                p = p.replace(var+" ","")
                p = p.replace(var,"")
                p = f"get {var.replace('$','')} | " + p
            else:
                p = p.replace("get get ","get ")
                for var in findVariables(p):
                    p = p.replace(var,var.lstrip("$"))
        split[i] = p
    string = '||'.join(split)
    return string