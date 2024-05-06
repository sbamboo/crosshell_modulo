def input_to_pipelineStructure(sinput=str,basicExecutionDelimiters=[";"],pipeingDelimiters=["|"],argReplacors={"!cs.nl!":"\n"}) -> list:
    """
    CSlib.execution: Function to convert input to the pipeline structure.\n
    Takes `sinput` as a string and uses the delimiters to split it up into a segments list,\n
    where each segment is a list containg al consequent executions (the ones that are linked together).\n
    The executions themself is a dict of `{"cmd":"<cmdlet/firstArg>", "args":[...argsExclFirst...], "type":None, "pipetype":<pipeType>}`\n
    Type is set to none since it should be determined later in the input handling.\n
    Example:\n
    `> cmd1 arg1 | cmd2 arg2; cmd3 arg3`\n
    Would become:\n
    ```
    [
        [
            {"cmd":"cmd1", "args":[ "arg1" ], "type":None, "pipetype":<pipeType>},
            {"cmd":"cmd2", "args":[ "arg2" ], "type":None, "pipetype":<pipeType>}
        ],
        [
            {"cmd":"cmd3", "args":[ "arg3" ], "type":None, "pipetype":<pipeType>}
        ]
    ]
    ```\n
    The function will also 
    """
    # Split to execution order
    execution_order = splitByDelimiters(sinput,basicExecutionDelimiters)
    # Split into pipeline (Note! this function should only ever be called with simple pipeline syntax: " | ")
    pipelineSplit_executionOrder = []
    for partial in execution_order:
        partial = partial.strip() # strip partials
        spartial = splitByDelimiters(partial,pipeingDelimiters)
        # Expression
        for i,expression in enumerate(spartial):
            stripped_expression = expression.strip() # strip expression
            # split by spaces to sepparete args from cmd
            split_expression = splitStringBySpaces(stripped_expression)
            # sort
            if len(split_expression) > 0:
                cmd = split_expression[0]
                split_expression.pop(0)
                # iterate over args and replace !cs.nl!
                for i2,part in enumerate(split_expression):
                    for k,v in argReplacors.items():
                        part = part.replace(k,v)
                    split_expression[i2] = part
            else:
                cmd,split_expression = expression,[]
            dict_expression = {"cmd":cmd, "args":split_expression, "type":None}
            # add
            spartial[i] = dict_expression
        # add to partial
        pipelineSplit_executionOrder.append(spartial)
    # return
    return pipelineSplit_executionOrder


