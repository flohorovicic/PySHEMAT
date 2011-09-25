"""
PySHEMAT is a free set of Python modules to create and process input
files for fluid and heat flow simulation with SHEMAT (http://137.226.107.10/aw/cms/website/zielgruppen/gge/research_gge/~uuv/Shemat/?lang=de)

******************************************************************************************
PySHEMAT is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

PySHEMAT is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with PyTOUGH.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************************

For module, update and documentation of PySHEMAT please see:
https://github.com/flohorovicic/PySHEMAT

If you use PySHEMAT for a scientific study, please cite our publication in Computers and Geosciences

"""

import re # for regular expression fit, neccessary for stupid nlo files
import matplotlib as m

class Shemat_file:
    """Class for shemat model file .nml"""
    # class needed? maybe good as a "containter -> might be good
    # to assure compatibility with future versions...
    def __init__(self, filename='', **kwds):
        """read file
        kwds:
        new_filename = string: filename in case an empty file is created
        offscreen = True/False: set variables for offscreen rendering, e.g. to create plots on
                a remote machine via ssh
        """
        if filename == '':
            print "create empty file"
            if kwds.has_key('new_filename'): self.filename = kwds['new_filename']
        else:
            self.filelines = self.read_file(filename)
            self.filename = filename
            self.idim = int(self.get("IDIM"))
            self.jdim = int(self.get("JDIM"))
            self.kdim = int(self.get("KDIM"))
        if kwds.has_key('offscreen') and kwds['offscreen']:
            m.use('Agg')
                
    def read_file(self, filename):
        """open and read file, return list with filelines
        either filename or projectname as argument (projectname
        is filename without .nml)"""
        try:
            file = open(filename, "r")
        except IOError, (nr, string_err):
            print "Can not open file " + filename + ": " + string_err + " Err#" + str(nr)
            print "Please check file name and directory and try again"
            raise IOError
        # check if number of entries correct
        filelines = file.readlines()
        file.close()
        # set local variables
        return filelines
        
    def write_file(self, filename):
        """open and write file to filename.nml
        either filename or projectname as argument (projectname
        is filename without .nml)"""
        if filename[-4:] != ".nml":
            # print "Add extesion .nml to filename " + filename
            filename += ".nml"
        try:
            file = open(filename,"w")
        except IOError, (nr, string_err):
            print "Can not open file" + filename + ": " + string_err + " Err#" + str(nr)
            print "Please check file name and directory and try again"
            exit(0)        
        print "Write new SHEMAT file: " + filename
        file.writelines(self.filelines)
        file.close()
        
    def adjust_ctl_file(self, old_filename, new_filename, **kwds):
        """adjust name in shemat.ctl file to run SHEMAT from command
        line; shemat.ctl file has to be in same directory and already
        exist, only shemat-filename within ctl-file is changed
        (from old_filename to new_filename)
        possible optional arguments:
        backup = False/ True: create shemat_ctl.bak backup file, default true
        ctl_filename = "shemat.ctl" : set other ctl filename
        """
        # check, if extension at filename
        if new_filename[-4:] != ".nml":
            # print "Add extesion .nml to filename " + filename
            new_filename += ".nml"
        if kwds.has_key("ctl_filename"):
            ctl_file = kwds["ctl_filename"]
        else:
            ctl_file = "shemat.ctl"        
        try:
            file = open(ctl_file,"r")
        except IOError, (nr, string_err):
            print "Can not open file " + ctl_file + ": " + string_err + " Err# " + str(nr)
            from os import getcwd
            print "Please check if file exists in working directory " + getcwd()
            exit(0)        
        ctl_lines = file.readlines()
        file.close()
        # write backup file
        if kwds.has_key("backup") and not kwds["backup"]:
            print "do not write backup file"
            from os import remove
            remove(ctl_file)
        else:
            print "Rename " + ctl_file + " to backup file shemat_ctl.bak"
            from os import rename, remove
            try:
                rename(ctl_file, "shemat_ctl.bak")
            except WindowsError:                
                try:
                    remove("shemat_ctl.bak")
                    rename(ctl_file, "shemat_ctl.bak")
                except WindowsError, (nr, string_err):
                    print "Error renaming file: " + string_err + " Err# " + str(nr)
                    exit(0)
        for i,l in enumerate(ctl_lines):
            if "SHEMAT Control File" in l:
                ctl_lines[i] = "# SHEMAT Control File (generated by Shemat_file.py)\n"
            if l[0] != "#":
                if old_filename in l:
                    ctl_lines[i] = new_filename + "\n"
                if old_filename[0:-4] + " 3" in l:
                    ctl_lines[i] = new_filename[0:-4] + " 3\n"
        # write new file
        try:
            file = open(ctl_file,"w")
        except IOError, (nr, string_err):
            print "Can not open file " + ctl_file + ": " + string_err + " Err# " + str(nr)
            from os import getcwd
            print "Please check if file exists in working directory " + getcwd()
            exit(0)        
        file.writelines(ctl_lines)
        file.close()
        
    def coupling_info(self):
        """read coupling information out of variable KOPLNG and
        dechipher; return as string"""
        coupl_str = self.get("KOPLNG")
        # dechipher
        str_out = ""
        if coupl_str[0] == "C":
            str_out = str_out + "Coupled simulation of flow and heat\n"
        elif coupl_str[1] == "O":
            str_out = str_out + "density = function of concentration flow and chemical reaction:\n"
            if coupl_str[2] == "U":
                str_out = str_out + "\t- Kozeny-Carman-Pape\n"
            else:
                str_out = str_out + "\t- other coupling, see book pg. 37\n"
        elif coupl_str[3] == "P":
            str_out = str_out + "rock thermal cond = f(T)\n"
        else:
            str_out = str_out + "no coupling defined\n"
        return str_out
    
    def fixed_parameter_info(self):
        """return status of fixed parameters and return as string"""
        s = ""
        f = self.get_array("KOPPX_FLAG")
        v = self.get_array("KOPPX_FIELD")
        n = ['Density:\t\t', 'Thermal Conductivity:\t', 
             'Compressibility:\t', 'Thermal capacity:\t', 'Viscosity:\t\t']
        for i,f in enumerate(f):
            s += n[i]
            if f == 0: s += "not fixed\n"
            else: s+= "%f (fixed) \n"
        return s
            
        
    def get(self, var_name, line=1):
        """get scalar variable from .nml file; 
        default: variabel in one line after var_name
        if more than one line: set with argument line=n"""
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                return self.filelines[i+1]
                break
        
    def get_array(self, var_name):
        """get array variable from .nml file
        array data with mulitplier "*" is de-constructed and everything
        is returned as a list
        Special consideration of boundary conditions:
        these are implemented as:
        - self.diri_conc: Dirichlet BC for concentration => PRES neg
        - self.diri_temp: Dirichlet BC for temperature => POR neg
        - self.diri_head: Dirichlet BC for hydr head => PERM neg
        these object variables/ local variables are automatically
        read if PERM, POR or PRES are read         
        """
        for (i,l) in enumerate(self.filelines):
            # Include: explicit definition of var_name to prevent double-matching
            if var_name[0] == "#":
                if not var_name in l: continue
            elif not "# " + var_name in l: continue
            if True: 
                # problem with .nlo files: strangely other value separators
                # (csv) and unfortunately also some extra newlines...
                # thus: read data until next # separator (can this cause problems?)
                j = 1
                data_raw = ''
                if 'AREAKT' in var_name: data_raw = data_raw + self.filelines[i+j]
                else:
                    while "#" not in self.filelines[i+j]:
                        data_raw = data_raw + self.filelines[i+j]
                        # print "used %d" % j
                        j += 1
                # data_raw = self.filelines[i+1]
                # if "#" not in self.filelines[i+2]: data_raw = data_raw + self.filelines[i+2]
                data_raw = re.split(', *| *', data_raw)
                data = []
                # print "length of data for " + var_name +  " %d" % len(data_raw)
                if len(data_raw) == 1: # new_line at end of string!
                    if data_raw[0][-1] == '\n':
                        data_raw[0] = data_raw[0][0:-1] # last "entry" is newline command!
                    else:
                        data_raw[0] = data_raw[0][0:-2]
                else:
                    if data_raw[-1] == '\n':
                        data_raw = data_raw[0:-1] # last "entry" is newline command!
                for d in data_raw: 
                    # if multiple definition with "*": split
                    if "*" in d:
                        d1 = d.split("*")
                        for i in range(int(d1[0])):
                            data.append(float(d1[1]))
                    else:
                        if d == '' or d == ' ' or d == '\n': continue # last value is an empty string
                        try:
                            data.append(float(d))
                        except ValueError:
                            print "Problem with value " + d
        # check, if Boundary Conditions are affected
        if var_name == "POR" or var_name == "PERM" or var_name == "PRES":
            # check, if bcs are already read:
            try:
                self.diri_temp
            except AttributeError:                
                self.get_bcs()
            # now: check data itself and return as positive value!
            for i,d in enumerate(data):
                if d < 0:
                    data[i] = -d
        try:
            data
        except UnboundLocalError:
            print "Variable " + var_name + " not defined in Shemat file!"
            return None
        return data
    
    
    def get_bcs(self):
        """get dirichlet boundary conditions; these are stored in .nml file as:
        - conc: negative PRES values
        - temp: negative POR values
        - head: neagitve PERM values
        store in self.diri_temp, self.diri_conc, self.diri_head variables"""
        # initialize object variables
        print "get BCs and store in object variables"
        self.diri_conc = []
        self.diri_temp = []
        self.diri_head = []
        for var_name in ["POR", "PRES", "PERM"]:
            if var_name == "POR":
                print "read temperature boundary conditions"
            elif var_name == "PRES":
                print "read concentration boundary conditions"
            elif var_name == "PERM":
                print "read hydraulic head boundary conditions"           
            for (i,l) in enumerate(self.filelines):
                if var_name in l:
                    # problem with .nlo files: strangely other value separators
                    # (csv) and unfortunately also some extra newlines...
                    # thus: read data until next # separator (can this cause problems?)
                    j = 1
                    data_raw = ''
                    while "#" not in self.filelines[i+j]:
                        data_raw = data_raw + self.filelines[i+j]
                        # print "used %d" % j
                        j += 1
                    # data_raw = self.filelines[i+1]
                    # if "#" not in self.filelines[i+2]: data_raw = data_raw + self.filelines[i+2]
                    data_raw = re.split(', *| *', data_raw)
                    for d in data_raw[0:-1]: # last "entry" is newline command!
                        # if multiple definition with "*": split
                        if "*" in d:
                            d = d.split("*")
                            for i in range(int(d[0])):
                                if d == '' : continue
                                # now, if value is negative: BC!
                                if float(d[1]) < 0: tmp = True
                                else: tmp = False
                                if var_name == "POR":
                                    self.diri_temp.append(tmp)
                                elif var_name == "PRES":
                                    self.diri_conc.append(tmp)
                                elif var_name == "PERM":
                                    self.diri_head.append(tmp)
                        else:
                            if d == '' : continue
                            try:
                                if float(d) < 0: tmp = True
                            except ValueError:
                                continue
                            else: tmp = False
                            if var_name == "POR":
                                self.diri_temp.append(tmp)
                            elif var_name == "PRES":
                                self.diri_conc.append(tmp)
                            elif var_name == "PERM":
                                self.diri_head.append(tmp)
        return True

    
    def set(self, var_name, value, line=1):
        """set variable 'var_name' with value 'value' in .nml file; 
        default: variabel in one line after var_name
        if more than one line: set with argument line=n"""
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                self.filelines[i+line] = str(value) + "\n"

    def set_array(self, var_name, value_list, **kwds):
        """set variable 'var_name' with values in 'value_list' in .nml_file;
        mulitpliers "*" are constructed (as used in Shemat .nml file)
        Special consideration of boundary conditions:
        these are implemented as:
        Special consideration of boundary conditions:
        these are implemented as:
        - self.diri_conc: Dirichlet BC for concentration => PRES neg
        - self.diri_temp: Dirichlet BC for temperature => POR neg
        - self.diri_head: Dirichlet BC for hydr head => PERM neg
        these object variables/ local variables are automatically
        set if PERM, POR or PRES are set
        optional keywords:
        float_type = 'high_res', 'normal' : precision of floating point; normal: 2 digits only                 
        """
        value = ""
        # check, if Boundary Conditions are affected
        if var_name == "POR" or var_name == "PERM" or var_name == "PRES":
            # check, if bcs are already read:
            try:
                self.diri_temp
            except AttributeError:                
                self.get_bcs()
            # now: set negative values, if BCs are defined at list positions
            if var_name == "POR":
                for i,l in enumerate(value_list):
                    if self.diri_temp[i]:
                        value_list[i] = -l
            if var_name == "PERM":
                for i,l in enumerate(value_list):
                    if self.diri_head[i] == True:
                        value_list[i] = -l
            if var_name == "PRES":
                for i,l in enumerate(value_list):
                    if self.diri_conc[i] == True:
                        value_list[i] = -l                
        # search variable position in .nml file
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                # construct variable in correct format with multiplier "*"
                n = 1
                for (j,val) in enumerate(value_list):
                    try:
                        if val == value_list[j+1]:
                            n += 1
                            continue
                    except IndexError: pass
                    if n == 1:
                        if var_name == "PERM" or var_name == "HPR":
                            # check if value == 0, then: assign 0 only
                            if val == 0:
                                value += "0 "
                            else:
                                value += "%.2e " % val
                        elif var_name == "GEOLOGY": # or var_name == "ANISOJ" or var_name == "ANISOI":
                            # integer value
                            value += "%d " % val
                        elif var_name == "QBASAL3D":
                            # assign three digits
                            value += "%.3e " % val
                        elif kwds.has_key('float_type'):
                            if kwds['float_type'] == 'high_res':
                                value += "%.2e " % val
                        else:
                            value += "%.2f " % val
                    else:
                        if var_name == "PERM" or var_name == "HPR":
                            # check if value == 0, then: assign 0 only
                            if val == 0:
                                value += "%d*0 " % n
                            else:
                                value += "%d*%.2e " % (n,val)
                        elif var_name == "GEOLOGY": # or var_name == "ANISOJ" or var_name == "ANISOI":
                            # integer value
                            value += "%d*%d " % (n,val)
                        elif var_name == "QBASAL3D":
                            # assign three digits
                            value += "%d*%.3e " % (n,val)
                        elif kwds.has_key('float_type'):
                            if kwds['float_type'] == 'high_res':
                                value += "%d*%e " % (n, val)
                        else:
                            value += "%d*%.2f " % (n, val)
                        n = 1
                # set in .nml file
                self.filelines[i+1] = value + "\n"
    
    def set_array_from_xyz_structure(self,var_name, xyz_structure_list,**kwds):
        """set variable 'var_name' with values in 'xyz_structure_list' in .nml_file;
        xyz_structure_list can be one of those derived from get_array_as_xyz_structure
        mulitpliers "*" are constructed (as used in Shemat .nml file)
        Special consideration of boundary conditions:
        these are implemented as:
        Special consideration of boundary conditions:
        these are implemented as:
        - self.diri_conc: Dirichlet BC for concentration => PRES neg
        - self.diri_temp: Dirichlet BC for temperature => POR neg
        - self.diri_head: Dirichlet BC for hydr head => PERM neg
        these object variables/ local variables are automatically
        set if PERM, POR or PRES are set                 
        optional keywords:
        float_type = 'high_res', 'normal' : precision of floating point; normal: 2 digits only
        """
        value = ""
        # decompose xyz-list into norma value list
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        value_list = []
        for k in range(kdim):
            for j in range(jdim):
                for i in range(idim):
                    value_list.append(xyz_structure_list[i][j][k])
        

        # check, if Boundary Conditions are affected
        if var_name == "POR" or var_name == "PERM" or var_name == "PRES":
            # check, if bcs are already read:
            try:
                self.diri_temp
            except AttributeError:                
                self.get_bcs()
            # now: set negative values, if BCs are defined at list positions
            if var_name == "POR":
                for i,l in enumerate(value_list):
                    if self.diri_temp[i]:
                        value_list[i] = -l
            if var_name == "PERM":
                for i,l in enumerate(value_list):
                    if self.diri_head[i] == True:
                        value_list[i] = -l
            if var_name == "PRES":
                for i,l in enumerate(value_list):
                    if self.diri_conc[i] == True:
                        value_list[i] = -l   
        # search variable position in .nml file
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                # construct variable in correct format with multiplier "*"
                n = 1
                for (j,val) in enumerate(value_list):
                    try:
                        if val == value_list[j+1]:
                            n += 1
                            continue
                    except IndexError: pass
                    if n == 1:
                        if var_name == "PERM" or var_name == "HPR":
                            value += "%.2e " % val
                        elif kwds.has_key('float_type'):
                            if kwds['float_type'] == 'high_res':
                                value += "%.2e " % val
                        else:
                            value += "%.2f " % val
                    else:
                        if var_name == "PERM" or var_name == "HPR":
                            value += "%d*%.2e " % (n,val)
                        elif kwds.has_key('float_type'):
                            if kwds['float_type'] == 'high_res':
                                value += "%d*%e " % (n, val)
                        else:
                            value += "%d*%.2f " % (n, val)
                        n = 1
                # set in .nml file
                self.filelines[i+1] = value + "\n"
    
    def create_formations_ids(self):
        """create array self.formation_ids with formation ids from geology data array"""
        # property zones in SHEMAT are defined from 1 to n => sufficient to find the maximum value of geology array
        geology = self.get_array("GEOLOGY")
        self.formation_ids = range(1,int(max(geology))+1)
        return self.formation_ids
    
    def array_to_xyz_structure_object(self, array):
        """restructure array into x,y,z 3-D structure as
        data[i][j][k]
        with i,j,k: counters in x,y,z direction
        arguments:
        array    : array to be restructured
        """
        from numpy import size
        if not (self.idim*self.jdim*self.kdim == size(array)):
            print "new dimensions not consistent with array size"
            print "can not create new array!"
            return
        
        # initialize output array
        data = []
        # iterate over dimensions and re-sort array
        n = 0
        # initialize array in x,y,z-order
        for i in range(self.idim):
            tmp2 = []
            for j in range(self.jdim):
                tmp = [0 for k in range(self.kdim)]
                tmp2.append(tmp)
            data.append(tmp2)
        
        # now, fill data structure in z,y,x loops for correct x,y,z order
        for k in range(self.kdim):
            for j in range(self.jdim):
                for i in range(self.idim):
                    data[i][j][k] = array[n]
                    n += 1
        return data
    
    def array_to_xyz_structure(self,array,idim,jdim,kdim):
        """restructure array into x,y,z 3-D structure as
        data[i][j][k]
        with i,j,k: counters in x,y,z direction
        arguments:
        array    : array to be restructured
        idim     : dimension of new array in x-direction (default: model dimensions)
        jdim     : dimension of new array in y-dircetion
        kdim     : dimension of new array in z-direction
        """
        # check if array length and new dimensions are consistent
        from numpy import size
        if not (idim*jdim*kdim == size(array)):
            print "new dimensions not consistent with array size"
            print "can not create new array!"
            return
        
        # initialize output array
        data = []
        # iterate over dimensions and re-sort array
        n = 0
        # initialize array in x,y,z-order
        for i in range(idim):
            tmp2 = []
            for j in range(jdim):
                tmp = [0 for k in range(kdim)]
                tmp2.append(tmp)
            data.append(tmp2)
        
        # now, fill data structure in z,y,x loops for correct x,y,z order
        for k in range(kdim):
            for j in range(jdim):
                for i in range(idim):
                    data[i][j][k] = array[n]
                    n += 1
        return data
        
    def get_cell_centres(self):
        """calculate centre of cells in absolute values"""
        # reload cell boundaries
        self.get_cell_boundaries()
        # calculate centres for x
        self.centre_x = []
        for i in range(len(self.boundaries_x[:-1])):
            self.centre_x.append((self.boundaries_x[i+1]-self.boundaries_x[i])/2.+self.boundaries_x[i])
        # calculate centres for y
        self.centre_y = []
        for i in range(len(self.boundaries_y[:-1])):
            self.centre_y.append((self.boundaries_y[i+1]-self.boundaries_y[i])/2.+self.boundaries_y[i])
        # calculate centres for z
        self.centre_z = []
        for i in range(len(self.boundaries_z[:-1])):
            self.centre_z.append((self.boundaries_z[i+1]-self.boundaries_z[i])/2.+self.boundaries_z[i])
            
    def update_model_from_geomodeller_xml_file(self, geomodeller_xml_file, **kwds):
        """use gemodeller direct dll access to directly read geology data into shemat object
        idea: also update poro, perm, and all other parameters directly?
        Either: evaluate from shemat-file or read from (external) parameter file?
        optional kwds:
        compute = True/False: (re-) compute geological model before processing
        lower_left_x = float : x-position of lower-left corner (default: model range)
        lower_left_y = float : y-position of lower-left corner (default: model range)
        lower_left_z = float : z-position of lower-left corner (default: model range)
        """
        import geomodeller_api as g_api
        g_api.initialise_geomodeller_api(r'C:\Geomodeller\GeoModeller_1502\bin')
        g_api.load_model(geomodeller_xml_file)
        if kwds.has_key('compute') and kwds['compute']==True:
            g_api.compute()
        (geo_dx,geo_dy,geo_dz) = g_api.get_model_extent()
        (xmin,ymin,zmin,xmax,ymax,zmax) = g_api.get_model_bounds()
        if kwds.has_key('lower_left_x') and kwds['lower_left_x'] != '':
            xmin = kwds['lower_left_x']
        if kwds.has_key('lower_left_y') and kwds['lower_left_y'] != '':
            ymin = kwds['lower_left_y']
        if kwds.has_key('lower_left_z') and kwds['lower_left_z'] != '':
            zmin = kwds['lower_left_z']
        # check model extents of GeoModeller model and SHEMAT file
        self.get_cell_centres()
        geo_new = [] # new geology array
        n_cells = len(self.centre_z) * len(self.centre_y) * len(self.centre_x)
        i = 0
        for z in self.centre_z:
            for y in self.centre_y:
                for x in self.centre_x:
                    # geo_new.append(g_api.get_lithology(x,y,-geo_dz+z)) # old version
                    print "process cell %8d of %d, %4.1f Percent" % (i, n_cells, (float(i)/float(n_cells)*100))
                    geo_new.append(g_api.get_lithology(xmin + x, ymin + y, zmin + z))
                    i += 1
        self.set_array("GEOLOGY", geo_new)
    
    def update_properties_from_csv_list(self, csv_file_name):
        """update SHEMAT properties from csv file, based on property 
        distribution in GEOLOGY array;
        This function can be used
        - to populate SHEMAT input file with new parameters
        - to update SHEMAT input file when GEOLOGY array was changed
        (e.g. after update of GEOLOGY array from GeoModeller input file)
        conventions for .csv file:
        Header line neccessary, should include GEOLOGY column and one column
        for all the properties to be updated
        Header can contain a first column with Title 'NAME' for name of formation (not used,
        just for better overview in .csv file)
        
        Optional property lines in .csv-file:
        PERM_FUNC: indicating that definition of permeability function in following lines
        PERM_RANDOM: indicating that definition of permeability random distribution follows
        """
        geol = self.get_array("GEOLOGY")
        # open csv file
        csv = open(csv_file_name,'r')
        csv_lines = csv.readlines()
        csv.close()
        csv_header = csv_lines[0].split(',')
        # remove end of line character from last entry
        csv_header[-1] = csv_header[-1].rstrip()
        # test if file contains another column (e.g. a 'Name' column) before GEOLOGY column
        if csv_header[0] == 'GEOLOGY':
            start = 1
        else:
            start = 2 # in this case, GEOLOGY column HAS TO BE in the second column!!
        csv_datalines = []
        for i_csv,l in enumerate(csv_lines[1:]):
