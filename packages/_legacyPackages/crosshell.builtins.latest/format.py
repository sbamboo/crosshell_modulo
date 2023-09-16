from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat

toformat,excludes = exclude_nonToFormat(sargv)
formatted = csSession.data["txt"].parse(toformat)
sargv = include_nonToFormat(formatted,excludes)
print(sargv)