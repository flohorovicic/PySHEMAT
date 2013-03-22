"""Create a SHEMAT nml input file from a png image"""

from scipy import misc
import numpy

import PySHEMAT as PS

def load_image(image_name):
    """Open image, determine geological "units" and create figure for each separte unit"""
    im = misc.imread(image_name)
    cols = numpy.unique(im)
    
    print("The image %s has %d different colours/ geological layers" % (image_name, len(cols)))
    # save different units as image to make identification easier
    return im


def plot_units(im):
    """Create a plot of each unit separately for better analysis"""

    print("Create figures for different units for better comparison")
    cols = numpy.unique(im)
    print("The image %s has %d different colours/ geological layers" % (image_name, len(cols)))
   
    for col in cols:
       fig_tmp = numpy.ones(im.shape)
       fig_tmp[numpy.where(im==col)] = 0
       misc.imsave("unit_%d.png" % col, fig_tmp) 
   
def combine_units(im, units):
    """Combine different units into one with identifier of first element (after analysis of image)"""
    print("Combine units into one unit wiht identifier %d" % units[0])
    for unit in units:
        im[numpy.where(im == unit)] = units[0]
    return im

def clean_units(im):
    """Clean units in image file: assign ascending integer values 1 to max, from numpy.unique(im) array"""
    cols = numpy.unique(im)
    
    for i,col in enumerate(cols):
        im[numpy.where(im == col)] = i+1
        
    return im



if __name__ == '__main__':
    image_name = "Model02-grob-prim.png"
    im = load_image(image_name)
    im = combine_units(im, [9,10,11])
    im = clean_units(im)
    plot_units(im)
    
    # define model sizes
    size_x = 32000
    size_y = 100 
    size_z = 50000
    
    nx = numpy.size(im,1)
    ny = 1
    nz = numpy.size(im,0)
    
    dx = numpy.ones(nx) * (size_x / nx)
    dy = numpy.ones(ny) * (size_y / ny)
    dz = numpy.ones(nz) * (size_z / nz)
    
    
    
    
    title = "Slice model from png"

    S1=PS.create_empty_model(dx=dx, dy=dy, dz=dz,
                          title=title,
                          bc_temperature_side="no_flow",
                          bc_temperature_base="dirichlet",
                          bc_temperature_top="dirichlet",
                          value_temperature_base=200,
                          value_temperature_top=10,
                          bc_flow_side="no_flow",
                          bc_flow_base="no_flow",
                          bc_flow_top="no_flow",
                          compute_heat=True,
                          compute_fluid=False,
                          coupled_fluid_heat=False,
                          initialize_temp_grad=False,
                          initialize_heads=False,
                          nml_filename="model_from_png",
                          vertical_model_from_png_image = True,
                          image_array = im
                          )

# first step: open image, determine geological "units" and create properties.csv file


