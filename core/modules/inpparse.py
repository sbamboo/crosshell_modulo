from cslib._crosshellParsingEngine import orderParse_parenthesis,splitSafe_parse,useOnlyDoublePipeSplit
from cslib.execution import input_to_pipelineStructure,determine_delims

delims = determine_delims(csSession,["||"])

# Parsing Engline
parse1 = useOnlyDoublePipeSplit(CS_LastInput)
parse2 = orderParse_parenthesis(parse1)
parse3 = splitSafe_parse(parse2,delims)
# Global Text System
parse4 = csSession.data["txt"].parse(parse3)
# Pre-execution
parse5 = input_to_pipelineStructure(csSession,parse4,delims)

CS_PipeLine.setSegments(parse5)