#            print "line %d: %s" % (i_csv,l)
            if "PERM_FUNC" in l:
                print "permeability function defined"
                # test correct definition
                if csv_lines[i_csv+2].split(',')[0] != "Type":
                    print "please define type (kwd Type) in input line %d" % i_csv+2
                    break
                if csv_lines[i_csv+3].split(',')[0] != "Lines":
                    print "please define number of lines (kwd Lines) in input line %d" % i_csv+3
                    break
                # deconstruct input file and create permeability_function_dict with formation id as key
                type = csv_lines[i_csv+2].split(',')[1]
                lines = csv_lines[i_csv+3].split(',')[1]
                perm_func = {}
                perm_func['type'] = type
                if type == 'linear_global':
                    for n_line in range(int(lines)):
                        line = csv_lines[i_csv+5+n_line].split(',')
                        func_dict = {'k_min' : float(line[start]),
                                     'k_min_depth' : float(line[start+1]),
                                     'k_max' : float(line[start+2]),
                                     'k_max_depth' : float(line[start+3])}
                        perm_func[line[start-1]] = func_dict
            if "PERM_RANDOM" in l:
                print "permeability random distribution defined"
                # test correct definition
                if csv_lines[i_csv+2].split(',')[0] != "Type":
                    print "please define type (kwd Type) in input line %d" % i_csv+2
                    break
                if csv_lines[i_csv+3].split(',')[0] != "Lines":
                    print "please define number of lines (kwd Lines) in input line %d" % i_csv+3
                    break
                # deconstruct input file and create permeability_random_dict with formation id as key
                type = csv_lines[i_csv+2].split(',')[1]
                lines = csv_lines[i_csv+3].split(',')[1]
                perm_rand = {}
                perm_rand['type'] = type
                if type == 'lognormal':
                    for n_line in range(int(lines)):
                        line = csv_lines[i_csv+5+n_line].split(',')
                        rand_dict = {'log_stdev' : line[start]}
                        perm_rand[line[start-1]] = rand_dict
            else:
                csv_datalines.append(l.split(','))
        if csv_header[0] != "GEOLOGY" and csv_header[1] != "GEOLOGY":
            print "first or second column should contain GEOLOGY data!"
            return None
        prop_array = []
        for prop in csv_header[start:]:
            p = self.get_array(prop)
            prop_array.append(p)
        # initialise new array
        prop_array_new = []
        for p in prop_array:
            prop_array_new.append([])
        
        # determine row number of geology units (for correct mapping below)
        geol_pos = {}
        for i,line in enumerate(csv_datalines):
            geol_pos[int(line[1])] = i
