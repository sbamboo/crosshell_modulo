import re

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


print(useOnlyDoublePipeSplit("{hi;do};no;{;;};do"))