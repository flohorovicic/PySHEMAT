"""Simple example to determine the (interpolated) property value at a real-world
position within the model. The value is interpolated with a simple trilinear 
interpolation method.

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

import PySHEMAT as PS
from os import chdir

# Set path to directory with local SHEMAT output file
chdir(r'C:\GeoModels\SHEMAT\test_interpolation')

# Read in SHEMAT file and create object
S1 = PS.Shemat_file("test_trilinear_interpolation.nlo")

# Set model origin
S1.set_origin(0, 0, 0)

# Get interpolated value (real-world projected coordinates)
print S1.get_value_xyz("TEMP", 150,140,150)








