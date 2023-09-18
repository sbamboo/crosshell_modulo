# ColorTool v1.1
# Original author: Simon Kalmi Claesson

# Imports
from cslib import autopipImport
import os
#import webcolors
webcolors = autopipImport("webcolors")
import sys
import re

# Params
try:
    if argv != "" and argv != None:
        params_raw = argv
    else:
        params_raw = sys.argv
except:
    params_raw = sys.argv
if ("nc" in str(params_raw) or "nocolor" in str(params_raw)):
    params_nocolorrendering = True
else:
    params_nocolorrendering = False

# Enable ANSI
os.system("")  # enables ansi escape characters in terminal

# Variables
RESET = '\033[0m'

# Functions
def rgb_to_hex(rgb):
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

def color_GetANSICode(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - int(requested_colour[0])) ** 2
        gd = (g_c - int(requested_colour[1])) ** 2
        bd = (b_c - int(requested_colour[2])) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

# Get a color input
color_Hex = input("Enter a colors hex value or color name: ")
color_Hex = color_Hex.replace('#','')

color_RGB_list = None

# Check if input is not a hex string
IsHex = True
if (len(str(color_Hex)) > 8):
    IsHex = False
if bool(re.search('([A-Fa-f0-9]{8}|[A-Fa-f0-9]{6})',str(color_Hex))) == False:
    IsHex = False

# Get color hex
if (IsHex != True):
    color_name = color_Hex
    try:
        color_Hex = webcolors.name_to_hex(color_Hex)
        color_Hex = color_Hex.replace('#','')
    except:
        HasPrintedHead = False
        ColorFound = False
        for name, hex in webcolors.CSS3_NAMES_TO_HEX.items():
            if str(color_name) in str(name):
                if HasPrintedHead == False:
                    print("\033[32mThe color '" + str(color_name) + "' has no name, color names containing it is:\033[0m")
                    HasPrintedHead = True
                ColorFound = True
                print("\033[33m - " + str(name) + "\033[0m")
        if ColorFound != True:
            # check if rgb
            colorname = color_name.replace("rgb(","(")
            rgb_test = color_name.strip(" ").lstrip("(").rstrip(")").split(",")
            valid = False
            if len(rgb_test) > 2:
                valid = True
                rgb_test = [int(val) for val in rgb_test]
                color_RGB_list = rgb_test
                color_Hex = rgb_to_hex(rgb_test)
                if color_Hex == None:
                    valid = False
                else:
                    color_Hex = color_Hex.replace("#","")
                    color_RGB = tuple(color_RGB_list)
                    IsHex = True
            if valid == False:
                print("\033[31m'" + str(color_name).capitalize() + "' does not exist as a known color name.\033[0m")
                exit()

# Get RGB
if color_RGB_list == None:
    lv = len(color_Hex)
    color_RGB = tuple(int(color_Hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    color_RGB_str = str(color_RGB)
    color_RGB_str = color_RGB_str.replace(' ','')
    color_RGB_str = color_RGB_str.replace('(','')
    color_RGB_str = color_RGB_str.replace(')','')
    color_RGB_list = color_RGB_str.split(',')

# Get color name
if (IsHex == True):
    print(color_RGB_list)
    color_name = closest_colour(color_RGB_list)

color_name = color_name.capitalize()

# Split hex
x=2
color_Hex_list=[color_Hex[y-x:y] for y in range(x, len(color_Hex)+x,x)]
color_Hex_list_raw=[color_Hex[y-x:y] for y in range(x, len(color_Hex)+x,x)]
for i in range(0,len(color_Hex_list)):
    color_Hex_list[i] = int(color_Hex_list[i], base=16)

# Print colored text and result.
if (params_nocolorrendering == True):
    print(
            "\033[33mClosest name: \033[0m"
        + color_name
        + "\033[0m"
        + " ("
        + color_GetANSICode(color_RGB_list[0],color_RGB_list[1],color_RGB_list[2])
        + '████' 
        + RESET
        + ")"
        + " \033[33m Hex: \033[0m"
        + str(color_Hex)
        + ", \033[33mRGB: \033[0m("
        + (str(color_RGB).replace(')','').replace('(',''))
        + ")"
    )
else:
    print(
            "\033[33mClosest name: \033[0m"
        + color_GetANSICode(color_RGB_list[0],color_RGB_list[1],color_RGB_list[2])
        + color_name
        + "\033[0m"
        + " ("
        + color_GetANSICode(color_RGB_list[0],color_RGB_list[1],color_RGB_list[2])
        + '████' 
        + RESET
        + ")"
        + " \033[33m Hex: \033[0m"
        + color_GetANSICode(color_Hex_list[0],"00","00")
        + str(color_Hex_list_raw[0])
        + RESET
        + color_GetANSICode("00",color_Hex_list[1],"00")
        + str(color_Hex_list_raw[1])
        + RESET
        + color_GetANSICode("00","00",color_Hex_list[2])
        + str(color_Hex_list_raw[2])
        + RESET
        + ", \033[33mRGB: \033[0m("
        + color_GetANSICode(color_RGB_list[0],"00","00")
        + color_RGB_list[0]
        + RESET
        + ", "
        + color_GetANSICode("00",color_RGB_list[1],"00")
        + color_RGB_list[1]
        + RESET
        + ", "
        + color_GetANSICode("00","00",color_RGB_list[2])
        + color_RGB_list[2]
        + RESET
        + ")"
    )