#        print geol_pos
        # create new property array
        for i,g in enumerate(geol):
            for j,prop in enumerate(prop_array):
                try:
                    val = csv_datalines[geol_pos[int(g)]][j+start]
                    prop_array_new[j].append(float(val))
                except KeyError:
                    print "Geology: %d" % int(g-1)
                    print j
                    print start
#                    print "Value: %f" % csv_datalines
                    print 80*'*'
                    print "csv file not complete: no values for geology unit %d found!" % g
                    print "please check file and try again"
                    print 80*'*'
                    raise KeyError("Input file not complete, index for one geology unit not found!")
        # update propperty arrays in Shemat file
        for i,prop in enumerate(csv_header[start:]):
            self.set_array(prop,prop_array_new[i])
        # now: test, if permeability function defined and if so: (re-) compute permeability for thir formation
        try:
            perm_func
            perm_func_defined = True
        except NameError:
            pass
        # now: test, if permeability randm distribution defined and if so: (re-) compute permeability for thir formation
        try:
            perm_rand
            perm_rand_defined = True
        except NameError:
            pass
        try: 
            perm_func_defined
            print "Permeability function defined, recompute permeabilities for formations"
            # define peermeability function
            def permeability(z, total_depth, k_min, k_min_depth, k_max, k_max_depth, **kwds):
                """define permeability as a function of depth"""
                from numpy import log10
                # k = 10**(log10(k_max) - z * (log10(k_max) - log10(k_min)) / (k_max_depth - k_min_depth))
                k = 10**(log10(k_max) - (k_max_depth - z) * (log10(k_max) - log10(k_min)) / (k_max_depth - k_min_depth))
                return k
            # load relevant parameters
            geol_xyz = self.get_array_as_xyz_structure("GEOLOGY")
            idim = int(self.get("IDIM"))
            jdim = int(self.get("JDIM"))
            kdim = int(self.get("KDIM"))
            dz = self.get_array("DELZ")
            # calculate total depth, assuming constant layer thickness!!
            total_depth = sum(dz)
            perm_xyz = self.get_array_as_xyz_structure("PERM")
            # formation iD
            for j in range(jdim):
                for i in range(idim):
                    for k in range(kdim):
                        g = str(int(geol_xyz[i][j][k]))
                        if perm_func.has_key(g):
                            # perm_xyz[i][j][k] = permeability((total_depth - sum(dz[0:k])), total_depth, 1E-15, 1E-13)
                            perm_xyz[i][j][k] = permeability((total_depth - sum(dz[0:k])), 
                                                             total_depth,
                                                             perm_func[g]['k_min'],
                                                             perm_func[g]['k_min_depth'],
                                                             perm_func[g]['k_max'],
                                                             perm_func[g]['k_max_depth']
                                                             )
                        else:
                            perm_xyz[i][j][k]
            self.set_array_from_xyz_structure("PERM", perm_xyz)
        except NameError:
            pass
        return None
        
    def update_property_from_dict(self,property,property_dict):
        """update the value of one property according to geology id;
        properties are passed as a dictionary with assignments, e.g:
        {1 : 2.9, 2 : 3, ...} 
        property = string : property name, according to SHEMAT variable name
        property_dict = dict : assigned values; can be defined for a subset of
                        geological units only, all not defined are not changed
        """
        geol = self.get_array("GEOLOGY")
        prop_array = self.get_array(property)
        prop_array_new = []
        for i,g in enumerate(geol):
            if property_dict.has_key(g):
                prop_array_new.append(property_dict[g])
            else:
                prop_array_new.append(prop_array[i])
        self.set_array(property, prop_array_new)
        
    def get_model_extent(self):
        """determine model extent in x,y,z direction from self.boundaries_x,y,z
        return as tuple (extent_x, extent_y, extent_z) and store in self.extent_x, self.extent_y, self.extent_z"""
        # recompute boundaries (always or trigger with kwd?)
        self.get_cell_boundaries()
        self.extent_x = max(self.boundaries_x) - min(self.boundaries_x)    
        self.extent_y = max(self.boundaries_y) - min(self.boundaries_y)    
        self.extent_z = max(self.boundaries_z) - min(self.boundaries_z)
        return (self.extent_x, self.extent_y, self.extent_z)
            
            
    def get_cell_boundaries(self):
        """calculate cell boundaries from arrays DELX, DELY, DELZ and save
        to self.boundaries_x, self.boundaries_y, self.boundaries_z"""
        delx = self.get_array("DELX")
        dely = self.get_array("DELY")
        delz = self.get_array("DELZ")
        # x
        b = []
        laststep = 0
        b.append(laststep)
        for step in delx:
            b.append(laststep+step)
            laststep += step
        self.boundaries_x = b
        # y
        b = []
        laststep = 0
        b.append(laststep)
        for step in dely:
            b.append(laststep+step)
            laststep += step
        self.boundaries_y = b
        # z
        b = []
        laststep = 0
        b.append(laststep)
        for step in delz:
            b.append(laststep+step)
            laststep += step
        self.boundaries_z = b
        
        
    def get_array_as_xyz_structure(self,var_name):
        """read variable and order into 3-D structure as
        data[i][j][k]
        with i,j,k: counters in x,y,z direction
        arguments:
        var_name : property from SHEMAT file (read again in this function! rewrite?)
        """
        # initialize output array
        data = []
        # read array from SHEMAT file
        ori_array = self.get_array(var_name)
        # read array length from SHEMAT file
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        # iterate over dimensions and re-sort array
        n = 0
        # initialize array in x,y,z-order
        data = []
        for i in range(idim):
            tmp2 = []
            for j in range(jdim):
                tmp = [0 for k in range(kdim)]
                tmp2.append(tmp)
            data.append(tmp2)
        from pylab import shape
        # print shape(data)
        # now, fill data structure in z,y,x loops for correct x,y,z order
        for k in range(kdim):
            for j in range(jdim):
                for i in range(idim):
                    # print n
                    try:
                        data[i][j][k] = ori_array[n]
                    except IndexError:
                        print "PROBLEM WITH INDEX in self.get_array_as_xyz_structure"
                        print "assigned 0 to index value %d" % n
                        print "original array length: %d" % len(ori_array)
                    n += 1
        return data
    
    def calc_mean_formation_temp(self, formation_id):
        """calculate mean temperature of one formation at one location
        formation_id : corresponding to the property id in Shemat/ Geology Variable
        returns mean_temp = list (array with 2-D grid values in 1-D structure)
        """
        # load geology data to xyz array
        geology_xyz = self.get_array_as_xyz_structure("GEOLOGY")
        temp_xyz = self.get_array_as_xyz_structure("TEMP")
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        # now, iterate over x,y in geology array
        temp_xy = []
        for i in range(idim):
            for j in range(jdim):
                localtemp = 0
                i = 0
                for k in range(kdim):
                    if geology_xyz[i][j][k] == formation_id:
                        localtemp += temp_xyz[i][j][k]
                        i = i + 1
                if i != 0:
                    meantemp = localtemp / i
                else:
                    meantemp = 0
                temp_xy.append(meantemp)             
        return temp_xy
    
    def create_property_histogram(self, formation_id, property, **kwds):
        """create a histogram for a defined property, e.g.: histogram for
        temperature values of formation 1
        formation_id : corresponding to the property id in Shemat/ Geology Variable
        property : can be any of the properties in the SHEMAT nml/nlo files, e.g.: DICHTE, PERM, POR
        returns figure
        optional keywords:
        show = True/False: directly show plot of histogram
        property_name = Name of property, for title of plot
        """
        geology_xyz = self.get_array_as_xyz_structure("GEOLOGY")
        property_xyz = self.get_array_as_xyz_structure(property)
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        hist_data = []
        for i in range(idim):
            for j in range(jdim):
                for k in range(kdim):
                    if geology_xyz[i][j][k] == formation_id:
                        hist_data.append(property_xyz[i][j][k])
        import matplotlib.pyplot as plt
#        from pylab import hist, show, title, text, figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        h = ax.hist(hist_data, normed=True)

        if kwds.has_key('property_name'): 
            ax.set_title('Histogram of %s for formation id %d' % (kwds['property_name'],formation_id))
        from numpy import mean
        ax.text(0.75,0.8,"total mean value: \n%5.2f" % mean(hist_data), transform=ax.transAxes, horizontalalignment = 'center')
        if kwds.has_key('show') and kwds['show'] == True:
            print "show histogram"
            plt.show()
        else:
            figname = 'hist_form_%d_%s.png' % (formation_id, property)
            fig.savefig(figname)
        return fig     
    
    def create_delimiter_histogram(self, **kwds):
        """create histogram plots for DELX, DELY and DELZ arrays
        e.g. useful to check random grid values, etc.
        optional keywords:
        2d = True/False: consider DELY (or not)
        show = True/False: directly show plot of histogram
        """
        delx = self.get_array("DELX")
        if kwds.has_key("2d") and kwds['2d']:
            pass
        else:
            dely = self.get_array("DELY")
        delz = self.get_array("DELZ")
        import matplotlib.pyplot as plt
