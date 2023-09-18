from cslib import autopipImport
#import webcolors
webcolors = autopipImport("webcolors")

def autoIntTuple(pre=tuple) -> tuple:
    post = list(pre)
    for i in range(len(pre)):
        post[i] = int(pre[i])
    return tuple(post)

def autoStrTuple(pre=tuple) -> tuple:
    post = list(pre)
    for i in range(len(pre)):
        post[i] = str(pre[i])
    return tuple(post)

def getClosestWebcolor(rgb=tuple) -> list:
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - int(rgb[0])) ** 2
        gd = (g_c - int(rgb[1])) ** 2
        bd = (b_c - int(rgb[2])) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def rgb_to_hex(rgb=tuple) -> str:
    # Ensure that each component is within the valid range (0-255)
    if len(rgb) == 3:
        r, g, b = [max(0, min(255, x)) for x in rgb]
        # Convert each component to a 2-character hexadecimal string
        hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
    elif len(rgb) == 4:
        r, g, b, o = [max(0, min(255, x)) for x in rgb]
        # Convert each component to a 2-character hexadecimal string
        hex_color = "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, o)
    else:
        return None
    return hex_color

def rgb_to_webcolor(rgb=tuple):
    if type(rgb) != tuple:
        rgb = str_to_rgb(rgb)
    try:
        color_name = webcolors.rgb_to_name(rgb)
    except ValueError:
        color_name = getClosestWebcolor(rgb)
    return color_name

def webcolor_to_rgb(webcolor=str) -> tuple:
    return tuple(webcolors.name_to_rgb(webcolor))

def webcolor_to_hex(webcolor=str) -> str:
    return rgb_to_hex(tuple(webcolors.name_to_rgb(webcolor)))

def webcolor_to_ansi(webcolor=str) -> str:
    return rgb_to_ansi(tuple(webcolors.name_to_rgb(webcolor)))

def rgb_to_ansi(rgb=tuple, background=False) -> str:
    if type(rgb) == str:
        rgb = rgbString_to_rgbTuple(rgb)
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, *rgb)

