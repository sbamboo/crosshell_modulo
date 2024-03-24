import os
from cslib.pathtools import normPathSep

# FeatureManglers
def readerMangler(data=dict,addMethod=None,readerFile=None,readerFileEncoding="utf-8",readerFileIsStream=False) -> dict:
    # Add the readers to the readerFile
    readers = {}
    for packageType,readerIncludingPkg in data.items():
        for package,readerD in readerIncludingPkg.items():
            for reader in readerD.keys():
                if package.lower() != "builtins":
                    if packageType == "legacy": rootPath = "{CS_lPackPath}"
                    else: rootPath = "{CS_mPackPath}"
                    readerBase = os.path.join(rootPath,package,reader)
                    readerPath = readerBase + ".py"
                    readerName = os.path.splitext(os.path.basename(readerPath))[0]
                    addMethod(readerName,readerPath,readerFile,encoding=readerFileEncoding,isStream=readerFileIsStream)
    return data

def cmdletMangler(data=dict) -> dict:
    return data

def langpckMangler(data=dict,languageProvider=None,languagePath=None,mPackPath=str) -> dict:
    languageFiles = []
    for x in data.values():
        for package,y in x.items():
            for z in y.values():
                for file in z:
                    if mPackPath.endswith("."):
                        mPackPath = (mPackPath[::-1].replace(".","",1))[::-1]
                    fpath = mPackPath + "/" + package + "/Langpck/" + file
                    fpath = normPathSep(fpath)
                    languageFiles.append( fpath )
    if languageProvider != None and languagePath != None:
        for file in languageFiles:
            if os.path.exists(file):
                languagePath.append(os.path.dirname(file))
                languageProvider.populateList()
    return {"langfiles":languageFiles}