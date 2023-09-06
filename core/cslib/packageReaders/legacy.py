from ..datafiles import config_to_dict,dict_to_config
from ..externalLibs.filesys import filesys as fs
from ..cslib import handleOSinExtensionsList

def getDataFromList(packages=list,registry=list):
    # Load readerdata
    readerData = registry["readerData"]
    # Complete list of fendings
    allowedFendings = []
    for reader in readerData:
        print(reader["extensions"])
        allowedFendings.extend( handleOSinExtensionsList(reader["extensions"]) )
    # go through and list for package.json/root.ycfg, then .cfg
    print(packages)
    for package in packages:
        entries = fs.scantree(package)
        for entry in entries:
            fending = "." + fs.getFileExtension(entry.path)
            print(fending,allowedFendings)
    return registry