#        from pylab import hist, show, title, text, figure
        fig = plt.figure()
        ax = fig.add_subplot(311)
        h = ax.hist(delx, normed=True)
        ax = fig.add_subplot(312)
        h = ax.hist(dely, normed=True)
        ax = fig.add_subplot(313)
        h = ax.hist(delz, normed=True)
        if kwds.has_key('show') and kwds['show'] == True:
            fig.show()
        else:
            fig.savefig('delimiter_histogram.png')
        
    def calc_global_mean_value(self, property):
        """calculate mean value for one property, location based; similar to
        self.calc_mean_formation_value but without formation separation"""
        property_xyz = self.get_array_as_xyz_structure(property)
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        # now, iterate over x,y in geology array
        # print idim,jdim,kdim
        property_xy = []
        for j in range(jdim):
            for i in range(idim):
                local_property = 0
                n = 0
                for k in range(kdim):
                    local_property += property_xyz[i][j][k]
                    n += 1
                if n != 0:
                    property = local_property / n
                else:
                    property = 0
                property_xy.append(property)             
        return property_xy
    
    def random_property_change(self, formation_id, property, **kwds):
        """add a random value to a property of one formation
        formation_id : formation number
        property : SHEMAT property type (e.g. "PERM")
        optional keywords:
        type = (gaussian, log, one_over_f, ...) : statistics
        sigma = float : standard deviation for the case of gaussian statistics
        (more added when required)
        """
        geology = self.get_array("GEOLOGY")
        property_array = self.get_array(property)
        from random import gauss
        from numpy import random, array
#        
#    if kwds.has_key('random_perm_flux_sigma') and kwds['random_perm_flux_sigma'] > 0    :
#        from numpy import random, array
#        perm = S1.get_array("PERM")
#        n_layer = nx*ny
#        perm_top = perm[n_layer:]
#        perm_bottom = perm[:n_layer]
#        perm_flux = random.randn(len(perm))*kwds['random_perm_flux_sigma']
#        perm_new = array(perm) + array(perm_flux)
#        S1.set_array("PERM", perm_new)
#        
          
        for i in range(len(geology)):
            if geology[i] == formation_id:
                if kwds['type'] == 'gaussian':
                    r = gauss(0,kwds['sigma'])
                else:
                    print "No random type defined!"
                    raise AttributeError
                property_array[i] = property_array[i] + r
        self.set_array(property, property_array)
        
            
    
    def calc_mean_formation_value(self, formation_id, property):
        """calculate mean value for one property, location based
        formation_id : corresponding to the property id in Shemat/ Geology Variable
        property : can be any of the properties in the SHEMAT nml/nlo files, e.g.: DICHTE, PERM, POR
        returns list mean_value[n]
        """
        # load geology data to xyz array
        geology_xyz = self.get_array_as_xyz_structure("GEOLOGY")
        property_xyz = self.get_array_as_xyz_structure(property)
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        # now, iterate over x,y in geology array
        # print idim,jdim,kdim
        property_xy = []
        for j in range(jdim):
            for i in range(idim):
                local_property = 0
                n = 0
                for k in range(kdim):
                    if geology_xyz[i][j][k] == formation_id:
                        local_property += property_xyz[i][j][k]
                        n += 1
                if n != 0:
                    property = local_property / n
                else:
                    property = 0
                property_xy.append(property)             
        return property_xy

    def calc_formation_isopach(self, formation_id):
        """calculate voxel based isopach map for a formation at all locations
        formation_id : corresponding to the property id in Shemat/ Geology Variable
        returns list isopach_xy[n]
        """
        # load geology data to xyz array
        geology_xyz = self.get_array_as_xyz_structure("GEOLOGY")
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        # now, iterate over x,y in geology array
        delz = self.get_array("DELZ")
        print idim,jdim,kdim
        isopach_xy = []
        for j in range(jdim):
            for i in range(idim):
                local_isopach = 0
                for k in range(kdim):
                    if geology_xyz[i][j][k] == formation_id:
                        local_isopach += float(delz[k])
                isopach_xy.append(local_isopach)             
        return isopach_xy
         
    def property_xy_to_2D_points(self, property_xy):
        """create a list with coordinates and property values, e.g. for
        further data processing, import into MapInfo, etc.
        property_xy : list with property values, e.g. created from calc_mean_formation_value()
        up to now: only regular discretization in x- and y-direction!
        returns list property_2D_points[x_coord, y_coord, property_value]
        """
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        delx = int(self.get_array("DELX")[0])
        dely = int(self.get_array("DELY")[0])
        n = 0
        property_2D_points = []
        # resize to 1-D array
        
        for j in range(jdim):
            row = []
            for i in range(idim):
                property_2D_points.append([i*delx, j*dely, property_xy[n]])
                n += 1
        return property_2D_points
         
    def mu(self,T):
        """returns dynmaic viscosity of water at a given temperature
        T : temperature in degree Celcius
        """
        # factors: taken from wikipedia page on viscosity
        A = 2.414E-5
        B = 247.8
        C = 140
        T += 273.15  # convert to T in Kelvin
        return A * 10 ** (B/(T-C))
    
    def calc_local_transmissivity(self,formation_id):
        """calculate transmissivity at one location for one formation/ aquifer
        formation_id : corresponding to the property id in Shemat/ Geology Variable
        returns list transmissivity_xy[x][y]
        """
        # load geology data to xyz array
        geology_xyz = self.get_array_as_xyz_structure("GEOLOGY")
        density_xyz = self.get_array_as_xyz_structure("DICHTE")
        permeability_xyz = self.get_array_as_xyz_structure("PERM")
        temp_xyz = self.get_array_as_xyz_structure("TEMP")
        g = 9.81 # grav acceleration
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        dz = int(self.get_array("DELZ")[0])
        # now, iterate over x,y in geology array
        transmissivity_xy = []
        for j in range(jdim):
            for i in range(idim):
                local_transmissivity = 0
                for k in range(kdim):
                    if geology_xyz[i][j][k] == formation_id:
                        # calculate local hydraulic conductivity
                        K = permeability_xyz[i][j][k] * density_xyz[i][j][k] * g / self.mu(temp_xyz[i][j][k])
#                        K = 1E-13 * density_xyz[i][j][k] * g / viscosity
                        local_transmissivity += K * dz
                transmissivity_xy.append(local_transmissivity)             
        return transmissivity_xy
        
    
    def create_shemat_voxet_model(self,property,**kwds):
        """create a voxet model of a property/ variable in .vtk format
        to be viewed with Mayavi;
        optional arguemnts:
        variable = variable array : use variable array instead of property
        Attention: does *not* create an interpolation between points (no .vtk point file)
        but a true representation of the voxets as a "shoe box" model!
        Only (yet) works for a regular grid with constant spacing!
        
        optional keywords:
        show = True/False : open  Mayavi and show model
        
        IDEA:
        - implement for non-regular voxet models
        - visualise voxet "refinement" as voxet "volume" property as proxy
        (lower voxet volume = higher discretization) to check refinement of models
        - save_vtk : save to vtk file
        """
        from enthought.tvtk.api import tvtk
        # create points in structured grid
        pts = []
        # read information from shemat file
        nx = int(self.get("I0"))
        ny = int(self.get("J0"))
        nz = int(self.get("K0"))
#        dx = float(self.get("DELX").split("*")[1])
#        dy = float(self.get("DELY").split("*")[1])
#        dz = float(self.get("DELZ").split(' ')[0])
        dx = self.get_array("DELX")
        dy = self.get_array("DELY")
        dz = self.get_array("DELZ")
        for k in range(nz*2):
            for j in range(ny*2):
                for i in range(nx*2):
#                    pts.append([((i+1)/2)*dx, ((j+1)/2)*dy, ((k+1)/2)*dz])
                    x = sum(dx[0:(i+1)/2])
                    y = sum(dy[0:(j+1)/2])
                    z = sum(dz[0:(k+1)/2])
                    pts.append([x, y, z])
        tot_cells = 2 * nx * 2 * ny * 2 * nz # total number of cells
        # initialize scalar list    
        s = range(tot_cells)
        # set number of nodes in x,y direction (for assigment below)
        nnx = 2 * nx # number of nodes/points in x-dir (as related to num. of elements
        nny = 2 * ny # number of nodes/points in y-dir (as related to num. of elements
        # ! number of elements in z-dir not needed for assigment!
        
        # get data to be viewed
        if kwds.has_key('variable'):
            data = kwds['variable']
        else:
            data = self.get_array(property)
        
        for i in range(nx*ny*nz):
            # layer below element
            # calculate node position of lower left corner of element
            llc = i/(nx*ny)*2*nnx*nny+2*((i%(nx*ny))%nx)+2*nnx*(i%(nx*ny)/nx)
            # print llc
            # print i
            e = data[i]
            # now, assign all nodes of element e (element number i)
            s[llc] = e                  # lower left corner front
            s[llc+1] = e                # lower right corner front
            s[llc+nnx] = e              # lower left corner back
            s[llc+nnx+1] = e            # lower right corner back
            # layer above element
            s[llc+nnx*nny] = e          # upper left corner front
            s[llc+1+nnx*nny] = e        # upper right corner front
            s[llc+nnx+nnx*nny] = e      # upper left corner back
            s[llc+nnx+1+nnx*nny] = e    # upper right corner back
            # print s

        sgrid = tvtk.StructuredGrid(dimensions=(2 * nx, 2 * ny, 2 * nz))
        sgrid.points = pts
        scalar_vtk = s
        sgrid.point_data.scalars = scalar_vtk
        # print len(pts)
        # print pts
        # print len(scalar_vtk)
        sgrid.point_data.scalars.name = 'scalars'
        # print scalar_vtk
        if kwds.has_key('show') and kwds['show']:
            view(sgrid)
    
    def get_origin(self):
        """only alias for self.get_model_origin() for consistency"""
        self.get_model_origin()
        
    def set_origin(self, origin_x, origin_y, origin_z):
        """set model origin; this is not (or not correctly?) implemented
        in the SHEMAT nml file itself - and only part of the class definition!"""
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.origin_z = origin_z

    def get_model_origin(self):
        """the model origin is not (or not correctly?) implemented in the
        SHEMAT nml file itself - prompt user to input, if required!"""
        self.origin_x = raw_input("Model origin, x : ")
        self.origin_y = raw_input("Model origin, y : ")
        self.origin_z = raw_input("Model origin, z : ")

    def create_slice_plot(self, property, direction, position, **kwds):
        """create a 2-D plot of a property in a slice through the model, normal to
        the specified direction and at a given position along this direction;
        property = Shemat-Variable name, e.g. "TEMP"
        direction = x,y,z : direction normal to plot
        position = float : position of plot, real-world coordinates
        optional arguments:
        title = 'Title'  Main title, if not given: name of array (to be implemented, now: no title)
        colorbar = True/False : add colorbar to plot
        colorbar_orientation = horizontal/ vertical : orientation of colorbar
        two_plots = True/False : add a subplot with interpolated image
        show = True/False : show plot
        savefig = True/False : save figure to file
        filename = string : figure filename
        cmap = colormap name for image (cm.colormap)
        vmin = float : z-scale for image plot
        vmax = float
        aspect = float, 'auto', 'equal' : define aspect ratio of plot
        contour = True/False: add contour lines"""
        property_xy = self.get_slice(property, direction, position)
        print 80 * "*"
        print "\n\tCheck passing of keywords!!\n\n"
        print 80 * "*"
        self.create_2D_property_plot(property_xy, direction=direction, **kwds)


    def create_section_property_plot(self,property,interpolation='nearest',**kwds):
        """create a 2D plot of a property in a section,
        for example for 2-D SHEMAT calculations within a section (VERTICAL setting, jdim=1)
        passed array should be 1-D, reshaping done in this method (with idim, kdim)
        standard plot: two images, 
        left image: raw data in (regular) cell structure
        right image: interpolated data (with interpolation passed as argument, see 
        matplotlib.imshow for possible values)
        optional arguments:
        title = 'Title'  Main title, if not given: name of array (to be implemented, now: no title)
        colorbar = True/False : add colorbar to plot
        colorbar_orientation = horizontal/ vertical : orientation of colorbar
        two_plots = True/False : add a subplot with interpolated image
        show = True/False : show plot
        savefig = True/False : save figure to file
        filename = string : figure filename
        cmap = colormap name for image (cm.colormap)
        vmin = float : z-scale for image plot
        vmax = float
        aspect = float, 'auto', 'equal' : define aspect ratio of plot
        contour = True/False: add contour lines
        """ 
        # reshape data
        idim = int(self.get("IDIM"))
        kdim = int(self.get("KDIM"))
        from numpy import array, reshape, rot90, transpose
        property_xz = array(property).reshape(kdim,idim)# .transpose()
