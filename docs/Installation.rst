Usage
=========
-------------
Installation
-------------
Currently, to install the package, the github repository must to be cloned. To do this:

* Open a terminal and navigate to the directory you wish to install the package in. It is recommended that this be a new directory with a clean virtual environment.
* Copy the following commands into your terminal, this will clone the repository.

.. code-block:: linux

    git clone https://github.com/mcnichon/edgefinder.git

**NOTE:** More detailed instructions pertaining to cloning github repositories can be found `here <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`_

* Navigate to the repository's directory, which should contain a ``pyproject.toml`` file.
* From this repository copy the following code into your terminal to install the package and all dependencies:

.. code-block:: python

    pip install .

* Verify that the package and dependencies have been installed with:

.. code-block:: python

    pip list

To utilize the code within a python workspace, one must add the following to their code. The package alias can be whatever the user wants, here ``ef`` is used.

.. code-block:: python

    import edgefinder.edgefinder as ef

Currently there exists no support to install the package with PyPi.

-------------
Example Problems
-------------

Two example problems are provided in the repository ``Example_Single_Image.py`` and ``Example_Multiple_Images.py``, located in the Examples directory. The first example analyzes a single image utilizing all package functions except ``ef_full_analysis``. A snippet of the example code is provided below:

.. code-block:: python

    image_test = Image.open(r"Example_Images/Example_Image_2.png")
    
    #Functions from package
    image_crop= ef.ef_crop(image_test)
    image_subpixel = ef.ef_subpixel(image_crop)
    image_baseline, image_baseline_coe = ef.ef_baseline(image_subpixel)
    image_edge_l, image_edge_r = ef.ef_drop_edge(image_subpixel, image_baseline)
    image_tan_l, image_tan_r, intersection_l, intersection_r, image_angle = ef.ef_angle_tan(image_subpixel, image_edge_l, image_edge_r, image_baseline_coe)

First,  an image needs to be opened utilizing the ``Pillow Image`` class. ``image_test = Image.open(r"Example_Images/Example_Image_1.png")``

``ef.ef_crop`` converts the image to greyscale and then an ``np.array`` that contains the pixel light intensity values (0-255, with 0 and 255 being black and white respectively). The image is then cropped around the ``illuminated region`` that is defined by ``threshold_light`` with a default value of 200 or a user specified value. This is shown below.

.. image:: images/crop.png
    :width: 600

``ef.ef_subpixel`` linearly interpolates between all points in the image matrix to artificially  increase its resolution.

``ef.ef_baseline`` iterates through the pixel array, starting at the bottom left corner of the image. The first instance in each column where the pixel reaches the edge of the baseplate/drop via the ``threshold_dark`` pixel value is recorded. Points from this array corresponding to the edges of the illuminated region, and further defined by ``bl_fit`` and ``bl_ignore`` are then used to find a linear fit for the baseline of the sample stage. 

``ef.ef_edge`` finds the left and right edge of the droplet, as defined by the ``threshold_dark`` value. Starting at the droplets approximate center, pixel values in the row will be iterated through until reaching the ``threshold_dark`` value. This will be repeated in every row until the center column also passes this value, after which we will leave the top of the droplet. If the pixel location that is being evaluated drops below the baseline before reaching the threshold value, then it stops searching in that direction. This can be seen in the expanded view in the image below. The green droplet edge does not drop below the red baseline. This function is capable of analyzing non-horizontal baseplates.

``ef.ef_tan`` finds the tangent line next of the droplet where it touches the baseplate. Similar to the baseline, the points used for this linear interpolation are defined by the ``tan_fit`` and ``tan_ignore`` variables to account for inconsistencies in the image. Additionally, within this function, vector math between the tangent and baseline is done to calculate the contact angle between the droplet and baseplate.

The result of each of these functions is shown below.

.. image:: images/fullanalysis.png
    :width: 800

All functions have default values pertaining to fitting parameters and can be finetuned by the user. The default values provided produce good results on the example images.

The second example, ``Example_Multiple_Images.py`` shows how thispackage  might be applied to folders with more than one image.

Within these two examples, the function ``ef.ef_full_analysis`` is not used. This function is intended to simplify the entire process, combining all previously described functions into one, outputting only an angle. Thus, if one wishes to plot any of the results other than angle, the above process should be taken.
