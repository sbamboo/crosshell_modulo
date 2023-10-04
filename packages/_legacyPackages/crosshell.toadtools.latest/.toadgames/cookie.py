toadG = toadG

toadG.start()

maxlen = toadG.toad.getToadMaxMsgLen()

base = " "*maxlen

def setAtIndex(str,i,char):
    expl = list(str)
    expl[i] = char
    return ''.join(expl)

def setStrAtIndex(str,i,str2):
    ln = len(str2)
    expl = list(str)
    for j in range(ln):
        expl[i+j] = str2[j]
    return ''.join(expl)

try:
    # move cookie
    for i in range(maxlen)[::-1]:
        i = max(i-1,0)
        string = " "*i + "🍪"
        toadG.p(string)
        toadG.sleep(0.10)
    # munch
    t1 = "🍪\033[33m *munch*\033[0m"
    t2 = "🍪\033[30m *munch*\033[0m"
    sel = t1
    for _ in range(8):
        toadG.p(sel)
        if sel == t1:
            sel = t2
        else:
            sel = t1
        toadG.sleep(0.22)
    # thank you
    toadG.p("Thank you!")
    toadG.sleep(0.5)
except KeyboardInterrupt:
    toadG.reset()
    exit()

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