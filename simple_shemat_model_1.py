"""
Example script to create a simple SHEMAT model with PySHEMAT

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
# use numpy to define the grid dimensions; other array or list methods can be applied, as well
from numpy import ones  
# import os methods to adjust working directory
from os import chdir, getcwd

# change to some working directory
chdir(r'C:\GeoModels\test_PySHEMAT\simple_example_1')

dx = 50 * ones(50)
dy = 50 * ones(50)
dz = 50 * ones(20)

# Create empty model
S1=create_empty_model(dx=dx, dy=dy, dz=dz,
                      title="Convection_example",
                      bc_temperature_side="no_flow",
                      bc_temperature_base="dirichlet",
                      bc_temperature_top="dirichlet",
                      value_temperature_base=40,
                      value_temperature_top=10,
                      bc_flow_side="no_flow",
                      bc_flow_base="no_flow",
                      bc_flow_top="no_flow",
                      compute_heat=True,
                      compute_fluid=True,
                      coupled_fluid_heat=True,
                      initialize_temp_grad=True,
                      initialize_heads=True,
                      nml_filename="conv_ex_1"
                      )

print("\nNew SHEMAT nml file is in folder:")
print(getcwd())
