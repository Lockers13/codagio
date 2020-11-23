import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.image as mpimg
import random
# import cv2


class SourceDrawer:

    def __init__(self, outpath):
        self.outpath = outpath
        self.countx = 0
        self.county = 1

    def fcall_draw(self, fcall_dict):
        linenos = []
        numargs = []
        fnames = []
        args = []
        for key, value in fcall_dict.items():
            try:
                linenos.append(value["lineno"])
                numargs.append(len(value["args"]))
                fnames.append(value["name"])
                args.append([])
                for arg in value["args"]:
                    args[argercount].append(arg)
            except:
                pass
            # print(len(list(v["body"].keys())))
            # print(np.linspace(0, len(list(v.keys())), 1))

            self.county -= 0.2
            print()
        all_poss=['.','o','v','^']
        all_colors=['red', 'orange', 'green', 'purple']


        for x in range(len(linenos)):
            fstring = "{0}(".format(fnames[x])
            fstring += ')'
            y = random.random() * (numargs[x] + 0.1)
            plt.plot(linenos[x],y,marker=all_poss[numargs[x]], markerfacecolor=all_colors[numargs[x]], markersize=23, markeredgecolor="black", label=fstring)
            #plt.text(linenos[x]+0.5, y-0.5, fstring, horizontalalignment='left', size='medium', color='black', weight='semibold')

        plt.axis('off')
        plt.savefig(self.outpath)




# def draw_functiondef(fdef_dict, outpath):
#
#     def draw_for(body_dict):
#         for_loop = body_dict["for"]
#         iterable = for_loop["iter"]["id"]
#         target = for_loop["target"]["id"]
#         plt.text(countx+0.2, county-0.2, "For {0} in {1}".format(target, iterable), transform=plt.gca().transAxes)
#
#
#
#     img_list = []
#     plt.rcParams["font.family"] = "cursive"
#
#     countx = 0
#     county = 1
#     countpath = 0
#     outpath = outpath.split(".")[0]
#     for k, v in fdef_dict.items():
#         out = outpath + "_" + str(countpath) + ".jpg"
#         body = v["body"]
#         body_keys = list(body.keys())
#
#
#
#         arg_string = "{0}(".format(v["name"])
#         for i in range(len(v["args"])):
#             try:
#                 v["args"][i+1]
#                 arg_string += v["args"][i] + ", "
#             except IndexError:
#                 arg_string += v["args"][i]
#         arg_string += ")"
#         plt.text(countx, county, "{}".format(arg_string), transform=plt.gca().transAxes)
#         if "for" in body_keys:
#             n = 100
#             angle = np.linspace(0,12, n)
#             radius = np.linspace(.5,1.,n)
#
#             x = radius * np.cos(angle)
#             y = radius * np.sin(angle)
#             draw_for(body)
#             #plt.scatter(x,y,c = angle, cmap = cm.hsv, zorder=1)
#
#         x = [countx]
#         y = [county]
#         z = [1000]
#         print(z)
#
#         plt.scatter(x, y, s=z*2000, c=x, cmap="Blues", alpha=0.4, edgecolors="grey", linewidth=2)
#         countx+=0.1
#         county-=0.1
#         #plt.axis('off')
#     plt.savefig(outpath)
    # part_img = cv2.imread(out)
    # img_list.append(part_img)
    # plt.clf()
    #
    # countpath += 1
    # vstack = cv2.vconcat(img_list)
    # out = outpath + "_" + str(countpath) + ".jpg"
    # cv2.imwrite(out, vstack)




    # draw.ellipse((100, 100, 150, 200), fill=(255, 0, 0), outline=(0, 0, 0))
    # draw.rectangle((200, 100, 300, 200), fill=(0, 192, 192), outline=(255, 255, 255))
    # draw.line((350, 200, 450, 100), fill=(255, 255, 0), width=10)
