from cslib._crosshellGlobalTextSystem import removeAnsiSequences

remansi = removeAnsiSequences(sargv)

if remansi == sargv:
    from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
    toformat,excludes = exclude_nonToFormat(sargv)
    formatted = csSession.data["txt"].parse(toformat)
    sargv = include_nonToFormat(formatted,excludes)
    remansi = removeAnsiSequences(sargv)

print(remansi)