#        from pylab import figure, text, show, savefig
        import matplotlib.pyplot as plt
        from matplotlib import cm
        # set properties
        if kwds.has_key('cmap'):
            cmap = kwds['cmap']
        else:
            cmap = cm.jet
        if kwds.has_key('vmin'): vmin = kwds['vmin']
        else: vmin = None
        if kwds.has_key('vmax'): vmax = kwds['vmax']
        else: vmax = None
        if kwds.has_key('aspect'): aspect = kwds['aspect']
        else: aspect = 'auto'
        if kwds.has_key('colorbar_orientation'): orientation = kwds['colorbar_orientation']
        else: orientation = 'vertical'
        # set figure size and plot
        if kwds.has_key('two_plots') and kwds['two_plots'] == True:
            fig = plt.figure(figsize=(10,5))
            ax = fig.add_subplot(1,2,1)
            fig.subplots_adjust(wspace=0.3)        
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
        cax = ax.imshow(property_xz, interpolation = interpolation, 
                        origin = 'lower', 
                        cmap=cmap,
                        aspect=aspect,
                        vmin=vmin,
                        vmax=vmax) #, extent=(-4,4,-4,4))
        if kwds.has_key('contour') and kwds['contour']==True:
            cont = ax.contour(property_xz,20, origin='lower', colors='gray')
        if kwds.has_key('two_plots') and kwds['two_plots'] == True:
            ax.set_title("True voxel locations")
        if kwds.has_key('title'):
            main_title = kwds['title']
            fig.text(0.5,0.95,main_title,horizontalalignment='center',verticalalignment='top', fontsize=18)
        else:
            pass # no title at all
#            fig.text(0.5,0.95,main_title,horizontalalignment='center',verticalalignment='top', fontsize=20)
        if kwds.has_key('colorbar') and kwds['colorbar']==True:
            cbar = fig.colorbar(cax, orientation=orientation) #, ticks=[-1,0,1])
        if kwds.has_key('grid') and kwds['grid']==True: ax.grid()
    #    cbar.ax.set_yticklabels(['< -1','0','> 1'])    
        if kwds.has_key('two_plots') and kwds['two_plots'] == True:            
            ax2 = fig.add_subplot(1,2,2)
            cax2 = ax2.imshow(property_xz, 
                              origin = 'lower', 
                              interpolation = 'spline36',
                              aspect=aspect,
                              vmin=vmin,
                              vmax=vmax) #, extent=(-4,4,-4,4))
            ax2.set_title("Interpolated (Spline)")
            if kwds.has_key('colorbar') and kwds['colorbar']==True:
                cbar2 = fig.colorbar(cax2, orientation=orientation)
        if kwds.has_key('show') and kwds['show'] == True:
            fig.show()  
        if kwds.has_key('savefig') and kwds['savefig'] == True:
            if kwds.has_key('filename'):
                fig.savefig(kwds['filename'])
            else:
                fig.savefig('2D_property_section_plot.png')  
                
    def get_slice(self, property, direction, position):
        """get data for a property in a slice through the model, along a coordinate
        direction for a specified position;
        data is stored in a "xy"-type array, similar to calculated mean properties, etc.
        and can be plotted with self.create_2D_property_plot or exported to an ASCII
        grid file;
        property = SHEMAT variable name, e.g. "TEMP" for temperature
        direction = 'x','y','z' : coordinate direction
        position = float : position of slice in real-world coordinates
        returns property_xy array"""
        
        # get data at position and store in property array
        try:
            self.boundaries_x
        except AttributeError:
            self.get_cell_boundaries()
        try:
            self.origin_x
        except AttributeError:
            self.get_model_origin()

        
        # find position in array
        property_xyz = self.get_array_as_xyz_structure(property)
        
        if direction == 'x':
            # check if position is within bounds of model
            if position > self.boundaries_x[-1]:
                print "Position %s is out of bounds for direction x (max: %f)" % (position, self.boundaries_x[-1])
                raise ValueError
            rel_position = (position - self.origin_x)
            for i,b in enumerate(self.boundaries_x):
                if b > rel_position:
                    # correct position in the array is corresponding to the cell centre
                    # of the last cell!
                    array_pos = i-1
                    break
            # now determine correct slice; implementation with for-loops
            # as correct array assignment with Python somehow doesn't want to work...
            property_slice = []
            for z in range(self.kdim):
                for y in range(self.jdim):
                    property_slice.append(property_xyz[array_pos][y][z])
        elif direction == 'y':
            # check if position is within bounds of model
            if position > self.boundaries_y[-1]:
                print "Position %s is out of bounds for direction y (max: %f)" % (position, self.boundaries_y[-1])
                raise ValueError
            rel_position = (position - self.origin_y)
            for i,b in enumerate(self.boundaries_y):
                if b > rel_position:
                    # correct position in the array is corresponding to the cell centre
                    # of the last cell!
                    array_pos = i-1
                    break
            # now determine correct slice; implementation with for-loops
            # as correct array assignment with Python somehow doesn't want to work...
            property_slice = []
            for z in range(self.kdim):
                for x in range(self.idim):
                    property_slice.append(property_xyz[x][array_pos][z])
        elif direction == 'z':
            # check if position is within bounds of model
            if position > self.boundaries_z[-1]:
                print "Position %s is out of bounds for direction z (max: %f)" % (position, self.boundaries_z[-1])
                raise ValueError
            rel_position = (position - self.origin_z)
            for i,b in enumerate(self.boundaries_z):
                if b > rel_position:
                    # correct position in the array is corresponding to the cell centre
                    # of the last cell!
                    array_pos = i-1
                    break
            # now determine correct slice; implementation with for-loops
            # as correct array assignment with Python somehow doesn't want to work...
            property_slice = []
            for y in range(self.jdim):
                for x in range(self.idim):
                    property_slice.append(property_xyz[x][y][array_pos])
        else:
            print "Direction " + direction + " not correctly defined"
            raise AttributeError

        return property_slice
    
    def get_value_xyz(self,property,x,y,z,interpolate=False,**kwds):
        """get the value of the property at real-world position x,y,z;
        returns float value
        property = SHEMAT variable (e.g. "TEMP"
        x,y,z = float : position [m]
        optional keywords:
        interpolated = True/ False: interpolate value between adjacent cell centres
                     (simple linear interpolation, nothing fancy!)
        relative = True/False : relative to model origin (not in real-world coordinates)"""
        try:
            self.origin_z
        except AttributeError:
            self.get_model_origin()
        try:
            self.boundaries_x
        except AttributeError:
            self.get_cell_boundaries()
        
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_x = 0
            origin_y = 0
            origin_z = 0
        else:
            origin_x = self.origin_x
            origin_y = self.origin_y
            origin_z = self.origin_z

        for i,x_bound in enumerate(self.boundaries_x):
            if (x - origin_x) > self.boundaries_x[-1]:
                print "Position %s is out of bounds for direction x (max: %.2f)" % (x, self.boundaries_x[-1]+origin_x)
                raise ValueError
            if x_bound > (x - origin_x): 
                x_pos = i-1 # array position corresponds to cell centre of cell before boundary!
                break
        for j,y_bound in enumerate(self.boundaries_y):
            if (y - origin_y) > self.boundaries_y[-1]:
                print "Position %s is out of bounds for direction y (max: %.2f)" % (y, self.boundaries_y[-1]+origin_y)
                raise ValueError
            if y_bound > (y - origin_y): 
                y_pos = j-1 # array position corresponds to cell centre of cell before boundary!
                break
        for k,z_bound in enumerate(self.boundaries_z):
            if (z - origin_z) > self.boundaries_z[-1]:
                print "Position %s is out of bounds for direction z (max: %.2f)" % (z, self.boundaries_z[-1]+origin_z)
                raise ValueError
            if z_bound > (z - origin_z): 
                z_pos = k-1 # array position corresponds to cell centre of cell before boundary!
                break
        # now: get property array and return result
        property_xyz = self.get_array_as_xyz_structure(property)
        
        if interpolate==False: # simply use value of box that contains point
            return property_xyz[x_pos][y_pos][z_pos]
        else: # interpolate between adjacent values
            if x > self.boundaries_x[i]:
                pass
            else:
                pass
    
    def get_profile_xy(self,property,x,y,**kwds):
        """get property profile at real-world position x,y. e.g. the temperature
        profile with depth; returns a 1-D array
        property = SHEMAT variable (e.g. "TEMP"
        x,y = float : position [m]
        optional keywords:
        relative = True/False : relative to model origin (not in real-world coordinates)"""
        try:
            self.origin_x
        except AttributeError:
            self.get_model_origin()
        try:
            self.boundaries_x
        except AttributeError:
            self.get_cell_boundaries()
        
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_x = 0
            origin_y = 0
        else:
            origin_x = self.origin_x
            origin_y = self.origin_y

        # find position of x,y
        for i,x_bound in enumerate(self.boundaries_x):
            if (x - origin_x) > self.boundaries_x[-1]:
                print "Position %s is out of bounds for direction x (max: %.2f)" % (x, self.boundaries_x[-1]+origin_x)
                raise ValueError
            if x_bound > (x - origin_x): 
                x_pos = i-1 # array position corresponds to cell centre of cell before boundary!
                break
        for j,y_bound in enumerate(self.boundaries_y):
            if (y - origin_y) > self.boundaries_y[-1]:
                print "Position %s is out of bounds for direction y (max: %.2f)" % (y, self.boundaries_y[-1]+origin_y)
                raise ValueError
            if y_bound > (y - origin_y): 
                y_pos = j-1 # array position corresponds to cell centre of cell before boundary!
                break
        
        # get data and return slice
        property_xyz = self.get_array_as_xyz_structure(property)
        return property_xyz[x_pos][y_pos]
        
    
    def get_isohypse_data(self, property, value):
        """get an array of depth values for one property in the model, e.g.
        a map of depth to 100 C temperatures; The depth value is interpolated
        linearly between the two cell centres above and below the specified
        value.
        Attention: this method creates
        a "2.5-D" type map, i.e. only the first point that reaches the
        value below the surface is considered! For a true 3-D contour plot, use
        a voxet export and VTK viewer (e.g. Mayavi)!
        property = SHEMAT variable name, e.g. "TEMP"
        value = float : value
        returns 1-D array with the same structure as calculated mean temperatures,
        slice arrays (get_slice), etc. that can be plotted with
        self.create_2D_property_plot or exported to an ASCII grid"""
        # get property as an xyz-array
        property_xyz = self.get_array_as_xyz_structure(property)
        self.get_cell_centres()
