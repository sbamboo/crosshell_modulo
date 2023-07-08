
import json

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
                parts = inputString.split("+=")
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
    '''CSlib.CSPA: Pathtagmanager class'''
    def __init__(self,defaultPathtags=dict):
        self.defPathtags = defaultPathtags
        self.pathtags = self.defPathtags.copy()
    def addTag(self,tag,value):
        self.pathtags[tag] = value
    def remTag(self,tag):
        if self.pathtags.get(tag) != None:
            self.pathtags.pop(tag)
    def updateTag(self,tagDict=dict):
        self.pathtags.update(tagDict)
    def eval(self,string):
        for tagName,tagValue in self.pathtags.items():
            tagString = '{' + tagName + '}'
            string = string.replace(tagString,tagValue)
        return string