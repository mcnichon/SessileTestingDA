import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import scipy.interpolate as interp


def crop(pic, offset = 100, threshold_light = 200):
    """Crops given image based on upon  light intensity threshold and a pixel offset

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image to be cropped.
    offset : Integer
        Pixel crop offset in the conservative direction making image larger

    threshold_light : Integer
        light intensity threshold for edge of illuminated region(1-255)

    Returns
    -------
    crop_image : np.array
        cropped array (image) based upon threshold and offset
    """

    [x,y] = np.where(pic > threshold_light)

    xmin = np.min(x) - offset
    xmax = np.max(x) + offset
    ymin = np.min(y) - offset
    ymax = np.max(y) + offset

    if xmin < 0:
        xmin = 0
    if xmax > pic.shape[0]:
        xmax = pic.shape[0]
    if ymin < 0:
        ymin = 0
    if ymax > pic.shape[1]:
        ymax = pic.shape[1]

    crop_image = pic[xmin:xmax, ymin:ymax]

    return crop_image

def subpixel(pic, pixels = 2):
    """Creates additional subpixels using linear interpolation

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image to be cropped.
    pixels : Integer
        Number of linear interpolation steps between each array value

    Returns
    -------
    subpixel_image : Pillow Image
        image array with subpixels
    """

    X = np.linspace(0, pic.shape[0], pic.shape[0])
    Y = np.linspace(0, pic.shape[1], pic.shape[1])

    linear_interp = interp.RegularGridInterpolator((X, Y), pic)

    X = np.linspace(0, pic.shape[0], pic.shape[0] * pixels)
    Y = np.linspace(0, pic.shape[1], pic.shape[1] * pixels)
    x, y = np.meshgrid(X, Y)

    subpixel_image = linear_interp((x, y))
    subpixel_image = subpixel_image.transpose() #Transpose due to picture and plotting origin differences

    return subpixel_image

def baseline(pic, bl_fit = 20, bl_ignore = 20, threshold_light = 200 ,threshold_dark = 72):
    """Finds the baseline of the droplet/stage

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image to be cropped.
    bl_fit : Integer
        number of pixels used on the left and right side of image to linearly fit the baseline
    bl_ignore : Integer
        number of pixels to offset on the left and right edge of the image when linearly fitting baseline
    threshold_light : Integer
        light intensity threshold for edge of illuminated region (1-255)
    threshold_dark : Integer
        light intensity threshold for edge of baseplate (1-255)

    Returns
    -------
    baseline : np.array
        array of baseline xy locations
    """

    #Note X and Y are funky because the image origin is at the upper left and plotting starts at lower left
    x = pic.shape[0]
    y = pic.shape[1]
    edge_loc_y = np.zeros(y)
    edge_loc_x = np.linspace(0, pic.shape[1], pic.shape[1])
    #Finds the edge location of the "dark" region starting at bottom left of image
    for i in range(y):
        for j in range(x):
            if pic[x-j-1,i] > threshold_dark:
                edge_loc_y[i] = x-j-1
                break

    [___, y1] = np.where(pic > threshold_light)
    xmin = np.min(y1)
    xmax = np.max(y1)

    bl_x = np.zeros(2*bl_fit)
    bl_y = np.zeros(2*bl_fit)

    #Finds baseline points from edge of illuminated region
    for i in range(2*bl_fit):
        if i < bl_fit:
            bl_x[i] = xmin+i+bl_ignore+i
            bl_y[i] = edge_loc_y[xmin+i+bl_ignore+i]
        else:
            bl_x[i] = xmax-2*bl_fit + i - bl_ignore
            bl_y[i] = edge_loc_y[xmax-2*bl_fit + i - bl_ignore]

    baseline_coe = np.polyfit(bl_x,bl_y,1)
    bl_x_fit = np.linspace(0,pic.shape[1],pic.shape[1])
    bl_y_fit = np.polyval(baseline_coe,bl_x_fit)

    plt.scatter(bl_x, bl_y,s = 50, c="pink")

    plt.plot(edge_loc_x, edge_loc_y)
    baseline = np.stack((bl_x_fit,bl_y_fit))

    return baseline

