toadG = toadG

def setAtIndex(str,i,char):
    expl = list(str)
    expl[i] = char
    return ''.join(expl)


toadG.start()

maxlen = toadG.toad.getToadMaxMsgLen()

base = " "*maxlen

try:
    toadG.p("Do you want to take a walk? [y/n]: ")
    key = toadG.keyboard.waitForKey()
    if key != "y":
        toadG.p("Okay, have a good day!")
        toadG.sleep(1)
        toadG.exit()
    else:
        toadG.disablePrefix()
        ind = 0
        while ind < len(base)-1:
            key = toadG.keyboard.waitForKey()
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
        toadG.p("Thank you, have a good day!")
        toadG.sleep(1)
except KeyboardInterrupt:
    toadG.exit()

toadG.exit()