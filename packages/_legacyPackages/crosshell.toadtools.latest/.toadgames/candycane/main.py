toadG = toadG

import os
wav = os.path.join(os.path.dirname(__file__),"background.wav")
wav2 = os.path.join(os.path.dirname(__file__),"victory.wav")

toadG.setBgMusic(wav)
toadG.start()

maxlen = toadG.toad.getToadMaxMsgLen()

base = " "*maxlen

def setStrAtIndex(str,i,str2):
    ln = len(str2)
    expl = list(str)
    for j in range(ln):
        expl[i+j] = str2[j]
    return ''.join(expl)

try:
    white = ["\x1B[37m","\x1B[41m"]
    red = ["\x1B[31m","\x1B[47m"]
    sel = white
    filled_str = "\x1B[31m\x1B[47m"
    for _ in range(maxlen):
        st = f"{sel[0]}{sel[1]}"
        if sel == white:
            sel = red
        else:
            sel = white
        filled_str += st
        final_str = filled_str + "\033[0m" + " "*(maxlen-len(filled_str))
        toadG.p(final_str)
        toadG.sleep(0.20)
except KeyboardInterrupt:
    toadG.reset()
    exit()

toadG.playSound(wav2)

tx = "["+toadG.title+"]"
wp = round((maxlen-len(tx))/2)
t1 = " "*wp + "\033[33m" + tx + "\033[0m"
t2 = " "*wp + "\033[92m" + tx + "\033[0m"
sel = t1
for _ in range(10):
    toadG.p(sel)
    if sel == t1:
        sel = t2
    else:
        sel = t1
    toadG.sleep(0.15)
toadG.reset()