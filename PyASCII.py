"""
PyASCII is a module of PySHEMAT, a free set of Python modules to create and process input
files for fluid and heat flow simulation with SHEMAT (http://137.226.107.10/aw/cms/website/zielgruppen/gge/research_gge/~uuv/Shemat/?lang=de)

******************************************************************************************
PySHEMAT is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

PySHEMAT is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with PyTOUGH.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************************

For module, update and documentation of PySHEMAT please see:
https://github.com/flohorovicic/PySHEMAT

If you use PySHEMAT for a scientific study, please cite our publication in Computers and Geoscience


PyASCII provides methods to handle of ASCII-Gridfiles:

    - load as Object
    - define Object Overload:
        - __add__: add two ASCII Gridobjects (and save as new one)
        - other calculations possible (multiply __mul__, __sub__, ...)
        - __repr__: print with header
        - __len__: ASCII Grid dimensions and discretisation (makes comparison easier?)
        - __cmp__: Comparison: header and data!
    - grid trim to given Values, if compatible with header data
        (be careful not to change absolute data positioning!)
    - methods to analyse
    - methods to plot??
    - methods to write to file (incl. conversion/ formatting for FracSYS)
    - methods to write as xyz
    - methods to cut to given parameters (x, y, but also z- Values?)
    - methods to perform calculations?
    
    - cross-check data_array_3D data to exported XYZ grid with VerticalMappper!!
"""


from sys import exit
import string

