qrcode = csSession.cslib.piptools.autopipImport("qrcode")

from PIL import ImageColor

fgc_def = "black"
bgc_def = "white"

fgc = fgc_def
fgc_enabled = True
bgc = bgc_def
bgc_enabled = True

mode = "compact"

if len(args.argv) >= 3:
    fgc = args.argv[1]
    if fgc in [None,"None","none"]:
        fgc = fgc_def
        fgc_enabled = False
    elif fgc == "!":
        fgc = fgc_def
    bgc = args.argv[2]
    if bgc in [None,"None","none"]:
        bgc = bgc_def
        bgc_enabled = False
    elif bgc == "!":
        bgc = bgc_def

    if len(args.argv) >= 4:
        mode = args.argv[3]

    if mode.lower().strip().endswith("-strip"):
        strip = True
        mode = mode[::-1].replace("pirts-","",1)[::-1]

elif len(args.argv) == 2:
    print("To supply colors give three arguments: <str> <fg> <bg>")
    exit()
if len(args.argv) <= 0:
    print("This script takes one str as an argument!")
else:
    if args.targv[0][1] not in ["str","int","float"]:
        print("First argument must be string!")
    else:
        # get data
        data = str(args.pargv[0])

        if strip == True: data = data.strip('"')

        print(data)

        # make qr
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # make image
        img = qr.make_image(fill_color=fgc, back_color=bgc)

        if mode.lower() == "big":
            buildStr = ""
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    px = img.getpixel((x,y))
                    if type(px) == int:
                        r,g,b = px,px,px
                    elif type(px) in [list,tuple]:
                        r,g,b = px
                    else:
                        px = None
                    if px != None:
                        buildStr += f"\033[38;2;{r};{g};{b}m██\033[0m"
                    else:
                        buildStr += "  "
                buildStr += "\n"
            print(buildStr)

        elif mode.lower() == "copysafe":
            buildStr = ""
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    px = img.getpixel((x,y))
                    if px != 0:
                        if type(px) == int:
                            r,g,b = px,px,px
                        elif type(px) in [list,tuple]:
                            r,g,b = px
                        else:
                            px = None
                    if px != None and px != 0:
                        buildStr += f"\033[38;2;{r};{g};{b}m██\033[0m"
                    else:
                        buildStr += "░░"
                buildStr += "\n"
            print(buildStr)

        else:# make into grid (y-prio)
            grid = []
            rgb_list = []
            width, height = img.size
            for y in range(height):
                grid.append([]) 
                for x in range(width):
                    grid[-1].append( img.getpixel((x,y)) )
            
            # built string
            buildStr = ""
            if height % 2 != 0:
                grid.append([None for _ in range(width)])
            haveWarnedPx = False
            for y in range(0,len(grid),2):
                for x in range(width):
                    px1 = grid[y][x]
                    px2 = grid[y+1][x]
                    ## fgc disabled
                    if fgc_enabled == False and bgc_enabled != False:
                        #px1
                        if type(px1) == int:
                            fgcI1 = ImageColor.getcolor(fgc,"RGB")[0]
                        elif type(px1) in [list,tuple]:
                            fgcI1 = ImageColor.getcolor(fgc,"RGB")
                        if px1 == fgcI1: 
                            px1 = None
                        #px2
                        if type(px2) == int:
                            fgcI2 = ImageColor.getcolor(fgc,"RGB")[0]
                        elif type(px2) in [list,tuple]:
                            fgcI2 = ImageColor.getcolor(fgc,"RGB")
                        # if px2 matches our background color disable it
                        if px2 == fgcI2:
                            px2 = None
                    ## bgc disabled
                    elif fgc_enabled != False and bgc_enabled == False:
                        #px1
                        if type(px1) == int:
                            bgcI1 = ImageColor.getcolor(bgc,"RGB")[0]
                        elif type(px1) in [list,tuple]:
                            bgcI1 = ImageColor.getcolor(bgc,"RGB")
                        if px1 == bgcI1: 
                            px1 = None
                        #px2
                        if type(px2) == int:
                            bgcI2 = ImageColor.getcolor(bgc,"RGB")[0]
                        elif type(px2) in [list,tuple]:
                            bgcI2 = ImageColor.getcolor(bgc,"RGB")
                        # if px2 matches our background color disable it
                        if px2 == bgcI2:
                            px2 = None
                    ## both disabled
                    elif fgc_enabled == False and bgc_enabled == False:
                        if haveWarnedPx != True:
                            print("\033[31m! Both colors disabled, using defaults. !\033[0m")
                            haveWarnedPx = True
                    # convert based on type
                    if px1 != None:
                        if type(px1) == int:
                            r1,g1,b1 = px1,px1,px1
                        elif type(px1) in [list,tuple]:
                            r1,g1,b1 = px1
                        else:
                            px1 = None
                    if px2 != None:
                        if type(px2) == int:
                            r2,g2,b2 = px2,px2,px2
                        elif type(px2) in [list,tuple]:
                            r2,g2,b2 = px2
                        else:
                            px2 = None
                    # add to str build          fgc=px1, bgc=px2
                    if px1 != None and px2 != None:
                        buildStr += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    elif px1 != None and px2 == None:
                        buildStr += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                    elif px1 == None and px2 != None:
                        buildStr += f"\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                    else:
                        buildStr += " "
                # add newline
                buildStr += "\n"

            print(buildStr)