#        self.get_model_origin()
        
        isohypse_xy = []
        
        for y in range(self.jdim):
            for x in range(self.idim):
                for i,prop in enumerate(property_xyz[x][y]):
                    if prop < value:
                        # value between two centres, linear interpolation to approximate
                        # position
                        pos_ges = ((value - property_xyz[x][y][i]) / \
                                  (property_xyz[x][y][i-1] - property_xyz[x][y][i]) * \
                                  (self.centre_z[i-1] - self.centre_z[i])) + \
                                  float(self.origin_z) + self.centre_z[i]
                        isohypse_xy.append(pos_ges)
                        break
        return isohypse_xy
                    
                
                
    def create_2D_property_plot(self,property,interpolation='spline36',**kwds):
        """create a 2.5 D plot of a property, e.g. mean temperature calculated with
        self.calc_mean_formation_value(1,"TEMP")
        passed array should be 1-D, reshaping done in this method (with idim, jdim)
        ATTENTION: uses matplotlib.imshow for plot, only regular mesh possible!
        standard plot: two images, 
        left image: raw data in (regular) cell structure
        right image: interpolated data (with interpolation passed as argument, see 
        matplotlib.imshow for possible values)
        optional arguments:
        title = 'Title'  Main title, if not given: name of array (to be implemented, now: no title)
        xlabel = string : label of x-axis
        ylabel = string : label of y-axis
        xscale = 'meter', scale of x-axis (adjust tick labels)
        yscale = 'meter', scale of y-axis (adjust tick labels)
        colorbar = True/False : add colorbar to plot
        colorbar_label = string : label of colorbar
        colorbar_orientation = horizontal/ vertical
        two_plots = True/False : add a subplot with interpolated image
        show = True/False : show plot
        savefig = True/False : save figure to file
        filename = string : figure filename
        cmap = colormap name for image (cm.colormap)
        vmin = float : z-scale for image plot
        vmax = float
        vertical_ex = float : vertical exegeration, if set to 1: real aspect ratios
        """ 
        # reshape data
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        delx = self.get_array("DELX")
        dely = self.get_array("DELY")
        delz = self.get_array("DELZ")
        (dx, dy, dz) = self.get_model_extent()
        from numpy import array, reshape, rot90, transpose
        if kwds.has_key('direction'):
            if kwds['direction'] == 'x':
                property_xy = array(property).reshape(kdim,jdim)#.transpose()
                if kwds.has_key('vertical_ex'):
                    pass
            elif kwds['direction'] == 'y':
                property_xy = array(property).reshape(kdim,idim)
                if kwds.has_key('vertical_ex'):
                    extent_h = sum(delx)/idim # real extent horizontal
                    extent_v = sum(delz)/kdim # real extent vertical
                    ratio_v = extent_v / extent_h * kwds['vertical_ex']
                    print "Vertical Ex/ Aspect = %f" % ratio_v
                else: ratio_v = 1.
            elif kwds['direction'] == 'z':
                property_xy = array(property).reshape(jdim,idim)
        else:    
            property_xy = array(property).reshape(jdim,idim)#.transpose()
        #
        #
        # T O   C H E C K!!!!
        # When is rotation about 90 degree necessary???
        # Take also care with reshaping - can mess plot up for unequal cell numbers!
        #
        #
        # property_xy = rot90(property_xy)
        import matplotlib.pyplot as plt
#        from pylab import figure, text, show, savefig
#        from matplotlib import cm
        # set properties
        if kwds.has_key('cmap'):
            cmap = kwds['cmap']
        else:
            cmap = m.cm.jet
        if kwds.has_key('vmin'): vmin = kwds['vmin']
        else: vmin = None
        if kwds.has_key('vmax'): vmax = kwds['vmax']
        else: vmax = None
        # set figure size and plot
        if kwds.has_key('two_plots') and kwds['two_plots'] == True:
            fig = plt.figure(figsize=(10,5))
            ax = fig.add_subplot(1,2,1)
            fig.subplots_adjust(wspace=0.3)        
        else:
            fig = plt.figure()
#            if kwds.has_key('vertical_ex'):
#                ax = fig.add_axes([0.2,0.2,0.6,0.6])
#            else:
            ax = fig.add_subplot(1,1,1)
            if kwds.has_key('xlabel'):
                ax.set_xlabel(kwds['xlabel'])
            elif kwds.has_key('xscale'):
                ax.set_xlabel(kwds['xscale'])
            else:
                ax.set_xlabel('Cells')
            if kwds.has_key('ylabel'):
                ax.set_ylabel(kwds['ylabel'])
            elif kwds.has_key('zscale'):
                ax.set_ylabel(kwds['zscale'])
            else:
                ax.set_ylabel('Cells')
        if kwds.has_key('vertical_ex'): aspect = ratio_v
        else: aspect = 'auto'
        cax = ax.imshow(property_xy, interpolation = interpolation, 
                        origin = 'lower', 
                        cmap=cmap,
                        aspect=ratio_v,
                        vmin=vmin,
                        vmax=vmax) #, extent=(-4,4,-4,4))
        if kwds.has_key('contour') and kwds['contour']==True:
            cont = ax.contour(property_xy,20, origin='lower', colors='gray')

        if kwds.has_key('xscale'):
            self.get_cell_centres()
            if kwds['xscale'] == 'meter':
                xticks = ax.get_xticklabels()
                xlen = len(xticks)
                new_ticks = ['0']
                for i in range(xlen-1):
                    new_ticks.append('%5.f' % (dx / (xlen-2) * i))
                ax.set_xticklabels(new_ticks)
            elif kwds['xscale'] == 'kilometer':
                xticks = ax.get_xticklabels()
                xlen = len(xticks)
                new_ticks = ['0.0']
                for i in range(xlen-1):
                    new_ticks.append('%2.1f' % (dx / (xlen-2) * i / 1000))
                ax.set_xticklabels(new_ticks)
            else:
                print "Warning: xscale " + kwds['xscale'] + " not recognized!"


        if kwds.has_key('yscale'):
            if kwds['yscale'] == 'meter':
                ylen = len(ax.get_yticklabels())
                new_ticks = ['0']
                for i in range(ylen-1):
                    new_ticks.append('%5.f' % (dz / (ylen-2) * i))
                ax.set_yticklabels(new_ticks)
            elif kwds['yscale'] == 'kilometer':
                ylen = len(ax.get_yticklabels())
                new_ticks = ['0.0']
                for i in range(ylen-1):
                    new_ticks.append('%2.1f' % (dz / (ylen-2) * i / 1000))
                ax.set_yticklabels(new_ticks)
            else:
                print "Warning: yscale " + kwds['yscale'] + " not recognized!"

        if kwds.has_key('zscale'):
            if kwds['zscale'] == 'meter':
                ylen = len(ax.get_yticklabels())
                new_ticks = ['0']
                for i in range(ylen-1):
                    new_ticks.append('%5.f' % (dz / (ylen-2) * i))
                ax.set_yticklabels(new_ticks)
            elif kwds['zscale'] == 'kilometer':
                ylen = len(ax.get_yticklabels())
                new_ticks = ['0.0']
                for i in range(ylen-1):
                    new_ticks.append('%2.1f' % (dz / (ylen-2) * i / 1000))
                ax.set_yticklabels(new_ticks)
            else:
                print "Warning: zscale " + kwds['zscale'] + " not recognized!"



        if kwds.has_key('two_plots') and kwds['two_plots'] == True:
            ax.set_title("True voxel locations")
        if kwds.has_key('title'):
            main_title = kwds['title']
            fig.text(0.5,0.95,main_title,horizontalalignment='center',verticalalignment='top', fontsize=18)
        else:
            pass # no title at all
#            fig.text(0.5,0.95,main_title,horizontalalignment='center',verticalalignment='top', fontsize=20)
        if kwds.has_key('colorbar') and kwds['colorbar']==True:
            if kwds.has_key('colorbar_orientation'):
                cbar = fig.colorbar(cax, orientation=kwds['colorbar_orientation'])
            else:
                cbar = fig.colorbar(cax) #, ticks=[-1,0,1])
            if kwds.has_key('colorbar_label'):
                cbar.set_label(kwds['colorbar_label'])
    #    cbar.ax.set_yticklabels(['< -1','0','> 1'])    
        if kwds.has_key('two_plots') and kwds['two_plots'] == True:            
            ax2 = fig.add_subplot(1,2,2)
            cax2 = ax2.imshow(property_xy, 
                              origin = 'lower', 
                              interpolation = 'spline36',
                              vmin=vmin,
                              vmax=vmax) #, extent=(-4,4,-4,4))
            ax2.set_title("Interpolated (Spline)")
            if kwds.has_key('xlabel'):
                ax2.set_xlabel(kwds['xlabel'])
            else:
                ax2.set_xlabel('Cells')
            if kwds.has_key('ylabel'):
                ax2.set_ylabel(kwds['ylabel'])
            else:
                ax2.set_ylabel('Cells')

            if kwds.has_key('colorbar') and kwds['colorbar']==True:
                cbar2 = fig.colorbar(cax2)
                if kwds.has_key('colorbar_label'):
                    cbar.set_label(kwds['colorbar_label'])

        if kwds.has_key('show') and kwds['show'] == True:
            plt.show()  
        if kwds.has_key('savefig') and kwds['savefig'] == True:
            print "safe figure to file"
            if kwds.has_key('filename'):
                fig.savefig(kwds['filename'])
            else:
                fig.savefig('2D_property_plot.png')  
                
    def nu_eval_holzbecher_2d(self, **kwds):
        """calculate nusselt number at top boundary with simple assumption from Holzbecher,
        only valid for homogeneous thermal conductivity (?!?)
        this function works only for horizontal sections (in SHEMAT) with jdim=1
        optional kwds:
        estimation=[linear, quadradic, cubic]
        """
        # get temperatures
        # self.get_array_as_xyz_structure("TEMP")
        temp = self.get_array("TEMP")
        idim = int(self.get("IDIM"))
        kdim = int(self.get("KDIM"))
        delz = self.get_array("DELZ")
        delx = self.get_array("DELX")
        L = sum(delx)
        from numpy import array, reshape, shape
        # determine min and max temperatures
        t_min = min(temp)
        t_max = max(temp)
        z_max = sum(delz) - delz[len(delz)-1]
        # reshape temperature array
        try:
            temp_xz = array(temp).reshape(kdim,idim)# .transpose()
        except ValueError:
            print "Problem with array transpose in " + self.filename
            print "Skipping Nu-calculation, returns none"
            return None
        Nu_sum = 0
        n = 0
        def theta(t):
            """dimensionless temperature calculation"""
            return (t-t_min)/(t_max-t_min)
        if kwds.has_key('estimation'):
            if kwds['estimation'] == 'quadratic':
#                print "quadratic estimation"
                for i,t in enumerate(temp_xz[kdim-2][:]):    
                    t0 = theta(temp_xz[kdim-1][i])
                    t1 = theta(t)
                    t2 = theta(temp_xz[kdim-3][i])
                    # !!! Caution: added factor 1/3 to beginning! not in original formula of Holzbecher... check!!
                    dt_dz = 1./3. * 1 / delz[kdim-1] * z_max * (3*(t1-t0) - 1/3 * (t2-t0))
                    Nu_sum += dt_dz
                    n += 1
            if kwds['estimation'] == 'cubic':
