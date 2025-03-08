import edgefinder.edgefinder as ef
from PIL import Image, ImageOps
from pytest import approx
import numpy as np

def test_ef_crop():
    image_test = Image.open(r"Test_image.png")

    image_crop = ef.ef_crop(image_test)

    exp = np.genfromtxt('Crop.csv', delimiter=',')
    exp = exp[0:700,0:700]
    obs = image_crop[0:700,0:700]
    
    assert (exp == obs).all()

def test_ef_subpixel():
    image_test = Image.open(r"Test_image.png")

    image_crop = ef.ef_crop(image_test)
    image_subpixel = ef.ef_subpixel(image_crop)

    exp = np.genfromtxt('Multi.csv', delimiter=',')
    exp = exp[0:1199,0:1199]
    
    obs = image_subpixel[0:1199, 0:1199]

    assert (exp == obs).all

def test_ef_baseline():

    image_test = Image.open(r"Test_image.png")

    image_crop = ef.ef_crop(image_test)
    image_subpixel = ef.ef_subpixel(image_crop)
    image_baseline, image_baseline_coe = ef.ef_baseline(image_subpixel)

    obs = [image_baseline.shape[0], image_baseline.shape[1], image_baseline_coe[0], image_baseline_coe[1]]
    exp = [2, 3224, 0, 1208]

    assert exp == approx(obs)

def test_ef_drop_edge():
    image_test = Image.open(r"Test_image.png")

    image_crop = ef.ef_crop(image_test)
    image_subpixel = ef.ef_subpixel(image_crop)
    image_baseline, image_baseline_coe = ef.ef_baseline(image_subpixel)
    image_edge_l, image_edge_r = ef.ef_drop_edge(image_subpixel, image_baseline)

    obs = [image_edge_l.shape[0], image_edge_l.shape[1], image_edge_r.shape[0], image_edge_r.shape[1]]
    exp = [2, 222, 2, 222]
    assert exp == obs

def test_ef_angle_tan():
    image_test = Image.open(r"Test_image.png")

    image_crop = ef.ef_crop(image_test)
    image_subpixel = ef.ef_subpixel(image_crop)
    image_baseline, image_baseline_coe = ef.ef_baseline(image_subpixel)
    image_edge_l, image_edge_r = ef.ef_drop_edge(image_subpixel, image_baseline)
    image_tan_l, image_tan_r, intersection_l, intersection_r, image_angle = ef.ef_angle_tan(image_subpixel,
                                                                                            image_edge_l, image_edge_r,
                                                                                            image_baseline_coe)
    obs = [intersection_l[0], intersection_l[1], intersection_r[0], intersection_r[1], image_angle[0], image_angle[1]]
    exp = [1328.4,            1208,              1840.6,            1208,              76.5042667,     76.5042667]
    assert exp == approx(obs)

def test_ef_full_analysis():
    image_test = Image.open(r"Test_image.png")
    angle = ef.ef_full_analysis(image_test)

    obs = [angle[0], angle[1]]
    exp = [76.5042667, 76.5042667]

    assert exp == approx(obs)

