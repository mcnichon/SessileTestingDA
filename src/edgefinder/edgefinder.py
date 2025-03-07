import numpy as np
from PIL import Image, ImageOps
import scipy.interpolate as interp
import math


def ef_crop(pic, offset = 100, threshold_light = 200):
    """Crops given image based on upon  light intensity threshold and a pixel offset

    Parameters
    ----------
    pic : PIL.Image
    offset : Integer
        Crop offset in the conservative direction, resulting in larger image
    threshold_light : Integer
        light intensity threshold for edge of illuminated region (1-255)

    Returns
    -------
    crop_image : np.array
        cropped image based upon threshold and offset
    """

    pic = ImageOps.grayscale(pic)
    pic = np.array(pic)

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

def ef_subpixel(pic, pixels = 2):
    """Creates additional subpixels in the image using linear interpolation

    Parameters
    ----------
    pic : np.array
        Array of pixel values.
    pixels : Integer
        Number of linear interpolation steps between each array value

    Returns
    -------
    subpixel_image : np.array
        array of pixel values with linearly interpolated subpixels
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

def ef_baseline(pic, bl_fit = 20, bl_ignore = 20, threshold_light = 200, threshold_dark = 72):
    """Finds the baseline of stage.

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image.
    bl_fit : Integer
        number of pixels used on the left and right side of image to linearly fit the baseline
    bl_ignore : Integer
        number of pixels to offset on the left and right edge of the illuminated region when linearly fitting baseline
    threshold_light : Integer
        light intensity threshold for edge of illuminated region (1-255)
    threshold_dark : Integer
        light intensity threshold for edge of baseplate (1-255)

    Returns
    -------
    baseline_pts : np.array
        array of baseline xy locations
    baseline_coe : np.array
        array of coefficients for linear baseline equation [c1*x^n+c2*x^n-1...c3*x^0]
    """

    #Note X and Y are funky because the image origin is at the upper left and plotting starts at lower left
    x = pic.shape[0]
    y = pic.shape[1]
    edge_loc_y = np.zeros(y)
    edge_loc_x = np.linspace(0, pic.shape[1]-1, pic.shape[1])

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

    #Finds baseline points through linear fit of edge of illuminated region
    for i in range(2*bl_fit):
        if i < bl_fit:
            bl_x[i] = xmin+i+bl_ignore+i
            bl_y[i] = edge_loc_y[xmin+i+bl_ignore+i]
        else:
            bl_x[i] = xmax-2*bl_fit + i - bl_ignore
            bl_y[i] = edge_loc_y[xmax-2*bl_fit + i - bl_ignore]

    baseline_coe = np.polyfit(bl_x,bl_y,1)
    bl_y_fit = np.polyval(baseline_coe,edge_loc_x)

    baseline_pts = np.stack((edge_loc_x,bl_y_fit))

    return baseline_pts, baseline_coe

def ef_drop_edge(pic, baseline, bl_offset = 5, threshold_dark = 72):
    """Finds the edge of the drop.

    Parameters
    ----------
    pic : np.array
        Array of pixel values from image.
    baseline : np.array
        array of baseline xy locations calculated in "baseline"
    bl_offset : Integer
        number of pixels to offset above baseline when starting to find edge, should be greater than 1
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
    temp_y = bl_offset
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

    #If baseline is angled, will iterate "down and over" until reaching the baseline
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
    temp_y = bl_offset
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


    return drop_edge_left,drop_edge_right

