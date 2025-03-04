import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import scipy.interpolate as interp


def crop(pic, offset = 100, threshold = 140):
    """Crops given image based on upon  light intensity threshold and a pixel offset

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image to be cropped.
    offset : Integer
        Pixel crop offset in the conservative direction making image larger

    threshold : Integer
        light intensity threshold (1-240), default value = 140

    Returns
    -------
    crop_image : np.array
        cropped array (image) based upon threshold and offset
    """

    [x,y] = np.where(pic > threshold)

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
    subpixel_image = subpixel_image.transpose()

    return subpixel_image

def baseline(pic, pixels = 2):
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
    subpixel_image = subpixel_image.transpose()

    return subpixel_image

im = Image.open(r"C:\Users\ndmcn\PycharmProjects\SessileTestingDA\Example_Images\Test1.png")
im1 = np.array(im)

image_crop= crop(im1)
image = Image.fromarray(image_crop)

image_subpixel = subpixel(image_crop)
image1 = Image.fromarray(image_subpixel)

image1.show()
image.show()



print()