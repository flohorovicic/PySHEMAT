"""Detect a .nlo file in the current directory and create a temperature and geology plot

..note: if more than one .nlo file is in the directory, simply the first one will be taken"""

import os

import PySHEMAT as PS

# find .nlo file in direectory

for f in os.listdir("."):
    if os.path.splitext(f)[1] == ".nlo": break
    
print("SHEMAT output file is %s" % f)

S1 = PS.Shemat_file(f)

S1.set_origin(0,0,0)

S1.create_slice_plot("TEMP",'y',50, 
                     savefig=True, 
                     filename = "temperature.png", 
                     xlabel = 'E-W [km]',
                     ylabel = 'depth [km]',
                     xscale = 'kilometer',
                     yscale = 'kilometer',
                     vertical_ex = 1,
                     colorbar=True,
                     colorbar_label = "Temperature [C]")

S1.create_slice_plot("GEOL",'y',50, 
                     savefig=True,
                     colorbar = True,
                     colorbar_label = "Geology unit",
                     xlabel = 'E-W [km]',
                     ylabel = 'depth [km]',
                     xscale = 'kilometer',
                     yscale = 'kilometer',
                     vertical_ex = 1,
                     cmap = 'gray',
                     aspect = 'equal',
                     filename = "geology.png")



