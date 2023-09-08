from ..cslib.externalLibs.filesys import filesys as fs
from ..cslib import handleOSinExtensionsList

def determine_reader(command=str,registry=dict) -> str:
    # Get fending
    fending = fs.getFileExtension(command)
    if fending == None:
        fending = "MIME_EXECUTABLE"
    # Match
    readers = registry["readerData"]
    for reader in readers:
        if fending in handleOSinExtensionsList(reader["extensions"]):
            return reader

def command_to_path(command=str,registry=dict) -> str:
    for cmdlet,cmdletData in registry["cmdlets"]:
        if cmdlet.lower() == command.lower():
            return cmdletData["path"]

def execute_expression(command=str,args=list,capture=False):
    path = command_to_path(command)

# Pipeline class
class pipeline():
    '''CSlib: Main crosshell pipeline class.'''
    def __init__(self):
        self._reset_pipeline()
    def _reset_pipeline(self):
        self.pipeline = {
            "elements": [],
            "current_content": None,
            "current_elementIndex": 0
        }
    def _execute_element(self,command=str,args=list) -> dict:
        return execute_expression(command,args,True)
    def execute(self):
        elements = self.pipeline["elemenents"]
        for element in elements:
            element["args"] = [self.pipeline["current_content"],*element["args"]]
            self.pipeline["current_content"] = self._execute_element(element["command"],element["args"])
            self.pipeline["current_elementIndex"] += 1
        out = self.pipeline["current_content"]
        self._reset_pipeline()
        return out