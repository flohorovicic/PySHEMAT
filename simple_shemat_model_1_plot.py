"""
Example script to create a simple plot with PySHEMAT

This script can be used to plot the results of the simple model created with
simple_shemat_model_1.py

This file is part of PySHEMAT, a free set of Python modules to create and process input
files for fluid and heat flow simulation with SHEMAT (http://137.226.107.10/aw/cms/website/zielgruppen/gge/research_gge/~uuv/Shemat/?lang=de)

******************************************************************************************
PySHEMAT is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

PySHEMAT is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with PyTOUGH.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************************

For module, update and documentation of PySHEMAT please see:
https://github.com/flohorovicic/PySHEMAT

If you use PySHEMAT for a scientific study, please cite our publication in Computers and Geoscience:
J. Florian Wellmann, Adrian Croucher, Klaus Regenauer-Lieb, Python scripting libraries for subsurface fluid and heat flow simulations with TOUGH2 and SHEMAT, Computers & Geosciences, 
Available online 21 October 2011, ISSN 0098-3004, 10.1016/j.cageo.2011.10.011.
"""

# import PySHEMAT module
from PySHEMAT import *
# import os methods to adjust working directory
from os import chdir, getcwd

# change to directory where output file (.nlo) is located
chdir(r'C:\GeoModels\test_PySHEMAT\simple_example_1')

# create Shemat object for output file
S1_out = Shemat_file(filename='conv_ex_1.nlo')

# calculate mean temperature
mean_temp = S1_out.calc_global_mean_value("# TEMP")

# create plot and save as .png file
S1_out.create_2D_property_plot(mean_temp, 
            interpolation='bilinear',
            title='Mean temperature',
            colorbar=True,
            colorbar_label='Temperature',
            xscale='kilometer',
            yscale='kilometer',
            xlabel='E-W [km]',
            ylabel='N-S [km]',
            savefig=True,
            filename='mean_temp.png')

print("Mean temperature figure in folder\n" + getcwd())