def drop_edge(pic, baseline, threshold_dark = 72):
    """Finds the edge of the drop

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image to be cropped.
    baseline : np.array
        array of baseline xy locations calculated in "baseline"
    threshold_dark : Integer
        light intensity threshold for edge of baseplate/droplet (1-255)
    Returns
    -------
    drop_edge_left : np.array
        array of droplet edge xy locations left of "midpoint"
    drop_edge_right : np.array
        array of droplet edge xy locations right of "midpoint"
    """

    x = pic.shape[0]
    y = pic.shape[1]
    edge_loc_y = np.zeros(y)

    # Finds the edge location of the "dark" region starting at bottom left of image
    for i in range(y):
        for j in range(x):
            if pic[x - j - 1, i] > threshold_dark:
                edge_loc_y[i] = x - j - 1
                break


    drop_center_y = np.min(edge_loc_y[edge_loc_y > 0])
    drop_center_x = np.min(np.where(edge_loc_y == drop_center_y))

    bl_center_y = round(np.interp(drop_center_x,baseline[0],baseline[1]),0)

    drop_edge_left_x = []
    drop_edge_left_y = []
    drop_edge_right_x = []
    drop_edge_right_y = []

    temp = 0
    temp_x = 0
    temp_y = 0
    baseline_break = 0

    #Starts at the center point on the baseline, moves left/right until either going below baseline or reaching threshold value,
    # moves up one row and repeats
    while ~temp:
        while ~temp:
            if(pic[int(bl_center_y - temp_y), int(drop_center_x - temp_x)]) > threshold_dark:
                drop_edge_left_x.append(int(drop_center_x - temp_x))
                drop_edge_left_y.append(int(bl_center_y - temp_y))
                break
            elif bl_center_y - temp_y > baseline[1,drop_center_x - temp_x]:
                baseline_break = 1
                break
            else:
                temp_x += 1
        temp_y += 1
        temp_x = 0

        if(pic[int(bl_center_y - temp_y), int(drop_center_x - temp_x)]) > threshold_dark:
            drop_edge_left_x.append(int(drop_center_x - temp_x))
            drop_edge_left_y.append(int(bl_center_y - temp_y))
            break

    #If baseline is angled, will iterate "down and over" until reaching it
    #Left Side Angled Baseline
    if baseline_break == 0:
        temp_x = drop_edge_left_x[0]+15
        temp_y = 1
        while ~temp:
            while ~temp:
                if(pic[int(bl_center_y - temp_y), int(temp_x)]) > threshold_dark:
                    drop_edge_left_x.insert(0,int(temp_x))
                    drop_edge_left_y.insert(0,int(bl_center_y - temp_y))
                    break
                elif bl_center_y - temp_y > baseline[1,temp_x]:
                    baseline_break = 1
                    break
                else:
                    temp_x -= 1

            temp_x = drop_edge_left_x[0] + 15
            temp_y -= 1

            if baseline_break == 1:
                break

    #Right Side
    temp_x = 0
    temp_y = 0
    baseline_break = 0

    while ~temp:
        while ~temp:
            if(pic[int(bl_center_y - temp_y), int(drop_center_x + temp_x)]) > threshold_dark:
                drop_edge_right_x.append(int(drop_center_x + temp_x))
                drop_edge_right_y.append(int(bl_center_y - temp_y))
                break
            elif bl_center_y - temp_y > baseline[1,drop_center_x + temp_x]:
                baseline_break = 1
                break
            else:
                temp_x += 1
        temp_y += 1
        temp_x = 0

        if(pic[int(bl_center_y - temp_y), int(drop_center_x + temp_x)]) > threshold_dark:
            drop_edge_right_x.append(int(drop_center_x + temp_x))
            drop_edge_right_y.append(int(bl_center_y - temp_y))
            break


    #Right Side Angled Baseline
    if baseline_break == 0:
        temp_x = drop_edge_right_x[0]-15
        temp_y = 1
        while ~temp:
            while ~temp:
                if(pic[int(bl_center_y - temp_y), int(temp_x)]) > threshold_dark:
                    drop_edge_right_x.insert(0,int(temp_x))
                    drop_edge_right_y.insert(0,int(bl_center_y - temp_y))
                    break
                elif bl_center_y - temp_y > baseline[1,temp_x]:
                    baseline_break = 1
                    break
                else:
                    temp_x += 1

            temp_x = drop_edge_right_x[0] - 15
            temp_y -= 1

            if baseline_break == 1:
                break

    drop_edge_left = np.stack((np.array(drop_edge_left_x),np.array(drop_edge_left_y)))
    drop_edge_right = np.stack((np.array(drop_edge_right_x),np.array(drop_edge_right_y)))
    plt.scatter(drop_edge_left[0],drop_edge_left[1], s=0.1)
    plt.scatter(drop_edge_right[0],drop_edge_right[1], s=0.1)

    return drop_edge_left,drop_edge_right


im = Image.open(r"C:\Users\ndmcn\PycharmProjects\SessileTestingDA\Example_Images\Test1Flip.png")
im = ImageOps.grayscale(im)
im1 = np.array(im)


image_crop= crop(im1)
image = Image.fromarray(image_crop)

image_subpixel = subpixel(image_crop)
image1 = Image.fromarray(image_subpixel)

plt.imshow(image1)

image_baseline = baseline(image_subpixel)

plt.plot(image_baseline[0], image_baseline[1])

image_edge = drop_edge(image_subpixel, image_baseline)
plt.imshow(image1)

plt.plot(image_baseline[0], image_baseline[1])

plt.show()
print()

print()