#                print "cubic Nu estimation"
                for i,t in enumerate(temp_xz[kdim-2][:]):    
                    t0 = theta(temp_xz[kdim-1][i])
                    t1 = theta(t)
                    t2 = theta(temp_xz[kdim-3][i])
                    t3 = theta(temp_xz[kdim-4][i])
                    # !!! Caution: added factor 1/3 to beginning! not in original formula of Holzbecher... check!!
                    dt_dz = 1./3. * 1 / delz[kdim-1] * z_max * (15/4 *(t1-t0) - 5/6 * (t2-t0) + 3/20 * (t3-t0))
                    Nu_sum += dt_dz
                    n += 1
        else: # linear estimation
            for i,t in enumerate(temp_xz[kdim-2][:]):
                dt_dz = 1 / delz[kdim-1] * z_max * (theta(t)-theta(temp_xz[kdim-1][i]))
                Nu_sum += dt_dz
                n += 1
        N_sum = Nu_sum/n
        return Nu_sum / n
    
    def random_boundary_change_aniso(self, sigma_x, sigma_y, sigma_z, **kwds):
        """change boundaries by random value to test influence on numerical instabilities
        similar to self.random_boundary_change, but anisotropic changes possible
        optional kwds:
        max_diff = n % : maximal difference between two neigbouring cells in percent, e.g. 75% is reasonable
        two_d = True/False : for 2-D case (only x, z boundaries are changed)
        """
        self.get_cell_boundaries()
        from random import gauss
        # X-direction
        boundary_array = self.boundaries_x
        boundary_array_new = []
        boundary_array_new.append(boundary_array[0]) # start value
        for b in boundary_array[1:-1]: # exclude start and end value
            boundary_array_new.append(b+gauss(0,sigma_x))
        boundary_array_new.append(boundary_array[-1]) # end value
        self.boundaries_x = boundary_array_new
        # Y-direction, check for 2-D case!
        if kwds.has_key('two_d') and kwds['two_d'] == True:
            pass
        else:
            boundary_array = self.boundaries_y
            boundary_array_new = []
            boundary_array_new.append(boundary_array[0]) # start value
            for b in boundary_array[1:-1]: # exclude start and end value
                boundary_array_new.append(b+gauss(0,sigma_y))
            boundary_array_new.append(boundary_array[-1]) # end value
            self.boundaries_y = boundary_array_new
        # Z-direction
        boundary_array = self.boundaries_z
        boundary_array_new = []
        boundary_array_new.append(boundary_array[0]) # start value
        for b in boundary_array[1:-1]: # exclude start and end value
            boundary_array_new.append(b+gauss(0,sigma_z))
        boundary_array_new.append(boundary_array[-1]) # end value
        self.boundaries_z = boundary_array_new
        
    
    def random_boundary_change(self, sigma, **kwds):
        """change boundaries by random value to test influence on numerical instabilities
        optional kwds:
        max_diff = n % : maximal difference between two neigbouring cells in percent, e.g. 75% is reasonable
        two_d = True/False : for 2-D case (only x, z boundaries are changed)
        """
        # (re-)compute cell boundaries
        self.get_cell_boundaries()
        from random import gauss
        # X-direction
        boundary_array = self.boundaries_x
        boundary_array_new = []
        boundary_array_new.append(boundary_array[0]) # start value
        for b in boundary_array[1:-1]: # exclude start and end value
            boundary_array_new.append(b+gauss(0,sigma))
        boundary_array_new.append(boundary_array[-1]) # end value
        self.boundaries_x = boundary_array_new
        # Y-direction, check for 2-D case!
        if kwds.has_key('two_d') and kwds['two_d'] == True:
            pass
        else:
            boundary_array = self.boundaries_y
            boundary_array_new = []
            boundary_array_new.append(boundary_array[0]) # start value
            for b in boundary_array[1:-1]: # exclude start and end value
                boundary_array_new.append(b+gauss(0,sigma))
            boundary_array_new.append(boundary_array[-1]) # end value
            self.boundaries_y = boundary_array_new
        # Z-direction
        boundary_array = self.boundaries_z
        boundary_array_new = []
        boundary_array_new.append(boundary_array[0]) # start value
        for b in boundary_array[1:-1]: # exclude start and end value
            boundary_array_new.append(b+gauss(0,sigma))
        boundary_array_new.append(boundary_array[-1]) # end value
        self.boundaries_z = boundary_array_new
            
    def update_del(self):
        """update delimitor arrays DELX, DELY, DELZ if boundaries changed
        (e.g. with random change, ...)
        """
        # X
        del_array = []
        for i,step in enumerate(self.boundaries_x[1:]):
            del_array.append(step-self.boundaries_x[i])
        self.set_array("DELX", del_array)
        # Y
        del_array = []
        for i,step in enumerate(self.boundaries_y[1:]):
            del_array.append(step-self.boundaries_y[i])
        self.set_array("DELY", del_array)
        # Z
        del_array = []
        for i,step in enumerate(self.boundaries_z[1:]):
            del_array.append(step-self.boundaries_z[i])
        self.set_array("DELZ", del_array)
        

    def change_array_length(self, var_name, length):
        """change original array length to new length;
        *caution*: overwrites array and fills new array with value in first entry!!
        """
        value = self.get_array(var_name)[0]
        self.set_array(var_name, length * [value])
        return None

    def create_indicator_functions(self):
        """Indicator functions are defined at every voxet for each formation and = 1 if the formation
        exists at this voxet; They are essentially the same as the formation masks - method and variable name
        still included here for compatibility"""
        self.indicator_functions = self.create_formation_masks()
        

    def create_formation_masks(self):
        """create array masks for all geological units (from geology array) and store in self.formation_masks[id];
        also creates a list containing all formation ids of Shemat-file in self.formation_list
        """
        self.formation_list = []
        geology = self.get_array("GEOLOGY")
        # First: determine number and ids of formations
        for g in geology:
            if g not in self.formation_list:
                self.formation_list.append(int(g))
        # Now: create masks
        self.formation_masks = {}
        for f in self.formation_list:
            self.formation_masks[f] = [0 for x in geology]
        for i,g in enumerate(geology):
            self.formation_masks[int(g)][i] = 1
        return self.formation_masks

    def calc_block_volume(self):
        """compute the volume of each block (important for cases of non-regular meshes!)
        store and return as self.block_volume list
        Enables, for example, the simple calculation of the total formation volume in combination
        with self.formation_masks:
        volume_3 = sum(self.formation_masks[3] * self.block_volume)
        """
        idim = int(self.get("IDIM"))
        jdim = int(self.get("JDIM"))
        kdim = int(self.get("KDIM"))
        delx = self.get_array("DELX")
        dely = self.get_array("DELY")
        delz = self.get_array("DELZ")
        self.block_volume = [0 for x in range(idim * jdim * kdim)]
        i = 0
        for z in delz:
            for y in dely:
                for x in delx:
                    self.block_volume[i] = x * y * z
                    i += 1
        return self.block_volume

    def update_model_from_voxet_file(self, voxet_file, **kwds):
        """update shemat geology array from voxet file, exported with
        GeoModeller (Model -> Export)
        
        voxet_file = filename of voxet file
        
        optional kwds:
        dir = directory path to voxet file
        geomodel_properties = property_file : property file, as used in geomodeller2shemat
                to use identical identifiers"""
        if kwds.has_key('dir'):
            from os import chdir, getcwd
            oridir = getcwd()
            chdir(dir)
            
        """ create dictionary with geology identifyer ids for the SHEMAT file """
        geo_identifyer = {}
        if kwds.has_key('geomodel_properties') and kwds['geomodel_properties'] != "":
            # open csv file
            csv = open(kwds['geomodel_properties'],'r')
            csv_lines = csv.readlines()
            csv.close()
            csv_header = csv_lines[0].split(',')
            # remove end of line character from last entry
            csv_header[-1] = csv_header[-1].rstrip()
            # test if file contains another column (e.g. a 'Name' column) before GEOLOGY column
            if csv_header[1] == 'GEOLOGY':
                for line in csv_lines[1:]:
                    l = line.split(',')
                    geo_identifyer[l[0]] = l[1]
            else:
                print "Geology not defined in file " + kwds['geomodel_properties']
                print "Please check and try again!"
                raise AttributeError
            csv_datalines = []
            for i_csv,l in enumerate(csv_lines[1:]):
                pass
        else:
            """simply enumerate for values in voxet data file"""
            print "NOT IMPLEMENTED YET!"
            raise AttributeError
        
        from read_gradient_data_5 import Gradient_data
        G1 = Gradient_data(voxet_file)
        G1.read_data_nodes_1D()
        geo_new = [] # new geology array
        n_cells = int(G1.h['nx']) * int(G1.h['ny']) * int(G1.h['nz'])
        for i in range(n_cells):
            print "process cell %8d of %d, %4.1f Percent" % (i, n_cells, (float(i)/float(n_cells)*100))
            geo_new.append(int(geo_identifyer[G1.forms_1D[i]]))
            i += 1
        self.set_array("GEOLOGY", geo_new)                        
        if kwds.has_key('dir'):
            """ change back to original directory """
            chdir(oridir)
            
    def get_cell_pos(self,x,y,z):
        """get array position of cell that contains the coordinate x,y,z
        (in real world coordinates"""
        pass
        
        
    def interpolate_values_on_xy_grid(self, x_coords, y_coords, z_values, **kwds):
        """interpolate values on a regular grid with delauny triangulation,
        for example to enable a lateral change of porosity values
        (can then be assigned to one formation) or to interpolate surface
        temperature variations (can then be used as initial temperature condition);
        x_coords = 1D-array : coordinate values in x-direction
        y_coords = 1D-array : coordinate values in y-direction
        z_values = 1D-array : values to be interpolated
        returns an array with interpolated values, similar to mean temperature and
        extracted model slice, that can then be used to plot and further processing
        of the data;
        optional keywords:
        relative = True/False : relative to model origin (not in real-world coordinates)"""
        try:
            self.origin_z
        except AttributeError:
            self.get_model_origin()
        try:
            self.extent_x
        except AttributeError:
            self.get_model_extent()
            
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_x = 0
            origin_y = 0
        else:
            origin_x = self.origin_x
            origin_y = self.origin_y
        
        import numpy as np
        import matplotlib.mlab as mlab

        # generate regular grid to interpolate data
        xmin, xmax = origin_x, origin_x + self.extent_x
        ymin, ymax = origin_y, origin_y + self.extent_y
        xi = np.linspace(xmin, xmax, self.idim)
        yi = np.linspace(ymin, ymax, self.jdim)
        xi, yi = np.meshgrid(xi, yi)
        
        # Interpolate with delauny triangulation
        zi = mlab.griddata(x_coords,y_coords,z_values,xi,yi)
        # plot results: can be used to test method
#        import matplotlib.pyplot as plt
#        plt.figure()
#        plt.pcolormesh(xi,yi,zi)
#        plt.axis([xmin, xmax, ymin, ymax])
#        plt.colorbar()
#        plt.show()
        from scipy import ravel
        zi = ravel(zi)
        return zi
        
    def assign_xy_values_from_grid(self, grid_xy, property, **kwds):
        """Initiate temperature with values from a temperature grid, e.g.:
        from interpolated surface temperature values, with
        self.interpolate_values_on_xy_grid;
        can be assigned for the whole model, e.g. to initiate temperature values
        from a grid to all x,y coordinates, or for one property zone only, e.g.
        to allow lateral changes of porosity, etc.
        arguments:
        grid_xy = 1-D array with grid values, for example created with 
            self.interpolate_values_on_xy_grid
        property = SHEMAT variable name, e.g. "TEMP": variable to assign interpolated values
        optional keywords:
        formation_id = int : formation id for which assignment should be performed
        """
        
        # idea: for formation id assignment: use formation masks, as used for mean temp
        # calculations, etc.
        
#        # get values in xyz format
#        property_xyz = self.get_value_xyz(property)
        
        property_new = []
        for z in range(self.kdim):
            i = 0 # assign same property values to all z values
            for y in range(self.jdim):
                for x in range(self.idim):
                    property_new.append(grid_xy[i])
                    i += 1
        
        if kwds.has_key('formation_id'):
            try:
                self.formation_masks[kwds['formation_id']]
            except AttributeError:
                self.create_formation_masks()
            # assign values to grid; this method is pretty bulky,
            # I am sure it could be done more elegangtly...
            property_updated = self.get_array(property)
            for i,m in enumerate(self.formation_masks[kwds['formation_id']]):
                if m == 1:
                    property_updated[i] = property_new[i]
            self.set_array(property, property_updated)
        else: # assign to all formations, i.e. the whole model!
            self.set_array(property, property_new)
        
    def fix_const_bc_for_one_formation(self,bc_type,formation_id):
        """fix constant value boundary condition for one formation, e.g.
        to assign a fixed temperature to all values above topography, in the
        "Air"-formation;
        bc_type = 'Temp','Head','Conc' : type of BC
        formation_id = int : formation identifyer
        """
        try:
            self.formation_masks[formation_id]
        except AttributeError:
            self.create_formation_masks()
        try:
            self.diri_temp
        except AttributeError:
            self.get_bcs()
        if bc_type == 'Temp' or bc_type == 'temp': # assign to temperature BC
            # fixed temp BC are assigned as negative POR values
            # porosity data has to be loaded and reassigned for correct BC definition
            por = self.get_array("POR")
            for i,m in enumerate(self.formation_masks[formation_id]):
                if m == 1:
                    self.diri_temp[i] = True
