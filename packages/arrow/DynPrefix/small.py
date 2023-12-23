# This script will get executed by crosshells "getPrefix" function and then the generate() function will be called.
# GlobalVaraibles are send to this file apon first execution.

main = include("_main")

char = "⟩"

def generate():
    return main.buildPrefix(char,globals())