import edgefinder.edgefinder as ef
from PIL import Image, ImageOps
import matplotlib.pyplot as plt

#Use Example_Image_1.png or Example_Image_2.png
image_test = Image.open(r"Example_Images/Example_Image_2.png")

#call functions from package
image_crop= ef.ef_crop(image_test)
image_subpixel = ef.ef_subpixel(image_crop)
image_baseline, image_baseline_coe = ef.ef_baseline(image_subpixel)
image_edge_l, image_edge_r = ef.ef_drop_edge(image_subpixel, image_baseline)
image_tan_l, image_tan_r, intersection_l, intersection_r, image_angle = ef.ef_angle_tan(image_subpixel, image_edge_l, image_edge_r, image_baseline_coe)

#convert np array back to pillow image
image_plot = Image.fromarray(image_subpixel)

#plotting results
plt.rcParams['figure.dpi']=300

fig, main_ax = plt.subplots(); main_ax.set_box_aspect(0.5)
inset_ax = main_ax.inset_axes(
    [0.05, 0.5, 0.35, 0.35],
    xlim = [intersection_l[0]-25,intersection_l[0]+25],
    ylim = [intersection_l[1]-25,intersection_l[1]+25],
    xticklabels=[], yticklabels=[] )

for ax in main_ax, inset_ax:
    ax.imshow(image_plot)
    ax.plot(image_baseline[0], image_baseline[1],  c="red", linewidth=0.5, alpha=0.5)
    ax.plot(image_edge_l[0],   image_edge_l[1],    c="green", linewidth=0.5, alpha=0.8)
    ax.plot(image_edge_r[0],   image_edge_r[1],    c="green", linewidth=0.5, alpha=0.8)
    ax.plot(image_tan_l[0,round(intersection_l[0]-30):round(intersection_l[0]+30)], image_tan_l[1,round(intersection_l[0]-30):round(intersection_l[0])+30],
             c="blue", linewidth=0.5, alpha=0.5)
    ax.plot(image_tan_r[0,round(intersection_r[0]-30):round(intersection_r[0]+30)], image_tan_r[1,round(intersection_r[0]-30):round(intersection_r[0]+30)],
             c="blue", linewidth=0.5, alpha=0.5)
    ax.scatter(intersection_l[0], intersection_l[1], s=1, marker = 'o', color='red', alpha=0.5)
    ax.scatter(intersection_r[0], intersection_r[1], s=1, marker = 'o', color='red', alpha=0.5)

main_ax.indicate_inset_zoom(inset_ax,edgecolor='blue')

plt.show()
print(image_angle)