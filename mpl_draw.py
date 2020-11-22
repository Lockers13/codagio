import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.image as mpimg

def draw_functiondef(fdef_dict, outpath):
    def draw_for(body_dict):
        for_loop = body_dict["for"]
        iterable = for_loop["iter"]["id"]

    plt.rcParams["font.family"] = "cursive"

    countx = 0.35
    county = 0.58

    for k, v in fdef_dict.items():
        body = v["body"]
        body_keys = list(body.keys())
        if "for" in body_keys:
            draw_for(body)

        arg_string = "{0}(".format(v["name"])
        for i in range(len(v["args"])):
            try:
                v["args"][i+1]
                arg_string += v["args"][i] + ", "
            except IndexError:
                arg_string += v["args"][i]
        arg_string += ")"
        plt.text(countx, county, "{}".format(arg_string), transform=plt.gca().transAxes)


        county -= 0.1
        n = 256
        angle = np.linspace(0,12*2*np.pi, n)
        radius = np.linspace(.5,1.,n)

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        plt.scatter(x,y,c = angle, cmap = cm.hsv)
        plt.axis('off')
        plt.savefig(outpath)
    # draw.ellipse((100, 100, 150, 200), fill=(255, 0, 0), outline=(0, 0, 0))
    # draw.rectangle((200, 100, 300, 200), fill=(0, 192, 192), outline=(255, 255, 255))
    # draw.line((350, 200, 450, 100), fill=(255, 255, 0), width=10)
