#!/usr/bin/env python

import glob
import numpy as np
from subprocess import call
import sys, os
import math

from my_hdf_cdf_utilities import *
from my_general_utilities import *
from my_general_read_utilities import *

import scipy.misc
import scipy.stats
from scipy.linalg import svd



import matplotlib.pyplot as plt

from pylab import *

from PIL import Image


xdim=1000
ydim=500

data_dir=  '/Users/bmonger/rsclass/data'
fname= glob.glob(data_dir + '/' + 'global_reynolds_oi/oiv2*')
geophys=read_reynolds_oi(fname[0])



im=Image.fromarray(geophys)
im= im.resize((xdim, ydim), resample=Image.BILINEAR)
geophys_big= np.array(im)


mycmap = get_cmap('jet')
mycmap.set_bad('k')

plt.figure('orignal size')
plt.imshow(geophys, cmap=mycmap, vmin=-2, vmax=35)

plt.figure('resized image')
plt.imshow(geophys_big, cmap=mycmap, vmin=-2, vmax=35)


plt.show()
