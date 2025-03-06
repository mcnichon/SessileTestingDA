import src.edgeFinder.edgeFinder as eff
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import math

#def EF_full_analysis(pic)
im = Image.open(r"Example_Images/TEMP.png")
im = ImageOps.grayscale(im)
im1 = np.array(im)


image_crop= eff.EF_crop(im1)
image = Image.fromarray(image_crop)

image_subpixel = eff.EF_subpixel(image_crop,pixels=2)
image1 = Image.fromarray(image_subpixel)

plt.imshow(image1)

image_baseline, image_baseline_coe = eff.EF_baseline(image_subpixel)

image_edge_l, image_edge_r = eff.EF_drop_edge(image_subpixel, image_baseline)

image_tan_l, image_tan_r, intersection_l, intersection_r, image_angle = eff.EF_angle_tan(image_subpixel, image_edge_l, image_edge_r, image_baseline_coe)

plt.plot(image_baseline[0], image_baseline[1])
plt.plot(image_edge_l[0], image_edge_l[1])
plt.plot(image_edge_r[0], image_edge_r[1])
plt.plot(image_tan_l[0,round(intersection_l[0]-30):round(intersection_l[0]+30)], image_tan_l[1,round(intersection_l[0]-30):round(intersection_l[0])+30])
plt.plot(image_tan_r[0,round(intersection_r[0]-30):round(intersection_r[0]+30)], image_tan_r[1,round(intersection_r[0]-30):round(intersection_r[0]+30)])
plt.scatter(intersection_l[0], intersection_l[1],s=10)
plt.scatter(intersection_r[0], intersection_r[1],s=10)

plt.show()

#EF_full_analysis(im, threshold_dark=140)

print(image_angle)

print()