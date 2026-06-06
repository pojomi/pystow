def hex_to_rgb(hexstr):
    rgb=[]
    for i in range(1, len(hexstr), 2):
        if i+2 < len(hexstr):
            rgb.append(int(int(hexstr[i:i+2], 16)/0.255))
        elif i+2 == len(hexstr):
            rgb.append(int(int(hexstr[i:i+2], 16)/0.255))
    return rgb