class ASCII_File:
    def __init__(self, *args):
        # read ASCII_File directly with object instantiation
        if len(args) != 0:
            file_name = args[0]
            self.file_name_str = file_name
            self.f_ascii = self.load_grid(file_name)
            self.header = self.read_header(self.f_ascii)
            # store data in list to avoid problems of pointer in file...
            self.data = self.f_ascii.readlines()
        else:
            # create default Attributes
            self.header = {}
            self.data = []
            self.file_name_str = "__no_Filename_given__"

    def __repr__(self):
        """define Object representation: header and data in string, can be
        used to output Object"""
        # ToDo: output format as FracSYS input format -> make conversion easier
        # print header
        header_str = ''
        header_str += "ncols %d\n" % self.header['ncol']
        header_str += "nrows %d\n" % self.header['nrow']
        header_str += "xllcorner %d\n" % self.header['xllcorner']
        header_str += "yllcorner %d\n" % self.header['yllcorner']
        header_str += "cellsize %d\n" % self.header['cellsize']
        header_str += "NODATA_value %f\n" % self.header['NODATA_value']
        # print data out of data_array row per row
        data_str = ''
        for row in self.data_array:
            line_str = ''
            for val in row:
                line_str += "%f " % val
            line_str += "\n"
            data_str += line_str
        return header_str + data_str

    def __sub__(self, other_AFO):
        """overload - function: substract values of two ASCII File objects
        if header data are equal
        returns new AFO with substracted values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 - data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out
    
    def __add__(self, other_AFO):
        """overload - function: substract values of two ASCII File objects
        if header data are equal
        returns new AFO with substracted values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 + data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out

    def __mul__(self, other_AFO):
        """overload - function: multiply values of two ASCII File objects
        if header data are equal
        returns new AFO with multiplied values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 * data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out
    
    
    def __div__(self, other_AFO):
        """overload - function: divide values of two ASCII File objects
        if header data are equal
        returns new AFO with divided values and same header data and
        NODATA_values of both grids
        flo 04/2008"""
        # test, if header data are equal
        other_AFO.check_data_array()
        if not self.header_equal_to(other_AFO):
            print "Header Data not equal or not an ASCII Fiel Object, substraction not reasonable..."
            return
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        self.check_data_array()
        other_AFO.check_data_array()
        data1 = array(self.data_array)
        data2 = array(other_AFO.data_array)
        # keep NODATA values -> not possible as simple calculation with numpy...
        # or: try with masks? Advantage: once created, can be used for several calculations -> save time?
        result = data1 / data2
        # evaluate NODATA_Values with masks
        self.check_mask()
        other_AFO.check_mask()
        data1_mask = array(self.data_array_mask)
        data2_mask = array(other_AFO.data_array_mask)
        # evaluate, where both grids have values and substract to get again a mask with 0 and 1 only
        # and keep only values, where both grids have data
        data_out_mask = (data1_mask + data2_mask) // 2
        AFO_out = ASCII_File()
        AFO_out.data_array = list(result)
        # check with mask for NODATA_values and change in data_array
        AFO_out.header = self.header
        print AFO_out.header
        AFO_out.set_NODATA_values(list(data_out_mask), AFO_out.header['NODATA_value'])
        return AFO_out


        
    def size(self):
        """Calculate grid extend
        returns (x_min, x_max, y_min, y_max)
        flo, 04/2008"""
        x_min = self.header['xllcorner']
        x_max = x_min + self.header['ncol'] * self.header['cellsize']
        y_min = self.header['yllcorner']
        y_max = y_min + self.header['nrow'] * self.header['cellsize']
        return((x_min, x_max, y_min, y_max))

    def resize_grid(self, extend):
        """Trim grid to given extend; only performed, if in accordance with header data
        and absolute positioning is not changed:
            remainder of (x_min - xllcorner) % 500 should be 0 (other points equivalent)
        if new grid extends old grid: fill with NODATA_values (does not work yet!!!)

        extend is tuple with (x_min, x_max, y_min, y_max) as produced with ASCII_File.size()
        x_min: will be new xllcorner
        y_min: will be new yllcorner
        x_max: not included (check if senseful!!!)
        y_max: not included
        
        Caution: AFO itself is changed!
        flo, 04/2008"""
        x_min = extend[0]
        x_max = extend[1]
        y_min = extend[2]
        y_max = extend[3]
        # check, if given values are in accordance to grid metadata
        if not (
            ((x_min - self.header['xllcorner']) % self.header['cellsize'] == 0) &
            ((x_max - self.header['xllcorner']) % self.header['cellsize'] == 0) &
            ((y_min - self.header['yllcorner']) % self.header['cellsize'] == 0) &
            ((y_max - self.header['yllcorner']) % self.header['cellsize'] == 0)):
            print "Grid resizing not possible, given values not in accordance to header data"
        # calculate offset of x and y values
        x_min_offset = (x_min - self.header['xllcorner']) // self.header['cellsize']
        x_max_offset = (x_max - self.header['xllcorner']) // self.header['cellsize']
        y_min_offset = (y_min - self.header['yllcorner']) // self.header['cellsize']
        y_max_offset = (y_max - self.header['yllcorner']) // self.header['cellsize']
        # check, if values are in current grid extend
        if not ((0 < x_min_offset < self.header['ncol']) &
            (0 < x_max_offset < self.header['ncol']) &
            (0 < y_min_offset < self.header['nrow']) &
            (0 < y_max_offset < self.header['nrow'])):
                print "Grid resizing not possible, given values extend grid"
                return
        # calculate new grid
        self.check_data_array()
        # process every row separately: is there a more elegant way to perform the slicing?
        data_array_temp = []
        # Caution! Data rows are in reverse order, as llcorner as reference!
        self.data_array.reverse()
        for i in range(int(y_min_offset), int(y_max_offset)):
            row = self.data_array[i]
            data_array_temp.append(row[int(x_min_offset):int(x_max_offset)])
            
        data_array_temp.reverse()
        self.data_array = data_array_temp
        # adjust header data
        self.header['xllcorner'] = x_min
        self.header['yllcorner'] = y_min
        self.header['ncol'] = (x_max_offset - x_min_offset)
        self.header['nrow'] = (y_max_offset - y_min_offset)
        return
        
    def header_equal_to(self, other_AFO):
        """Check if header data of ASCII File object instance are equal to other
        AFO instance
        returns boolean
        flo 04/2008"""
        # test, if other_AFO is really an ASCII File Object
        if not isinstance(other_AFO, ASCII_File):
            print "Not an ASCII File object!"
            return False
        if self.header == other_AFO.header:
            return True
        else:
            return False
    
    def load_grid(self, file_name):
        print "load File " + file_name
        try:
            f_ascii = open(file_name)
        except IOError, (nr, string_err):
            print "\n\tNot able to open file:", string_err
            print "\tPlease check file name and run program again\n"
            exit(0)

        return(f_ascii)
    
    def read_header(self, f_ascii):
        """ returns the 6 line header as a dict"""
        print "read Header of file " + self.file_name_str
        header = {}
        line = f_ascii.readline().split()
        header['ncol'] = int(line[1])
        line = f_ascii.readline().split()
        header['nrow'] = int(line[1])
        line = f_ascii.readline().split()
        header['xllcorner'] = float(line[1])
        line = f_ascii.readline().split()
        header['yllcorner'] = float(line[1])
        line = f_ascii.readline().split()
        header['cellsize'] = float(line[1])
        line = f_ascii.readline().split()
        header['NODATA_value'] = int(line[1])
        return(header)
   
    def import_SHEMAT_2D_array(self, S1, property_xy, **kwds):
        """Import a 2D array, created from a PySHEMAT object
        
        This method can be used to import a 2D array created from a PySHEMAT object,
        for example mean temperatures of a specific formation, created with:
        temperature_xy = S1.calculate_mean_form_temp(formation_id);
        
        The header of the PyASCII object is adapted according to the dimensions
        of the PySHEMAT object.
        
        ..Attention..: ASCII grid object are per definition regular grid objects!
        Therefore, the conversion only works when the original SHEMAT grid is completely regular (dx = dy).

        **Arguments**:
            - *S1* = PySHEMAT.Shemat_file : original SHEMAT object (for dimensions, etc.)
            - *property_xy* = 2D property array, created with PySHEMAT
            
        **Optional Keywords**:
            - *set_nodata_value* = True/ False : set Nodata value for a defined range
            - *nodata_range_min* = float : minimum for nodata range
            - *nodata_range_max* = float : maximum for nodata range
            - filename = string : filename of ASCII grid file
        
        **Returns**: None
        """
        # this has to be defined:
        self.header = {'ncol' : int(S1.get("IDIM")),
                       'nrow' : int(S1.get("JDIM")),
                       'xllcorner' : float(S1.get("I0")),
                       'yllcorner' : float(S1.get("J0")),
                       'cellsize' : float(S1.get_array("DELX")[0]),
                       'NODATA_value' : -9999
                        }

        # set nodata value, if required
        if kwds.has_key('set_nodata_value') and kwds['set_nodata_value']:
            for i,t in enumerate(property_xy):
                if t < kwds['nodata_range_max'] and t > kwds['nodata_range_min']:
                    property_xy[i] = self.header['NODATA_value']

        # data organisation in ASCII grid: one row per list entry
        n = 0
        rows_tmp = []
        for row in range(self.header['nrow']):
            data_row = []
            for col in range(self.header['ncol']):
                data_row.append(property_xy[n])
                n += 1
            rows_tmp.append(data_row)
        # reverse rows_temp because of strange orientation of lines in ASCII
        # grid file (first line corresponds to most Northern line)
        rows_tmp.reverse()
        self.data_array = rows_tmp
        if kwds.has_key('filename'):
            self.file_name_str = kwds['filename']
        else:
            self.file_name_str = "imported_from_PySHEMAT"
        
    def write_file(self, **kwds):
        """Write ASCII grid to file
        
        Write the ASCII grid object to a .txt file. This file should be usable
        for both MapInfo and ArcGIS. Per default, the filename defined in
        self.file_name_str is used, but another filename can be defined with
        an optional keyword.
        
        **Optional Keywords**:
            - *filename* = string : filename (with or without extension); default: self.file_name_str
            - *path* = string : path where file is saved, default: cwd
        """
        from os import path, chdir, getcwd
        if kwds.has_key('filename'):
            if path.splitext(kwds['filename'])[1] == "":
                filename = kwds['filename']+".txt"
            else:
                filename = kwds['filename']
        else:
            if path.splitext(self.file_name_str)[1] == "":
                filename = self.file_name_str+".txt"
            else:
                filename = self.file_name_str
        if kwds.has_key('path'):
            ori_dir = getcwd()
            chdir(path)
        
        f = open(filename, 'w')
        f.write(repr(self))
        f.close()
            
        if kwds.has_key('path'):
            # return to original working directory
            chdir(ori_dir)
            
        
   
    def convert_SHEMAT_results_to_header(self, S1, property_xy):
        """convert a calulcated SHEMAT property array to an ASCII grid
        using the original SHEMAT object to set the header properties
        !!! ATTENTION: ASCII grid only for regular space grids with dx = dy! 
        S1 : Shemat Object
        property_xy : property array (1D) with 2.5 D grid info as written by various
        Shemat_file methods, e.g. mean properties
        """        
        # this has to be defined:
        self.header = {'ncol' : int(S1.get("IDIM")),
                       'nrow' : int(S1.get("JDIM")),
                       'xllcorner' : float(S1.get("I0")),
                       'yllcorner' : float(S1.get("J0")),
                       'cellsize' : float(S1.get_array("DELX")[0]),
                       'NODATA_value' : -9999
                        }
        # data organisation in ASCII grid: one row per list entry
        n = 0
        rows_tmp = []
        for row in range(self.header['nrow']):
            data_row = []
            for col in range(self.header['ncol']):
                data_row.append(property_xy[n])
                n += 1
            rows_tmp.append(data_row)
        # reverse rows_temp because of strange orientation of lines in ASCII
        # grid file (first line corresponds to most Northern line)
        rows_tmp.reverse()
        self.data_array = rows_tmp
        self.file_name_str = "__no_Filename_given__"        
        
    def save(self, filename, **kwds):
        """save ASCII grid to file;
        filename = string : filename of grid file
        optional keywords:
        dir = directory path : path where file is saved"""
        if kwds.has_key('dir'):
            from os import getcwd, chdir
            ori_dir = getcwd()
            chdir(kwds['dir'])
            
        # write ASCII grid to new file
        myfile = open(filename, 'w')
        # use repr to derive a string representation of the Object, as defined in __repr__
        myfile.write(repr(self))
        myfile.close()
        

        
        
        # go back to original directory
        if kwds.has_key('dir'):
            chdir(ori_dir)

    def print_detailed_header_data(self):
        # print header data to output (flo, 04/2008)
        
        # print "Number of Columns:\t%d" % self.header['ncol']
        # print "Number of Rows:\t\t%d" % self.header['nrow']
        print "%s is a %d x %d grid (columns x rows)" % (self.file_name_str, self.header['ncol'], self.header['nrow'])
        print "with "
        print "\tlower-left corner at \t(%d, %d)" % (self.header['xllcorner'], self.header['yllcorner'])
        print "\tupper-right corner at \t(%d, %d)" % (self.header['xllcorner']+self.header['ncol']*self.header['cellsize'],
                                                        self.header['yllcorner']+self.header['nrow']*self.header['cellsize'])
        print "and a cellsize of %d" % self.header['cellsize']


# what for???
    def float2str(self, number):
        """ strips off trailing zeros from coordinates """
        s = "%f" % number
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s

##    def process_z_values_to_array(self):
##        x_list = self.xcoords(self.header)
##        y_list = self.ycoords(self.header)
##        return self.grid_z_values_to_array(self.data, self.header, x_list, y_list)

    def xcoords(self, header):
        """ calculates x coordinates of a grid"""
        x = []
        for col in range(header['ncol']):
            x.append(ASCII_File.float2str(self,header['xllcorner'] + (0.5 * header['cellsize']) + (col * header['cellsize'])))
        return(x)

    def ycoords(self, header):
        """ calculates y coordinates of a grid"""
        y = []
        for (j, row) in enumerate(range(header['nrow'])):
            y.append(ASCII_File.float2str(self,header['yllcorner'] -
                               (0.5 * header['cellsize']) + (header['nrow'] - row) * header['cellsize']))
        return(y)

    def process_z_values_to_array(self):
        """ Read data in list and write to array, flo 03/2008 """
        # if talk: print "\tread data file line by line"
        self.data_array = []
        # L_col = []
        for row in range(self.header['nrow']):
            for col in range(self.header['ncol']):
                # Get new data if necessary
                if col == 0:
                    L_col = []
                    line = self.data[row].split()

                # Write output to array
                L_col.append(string.atof(line[col]))

            self.data_array.append(L_col)
        return self.data_array
    
    def check_data_array(self):
        """ Check if data_array already exists, if not -> create """
        try:
            self.data_array
        except AttributeError:
            print "Create z-Value Data array"
            self.process_z_values_to_array()

    def check_mask(self):
        """Check, if data_array_masks exisist, if not -> create """
        try:
            self.data_array_mask
        except AttributeError:
            print "Create Mask for Data with values:"
            print "0: if NODATA_value, 1: else"
            self.create_z_value_mask()
    
    def check_hist(self):
        """Check, if hist_data exists, if not -> create """
        try:
            self.hist_data
        except AttributeError:
            print "Calculate histogram data"
            self.calculate_histogram()

    
    def set_NODATA_values(self, data_mask, NODATA_value = -9999):
        """write NODATA_value (defined in header) to all positions, where
        data_mask == 0
        flo, 04/2008"""
        # Maybe all this mask-thing too complicated?? Advantage: can be handled
        # with Matrix functionality implemented in numpy...
        try:
            from numpy import array
        except ImportError:
            print "Module NumPy not found but needed for calulation! Install/ check and try again"
            return
        data_mask = array(data_mask)
        data_mask_inv = 1 - data_mask
        self.check_data_array()
        data_array = array(self.data_array)
        data_array = data_array * data_mask + data_mask_inv * NODATA_value
        self.data_array = list(data_array)
        
    
    def create_z_value_mask(self):
        """ Create grid mask out of data_array (0 for 'NODATA_value', 1 else) """

        # Check if data_array already exists, if not -> create
##        try:
##            self.data_array
##        except AttributeError:
##            print "Create z-Value Data array"
##            self.process_z_values_to_array
        self.check_data_array()
        self.data_array_mask = [] # = self.data_array[:][:]
        # TO DO: simplify with "list comprehensives"???
        # self.data_array_mask = [0 for val in self.data_array if val=='-9999']
        for row in self.data_array:
            data_row = []
            for val in row:
                if val == self.header['NODATA_value']:
                    data_row.append(0)
                else:
                    data_row.append(1)

            self.data_array_mask.append(data_row)

                    

##
##
##        for val in self.data_array:
##            if j==2:
##                print val
##

        
    
    def process_xyz_values_to_3D_array(self):
        """Read data and store X,Y,Z values in 3D array, flo 03/2008 """
        self.data_array_3D = []
        # read self.x_data and self.y_data if they do not already exist...
        # to save computation time??
        try:
            (self.x_data, self.y_data)
        except AttributeError:
            print "Create x- and y- coordinates"
            self.x_data = self.xcoords(self.header)
            self.y_data = self.ycoords(self.header)
            
        for row in range(self.header['nrow']):
            for col in range(self.header['ncol']):
                # Get new data if necessary
                if col == 0:
                    L_col = []
                    line = self.data[row].split()
                    
                L_col.append([self.x_data[col], self.y_data[row], line[col]])

            self.data_array_3D.append(L_col)

        return self.data_array_3D
    
    def calculate_histogram(self):
        """Read Data from data_array and create histogram over z-values
        uses matplotlib/
        """
        # test, if data_array exists, if not -> create
        try:
            self.data_array
        except AttributeError:
            print "Create z-Value Data array"
            self.process_z_values_to_array()
        self.hist_data = []
        for row in self.data_array:
            for val in row:
                if val != self.header['NODATA_value']:
                    self.hist_data.append(val)

    def plot_ASCII_grid_histogram(self,n=100):
        """Plot histogram created with self.calculate_histogram()
        n: number of bins"""
        # test, if self.hist_data exists, if not -> create
        try:
            self.hist_data
        except AttributeError:
            self.calculate_histogram()
        # Import matplotlib modules, test, if matplotlib installed
        try:
            from pylab import hist,show
        except ImportError:
            print "Sorry, Module matplotlib is not installed."
            print "Histogram can not be plotted."
            print "Install Matplotlib and try again ;-) "
            return
        hist(self.hist_data,n)
        show()
          
    def plot_ASCII_grid_2D(self, **kwds):
        """Create 2D plot of ASCII grid
        optional keywords:
        filename = string : filename (and, implicitly, the format) of plot file
        """
        # read self.x_data and self.y_data if they do not already exist...
        # to save computation time??
        try:
            (self.x_data, self.y_data)
        except AttributeError:
            print "Create x- and y- coordinates"
            self.x_data = self.xcoords(self.header)
            self.y_data = self.ycoords(self.header)
        # check, if data_array with z values is already created
        try:
            self.data_array
        except AttributeError:
            print "Create z-Value Data array"
            self.process_z_values_to_array
        # Import matplotlib modules, test, if matplotlib installed
        # export test to separate function?
        try:
            from pylab import imshow, gray, colorbar, title, savefig
        except ImportError:
            print "Sorry, Module matplotlib is not installed."
            print "Histogram can not be plotted."
            print "Install Matplotlib and try again ;-) "
            return
        
        # [X,Y] = meshgrid(self.xcoords, self.ycoords)
        #
        # self.check_data_array()
        self.check_hist()
        im = imshow(self.data_array, vmin=min(self.hist_data), vmax=max(self.hist_data))
        # im = imshow(self.data_array)
        
        gray()
        colorbar()
        # plot contour lines on top? -> TEST!!

        # axis('off')
        title(self.file_name_str)
        if kwds.has_key('filename'):
            savefig(kwds['filename'])
        else:
            savefig('ascii_grid.png')
        





           

### End of Class definition for ASCII grid object

def calculate_Ra_number(ASCII_grid_object):
    """Simple 1D Ra-Number Analysis based on
    - formation thickness values stored in ASCII Gridfile
    - simple 1set order estimations of phyiscal parameters
    Output:
    new ASCII Grid-Object with Ra-Values in Grid
    flo, 04/2008"""
    pass



# test object/ module
if __name__ == '__main__':
    import string
    from os import chdir
    from PySHEMAT import Shemat_file

#    chdir("C:\GeoModels\Evaluation_Models\Eval_Model_2_Graben_2d")
#    A1 = ASCII_File("test2_Isobaths_Formation3.txt")
    chdir(r'C:\GeoModels\WAGCoE\North_Perth_Basin\nml_run_14')
    S1 = Shemat_file("PB_N_nml14_updated.nlo")
    form_id = 6
    temperature_xy = S1.calc_mean_formation_value(form_id, "TEMP")
    A2 = ASCII_File()
    A2.import_SHEMAT_2D_array(S1, temperature_xy,
                              set_nodata_value = True,
                              nodata_range_min = -0.0001,
                              nodata_range_max = 0.0001,
                              filename = 'mean_temp_formation_%d_a' % form_id)
    print("write ASCII grid file")
    A2.write_file()
#    write_str = repr(A2)
#    myfile = open('Grad_grid_out1.txt', 'w')
#    # use repr to derive a string representation of the Object, as defined in __repr__
#    myfile.write(repr(A2))
#    myfile.close()
    exit()
    # A1 = ASCII_File("iso_080326_Isopachs_Leseur.txt")
    # A1.print_detailed_header_data()
    # f_ascii = A1.load_grid("bla.txt")
    # head = A1.read_header(A1.f_ascii)
    # A1.process_grid_to_array()
#    A1.process_xyz_values_to_3D_array()

 #   from pylab import *
    # test fpconst module (has to be downloaded separately!!!) for NaN
##    import fpconst
##    i=0
##    for data in A1.data_array:
##        if data == A1.header['NODATA_value']:
##            A1.data_array[i] = 17
##            print A1.data_array[i]
##            # print A1.data_array[i]
##
##        i = i+1
##
##    hist(A1.data_array,100)
##    show()
#    print A1.data_array[2][4]
#    print A1.data_array_3D[2][4]
#    print A1.header['NODATA_value']
#    A1.create_z_value_mask()
#    print
#    print A1.data_array[2][4]
#    print A1.data_array_3D[2][4]
#    A1.calculate_histogram()
#    print A1.hist_data
#    # A1.plot_ASCII_grid_2D()
#    print "Calculate min/max values"
#    print min(A1.hist_data)
#    print max(A1.hist_data)
#
##    chdir(r'C:\GeoModels\Geothermal_Resource_Base\Talk_AGEC\Model_2\export\shemat_lowres\nml_run_2')
##    S1 = Shemat_file('agec2_2_lowres_model.nml')
#    A1.plot_ASCII_grid_2D()
    form_id = 6
    temperature_xy = S1.calc_mean_formation_value(form_id, "TEMP")
    print temperature_xy
    A2 = ASCII_File()
    A2.convert_SHEMAT_results_to_header(S1, temperature_xy)
    # write ASCII grid to new file
    write_str = repr(A2)
    myfile = open('Grad_grid_out1.txt', 'w')
    # use repr to derive a string representation of the Object, as defined in __repr__
    myfile.write(repr(A2))
    myfile.close()
    # A1.plot_ASCII_grid_2D()
    

#    print A1.data_array_mask
    
    # xstr = A1.xcoords(head)
    # ystr = A1.ycoords(head)

    # ascii_array = A1.grid_xyz_to_array(f_ascii, head, xstr, ystr)

    # print(ascii_array[0][1])
