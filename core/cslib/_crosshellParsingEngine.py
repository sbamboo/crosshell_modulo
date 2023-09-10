
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
    # Function to reparse pipe elements
    def reparsePipeElements(pipeString):
        split = pipeString.split("|")
        handledString = ""
        for s in split:
            s = s.strip()
            handledString += parseInputString(s) + " | "
        handledString = handledString.rstrip("| ")
        return handledString
    # Function to replace placeholders
    def reReplacePlaceholders(_string):
        return _string.replace("%variableOperator%","$")
    # [Parse]
    stringToParse = parseInputString(stringToParse)
    stringToParse = parseReorderPipes(stringToParse)
    stringToParse = reparsePipeElements(stringToParse)
    stringToParse = reReplacePlaceholders(stringToParse)
    return stringToParse


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
        for tagName,tagValue in toParse.items():
            tagString = '{' + tagName + '}'
            string = string.replace(tagString,tagValue)
        return string
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
    for elem in p_order:
        elem = elem.strip()
        if elem.startswith("||"):
            elem = elem.replace("||","")
            elem = elem.strip()
        if not elem.endswith("||"):
            elem = elem + "||"
        semiorder_str += elem
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