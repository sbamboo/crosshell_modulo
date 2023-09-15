from execution import execute_string

'''
CSlib: conditions, contains condition logic
'''

# Define a blacklist of unsafe functions and commands
_pycondition_UNSAFE_BLACKLIST = [
    'eval',
    'exec',
    'import',
    'open',
    # Add more functions and commands to block
]

def pyCondition(condition):
    '''CSlib.condition: Evaluates a pyCondition (Experimental and not safe, sanitise input)'''
    # Check if the condition string contains any unsafe functions or commands
    if any(unsafe_command in condition for unsafe_command in _pycondition_UNSAFE_BLACKLIST):
        print("PyCondition: Unsafe function or command detected, returning False.")
        return False
    try:
        result = eval(condition)
        if isinstance(result, bool):
            return result
        else:
            print("PyCondition: Condition does not evaluate to a boolean value, returning False.")
            return False
    except:
        print("PyCondition: Invalid condition string, returning False.")
        return False
    
def crshCondition(condition,csSession,globalvals):
    str_bool = execute_string(condition,csSession,True,globalvals)
    cond = None
    if str_bool != None:
        if str_bool.lower() == "true":
            cond = True
    if cond != True:
        cond == False
    return cond