#                    if por[i] < 0:
#                        pass # in this case: BC already fixed!
#                    else:
#                        por[i] = - por[i]
#                else:
#                    por_new[i] = por[i]
            # assign back to shemat object
            # BC definition is now updated in self.diri_temp and can now
            # be reassinged to Porosity values
            self.set_array("POR", por)
        elif bc_type == 'Head' or bc_type == 'head':
            # head: neagitve PERM values
            print "Fixed head not yet implemented"
        elif bc_type == 'Conc' or bc_type == 'conc':
            # conc: negative PRES values
            pass
        else:
            print "Boundary condition type " + type + " not recognized!"
            raise ValueError
        
    def assign_temperatures_function(self, a, b, **kwds):
        """Assign initial temperatures as a linear function of 
        altitude; function: ax + b
        a = float : gradient
        b = float : y-axis intercept
        assigns all valus to initial temperatures; "Air"-values can then
        be fixed with self.fix_const_bc_for_one_formation
        optional keywords:
        min_alt = float : minimum altitude to assign temperature function
        relative = float : calculate values relative to model origin (in model
                    coordinate system)
        """
        try:
            self.origin_z
        except AttributeError:
            self.get_model_origin()
        try:
            self.centre_z
        except AttributeError:
            self.get_cell_centres()
        
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_z = 0
        else:
            origin_z = self.origin_z

        temp_xyz = self.get_array_as_xyz_structure("# TEMP")

        for k,z_val in enumerate(self.centre_z):
            # check for minimal altitude contidtion
            z_real = z_val + origin_z
            print z_real
            if kwds.has_key('min_alt'):
                if z_real < kwds['min_alt']:
                    continue
            # estimate temperature at altitude
            temp = a * z_real + b
            # assing temperature value to all cells in x,y-plane
                        
            for j in range(self.jdim):
                for i in range(self.idim):
                    temp_xyz[i][j][k] = temp
        
        # assign temperature values back to nml file
        self.set_array_from_xyz_structure("# TEMP", temp_xyz)
    
    def assign_new_unit_to_layers(self,n_layers,start=0):
        """assign a new geological unit to one or more layers, e.g. to create a 
        thermal equilibrium layer at the bottom of the model;
        start = int : start from this layer, default=0: at bottom of model
        n_layers = int : number of layers with new geological unit
        """
        try:
            self.idim
        except AttributeError:
            self.idim = self.get("IDIM")
            self.jdim = self.get("JDIM")
            self.kdim = self.get("KDIM")
        layer_n = int(self.idim) * int(self.jdim)
        total_n = layer_n * n_layers # total number of nodes to be changed
        # get geology array and determine max unit id
        try:
            self.formation_ids
        except AttributeError:
            self.create_formations_ids()
        geol = self.get_array("GEOLOGY")       
        
        for i in range(total_n):
            geol[i+start*layer_n] = max(self.formation_ids) + 1
        
        self.set_array("GEOLOGY", geol)   
        

    def assing_thermal_equil_layers(self,n,**kwds):
        """assing layers with high lateral thermal conductivity at base of
        model to allow for lateral equilibration of thermal heat flux;
        values for WLXANI and WLYANI are set to very high values;
        n = int : number of layers with high anisotropy
        optional keywords:
        aniso_val = float : value of anisotropy; default: 999.
        """
        wlxani = self.get_array("WLXANI")
        wlxanj = self.get_array("WLYANI")
        if kwds.has_key('aniso_val'):
            aniso_val = kwds['aniso_val']
        else:
            aniso_val = 999 # anisotropy multiplier
        try:
            self.idim
        except AttributeError:
            self.idim = self.get("IDIM")
            self.jdim = self.get("JDIM")
            self.kdim = self.get("KDIM")
        total_n = int(self.idim) * int(self.jdim) * n # total number of nodes to be changed
        
        for i in range(total_n):
            wlxani[i] = aniso_val
            wlxanj[i] = aniso_val
        
        # store back in object variables
        self.set_array("# WLXANI", wlxani)
        self.set_array("# WLYANI", wlxanj)

    
    def grid_2D_to_ASCII_grid(self,property_xy, **kwds):
        """save a 2-D grid array, e.g. calculated mean temperature or
        isopach maps, to an ASCII grid file;
        returns ASCII grid object
        Attention: works only for regular (x,y) grids (due to limitations of
        ASCII grid file definition);
        property_xy = list : (1-D) list with grid values, e.g. created
                            with self.calc_mean_formation_value
        ascii_filename = string : filename of ASCII grid file (without path)
        optional keywords:
        dir = directory path to store file
        """
        from PyASCII import ASCII_File
        
        # write properties to ASCII grid
        A2 = ASCII_File()
        A2.convert_SHEMAT_results_to_header(self, property_xy)
        return A2

    def export_to_voxet_object(self, property):
        """export a property/ variable of the SHEMAT input or output
        file into a voxet object"""
        from voxet_object_2 import Voxet
        V1 = Voxet()
#        V1.set_nodes(int(self.get("IDIM")), int(self.get("JDIM")), int(self.get("KDIM")))
        V1.set_spacing(self.get_array("DELX"), self.get_array("DELY"), self.get_array("DELZ"))
        V1.set_scalar_values_list(self.get_array(property))
        V1.set_scalar_name(property)
        return V1
        

# ********************************************************************

#     End of Shemat_file class definition       

# ********************************************************************


def execute_shemat(**kwds):
    """call shemat on system side and process converted file
    optional keywords:
    dir = dirpath : directory where shemat is executed
    
    Note: function determines operating system (NT or Linux/Mac) but program
    names are hardcoded and might have to be adapted    
    """
    from os import system, execvp, waitpid, popen, chdir, getcwd, name
    # from subprocess import Popen,call,check_call
    if kwds.has_key('dir'):
        from os import chdir, getcwd
        ori_dir = getcwd()
        chdir(kwds['dir'])
    # 
    # Determine operating system and handle appropriately
    #
    if name == 'nt':
        import win32pipe
        return win32pipe.popen("shemat").readlines()
    if name == 'posix' or name == 'mac':
        import subprocess
        subprocess.popen("shemat64int.x").readlines()
    # return process.stdout.readlines()
    # return to original directory
    if kwds.has_key('dir'):
        chdir(ori_dir)


def create_nml_dir(**kwds):
    """create directory to store new .nml and .ctl files, 
    default: .\nml_run_n
    n is automatically asigned as continuous numbers, starting with "1"
    but can also be manually set with kwds: dir = str
    optional kwds:
    basename = string : basename of directory, number added
    n_format = int : number of integers (for %0nd format description)
    """
    from os import chdir, path, mkdir, getcwd
    if kwds.has_key(dir):
        mkdir(dir)
    else:
        if kwds.has_key('basename'):
            basename = kwds['basename']
        else:
            basename = 'nml_run'
        for n in range(1,100000): # sets a maximum of 100 result directories...
            if not path.isdir(path.join(".","%s_%02d" % (basename,n))):
                print "create results directory %s\\%s_%02d" % (getcwd(), basename, n)
                resultsdir = path.join(".","%s_%02d" % (basename, n))
                mkdir(resultsdir)
                break
    return resultsdir


def create_shemat_control_file(filename, **kwds):
    """create shemat.ctl file that is needed to run shemat
    optinal kwds:
    dir = dirpath : directory where file is created
    """
    if filename[-3:] == 'nml':
        filename = filename[:-4]
    if kwds.has_key('dir'):
        from os import chdir, getcwd
        ori_dir = getcwd()
        chdir(kwds['dir'])
    ctl_file = open("shemat.ctl", "w")
    text1 = """# SHEMAT Control File (Created with Geomodeller2Shemat)
# Version 8.0 of DEZ 2005
#Insert name of default file here (of type 2):
"""
    text2 = """
#Project:
#
#   Type:                   Number:   Suffix:
#   old formated type          1        .dat
#   old type with NAMELIST     2        .nml
#     Type 2 is not surported any more.
#   new type with NAMELIST     3        .nml
#Insert name of project and type here:
"""
    text3 = """ 3
# (The correct suffix will be added.)"""
    text = text1 + filename + ".nml\n" + text2 + filename + text3
    ctl_file.write(text)
    ctl_file.close()
    # return to original directory
    if kwds.has_key('dir'):
        chdir(ori_dir)

def create_jobscript_multiple_nmls(nml_files):
    """create a TORQUE/PBS jobscript to run the shemat simulation on XE
    Concept:
    - this function is designed to create one jobscript for multiple processes
    on XE
    - from one basedir (which is included as a bash variable and can be changed later),
    processes are called in subdirectories
    arguments:
    nml_files = list of filenames, path reference to basedir
    optional keywords:
    walltime = hh:mm:ss : requested walltime for process
    cpus = n : number of cpus requested
    basedir = directory path : path on XE where nml-files/ directories are placed
    To Do: include moving job (or write other jobscript?) to move results directly
    to pbstore after job execution
    move_to_pbstore
    pbstore_dir
    """
    # check if correct function call!
    if type(nml_files) != list:
        print "Please pass nml-files in list!"
        print "No jobfile created"
        return None
    # write basic jobscript structure
    print "\n\n\n" + 80 * "!"
    print "Jobscript creation not yet implemented!"
    print 80 * "!"
    for nml_file in nml_files:
        pass
    
def create_jobscript(**kwds):
    """create a TORQUE/PBS jobscript for one
    nml simulation;
    optional keywords:
    name = string : simulation identifyer
    mail = string with mail address : send mail to this address when simulation finished
    ncpus = int : number of cpus for simulation (default: 4)
    vmem = int : number of GB for simulation run (default: 4)
    walltime = hh:mm:ss : requested simulation walltime (default: 00:30:00)
    job_filename = string : filename of jobscript (default: shemat_job)
    steady_state_init = True/ False : run as steady state first, then
        adapt .nlo file and run as transient simulation
    """
    if kwds.has_key('name'):
        name = kwds['name']
    else:
        name = "Shemat_Simulation"
    if kwds.has_key('ncpus'):
        ncpus = kwds['ncpus']
    else:
        ncpus = 4
    if kwds.has_key('vmem'):
        vmem = kwds['vmem']
    else:
        vmem = 4
    if kwds.has_key('walltime'):
        walltime = kwds['walltime']
    else:
        walltime = "00:30:00"
    if kwds.has_key('job_filename'):
        job_filename = kwds['job_filename']
    else:
        job_filename = 'job_shemat'
    # now: create single textblocks based on template jobscript
    text1 = """ #!/bin/bash
#
# Jobscript for Shemat simulation: """ + name + """
#
#PBS -N """ + name
    # check if mail defined
    if kwds.has_key('mail'):
        text2 = """
#PBS -m e
#PBS -M """ + kwds['mail']
    else:
        text2 = ""
    text3 = """
#PBS -q normal
#PBS -l ncpus=""" + str(ncpus) + """,vmem=""" + str(vmem) + """GB,walltime=""" + walltime + """

# use $PBS_O_WORKDIR to use directory from which job was called
cd $PBS_O_WORKDIR
echo "Shemat Simulation"

echo
echo "Environment variables"
echo
printenv

echo
echo "Starting time:" > time.txt
date >> time.txt
START=$(date +%s)

# run Shemat simulation
~/bin/shemat64int.x
"""
    if kwds.has_key("steady_state_init") and kwds['steady_state_init']:
        text4 = """
echo
echo "Adapt values in results file"
python stat_to_inst.py

echo "Run transient simulation"
~/bin/shemat64int.x"""
    else: text4 = ""
    text5 = """
echo "Simulation finished:" >> time.txt
echo
echo "Sort and zip resultfiles"
# Sort and zip results

# $HOME/scripts/zip_vtk_nlo_files.bsh

# Calculate time difference
date >> time.txt
END=$(date +%s)
DIFF=$(( $END - $START ))

echo "Total simulation time [s]: $DIFF" >> time.txt
"""
    # now: save jobscript to file
    f = open(job_filename, 'w')
    f.write(text1 + text2 + text3 + text4 + text5)
    f.close()
