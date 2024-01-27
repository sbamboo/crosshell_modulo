from cslib._crosshellParsingEngine import orderParse_parenthesis,splitSafe_parse,useOnlyDoublePipeSplit,fixDoubleGet
from cslib.execution import input_to_pipelineStructure,determine_delims,exclude_codeblocks,include_codeblocks

# ask for debug?
debug = csSession.data["set"].getProperty("crsh_debugger","Parsing.AskForDebug")

delims = determine_delims(csSession,["||"])

# Parsing Engline
parse1 = useOnlyDoublePipeSplit(CS_LastInput)
parse2 = orderParse_parenthesis(parse1)
parse3,excludes = exclude_codeblocks(parse2)
for i,excl in enumerate(excludes): excludes[i] = excl.replace("\n","!cs.nl!")
parse4 = splitSafe_parse(parse3,delims)
parse5 = include_codeblocks(parse4,excludes)
# Global Text System
#parse6 = csSession.data["txt"].parse(parse5)
parse6 = fixDoubleGet(parse5,csSession)

# Pre-execution
segments = input_to_pipelineStructure(csSession,parse6,delims)

# debug?
if debug == True:
    def sf(s):
        return s.replace("\n","{strnl}")
    debugCB = f"""
    cat@Crosshell Parsing Debug
    ":"sub@Input:{sf(CS_LastInput)}
    ":"sub@OnlyDblSplt:{sf(parse1)}
    ":"sub@ParseParenthesis:{sf(parse2)}
    ":"sub@{'{tab}'}NoCodeBL:{sf(parse3)}
    ":"sub@{'{tab}'}Codeblocks:{sf(';'.join(excludes))}
    ":"sub@splitSafeParse:{sf(parse4)}
    ":"sub@IncludedBL:{sf(parse5)}
    ":"sub@FixDblGet:{sf(parse6)}
    ":"sub@PipelineStruct:{sf(str(segments))}
    """
    debugCB = debugCB.split("\n")
    debugCB = [e.strip() for e in debugCB]
    debugCB = "\n".join(debugCB)
    debugCB = debugCB.strip('\n')
    segments = [
        [{"cmd":"debad","args":[debugCB]}]
    ]

CS_PipeLine.setSegments(segments)