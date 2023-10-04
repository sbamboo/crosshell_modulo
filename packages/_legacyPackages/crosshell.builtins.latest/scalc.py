from cslib._crosshellParsingEngine import is_simple_math_expression

_ans = csSession.data["cvm"].getvar("ans")
if _ans == None:
    _ans = ""

sargv = sargv.replace("ans",_ans)

def mexpr_eval(mexpr):
    try:
        return eval(mexpr)
    except ZeroDivisionError:
        if csSession.registry["toadInstance"].sInputInstance == None:
            csSession.registry["toadInstance"].timedMsg("\033[31mDividing by zero, dosen't make you a hero! (ZeroDivisionError)",1)
            csSession.registry["toadInstance"].updNoSIToad()
        else:
            csSession.registry["toadInstance"].screamToadNow("\033[31mDividing by zero, dosen't make you a hero! (ZeroDivisionError)")
        return 0

if is_simple_math_expression(sargv):
    a = ""
    # <mexpr>
    sargv = sargv.replace("^","**")
    try:
        a = mexpr_eval(sargv)
    except:
        # X<opr><mexpr>
        sargv2 = _ans + sargv
        try:
            a = mexpr_eval(sargv2)
        except:
            # <mexp><opr>X
            sargv2 = sargv + _ans
            a = mexpr_eval(sargv2)
    print(a)