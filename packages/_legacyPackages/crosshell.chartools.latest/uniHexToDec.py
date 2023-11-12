if "{u." in sargv:
    sargv = sargv.replace("{u.","",1)
    sargv = sargv.rstrip("}")

def hex_to_decimal(unicode_hex):
    try:
        decimal_value = int(unicode_hex, 16)
        return decimal_value
    except:
        try:
            unicode_hex = unicode_hex.replace("u","",1)
            decimal_value = int(unicode_hex, 16)
            return decimal_value
        except:
            return None

print(hex_to_decimal(sargv))