def hex_to_rgb(hex=str) -> str:
    lv = len(hex)
    tup = tuple(int(hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return autoIntTuple(tup)

def hex_to_webcolor(hex=str) -> str:
    return rgb_to_webcolor(hex_to_rgb(hex))

def hex_to_ansi(hex=str) -> str:
    return rgb_to_ansi(hex_to_rgb(hex))

def rgbString_to_rgbTuple(string=str) -> tuple:
    if ";" in string:
        rgb = tuple(string.replace("rgb(","(").strip(" ").lstrip("(").rstrip(")").split(";"))
    else:
        rgb = tuple(string.replace("rgb(","(").strip(" ").lstrip("(").rstrip(")").split(","))
    return autoIntTuple(rgb)

def rgbTuple_to_rgbString(rgb=tuple,delim=None,rgbPrefix=False,shortSyntax=False) -> str:
    if shortSyntax == True:
        if delim == None: delim = ";"
        rgb = autoStrTuple(rgb)
        return delim.join(rgb)
    else:
        if delim == None: delim = ","
        rgb = autoStrTuple(rgb)
        string = "(" + delim.join(rgb) + ")"
        if rgbPrefix == True:
            string = "rgb" + string
        return string

def rgb_to_str(rgb=tuple,delim=None,rgbPrefix=False,shortSyntax=False) -> str:
    return rgbTuple_to_rgbString(rgb,delim,rgbPrefix,shortSyntax)

def hex_to_str(hex=str) -> str:
    return "#" + hex

def webcolor_to_str(webcolor=str) -> str:
    return webcolor

def ansi_to_str(ansi=str) -> str:
    _ansi = ansi.replace("\033","ESC").split(";")
    _ansi.pop(0)
    _ansi.pop(0)
    return ';'.join(_ansi)

def ansi_to_rgb(ansi=str) -> tuple:
    ansi = str_to_ansi(ansi)
    ansi = ansi.replace("\033[","")
    ansi = ansi.rstrip("m")
    _ansi = ansi.split(";")
    _ansi.pop(0)
    _ansi.pop(0)
    tup = tuple(_ansi)
    return autoIntTuple(tup)

def ansi_to_hex(ansi=str) -> str:
    return rgb_to_hex(ansi_to_rgb(ansi))

def ansi_to_webcolor(ansi=str) -> str:
    return rgb_to_webcolor(ansi_to_rgb(ansi))

def str_to_ansi(string=str) -> str:
    return string.replace("ESC","\033")

def str_to_hex(string=str) -> str:
    return string.replace("#","")

def str_to_webcolor(string=str) -> str:
    return string

def str_to_rgb(string=str) -> tuple:
    return rgbString_to_rgbTuple(string)

class xcolor_rgb():
    def __init__(self,rgb=None):
        if type(rgb) == str:
            self.rgb = rgbString_to_rgbTuple(rgb)
        else:
            self.rgb = rgb
    def toRgb(self) -> tuple:
        return self.rgb
    def toHex(self) -> str:
        return rgb_to_hex(self.rgb)
    def toWebcolor(self) -> str:
        return rgb_to_webcolor(self.rgb)
    def toAnsi(self) -> str:
        return rgb_to_ansi(self.rgb)
    def toStr(self, delim=None,rgbPrefix=False,shortSyntax=False) -> str:
        return rgb_to_str(self.rgb,delim,rgbPrefix,shortSyntax)

class xcolor_hex():
    def __init__(self,hex=None):
        self.hex = hex
        self.hex = self.hex.replace("#","")
    def toRgb(self) -> tuple:
        return hex_to_rgb(self.hex)
    def toHex(self) -> str:
        return self.hex
    def toWebcolor(self) -> str:
        return hex_to_webcolor(self.hex)
    def toAnsi(self) -> str:
        return hex_to_ansi(self.hex)
    def toStr(self) -> str:
        return hex_to_str(self.hex)

class xcolor_webcolor():
    def __init__(self,webcolor=None):
        self.webcolor = webcolor
    def toRgb(self) -> tuple:
        return webcolor_to_rgb(self.webcolor)
    def toHex(self) -> str:
        return webcolor_to_hex(self.webcolor)
    def toWebcolor(self) -> str:
        return self.webcolor
    def toAnsi(self) -> str:
        return webcolor_to_ansi(self.webcolor)
    def toStr(self) -> str:
        return webcolor_to_str(self.webcolor)

class xcolor_ansi():
    def __init__(self,ansi=None):
        self.ansi = str_to_ansi(ansi)
    def toRgb(self) -> tuple:
        return ansi_to_rgb(self.ansi)
    def toHex(self) -> str:
        return ansi_to_hex(self.ansi)
    def toWebcolor(self) -> str:
        return ansi_to_webcolor(self.ansi)
    def toAnsi(self) -> str:
        return self.ansi
    def toStr(self) -> str:
        return ansi_to_str(self.ansi)

def getColorType(value):
    '''Returns: "rgb"/"ansi"/"hex"/"webcolor"/"str"/None'''
    if type(value) == tuple:
        return "rgb"
    else:
        if type(value) == str:
            if "ESC" in value or "\033" in value:
                return "ansi"
            elif "#" in value:
                return "hex"
            else:
                if value in webcolors.CSS3_NAMES_TO_HEX.keys():
                    return "webcolor"
                else:
                    try:
                        int(value)
                        if len(value) == 6 or len(value) == 8:
                            return "hex"
                    except:
                        return "str"
        else:
            return None

def getColorTypeStr(value=str):
    '''Returns: "rgb"/"ansi"/"hex"/"webcolor"/"str"'''
    if "ESC" in value or "\033" in value:
        return "ansi"
    else:
        if "#" in value:
            return "hex"
        elif "rgb(" in value:
            return "rgb"
        elif value in webcolors.CSS3_NAMES_TO_HEX.keys():
            return "webcolor"
        else:
            try:
                int(value)
                if len(value) == 6 or len(value) == 8:
                    return "hex"
            except: pass
            if "(" in value and ")" in value:
                value2 = value.lstrip("(").rstrip(")")
                value3 = []
                if "," in value2: value3 = value2.split(",")
                elif ";" in value2: value3 = value2.split(";")
                try:
                    if len(value3) == 3:
                        int(value3[0])
                        int(value3[1])
                        int(value3[2])
                        return "rgb"
                    elif len(value3) == 4:
                        int(value3[0])
                        int(value3[1])
                        int(value3[2])
                        int(value3[3])
                        return "rgb"
                    else:
                        return "str"
                except:
                    return "str"
            else:
                return "str"

def autoToRgb(value) -> tuple:
    t = getColorType(value)
    if t == "rgb":
        return value
    elif t == "ansi":
        if type(value) == str:
            return ansi_to_rgb(str_to_ansi(value))
        else:
            return ansi_to_rgb(value)
    elif t == "hex":
        if type(value) == str:
            return hex_to_rgb(str_to_hex(value))
        else:
            return hex_to_rgb(value)
    elif t == "webcolor":
        return webcolor_to_rgb(value)
    elif t == "str":
        return str_to_rgb(value)

def autoToHex(value) -> str:
    t = getColorType(value)
    if t == "rgb":
        return rgb_to_hex(value)
    elif t == "ansi":
        if type(value) == str:
            return ansi_to_hex(str_to_ansi(value))
        else:
            return ansi_to_hex(value)
    elif t == "hex":
        if type(value) == str:
            return str_to_hex(value)
        else:
            return value
    elif t == "webcolor":
        return webcolor_to_hex(value)
    elif t == "str":
        return str_to_hex(value)

def autoToWebcolor(value) -> str:
    t = getColorType(value)
    if t == "rgb":
        return rgb_to_webcolor(value)
    elif t == "ansi":
        if type(value) == str:
            return ansi_to_webcolor(str_to_ansi(value))
        else:
            return ansi_to_webcolor(value)
    elif t == "hex":
        if type(value) == str:
            return hex_to_webcolor(str_to_hex(value))
        else:
            return hex_to_webcolor(value)
    elif t == "webcolor":
        return value
    elif t == "str":
        return value

def autoToAnsi(value) -> str:
    t = getColorType(value)
    if t == "rgb":
        return rgb_to_ansi(value)
    elif t == "ansi":
        if type(value) == str:
            return str_to_ansi(value)
        else:
            return value
    elif t == "hex":
        if type(value) == str:
            return hex_to_ansi(str_to_hex(value))
        else:
            return hex_to_ansi(value)
    elif t == "webcolor":
        return webcolor_to_ansi(webcolor)
    elif t == "str":
        return str_to_ansi(value)

def autoToStr(value) -> str:
    t = getColorType(value)
    if t == "rgb":
        return rgb_to_str(str_to_rgb(value))
    elif t == "ansi":
        if type(value) == str:
            return ansi_to_str(str_to_ansi(value))
        else:
            return ansi_to_str(value)
    elif t == "hex":
        if type(value) == str:
            return hex_to_str(str_to_hex(value))
        else:
            return hex_to_ansi(value)
    elif t == "webcolor":
        return webcolor
    elif t == "str":
        return value

def autoToRgbStr(value=str) -> tuple:
    t = getColorTypeStr(value)
    if t == "rgb":
        return value
    elif t == "ansi":
        return ansi_to_rgb(str_to_ansi(value))
    elif t == "hex":
        return hex_to_rgb(str_to_hex(value))
    elif t == "webcolor":
        return webcolor_to_rgb(value)
    elif t == "str":
        return str_to_rgb(value)

def autoToHexStr(value=str) -> str:
    t = getColorTypeStr(value)
    if t == "rgb":
        return rgb_to_hex(str_to_rgb(value))
    elif t == "ansi":
        return ansi_to_hex(str_to_ansi(value))
    elif t == "hex":
        return value
    elif t == "webcolor":
        return webcolor_to_hex(value)
    elif t == "str":
        return str_to_hex(value)

def autoToWebcolorStr(value=str) -> str:
    t = getColorTypeStr(value)
    if t == "rgb":
        return rgb_to_webcolor(value)
    elif t == "ansi":
        return ansi_to_webcolor(str_to_ansi(value))
    elif t == "hex":
        return hex_to_webcolor(str_to_hex(value))
    elif t == "webcolor":
        return value
    elif t == "str":
        return value

def autoToAnsiStr(value=str) -> str:
    t = getColorTypeStr(value)
    if t == "rgb":
        return rgb_to_ansi(value)
    elif t == "ansi":
        return str_to_ansi(value)
    elif t == "hex":
        return hex_to_ansi(str_to_hex(value))
    elif t == "webcolor":
        return webcolor_to_ansi(webcolor)
    elif t == "str":
        return str_to_ansi(value)

def autoToStrStr(value=str) -> str:
    t = getColorTypeStr(value)
    if t == "rgb":
        return rgb_to_str(str_to_rgb(value))
    elif t == "ansi":
        return ansi_to_str(str_to_ansi(value))
    elif t == "hex":
        return hex_to_str(str_to_hex(value))
    elif t == "webcolor":
        return webcolor
    elif t == "str":
        return value

def inputHandler(string=str) -> str:
    if "ESC" in string or "\033" in string:
        string = string.replace(",",";")
    if getColorTypeStr(string) == "str":
        string = "(" + string + ")"
    if getColorTypeStr(string) == "rgb" and "rgb(" not in string:
        string = "rgb(" + string + ")"
    return string

def outputHandler(string=str) -> str:
    if type(string) != str:
        string = str(string)
    if "\033" in string:
        string = string.replace("\033","ESC")
    if "ESC" in string:
        string = string.replace(";",",")
    string = string.replace(" ","").lstrip("(").rstrip(")").replace(";",",")
    return string