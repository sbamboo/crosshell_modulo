toadG = toadG

import os

def setAtIndex(str,i,char):
    expl = list(str)
    expl[i] = char
    return ''.join(expl)

wav = os.path.join(os.path.dirname(__file__),"background1.wav")
wav2 = os.path.join(os.path.dirname(__file__),"background2.wav")
wav3 = os.path.join(os.path.dirname(__file__),"background3.wav")
wav4 = os.path.join(os.path.dirname(__file__),"victory.wav")

#toadG.setBgMusic([wav,wav2,wav3],"random")
toadG.setBgMusic([wav,wav2],"random")
toadG.start()

maxlen = toadG.toad.getToadMaxMsgLen()

base = " "*maxlen

try:
    toadG.p("Do you want to take a walk? [y/n]: ")
    key = toadG.waitForKey()
    if key != "y":
        toadG.p("Okay, have a good day!")
        toadG.sleep(1)
        toadG.exit()
    else:
        toadG.disablePrefix()
        ind = 0
        while ind < len(base)-1:
            key = toadG.waitForKey()
            if key == "d":
                ind += 1
            elif key == "a":
                ind -= 1
            elif key == "q" or key == "\x1b":
                toadG.exit()
            ind = max(ind, 0)
            ind = min(ind, len(base)-1)
            string = setAtIndex(base,ind,"🐸")
            string = setAtIndex(string,len(base)-1,"»")
            toadG.p(string)
        toadG.enablePrefix()
        toadG.p("Thank you, have a good day!")
        toadG.sleep(1)
except KeyboardInterrupt:
    toadG.exit()

toadG.playSound(wav4)

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

toadG.exit()