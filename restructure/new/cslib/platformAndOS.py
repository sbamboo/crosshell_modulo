from cslib.externalLibs.conUtils import *

def handleOSinExtensionsList(extensions=list) -> list:
    '''CSlib: Smal function for checking os-specific extensions.'''
    newList = []
    for extension in extensions:
        # multi
        if "win;mac@" in extension:
            if IsWindows() == True or IsMacOS() == True:
                newList.append( extension.replace("win;mac@","") )
        elif "win;lnx@" in extension:
            if IsWindows() == True or IsLinux() == True:
                newList.append( extension.replace("win;lnx@","") )
        elif "mac;lnx@" in extension:
            if IsMacOS() == True or IsLinux() == True:
                newList.append( extension.replace("mac;lnx@","") )
        elif "lnx;mac@" in extension:
            if IsMacOS() == True or IsLinux() == True:
                newList.append( extension.replace("lnx;mac@","") )
        # single
        elif "win@" in extension:
            if IsWindows() == True:
                newList.append( extension.replace("win@","") )
        elif "mac@" in extension:
            if IsMacOS() == True:
                newList.append( extension.replace("mac@","") )
        elif "lnx@" in extension:
            if IsLinux() == True:
                newList.append( extension.replace("lnx@","") )
        # all
        elif "all@" in extension:
            newList.append( extension.replace("all@","") )
        # fallback
        else:
            newList.append(extension)
    return newList