def ef_angle_tan(pic, edge_left, edge_right, baseline_coe, tan_ignore = 10, tan_fit = 15):
    """Finds tangent line of the drop and the angle it forms with the baseline.

    Parameters
    ----------
    pic : np.array
        Array of pixel values.
    edge_left : np.array
        array of droplet edge xy locations left of "midpoint"
    edge_right : np.array
        array of droplet edge xy locations right of "midpoint"
    baseline_coe : np.array
        array of coefficients of baseline
    tan_ignore : Integer
        number of points to ignore when fitting tan line
    tan fit : Integer
        number of points to fit tan line

    Returns
    -------
    tan_left_poionts : np.array
        array of tangent xy locations for left edge of drop
    tan_right_points : np.array
        array of tangent xy locations for right edge of drop
    intersection_left : np.array
        xy location of intersection between tanget line and baseline right (3 phase point)
    intersection_right : np.array
        xy location of intersection between tanget line and baseline right (3 phase point)
    angle   : np.array
        left and right drop contact angle

    """

    edge_loc_x = np.linspace(0, pic.shape[1]-1, pic.shape[1])

    tan_left_coe = np.polyfit(edge_left[0,tan_ignore:tan_ignore+tan_fit],edge_left[1,tan_ignore:tan_ignore+tan_fit],1)
    tan_left_fit = np.polyval(tan_left_coe,edge_loc_x)

    tan_left_points = np.stack((edge_loc_x, tan_left_fit))

    tan_right_coe = np.polyfit(edge_right[0,tan_ignore:tan_ignore+tan_fit],edge_right[1,tan_ignore:tan_ignore+tan_fit],1)
    tan_right_fit = np.polyval(tan_right_coe,edge_loc_x)

    tan_right_points = np.stack((edge_loc_x, tan_right_fit))

    tan_left_vec = np.array([1, tan_left_coe[0]])
    tan_right_vec = np.array([1, tan_right_coe[0]])
    bl_vec = np.array([1, baseline_coe[0]])

    #Calculates liquid angle of three phase point
    if tan_left_coe[0] > 0:
        angle_left = 180-math.acos(np.dot(bl_vec,tan_left_vec)/np.linalg.norm(tan_left_vec)*np.linalg.norm(bl_vec))*180/math.pi
    else:
        angle_left = math.acos(np.dot(bl_vec,tan_left_vec)/np.linalg.norm(tan_left_vec)*np.linalg.norm(bl_vec))*180/math.pi
    if tan_right_coe[0] < 0:
        angle_right = 180-math.acos(np.dot(bl_vec,tan_right_vec)/np.linalg.norm(tan_right_vec)*np.linalg.norm(bl_vec))*180/math.pi
    else:
        angle_right = math.acos(np.dot(bl_vec,tan_right_vec)/np.linalg.norm(tan_right_vec)*np.linalg.norm(bl_vec))*180/math.pi

    angle = np.array([angle_left,angle_right])

    #Calculates left and right intersection point between tangent line and baseline
    x = (baseline_coe[1]-tan_left_coe[1])/(tan_left_coe[0]-baseline_coe[0])
    y = baseline_coe[0]*x+baseline_coe[1]
    intersection_left = np.array([x,y])

    x = (baseline_coe[1]-tan_right_coe[1])/(tan_right_coe[0]-baseline_coe[0])
    y = baseline_coe[0]*x+baseline_coe[1]
    intersection_right = np.array([x,y])

    print()

    return tan_left_points, tan_right_points, intersection_left, intersection_right, angle

def ef_full_analysis(pic, offset = 100, pixels = 2, threshold_light = 200, threshold_dark = 72, bl_fit = 20, bl_ignore = 20, bl_offset = 5, tan_ignore = 10, tan_fit = 10):
    """finds tangent line of the drop and the angle it forms with the baseline

    Parameters
    ----------
    pic : PIL.Image
    offset : Integer
        Crop offset in the conservative direction, resulting in larger image
    pixels : Integer
        Number of linear interpolation steps between each array value
    threshold_light : Integer
        light intensity threshold for edge of illuminated region (1-255)
    threshold_dark : Integer
        light intensity threshold for edge of baseplate (1-255)
    bl_fit : Integer
        number of pixels used on the left and right side of image to linearly fit the baseline
    bl_ignore : Integer
        number of pixels to offset on the left and right edge of the illuminated region when linearly fitting baseline
    bl_offset : Integer
        number of pixels to offset above baseline when starting to find edge, should be greater than 1
    tan_ignore : Integer
        number of points to ignore when fitting tan line
    tan fit : Integer
        number of points to fit tan line

        Returns
        -------
    angle   : np.array
        left and right drop contact angle
        """

    pic_crop = ef_crop(pic, offset = offset, threshold_light = threshold_light)
    pic_subpixel = ef_subpixel(pic_crop, pixels = pixels)

    pic_baseline, pic_baseline_coe = ef_baseline(pic_subpixel, bl_fit = bl_fit, bl_ignore = bl_ignore, threshold_light = threshold_light, threshold_dark = threshold_dark)

    pic_edge_l, pic_edge_r = ef_drop_edge(pic_subpixel, pic_baseline, bl_offset=bl_offset, threshold_dark=threshold_dark)

    pic_tan_l, pic_tan_r, pic_l, pic_intersection_r, pic_angle = ef_angle_tan(pic_subpixel, pic_edge_l, pic_edge_r, pic_baseline_coe, tan_ignore=tan_ignore, tan_fit=tan_fit)

    return pic_angle
