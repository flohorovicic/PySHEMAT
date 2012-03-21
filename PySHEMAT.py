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

If you use PySHEMAT for a scientific study, please cite our publication in Computers and Geoscience:
J. Florian Wellmann, Adrian Croucher, Klaus Regenauer-Lieb, Python scripting libraries for subsurface fluid and heat flow simulations with TOUGH2 and SHEMAT, Computers & Geosciences, 
Available online 21 October 2011, ISSN 0098-3004, 10.1016/j.cageo.2011.10.011.

"""

import re # for regular expression fit, neccessary for stupid nlo files
from matplotlib import use
use("Agg")
import matplotlib as m

class Shemat_file:
    """Class for SHEMAT simulation input and output files
    
    Object definition for SHEMAT simulation files. The Object
    can be used for simulation input files (.nml) and output files (.nlo).
    Object methods enable a direct access of all variables and parameters
    defined in the input file. Further methods are available for a
    simplified generation of result plots in 2-D sections and to export simulation
    results in a variety of different formats.

   **Arguments**:
        - *new_filename* = string: filename in case an empty file is created
    
    **Optional keywords**:
        - *offscreen* = True/False: set variables for offscreen rendering, e.g. to create plots on
            a remote machine via ssh     
    """
    # class needed? maybe good as a "containter -> might be good
    # to assure compatibility with future versions...
    def __init__(self, filename='', **kwds):
        """Initialization of SHEMAT object
        
        **Arguments**:
            - *new_filename* = string: filename in case an empty file is created
        
        **Optional keywords**:
            - *offscreen* = True/False: set variables for offscreen rendering, e.g. to create plots on
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
        """Open and read a SHEMAT .nml or .nlo file
        
        **Arguments**:
            - *filename* = string: filename

        **Returns**:
            List of lines in the file
        """
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
        """Write SHEMAT object to file
        
       **Arguments**:
            - *filename* = string: filename of SHEMAT file (extension .nml is
            automatically assigned if not given)
        """
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
        """Adjust an existing SHEMAT control file with a new filename
        
        SHEMAT control files (.ctl) are required to run a SHEMAT simulation
        from the command line. This function changes the filename settings
        within a control file in the current directory from old_filename to 
        new_filename.
        
        **Arguments**:
            - *old_filename* = string: filename of original SHEMAT file in directory
            - *new_filename* = string: filename of new SHEMAT file
        
        **Optional keywords**:
            - *backup* = False/ True: create shemat_ctl.bak backup file, default true
            - *ctl_filename* = "shemat.ctl" : set other ctl filename
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
        """Determine coupling settings
        
        Read coupling information out of variable KOPLNG and
        dechipher.
        
        **Returns**:
            String with clear text about coupling settings"""
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
        """Determine status of fixed parameters and return as string
        
        **Returns**:
            String with clear text about fixed parameters
        """
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
        """Get the value of a scalar variable
        
        Determines the value of a scalar variable in the SHEMAT object
        
        **Arguments**:
            - *var_name* = string : Name of scalar variable
            
        **Optional keywords**:
            - *line* = int : Number of lines for multiline variables
            
        **Returns**:
            String with variable    
        """
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                if line == 1:
                    return self.filelines[i+1]
                    break
                else:
                    lines = []
                    for j in range(line):
                        lines.append(self.filelines[i+1])
                    return lines
                    break

        
    def get_array(self, var_name):
        """Get the value of an array variable
        
        Array variables (e.g. temperature, pressure, etc.) in SHEMAT are stored
        in 1-D arrays in a compressed format. With this method, the variables
        are decompressed and returned as a 1-D list. The method also adjusts
        special boundary condition settings which are partly implemented as
        negative values of pressure, porosity and permeability.

        **Arguments**:
            - *var_name* = string : Name of scalar variable
            
        **Returns**:
            - 1-D list with values
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
                            print "Problem with value, probably empty string: " + d
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
        """Determine the boundary conditions and return as 1-D list
        
        Dirichlet boundary conditions are stored in a .nml file as:
        - conc: negative PRES values
        - temp: negative POR values
        - head: neagitve PERM values
        
        With this method, boundary conditions are evaluated and stored in
        object variables self.diri_temp, self.diri_conc, and self.diri_head"""
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
        """Set a SHEMAT variable to a specific value
        
        **Arguments**:
            - *var_name* = string : name of the SHEMAT variable
            - *value* = string or number : variable value"""
        for (i,l) in enumerate(self.filelines):
            if var_name in l:
                self.filelines[i+line] = str(value) + "\n"

    def set_array(self, var_name, value_list, **kwds):
        """Set a SHEMAT array variable to values in a 1-D list
        
        Set variable 'var_name' with values in 'value_list' in .nml_file;
        mulitpliers "*" are constructed (as used in Shemat .nml file).
        The SHEMAT boundary condition definitions are considered:
        - self.diri_conc: Dirichlet BC for concentration => PRES neg
        - self.diri_temp: Dirichlet BC for temperature => POR neg
        - self.diri_head: Dirichlet BC for hydr head => PERM neg
        these object variables/ local variables are automatically
        set if PERM, POR or PRES are set
        
        **Arguments**:
            - *var_name* = string : Name of SHEMAT variable
            - *value_list* = 1-D list of strings or numbers : Values
        
        **Optional keywords**:
            - float_type = 'high_res', 'normal' : precision of floating point; normal: 2 digits only                 
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
        """Set a SHEMAT variable from a 3-D list of values
        
        Set variable 'var_name' with values in 'xyz_structure_list' in .nml_file;
        xyz_structure_list can be one of those derived from get_array_as_xyz_structure
        mulitpliers "*" are constructed (as used in Shemat .nml file)
        The SHEMAT boundary condition definitions are considered:
        - self.diri_conc: Dirichlet BC for concentration => PRES neg
        - self.diri_temp: Dirichlet BC for temperature => POR neg
        - self.diri_head: Dirichlet BC for hydr head => PERM neg
        these object variables/ local variables are automatically
        set if PERM, POR or PRES are set.
                
        **Arguments**:
            - *var_name* = string : Name of SHEMAT variable
            - *value_list* = 1-D list of strings or numbers : Values
        
        **Optional keywords**:
            - float_type = 'high_res', 'normal' : precision of floating point; normal: 2 digits only                 
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
        """restructure array into x,y,z 3-D structure as data[i][j][k]
        
        i,j,k are counters in x,y,z-direction, determined from the object itself
        
        **Arguments**:
            - *array* = list or array to be restructured
        
        **Returns**:
            Restructured 3-D list of data values
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
        """restructure array into x,y,z 3-D structure as data[i][j][k]
        
        with i,j,k: counters in x,y,z direction
        
        **Arguments**:
            - *array*: array to be restructured
            - *idim* = int : dimension of new array in x-direction (default: model dimensions)
            - *jdim* = int : dimension of new array in y-dircetion
            - *kdim* = int : dimension of new array in z-direction

        **Returns**:
            Restructured 3-D list of data values
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
        """Calculate centre of cells in absolute values
        
        Cell centres are stored in object variables
        
        self.centre_x, self.centre_y, self.centre_z
        """
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
        """Determine the model geology from a geological model created with GeoModeller
        
        With this method, it is possible to map the distribution of geological units
        from a 3-D geological model, created with GeoModeller, on the mesh used 
        in the SHEMAT simulation. This is here done with a direct dll access to read 
        the geology data into shemat object.
        
        .. warning: directory path to GeoModeller bin directory has to be adjusted in code!
        
        **Arguments**:
            - *geomodeller_xml_file* = string : XML file of GeoModeller project
        
        **Optional keywords**:
            - *compute* = True/False: (re-) compute geological model before processing
            - *lower_left_x* = float : x-position of lower-left corner (default: model range)
            - *lower_left_y* = float : y-position of lower-left corner (default: model range)
            - *lower_left_z* = float : z-position of lower-left corner (default: model range)
        
        .. note: for more information on GeoModeller see the `GeoModeller page <http:www.geomodeller.com\>`_
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
        """Caluclate the mean temperature for one formation at each location
        
        Mean temperatures in z-direction are calculated at every location (x,y) for
        a specified geological formation, for example to create a map of mean temperatures
        
        **Arguments**:
            - *formation_id* = string : corresponding to the property id in Shemat/ Geology Variable
        **Returns**:
            - *mean_temp* = 1-D list of mean temperatures (array with 2-D grid values in 1-D structure)
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
        """Calculate the mean value of one property
        
        Calculate the mean value for one SHEMAT property, location based, i.e. the
        mean value in z-direction at every location (x,y); similar to
        self.calc_mean_formation_value but without formation separation;
        Can, for example, be used to calculate mean temperatures at each
        location with
        
        mean_temp = S1.calc_global_mean_value("TEMP")
        
        **Arguments**:
            - *property* = string : Name of SHEMAT property/ variable
            
        **Returns**:
            - *mean_value* = list : 1-D list of mean values at each location (x,y)
        """
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
        """Add a random vaule to a property, based on geology identifyer
        
        Function can be used to randomize properties, e.g. permeability: a random
        value is added (or substracted) to every *cell*, for a defined geological 
        formation; 
        
        *note*: this function adds a value to each cell, not to the
        value mapped to each formation! Therefore, the internal structure within
        one formation is randomized.
        
        **Arguments**:
            - formation_id = int : formation/ geology identifyer
            - property = string : SHEMAT property/ variable (e.g. "PERM")
        
        **Optional Keywords**:
            - type = (gaussian, log, one_over_f, ...) : statistics
            - sigma = float : standard deviation for the case of gaussian statistics
        
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
        """Calculate the mean value for one property in z-direction for one formation
        
        The mean value for one property in z-direction is calculated at every
        location (x,y) in the SHEMAT mesh for one specified formation;
        
        **Arguments**:
            - *formation_id* = int : corresponding to the property id in Shemat/ Geology Variable
            - *property* = sring : can be any of the properties/ variables  in the SHEMAT nml/nlo files, e.g.: DICHTE, PERM, POR
        
        **Returns**:
            *mean_value* = 1-D list of mean values at every location
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
        """Calculate isopach map for one formation, based on discretization
        
        Calculate an isopach map for a formation based on the discretization
        in the simulation at all locations
        
        **Arguments**:
            - *formation_id* = int : corresponding to the property id in Shemat/ Geology Variable
        
        **Returns**:
            *isopach_xy[n]* = list : 1D list of isopach values
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
        """Calculate the transmissivity at every location for one formation/ aquifer

        **Arguments**:
            - *formation_id* = string : corresponding to the property id in Shemat/ Geology Variable
        
        **Returns**:
            - *transmissivity_xy* = 1-D list of transmissivity values for each location
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
        self.origin_x = float(raw_input("Model origin, x : "))
        self.origin_y = float(raw_input("Model origin, y : "))
        self.origin_z = float(raw_input("Model origin, z : "))

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
    
    def get_array_pos_xyz(self,x,y,z,**kwds):
        """Determine the array position of a real-world coordinate value
        
        The function determines the position in the SHEMAT 1-D arrays of a 
        coordinate value, given as (x,y,z) real-world coordinates; function
        can be used to search for a several values first, and then load the
        data arrays and determine values for all positions at once to speed up
        search (originally programmed to speed-up calibration with multiple
        wells).
        
        **Arguments**:
             - *x,y,z* = floats : position of values

        **Optional Keywords**:
            - *relative* = True/ False: relative to model origin (i.e.: not in real-world
            coordinates).
            - *check_out_of_bounds* = True/ False: check if point is actually within model range
            (otherwise, wrong results might be obtained or the method can crash). The check
            can be deactivated to speed up calculation. Default: check is performed!
            - *three-d* = True/ False: return a tuple of positions in i,j,k coordinates, i.e.
            the array position in 3-D as (i,j,k).

        **Returns**:
             integer of array position corresponding to value
        """
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_x = 0
            origin_y = 0
            origin_z = 0
        else:
            try:
                self.origin_z
            except AttributeError:
                self.get_model_origin()
            origin_x = self.origin_x
            origin_y = self.origin_y
            origin_z = self.origin_z

        if kwds.has_key('check_out_of_bounds') and kwds['check_out_of_bounds'] == False:
            pass
        else:
            # default: perform check
            # first: check if value is smaller than origin
            if x < origin_x:
                print "Position %s is out of bounds for direction x (min: %.2f)" % (x, origin_x)
                raise ValueError
            if y < origin_y:
                print "Position %s is out of bounds for direction y (min: %.2f)" % (x, origin_x)
                raise ValueError
            if z < origin_z:
                print "Position %s is out of bounds for direction z (min: %.2f)" % (x, origin_x)
                raise ValueError
                
            
            try:
                self.boundaries_x
            except AttributeError:
                self.get_cell_boundaries()
    
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
            if kwds.has_key("three_d") and kwds['three_d'] == True:
                return (x_pos,y_pos,z_pos)
            else:
                return x_pos + self.idim * y_pos + self.idim * self.jdim * z_pos
    
    def get_value_xyz(self,property,x,y,z,interpolate=True,**kwds):
        """Get the (interpolated )value of the property at real-world position
        
        Determine the value of a property at a position (x,y,z) in the model. The
        value is interpolated from the surrounding grid cell centers with a simple
        trilinear interpolation method. If the argument interpolate is set to False,
        the value of the grid cell in which the position falls is returned. Requires
        the origin of the model defined (self.set_origin).
        
        **Arguments**:
            - *property* = string : SHEMAT property variable name, e.g. TEMP for temperature
            - *x,y,z* = floats : position of values
            - *interpolate* = True/ False: approximate true value at position x,y,z (*not* the value of the cell!)
            through trilinear interpolation
        
        **Optional Keywords**:
            - *relative* = True/ False: relative to model origin (i.e.: not in real-world
            coordinates).
            - *check_out_of_bounds* = True/ False: check if point is actually within model range
            (otherwise, wrong results might be obtained or the method can crash). The check
            can be deactivated to speed up calculation. Default: check is performed!
            
        **Returns**:
            Variable value at x,y,z (float)
        """
        
        if kwds.has_key('relative') and kwds['relative']:
            # get value relative to model origin, not in real-world coordinates!
            origin_x = 0
            origin_y = 0
            origin_z = 0
        else:
            try:
                self.origin_z
            except AttributeError:
                self.get_model_origin()
            origin_x = self.origin_x
            origin_y = self.origin_y
            origin_z = self.origin_z

        if kwds.has_key('check_out_of_bounds') and kwds['check_out_of_bounds'] == False:
            pass
        else:
            # default: perform check
            # first: check if value is smaller than origin
            if x < origin_x:
                print "Position %s is out of bounds for direction x (min: %.2f)" % (x, origin_x)
                raise ValueError
            if y < origin_y:
                print "Position %s is out of bounds for direction y (min: %.2f)" % (x, origin_x)
                raise ValueError
            if z < origin_z:
                print "Position %s is out of bounds for direction z (min: %.2f)" % (x, origin_x)
                raise ValueError
                
            
            try:
                self.boundaries_x
            except AttributeError:
                self.get_cell_boundaries()
    
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

        
        if interpolate==False: # simply use value of box that contains point
            property_xyz = self.get_array_as_xyz_structure(property)
            return property_xyz[x_pos][y_pos][z_pos]
        else: # interpolate between adjacent values
            # determine position of cell centers (not boundaries as for the case above!)
            
            # Use cell centers for interpolation
            try:
                self.centre_z
            except AttributeError:
                self.get_cell_centres()

            
            for i,x_bound in enumerate(self.centre_x):
                if (x - origin_x) > self.centre_x[-1]:
                    print "Position %s is out of bounds for direction x (max: %.2f)" % (x, self.boundaries_x[-1]+origin_x)
                    raise ValueError
                if x_bound >= (x - origin_x): 
                    i = i-1 # array position corresponds to cell centre of cell before boundary!
                    break
            for j,y_bound in enumerate(self.centre_y):
                if (y - origin_y) > self.centre_y[-1]:
                    print "Position %s is out of bounds for direction y (max: %.2f)" % (y, self.boundaries_y[-1]+origin_y)
                    raise ValueError
                if y_bound >= (y - origin_y): 
                    j = j-1 # array position corresponds to cell centre of cell before boundary!
                    break
            for k,z_bound in enumerate(self.centre_z):
                if (z - origin_z) > self.centre_z[-1]:
                    print "Position %s is out of bounds for direction z (max: %.2f)" % (z, self.boundaries_z[-1]+origin_z)
                    raise ValueError
                if z_bound >= (z - origin_z): 
                    k = k-1 # array position corresponds to cell centre of cell before boundary!
                    break
            
            # Get data
            prop = self.get_array(property)
            
            # interpolate values in x-direction for all surrounding cell centers (from volumes to plane)
            p_x1 = (prop[self.ap(i+1,j,k)] - prop[self.ap(i,j,k)]) / (self.centre_x[i+1]-self.centre_x[i]) \
                    * ((x - origin_x) - self.centre_x[i]) + prop[self.ap(i,j,k)]
            p_x2 = (prop[self.ap(i+1,j+1,k)] - prop[self.ap(i,j+1,k)]) / (self.centre_x[i+1]-self.centre_x[i]) \
                    * ((x - origin_x) - self.centre_x[i]) + prop[self.ap(i,j+1,k)]
            p_x3 = (prop[self.ap(i+1,j,k+1)] - prop[self.ap(i,j,k+1)]) / (self.centre_x[i+1]-self.centre_x[i]) \
                    * ((x - origin_x) - self.centre_x[i]) + prop[self.ap(i,j,k+1)]
            p_x4 = (prop[self.ap(i+1,j+1,k+1)] - prop[self.ap(i,j+1,k+1)]) / (self.centre_x[i+1]-self.centre_x[i]) \
                    * ((x - origin_x) - self.centre_x[i]) + prop[self.ap(i,j+1,k+1)]
            # now interpolate between these values in y - direction (from plane to line)
            p_y1 = (p_x2 - p_x1) / (self.centre_y[j+1] - self.centre_y[j]) \
                    * ((y - origin_y) - self.centre_y[j]) + p_x1
            p_y2 = (p_x4 - p_x3) / (self.centre_y[j+1] - self.centre_y[j]) \
                    * ((y - origin_y) - self.centre_y[j]) + p_x3
            # now interpolate in z-direction (from line to point)
            p_z = (p_y2 - p_y1) / (self.centre_z[k+1] - self.centre_z[k]) \
                    * ((z - origin_z) - self.centre_z[k]) + p_y1
            
            return p_z
            
    def ap(self,i,j,k):
        """Shorthand for self.determine_array_pos(i,j,k)"""
        return self.determine_array_pos(i,j,k)
            
    def determine_array_pos(self,i,j,k):
        """Determine the position of an element in property array
        
        ..Note: deprecated function, use self.get_array_pos_ijk() instead!!
        
        The SHEMAT properties are stored in 1-D array structures, in
        x-, y-, z-dominance. This function determines the corresponding
        position of an element in the 1-D array from the grid coordinate
        position (i,j,k) and the number of cells in each direction.
        
        **Arguments**:
            - *i,j,k* = int : grid coordinate position of cell
            
        **Returns**:
            i = int : corresponding position in 1-D array
        """
        return i + self.idim * j + self.idim * self.jdim * k
                
    def get_array_pos_ijk(self,i,j,k):
        """Determine the position of an element in property array
        
        The SHEMAT properties are stored in 1-D array structures, in
        x-, y-, z-dominance. This function determines the corresponding
        position of an element in the 1-D array from the grid coordinate
        position (i,j,k) and the number of cells in each direction.
        
        **Arguments**:
            - *i,j,k* = int : grid coordinate position of cell
            
        **Returns**:
            i = int : corresponding position in 1-D array
        """
        return i + self.idim * j + self.idim * self.jdim * k
        

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
        """Create a 2-D map/ (x,y) plot of a property
        
        Function to create a plot of a 2.5-D property that has been calculated with
        some other function, for example the mean temperature in a formation, calculated
        with S1.calc_mean_formation_value(4,"TEMP"); The "property" is a 1-D list,
        as returned by the standard methods of this object for these types of 2.5-D structures;
        The correct reformating into a (x,y) field is done within this method.

        Two plots are created with the standard settings: left image with the raw data,
        the original cell structure is visible; right image: interpolated data

        ATTENTION: uses matplotlib.imshow for plot, only plots for regular mesh possible!

        The figure can be opened on screen or directly saved to a file.

        **Arguments**:
            - *property* = 1-D list : list of values to be plotted
        
        **Optional Arguments**:
            - *interpolation* = 'spline36','nearest',... : interpolation method, see matplotlib
            documentation for detail
        
        **Optional Keywords**:
            - *title* = string : Main title, if not given: name of array (to be implemented, now: no title)
            - *xlabel* = string : label of x-axis
            - *ylabel* = string : label of y-axis
            - *xscale* = 'meter', scale of x-axis (adjust tick labels)
            - *yscale* = 'meter', scale of y-axis (adjust tick labels)
            - *colorbar* = True/False : add colorbar to plot
            - *colorbar_label* = string : label of colorbar
            - *colorbar_orientation* = horizontal/ vertical
            - *two_plots* = True/False : add a subplot with interpolated image
            - *show* = True/False : show plot
            - *savefig* = True/False : save figure to file
            - *filename* = string : figure filename
            - *cmap* = colormap name for image (cm.colormap)
            - *vmin* = float : z-scale for image plot
            - *vmax* = float
            - *vertical_ex* = float : vertical exegeration, if set to 1: real aspect ratios
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
                        aspect=aspect,
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
        """Change the length of a variable array
        
        *caution*: overwrites array and fills new array with value in first entry!!
        
        **Arguments**:
            - *var_name* = string : name of variable/ property to be changed
            - *length* = int : new length of array
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
        """Compute the volume of each block in the model
        
        Function calculates the volume of each cell, can be important to process
        results for cases of non-regular meshes. Results are stored in self.block_volume list
        and returned as list; Enables, for example, the simple calculation of the total formation volume in combination
        with self.formation_masks:
        volume_3 = sum(self.formation_masks[3] * self.block_volume)
        
        **Arguments**:
            none
        
        **Returns**:
            - *block_volume* = list : list (1D) of block volumes
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
            
    def update_model_from_geology_grid(self, grid_file, **kwds):
        """Update the model geology from an exported geomodel grid file
        
        This method can be used to import the simulation model geology
        (i.e. the distribution of geological units) from an external geology
        grid file, for example created from a Geomodeller model with
        the DOS program exportRectilinearMeshCellCenter.exe; This method is
        considerably faster than exporting the model from the Geomodeller
        xml file with self.update_from_geomodeller_xml_file(), however it
        requires running the external grid generation first.
        
        **Arguments**:
            - *grid_file* = string : filename of external grid file
        """
        f = open(grid_file, 'r')
        filelines = f.readlines()
        # the grid file is a csv file, structured in x-dominance, origin lower-left corner,
        # with an end of line for each z-layer
        geol = []
        
        
        
        
    def get_cell_pos(self,x,y,z):
        """get array position of cell that contains the coordinate x,y,z
        (in real world coordinates"""
        pass
        
        
    def interpolate_values_on_xy_grid(self, x_coords, y_coords, z_values, **kwds):
        """Interpolate values on a regular grid with delauny triangulation
        
        The method can be used to interpolate values from a regular array structure
        onto the structure of the SHEMAT grid,       
        for example to enable a lateral change of porosity values
        (can then be assigned to one formation) or to interpolate surface
        temperature variations (can then be used as initial temperature condition);
        
        .. Attention:: Only works for a regular (x,y) grid!!!
        
        **Arguments**:
            - *x_coords* = 1D-array : coordinate values in x-direction
            - *y_coords* = 1D-array : coordinate values in y-direction
            - *z_values* = 1D-array : values to be interpolated

        **Optional Keywords**:
            - *relative* = True/ False: relative to model origin (not in real-world coordinates)
            
        **Returns**:
        1-D array with interpolated values (x-dominance 2-D grid)
        """
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
        """Assing initial values as a function of location to all model cells
        
        This function can be used to initiate temperature with values from a temperature grid, e.g.:
        from interpolated surface temperature values, with
        self.interpolate_values_on_xy_grid;
        can be assigned for the whole model, e.g. to initiate temperature values
        from a grid to all x,y coordinates;
        
        The function can also be used for one property zone only, e.g.
        to allow lateral changes of porosity, etc.
        
        **Arguments**:
            - *grid_xy* = 1-D array with grid values, for example created with 
            self.interpolate_values_on_xy_grid
            - *property* = SHEMAT variable name, e.g. "TEMP": variable to assign interpolated values
        
        **Optional Keywords**:
            - *formation_id* = int : formation id for which assignment should be performed
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
        
    def assign_value_to_one_formation(self,property,value,formation_id):
        """Assign a specific value to one formation
        
        Method can be used to assing a fixed value to a specific formation,
        for example to assing a temperature value for an "Ocean" formation
        and combine it with a dirichlet BC. It can also be used to change
        a property of one formation - without adjusting all others (as with
        update_property_from_csv_list()).
        
        **Arguments**:
            - *property* = string : SHEMAT property variable, e.g. "TEMP" for temperature
            - *value* = float : value to be assigned
            - *formation_id* = int : formation id to which property is assigned
        """
        try:
            self.formation_masks[formation_id]
        except AttributeError:
            self.create_formation_masks()

        property_array = self.get_array(property)
        for i,m in enumerate(self.formation_masks[formation_id]):
            if m == 1:
                property_array[i] = value
        self.set_array(property, property_array)
    
    def adjust_thickness_of_base_layers(self,n,thickness):
        """Adjust/ increse the thickness of the base layers
        
        Can be used to increase the overall thickness of the model
        and to extend it to a greater depth, e.g. to reach the Moho
        as a lower thermal boundary condition, without having to change
        the whole model structure.
        
        The argument thickness defines the overall thickness of all 
        layers that are added. The layer n+1 above the n increased thickness
        layers is itself increased to accommodate for the layers that were
        moved further down. Sounds complicated, is simple...
        
        **Arguments**:
            - *n* = int : number of layers to increase
            - *thickness* = float : overall thickness to be added
        """
        self.delz = self.get_array("DELZ")
        ori_thickness = sum(self.delz[:n+1])
        
        # assign thickness to extended layers
        for i in range(n):
            self.delz[i] = thickness / n
            
        # adjust thickness in n+1 layer
        self.delz[n+1] = ori_thickness
        
        # write back to object
        self.set_array("DELZ", self.delz)
            
        
        
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
        """Assign initial temperatures as a linear function of altitude
        
        This function can be used to e.g. to assign temperatures at the model
        surface as a function f(x) = ax + b of altitude for thermal boundary conditions
        Function assigns all valus to initial temperatures; these "Air"-values can then
        be fixed with self.fix_const_bc_for_one_formation
        
        **Arguments**:
            - *a* = float : gradient
            - *b* = float : y-axis intercept
        
        **Optional keywords**:
            - *min_alt* = float : minimum altitude to assign temperature function
            - *relative* = float : calculate values relative to model origin (in model
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
        """Assign a new geological unit to one or more layers
        
        This method can be used to create a thermal equilibrium layer at the
        base of the model
        
        **Arguments**:
            - *n_layers* = int : number of layers with new geological unit
        
        **Optional Arguments**:
            - *start* = int : start from this layer, default=0: at bottom of model
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
        """Assigni thermal equilibration layers to base of model
        
        Assing layers with high lateral thermal conductivity at base of
        model to allow for lateral equilibration of thermal heat flux;
        values for WLXANI and WLYANI are set to very high values;
        
        **Arguments**:
            - *n* = int : number of layers with high anisotropy
        
        **Optional Keywords**:
            - *aniso_val* = float : value of anisotropy; default: 999.
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

def create_empty_model(**kwds):
    """create a new SHEMAT model based on grid and boundary definition
    
    This method can be used to create a simple empty model box, defined with grid
    spacing in each direction (dx, dy, dz) and simple boundary conditions. The new
    model is created on basis of an nml-template file (defined in variable "lines" below).
    This method turned out to be the simplest way to keep the input file consistent.
    
    The standard base model is a conductive heat transport model, with a vtk file as graphic
    output, simulation is steady-state and no coupling is considered. All these settings can be
    changed with optional keywords (see below).
    
    .. note:: general procedure: key words are the same as those in shemat nml file (but lowercase, as python convention)
    
    **Optional Keywords**:
        - *dx* = [] : list of spacing in x-direction
        - *dy* = [] : list of spacing in y-direction
        - *dz* = [] : list of spacing in z-direction
        - *title* = string : set title of simluation NOTE: A SHEMAT PECULIARITY IS THAT THE TYPE OF SIM HAS TO BE DEFINED HERE!
        - *key* = 12345 : problem and numerical procedure key; specifically: set as FU--- for fluid and heat flow
        - *stat* = inst : if set to inst: transient simulation
        - *kopkng* = (4 char word) : coupling info, specifically: C--- : coupling of fluid and heat flow
        - *topt* = WSD/ TEMP/ NFLO : thermal top BC; see also: bc_temperature_base
        - *baset* = WSD/ TEMP/ NFLO : thermal base BC; see also: bc_temperature_top
        - *seitet* = WSD/ TEMP/ NFLO : thermal side BC (set to same value for all sides for now...); see also: bc_temperature_side
        - *transient* = True/False : perform transient simulation => 10 Periods, 100 k default setting
        - *monitoring* = [[i1,j1,k1],[i2,j2,k2],...,[in,jn,kn]] : list of monitoring positions
    
    .. note:: the following keywords are in addition to the standard SHEMAT variables, for simplification and additional features!
    
    **Additional Keywords**:
        - *nml_filename* = string : filename for nml file (extension .nml added as default)
        - *top_heat_flux* = int : one value for heat flux assigned to all cells
        - *basal_heat_flux* = int : one value for heat flux, assigned to all cells
        - *compute_heat* = True/False : set flags to compute heat transport (default = True)
        - *compute_fluid* = True/False : set flags to compute fluid flow (default = False)
        - *coupled_fluid_heat* = True/False : set flag for coupled simulation (default = True when both computed)
        - *execute_sheamt* = True/False : execute SHEMAT directly after model setup
        - *initialize_temp_grad* = True/False : set an initial temperature gradient (may speed up computation)
        - *initialize_heads* = True/False : set head values in all cells to total z-size of project (more stable?)
        - *set_head* = int : set all head values to given number; not working if initialize_heads = True!!
        - *lambda0* = float : thermal conductivity (for the whole model)
        - *vtk* = True/ False : toggle output to VTK file (default: True)
        - *thermal_cond_function_of_temp* = True/ False : calculate thermal conductivity as a function of temperature,
        see SHEMAT book pg. 14 for details

    .. note:: the following keywords address some SHEMAT variables with a more meaningful term
    
    **Additional Keywords for more meaningful BC definition**:
        - *bc_temperature_side* = 'dirichlet', 'neumann', 'no_flow': lateral thermal boundary conditions
        - *bc_temperature_top* = 'dirichlet', 'neumann', 'no_flow': top thermal boundary conditions
        - *bc_temperature_base* = 'dirichlet', 'neumann', 'no_flow': base thermal boundary conditions
        - *value_temperature_top* = float : fixed temperature at top for dirichlet bc
        - *value_temperature_base* = float : fixed temperature at base for dirichlet bc
        - *flux_temperature_top* = float : defined heat flux over top for neumann temperature bc
        - *flux_temperature_base* = float : defined heat flux over base for neumann temperature bc
        - *bc_flow_side* = 'dirichlet', 'neumann', 'no_flow': lateral flow boundary conditions
        - *bc_flow_top* = 'dirichlet', 'neumann', 'no_flow': top flow boundary conditions
        - *bc_flow_base* = 'dirichlet', 'neumann', 'no_flow': base flow boundary conditions
        - *value_head_top* = float : fixed head at top for dirichlet bc
        - *value_head_base* = float : fixed head at base for dirichlet bc
        - *flux_flow_top* = float : defined fluid flux over top for neumann temperature bc
        - *flux_flow_base* = float : defined fluid flux over base for neumann temperature bc
     
    .. note:: the following keywords address functionalities to read the model geometry from a GeoModeller model
        
    **Additional Keywords for geometry functionalities**:    
        - *update_from_geomodel* = True/False
        - *geomodeller_dir* = directory_path
        - *geomodel_filename* = geomodel_filename
        - *update_from_property_file* = True/ False: update model variables from property file
        - *geomodel_properties* = csv_file : csv file with model properties (see ge2she)
        - *extent_x* = (float, float) : range of geomodel in x-direction (default: model range)
        - *extent_y* = (float, float) : range of geomodel in y-direction (default: model range)
        - *extent_z* = (float, float) : range of geomodel in z-direction (default: model range)
        - *update_from_geology_grid* = True/ False : update geology array from exported grid, with
        x-dominance and a line break for each z-layer;
        - *grid_filename* = string : file with exported geology grid
        - *update_from_voxet_file* = True/ False: update geology properties from voxet file,
        for example exported from GoCAD voxet object (with GoCAD scripting methods).
    """
    print kwds['dx']
    print kwds['dy']
    print kwds['dz']
    nx = len(kwds['dx'])
    ny = len(kwds['dy'])
    nz = len(kwds['dz'])
    # caluclate layer grid size
    layer_grid_number = len(kwds['dx']) * len(kwds['dy'])
    model_grid_number = len(kwds['dx']) * len(kwds['dy'])* len(kwds['dz'])
    S1 = Shemat_file()
    # define basic project lines
    S1.filelines = []
    lines = """# TITLE
Horizontal -
# IPUTDI
1234567X9012
# LINFO
1
# I0
       10 
# J0
       10 
# K0
       10 
# IDIM
       10 
# JDIM
       10 
# KDIM
       10 
# KEY
-I---
# STAT
STAT
# KOPLNG
----
# KOPPX_FLAG
0 0 0 0 0 
# KOPPX_FIELD
998.0 0.61 4.5E-10 4179.0 8.9E-04 
# WARNG
WARN
# MXIT
20000
# NPER
       1 
# PICARD
1
# CHI
 0.5
# MAXPICARDIT
5
# ABSPICARDF
 0.001
# ABSPICARDT
 0.001
# ABSPICARDS
0
# RHOF
998.0
# TREF
20.0000
# CREF
120.000
# TOPF
NFLO
# BASEF
NFLO
# SEITEF
NFLO
NFLO
NFLO
NFLO
# NFREE
 0 
# KFREE
100*0
# IFLO
MASS
# IQRE
NIX
# GRAV
9.80665
# COMPF
0.460000E-09
# COMPM
1.0E-10
# VBASAL
0.0
# ERRF
1.0E-10
# OMF
1.0
# APARF
1.0
# CONTROLF
 48 
# TOPT
TEMP
# BASET
WSD
# SEITET
NFLO
NFLO
NFLO
NFLO
# CMA1
0.00000
# CMA2
0.00000
# CMA3
0.00000
# HPF
0.0
# QTOP3D
100*0. 
# QBASAL3D
100*0.08 
# OMT
1.0
# APART
1.0
# CONTROLT
 48 
# ERRT
1.0E-10
# TOPS
NFLO
# BASES
NFLO
# SEITES
NFLO
NFLO
NFLO
NFLO
# MDIFS1
0.5E-08
# MDIFD1
0.000
# MDIFD2
0.000
# MDIFD3
0.000
# DIFTS1
2.01
# DIFLS1
2.01
# ERRS
1.0E-10
# OMS
1.0
# APARS
1.0
# CONTROLS
 48 
# ANZSUBS
 0 
# BETAC
0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 
# ANZCHEM
 0 
# ANZMINS
0
# FRACEXP
1.
1.
1.
# IZV
100*0
# SIEQ
20*0.0
# VMOL
20*0.0
# AO
20*0.
# EACT
20*0.
# RATE
20*0.
# NWELAR
100*0
# DELTATMP
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# TMAXAR
1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# DELTAR
1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# TCON
10000*0.0
# SCON
10000*0.0
# IWL
1000*0
# WELLAR
10000*0.
# PUMPAR
10000*0.
# PMONIX
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIY
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIZ
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIFR
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 
# DELX
10*100. 
# DELY
10*100. 
# DELZ
100. 100. 100. 100. 100. 100. 100. 100. 100. 100. 
# GEOLOGY
1000*1 
# PRES
1000*0.1 
# POR
900*0.25 100*-0.25 
# DICHTE
1000*1000.
# PERM
1000*1.E-12 
# RHOCF
1000*0.
# PHI
1000*0. 
# VX
1000*0.
# VY
1000*0.
# VZ
1000*0.
# QRE
200*0.
# QRELR
200*0.
# QREVH
200*0.
# ANISOI
1000*1. 
# ANISOJ
1000*1. 
# TEMP
1000*10. 
# RHOCM
1000*2.06E6 
# WLFM0
1000*2.9 
# WLXANI
1000*1. 
# WLYANI
1000*1. 
# XANG
1000*0. 
# YANG
1000*0. 
# HPR
1000*0. 
# AREAKT
1000*0.
    """
    lines_trans = """# TITLE
Horizontal -
# IPUTDI
1234567X9012
# LINFO
1
# I0
       10 
# J0
       10 
# K0
       10 
# IDIM
       10 
# JDIM
       10 
# KDIM
       10 
# KEY
FI---
# STAT
INST
# KOPLNG
C---
# KOPPX_FLAG
0 0 0 0 0 
# KOPPX_FIELD
998.0 0.61 4.5E-10 4179.0 8.9E-04 
# WARNG
WARN
# MXIT
20000
# NPER
       10 
# PICARD
1
# CHI
 0.5
# MAXPICARDIT
5
# ABSPICARDF
 0.001
# ABSPICARDT
 0.001
# ABSPICARDS
0
# RHOF
998.0
# TREF
20.0000
# CREF
120.000
# TOPF
NFLO
# BASEF
NFLO
# SEITEF
NFLO
NFLO
NFLO
NFLO
# NFREE
 0 
# KFREE
100*0
# IFLO
MASS
# IQRE
NIX
# GRAV
9.80665
# COMPF
0.460000E-09
# COMPM
1.0E-10 
# VBASAL
0.0
# ERRF
1.0E-10
# OMF
1.0
# APARF
1.0
# CONTROLF
 48 
# TOPT
TEMP
# BASET
WSD
# SEITET
NFLO
NFLO
NFLO
NFLO
# CMA1
0.00000
# CMA2
0.00000
# CMA3
0.00000
# HPF
0.0
# QTOP3D
100*0. 
# QBASAL3D
100*0.08 
# OMT
1.0
# APART
1.0
# CONTROLT
 48 
# ERRT
1.0E-10
# TOPS
NFLO
# BASES
NFLO
# SEITES
NFLO
NFLO
NFLO
NFLO
# MDIFS1
0.5E-08
# MDIFD1
0.000
# MDIFD2
0.000
# MDIFD3
0.000
# DIFTS1
2.01
# DIFLS1
2.01
# ERRS
1.0E-10
# OMS
1.0
# APARS
1.0
# CONTROLS
 48 
# ANZSUBS
 0 
# BETAC
0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 
# ANZCHEM
 0 
# ANZMINS
0
# FRACEXP
1.
1.
1.
# IZV
100*0
# SIEQ
20*0.0
# VMOL
20*0.0
# AO
20*0.
# EACT
20*0.
# RATE
20*0.
# NWELAR
100*0
# DELTATMP
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# TMAXAR
3153600000000.0 6307200000000.0 9460800000000.0 12614400000000.0 15768000000000.0 18921600000000.0 22075200000000.0 25228800000000.0 28382400000000.0 31536000000000.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# DELTAR
315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 315360000000.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# TCON
10000*0.0
# SCON
10000*0.0
# IWL
1000*0
# WELLAR
10000*0.
# PUMPAR
10000*0.
# PMONIX
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIY
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIZ
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIFR
100 10 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 
# DELX
10*100. 
# DELY
10*100. 
# DELZ
100. 100. 100. 100. 100. 100. 100. 100. 100. 100. 
# GEOLOGY
1000*1 
# PRES
1000*0.1 
# POR
900*0.25 100*-0.25 
# DICHTE
1000*1000.
# PERM
1000*1.E-12 
# RHOCF
1000*0.
# PHI
1000*1000. 
# VX
1000*0.
# VY
1000*0.
# VZ
1000*0.
# QRE
200*0.
# QRELR
200*0.
# QREVH
200*0.
# ANISOI
1000*1. 
# ANISOJ
1000*1. 
# TEMP
1000*10. 
# RHOCM
1000*2.06E6 
# WLFM0
1000*2.9 
# WLXANI
1000*1. 
# WLYANI
1000*1. 
# XANG
1000*0. 
# YANG
1000*0. 
# HPR
1000*0. 
# AREAKT
1000*0."""
    lines_trans_2 = """# TITLE
Horizontal -
# IPUTDI
1234567X9012
# LINFO
1
# I0
       30 
# J0
       10 
# K0
       10 
# IDIM
       30 
# JDIM
       10 
# KDIM
       10 
# KEY
FI---
# STAT
INST
# KOPLNG
C---
# KOPPX_FLAG
0 0 0 0 0 
# KOPPX_FIELD
998.0 0.61 4.5E-10 4179.0 8.9E-04 
# WARNG
WARN
# MXIT
20000
# NPER
       100 
# PICARD
1
# CHI
 0.5
# MAXPICARDIT
5
# ABSPICARDF
 0.001
# ABSPICARDT
 0.001
# ABSPICARDS
0
# RHOF
998.0
# TREF
20.0000
# CREF
120.000
# TOPF
NFLO
# BASEF
FLO
# SEITEF
NFLO
NFLO
FLO
NFLO
# NFREE
 0 
# KFREE
100*0
# IFLO
MASS
# IQRE
NIX
# GRAV
9.80665
# COMPF
0.460000E-09
# VBASAL
0.0
# ERRF
1.0E-10
# OMF
1.0
# APARF
1.0
# CONTROLF
 48 
# TOPT
TEMP
# BASET
TEMP
# SEITET
NFLO
NFLO
NFLO
NFLO
# CMA1
0.00000
# CMA2
0.00000
# CMA3
0.00000
# HPF
0.0
# QTOP3D
300*0. 
# QBASAL3D
300*0.06
# OMT
1.0
# APART
1.0
# CONTROLT
 48 
# ERRT
1.0E-10
# TOPS
NFLO
# BASES
NFLO
# SEITES
NFLO
NFLO
NFLO
NFLO
# MDIFS1
0.5E-08
# MDIFD1
0.000
# MDIFD2
0.000
# MDIFD3
0.000
# DIFTS1
2.01
# DIFLS1
2.01
# ERRS
1.0E-10
# OMS
1.0
# APARS
1.0
# CONTROLS
 48 
# ANZSUBS
 0 
# BETAC
0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 
# ANZCHEM
 0 
# ANZMINS
0
# FRACEXP
1.
1.
1.
# IZV
100*0
# SIEQ
20*0.0
# VMOL
20*0.0
# AO
20*0.
# EACT
20*0.
# RATE
20*0.
# NWELAR
100*0
# DELTATMP
0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
# TMAXAR
31536000000.0 63072000000.0 94608000000.0 126144000000.0 157680000000.0 189216000000.0 220752000000.0 252288000000.0 283824000000.0 315360000000.0 346896000000.0 378432000000.0 409968000000.0 441504000000.0 473040000000.0 504576000000.0 536112000000.0 567648000000.0 599184000000.0 630720000000.0 662256000000.0 693792000000.0 725328000000.0 756864000000.0 788400000000.0 819936000000.0 851472000000.0 883008000000.0 914544000000.0 946080000000.0 977616000000.0 1009152000000.0 1040688000000.0 1072224000000.0 1103760000000.0 1135296000000.0 1166832000000.0 1198368000000.0 1229904000000.0 1261440000000.0 1292976000000.0 1324512000000.0 1356048000000.0 1387584000000.0 1419120000000.0 1450656000000.0 1482192000000.0 1513728000000.0 1545264000000.0 1576800000000.0 1608336000000.0 1639872000000.0 1671408000000.0 1702944000000.0 1734480000000.0 1766016000000.0 1797552000000.0 1829088000000.0 1860624000000.0 1892160000000.0 1923696000000.0 1955232000000.0 1986768000000.0 2018304000000.0 2049840000000.0 2081376000000.0 2112912000000.0 2144448000000.0 2175984000000.0 2207520000000.0 2239056000000.0 2270592000000.0 2302128000000.0 2333664000000.0 2365200000000.0 2396736000000.0 2428272000000.0 2459808000000.0 2491344000000.0 2522880000000.0 2554416000000.0 2585952000000.0 2617488000000.0 2649024000000.0 2680560000000.0 2712096000000.0 2743632000000.0 2775168000000.0 2806704000000.0 2838240000000.0 2869776000000.0 2901312000000.0 2932848000000.0 2964384000000.0 2995920000000.0 3027456000000.0 3058992000000.0 3090528000000.0 3122064000000.0 3153600000000.0 
# DELTAR
3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 3153600000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 6307200000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 31536000000.0 
# TCON
10000*0.0
# SCON
10000*0.0
# IWL
3000*0
# WELLAR
10000*0.
# PUMPAR
10000*0.
# PMONIX
5 10 15 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIY
6 6 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIZ
6 6 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
# PMONIFR
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 
# DELX
30*100. 
# DELY
10*100. 
# DELZ
100. 100. 100. 100. 100. 100. 100. 100. 100. 100. 
# GEOLOGY
1000*1 7*2 23*1 7*2 23*1 7*2 23*1 7*2 203*1 7*2 23*1 7*2 23*1 7*2 23*1 7*2 203*1 7*2 23*1 7*2 23*1 7*2 23*1 7*2 1303*1 
# PRES
3000*0.1 
# POR
300*-0.25 2400*0.25 300*-0.25 
# DICHTE
3000*1000.
# PERM
2729*1.E-13 -1.E-13 29*1.E-13 -1.E-13 29*1.E-13 -1.E-13 29*1.E-13 -1.E-13 6*1.E-13 3*-1.E-13 20*1.E-13 -1.E-13 6*1.E-13 3*-1.E-13 20*1.E-13 -1.E-13 6*1.E-13 3*-1.E-13 20*1.E-13 -1.E-13 29*1.E-13 -1.E-13 29*1.E-13 -1.E-13 29*1.E-13 -1.E-13 
# RHOCF
3000*0.
# PHI
2729*100. 110. 29*100. 110. 29*100. 110. 29*100. 110. 6*100. 3*105. 20*100. 110. 6*100. 3*105. 20*100. 110. 6*100. 3*105. 20*100. 110. 29*100. 110. 29*100. 110. 29*100. 110. 
# VX
3000*0.
# VY
3000*0.
# VZ
3000*0.
# QRE
300*0. 300*0. 
# QRELR
-0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 0. -0.0000001 102*0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 0. 1.E-08 
# QREVH
0. 5*-0.0000001 594*0. 
# ANISOI
3000*1. 
# ANISOJ
3000*1. 
# TEMP
300*90. 2400*0. 300*10. 
# RHOCM
3000*2.06E6 
# WLFM0
1000*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 203*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 203*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 23*1.5 7*2.9 1303*1.5 
# WLXANI
3000*1. 
# WLYANI
3000*1. 
# XANG
3000*0. 
# YANG
3000*0. 
# HPR
3000*0. 
# AREAKT
3000*0."""
    if kwds.has_key('transient') and kwds['transient']==True:
        lines = lines_trans_2
        
    for l in lines.split("\n"):
        print l
        S1.filelines.append(l+"\n")
    # get original dimensions for rescaling below
    ori_nx = int(S1.get("IDIM"))
    ori_ny = int(S1.get("JDIM"))
    ori_nz = int(S1.get("KDIM"))
    # now: define all variables
    if kwds.has_key('title'):
        if ("Horizontal" in kwds['title']) or ("Vertical" in kwds['title']):
            title = kwds['title']
        else:
            title = "Horizontal - " + kwds['title']
        S1.set("TITLE",title)
    else:
        S1.set("TITLE", "Horizontal - Model created with PySHEMAT")
    # set nodes and delimiters
    print "\n\n\tCheck implementation of I0,J0,K0!\n\n\n"
    S1.set("I0",len(kwds['dx']))
    S1.set("J0",len(kwds['dy']))
    S1.set("K0",len(kwds['dz']))
    S1.set("IDIM", len(kwds['dx']))
    S1.set("JDIM", len(kwds['dy']))
    S1.set("KDIM", len(kwds['dz']))
    S1.set_array("DELX", kwds['dx'])
    S1.set_array("DELY", kwds['dy'])
    S1.set_array("DELZ", kwds['dz'])
    # set problem key, if defined in kwds
    if kwds.has_key('key'): S1.set("KEY", kwds['key'])
    if kwds.has_key('stat'): S1.set("STAT", kwds['stat'])
    if kwds.has_key('koplng'): S1.set("KOPLNG", kwds['koplng'])
    #
    # use other keyword definitions to set key and coupling indirectly
    #
    if kwds.has_key('compute_heat') and kwds['compute_heat'] == False:
        H = '-'
    else: # default: True
        H = 'I'
    if kwds.has_key('compute_fluid') and kwds['compute_fluid'] == True:
        F = 'F'
    else: # default: False
        F = '-'
    S1.set("KEY", F + H + "---")    
    if kwds.has_key('coupled_fluid_heat') and kwds['coupled_fluid_heat'] == False:
        coupling = '----'
    else:
        coupling = 'C---'
    S1.set("KOPLNG", coupling)
    # set monitoring positions; check if in range of model before implementing (SHEMAT crashes otherwise)
    if kwds.has_key('monitoring') and len(kwds['monitoring']) != 0:
        mx = []
        my = []
        mz = []
        # check input and create arrays
        for i,m in enumerate(kwds['monitoring']):
            if m[0] > nx or m[1] > ny or m[2] > nz:
                print "\n\n\tMonitoring position %d not within model range! Please check!!\n\n\n" % i
            else:
                mx.append(int(m[0]))
                my.append(int(m[1]))
                mz.append(int(m[2]))
        # now: update monitoring variable
        pmonix = S1.get_array("PMONIX")
        pmoniy = S1.get_array("PMONIY")
        pmoniz = S1.get_array("PMONIZ")
        from numpy import r_
        pmonix_new = r_[mx,pmonix[len(mx):]]
        pmoniy_new = r_[my,pmoniy[len(my):]]
        pmoniz_new = r_[mz,pmoniz[len(mz):]]
        S1.set_array("PMONIX", pmonix_new)
        S1.set_array("PMONIY", pmoniy_new)
        S1.set_array("PMONIZ", pmoniz_new)

    # set fluid boundary conditions
    # (not yet impemented)
    # set temperature boundary conditions: SHEMAT notation (strange variable names)
    if kwds.has_key('topt'): S1.set("TOPT", kwds['topt'])
    if kwds.has_key('baset'): S1.set("BASET", kwds['baset'])
    if kwds.has_key('seitet'): 
        # problem here: defined in four proceeding lines... set all as the same (for now)
        S1.set("SEITET", kwds['seitet'])
        S1.set("SEITET", kwds['seitet'], line=2)
        S1.set("SEITET", kwds['seitet'], line=3)
        S1.set("SEITET", kwds['seitet'], line=4)
    # set top and bottom heat flux values (if defined... if not: adjust for number of cells)
    # or: use one value for heat flux, defined with kwds heat_flux_top and heat_flux_bottom
    if kwds.has_key('qtop3d'): 
        S1.set_array("QTOP3D", kwds['qtop3d'])
    else:
        if kwds.has_key('top_heat_flux'): S1.set_array("QTOP3D", layer_grid_number * [kwds['top_heat_flux']])
        elif kwds.has_key('flux_temperature_top'): S1.set_array("QBASAL3D", layer_grid_number * [kwds['flux_temperature_top']])
        else: # in this case: reset length of array only and use first value
            S1.change_array_length("QTOP3D", layer_grid_number)
    if kwds.has_key('qbasal3d'): 
        S1.set_array("QBASAL3D", kwds['qbasald'])
    else:
        if kwds.has_key('basal_heat_flux'): S1.set_array("QBASAL3D", layer_grid_number * [kwds['basal_heat_flux']])
        elif kwds.has_key('flux_temperature_base'): S1.set_array("QBASAL3D", layer_grid_number * [kwds['flux_temperature_base']])
        else: # in this case: reset length of array only and use first value
            S1.change_array_length("QBASAL3D", layer_grid_number)

    # set temperature boundary conditions: new method (adjusted variable names)
    if kwds.has_key('bc_temperature_side'):
        if kwds['bc_temperature_side'] == 'no_flow':
            S1.set("SEITET", 'NFLO')
            S1.set("SEITET", 'NFLO', line=2)
            S1.set("SEITET", 'NFLO', line=3)
            S1.set("SEITET", 'NFLO', line=4)
        else:
            print("\n\n\tOnly no flow side boundary conditions are implemented so far...n")
            print("\tBC side set to no-flow, adjust by hand (or in ProcessingSHEMAT) if required")
    if kwds.has_key('bc_temperature_top'):
        if kwds['bc_temperature_top'] == 'no_flow':
            S1.set("TOPT", 'NFLO')
        elif kwds['bc_temperature_top'] == 'dirichlet':
            S1.set("TOPT", 'TEMP')
        elif kwds['bc_temperature_top'] == 'neumann':
            S1.set("TOPT", 'WSD')
        else:
            print("Temperature BC " + kwds['bc_temperature_top'] + " not recognized!")
            print("Please check and try again")
            raise KeyError
    if kwds.has_key('bc_temperature_base'):
        if kwds['bc_temperature_base'] == 'no_flow':
            S1.set("BASET", 'NFLO')
        elif kwds['bc_temperature_base'] == 'dirichlet':
            S1.set("BASET", 'TEMP')
        elif kwds['bc_temperature_base'] == 'neumann':
            S1.set("BASET", 'WSD')
        else:
            print("\n\n\tTemperature BC " + kwds['bc_temperature_base'] + " not recognized!")
            print("\tPlease check and try again\n\n")
            raise KeyError
    
    # set flow boundary conditions: new method (adjusted variable names)
    if kwds.has_key('bc_flow_side'):
        if kwds['bc_flow_side'] == 'no_flow':
            S1.set("SEITET", 'NFLO')
            S1.set("SEITET", 'NFLO', line=2)
            S1.set("SEITET", 'NFLO', line=3)
            S1.set("SEITET", 'NFLO', line=4)
        else:
            print("\n\n\tOnly no flow side boundary conditions are implemented so far...n")
            print("\tBC side set to no-flow, adjust by hand (or in ProcessingSHEMAT) if required")
    if kwds.has_key('bc_flow_top'):
        if kwds['bc_flow_top'] == 'no_flow':
            S1.set("TOPF", 'NFLO')
        elif kwds['bc_flow_top'] == 'dirichlet':
            # S1.set("TOPF", 'FREE')
            print("\n\n\tNote: BC dirichlet for top flow not yet implemented!\n")
            print("\tSet to no_flow and adjust by hand or with ProcessingSHEMAT if required!\n")
            raise KeyError
        elif kwds['bc_flow_top'] == 'neumann':
            # S1.set("TOPF", 'RECH')
            print("\n\n\tNote: BC neumann for top flow not yet implemented!\n")
            print("\tSet to no_flow and adjust by hand or with ProcessingSHEMAT if required!\n")
            raise KeyError
        else:
            print("Flow BC " + kwds['bc_flow_top'] + " not recognized!")
            print("Please check and try again")
            raise KeyError
    if kwds.has_key('bc_flow_base'):
        if kwds['bc_flow_base'] == 'no_flow':
            S1.set("BASEF", 'NFLO')
        elif kwds['bc_temperature_base'] == 'dirichlet':
            print("\n\n\tDefinition of dirichlet BC at base not possible with SHEMAT, sorry!\n")
            raise KeyError
        elif kwds['bc_temperature_base'] == 'neumann':
            # S1.set("BASEF", 'FLO')
            print("\n\n\tDefinition of base neumann BC for flow not yet implemented in PySHEMAT!\n")
            print("\tSet to no_flow and adjust by hand or with ProcessingSHEMAT\n")
            raise KeyError
        else:
            print("\n\n\tFlow BC " + kwds['bc_flow_base'] + " not recognized!")
            print("\tPlease check and try again\n\n")
            raise KeyError

    
    # rescale recharge rate variables QRE, QRELR, QREVH
    S1.change_array_length("# QRE", len(kwds['dx']) * len(kwds['dy']) * 2)
    S1.change_array_length("# QRELR", len(kwds['dy']) * len(kwds['dz']) * 2)
    S1.change_array_length("# QREVH", len(kwds['dz']) * len(kwds['dx']) * 2)
    
    # change boundary condition arrays (self.diri_temp, self.diri_head and self.diri_conc)
    # !!! CAUTION !!! checks and adjusts for constant BC at top and bottom only!
    S1.get_bcs()
    diri_temp_new = (layer_grid_number * [S1.diri_temp[0]] + 
                     (model_grid_number - 2 * layer_grid_number) * [S1.diri_temp[ori_nx * ori_ny + 1]] + 
                     layer_grid_number * [S1.diri_temp[-1]])
    S1.diri_temp = diri_temp_new
    diri_conc_new = (layer_grid_number * [S1.diri_conc[0]] + 
                     (model_grid_number - 2 * layer_grid_number) * [S1.diri_conc[ori_nx * ori_ny + 1]] + 
                     layer_grid_number * [S1.diri_conc[-1]])
    S1.diri_conc = diri_conc_new
    diri_head_new = (layer_grid_number * [S1.diri_head[0]] + 
                     (model_grid_number - 2 * layer_grid_number) * [S1.diri_head[ori_nx * ori_ny + 1]] + 
                     layer_grid_number * [S1.diri_head[-1]])
    S1.diri_head = diri_head_new
    
    
    # change array length for POR, PERM and PRES; this has to be done seperately
    # due to the 'strange' convention of negative POR, PERM and PRES for Dirichlet BC temp, head and conc...
    

    # define here all other arrays that have to be re-scaled
    # some variables are defined in the whole model, some only in layers (takes layer_grid_num to resize)
    layer_vars = ["QTOP3D", 
                  "QBASAL3D"]
    model_vars = ["GEOLOGY",
                    "PRES",
                    "POR",
                    "DICHTE",
                    "PERM",
                    "RHOCF",
                    "PHI",
                    "VX",
                    "VY",
                    "VZ",
                    "# IWL",
                    "ANISOI",
                    "ANISOJ",
                    "# TEMP",
                    "RHOCM",
                    "WLFM0",
                    "WLXANI",
                    "WLYANI",
                    "XANG",
                    "YANG",
                    "HPR",
                    "AREAKT"                  
                    ]
    for var_name in layer_vars:
        print var_name
        S1.change_array_length(var_name, layer_grid_number)
    for var_name in model_vars:
        print var_name
        S1.change_array_length(var_name, model_grid_number)
    #
    # now: initialize temperature gradient and/ or hydraulic heads
    #
    if kwds.has_key('initialize_temp_grad') and kwds['initialize_temp_grad']:
        # calculate thermal gradient from basal heat flux value, thermal conductivity and top temperature
        print "Initialize temperature gradient"
        if kwds.has_key('basal_heat_flux'):
            q = kwds['basal_heat_flux']
            l = S1.get_array("WLFM0")[0]
            t_grad = q/l
            t0 = S1.get_array("# TEMP")[-1] # get surface temperature
            temp_xyz = S1.get_array_as_xyz_structure("# TEMP")
            total_depth = sum(kwds['dz'])
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        depth = total_depth - sum(kwds['dz'][0:z])
                        temp_xyz[x][y][z] = t0 + depth * t_grad
            S1.set_array_from_xyz_structure("# TEMP", temp_xyz)
        else: print "need basal heat flux (kwds: basal_heat_flux) to calculate initial gradient!"
    if kwds.has_key('initialize_heads') and kwds['initialize_heads']:
        print "Intitialize hydraulic heads"
        # set head values all to project depth (matter of stability?)
        heads = S1.get_array("PHI")
        total_depth = sum(kwds['dz'])
        new_heads = []
        for h in heads:
            new_heads.append(total_depth)
        S1.set_array("PHI", new_heads)
    if kwds.has_key('set_head'):
        new_h = kwds['set_head']
        heads = S1.get_array("PHI")
        new_heads = []
        for h in heads:
            new_heads.append(new_h)
        S1.set_array("PHI", new_heads)
    if kwds.has_key('lambda0'):
        from numpy import ones
        lambda0 = ones(len(kwds['dx']) * len(kwds['dy']) * len(kwds['dz'])) * kwds['lambda0']
        S1.set_array("WLFM0",lambda0)
        
    if kwds.has_key('vtk') and kwds['vtk'] == False:
        # no vtk export of results (to save disk space)
        iputdi = S1.get('IPUTDI')
        iputdi = iputdi.rstrip()
        iputdi = iputdi[:7] + '8' + iputdi[8:]
        S1.set('IPUTDI',iputdi)

### added 28/07/2010
    if kwds.has_key('topt') and kwds['topt'] == "TEMP" and kwds.has_key('top_temperature'):
        temp = S1.get_array("# TEMP")
        from numpy import ones
        n_layer = nx*ny
        temp[-n_layer:] = ones(n_layer) * float(kwds['top_temperature'])
        S1.set_array("# TEMP", temp)
        
    if kwds.has_key('baset') and kwds['baset'] == "TEMP" and kwds.has_key('base_temperature'):
        # set temperature at base of model
        temp = S1.get_array("# TEMP")
        from numpy import ones
        n_layer = nx*ny
        temp[:n_layer] = ones(n_layer) * float(kwds['base_temperature'])
        S1.set_array("# TEMP", temp)
    
    # adjust base and top temperatures for defined dirichlet BC with new methods
    if kwds.has_key('bc_temperature_top') and kwds['bc_temperature_top'] == "dirichlet":
        temp = S1.get_array("# TEMP")
        from numpy import ones
        n_layer = nx*ny
        try:
            temp[-n_layer:] = ones(n_layer) * float(kwds['value_temperature_top'])
        except KeyError:
            print("\n\n\tIf bc_temperature_top is set to 'dirichlet', value_temperature_top has to be passed as keyword!\n")
            print("\tvalue_temperature_top = float : temperature at top of model\n")
            print("\tPlease adjust and try again!\n\n")
            raise KeyError
        S1.set_array("# TEMP", temp)
        
    if kwds.has_key('bc_temperature_base') and kwds['bc_temperature_base'] == "dirichlet":
        # set temperature at base of model
        temp = S1.get_array("# TEMP")
        from numpy import ones
        n_layer = nx*ny
        try:
            temp[:n_layer] = ones(n_layer) * float(kwds['value_temperature_base'])
        except KeyError:
            print("\n\n\tIf bc_temperature_base is set to 'dirichlet', value_temperature_base has to be passed as keyword!\n")
            print("\tvalue_temperature_base = float : temperature at base of model\n")
            print("\tPlease adjust and try again!\n\n")
            raise KeyError

        S1.set_array("# TEMP", temp)
    
    
    if kwds.has_key('random_perm_flux_sigma') and kwds['random_perm_flux_sigma'] > 0    :
        from numpy import random, array
        perm = S1.get_array("PERM")
        n_layer = nx*ny
        perm_top = perm[n_layer:]
        perm_bottom = perm[:n_layer]
        perm_flux = random.randn(len(perm))*kwds['random_perm_flux_sigma']
        perm_new = array(perm) + array(perm_flux)
        S1.set_array("PERM", perm_new)
        
    if kwds.has_key('random_init_temperature_flux_sigma') and kwds['random_init_temperature_flux_sigma'] > 0:
        # introduce random temperature fluctiations in nml file
        from numpy import random, array
        temp = S1.get_array("# TEMP")
        n_layer = nx*ny
        temp_top = temp[-n_layer:]
        temp_bottom = temp[:n_layer]
        temp_flux = random.randn(len(temp))*kwds['random_init_temperature_flux_sigma']
        temp_new = array(temp) + array(temp_flux)
        if kwds.has_key('exclude_top_bottom') and kwds['exclude_top_bottom']:
            temp_new[-n_layer:] = temp_top
            temp_new[:n_layer] = temp_bottom
        S1.set_array("# TEMP", temp_new)
### end added

    
    # update from GeoModel
    """
        update_from_geomodel = True/False
        geomodeller_dir = directory_path
        geomodel_filename = geomodel_filename
        geomodel_properties = csv_file : csv file with model properties (see ge2she)
    """
    from os import getcwd, chdir
    ori_dir = getcwd()
    # check if model extent defined
    if kwds.has_key('extent_x'):
        lower_left_x = min(kwds['extent_x']) # [0]
#        lower_left_x = 0
    else:
        lower_left_x = ''
    if kwds.has_key('extent_y'):
        lower_left_y = min(kwds['extent_y']) # [0]
#        lower_left_y = 0
    else:
        lower_left_y = ''
    if kwds.has_key('extent_z'):
        lower_left_z = min(kwds['extent_z']) # [0]
#
#   !!!!!!!!!!!!!!!!! HARDCODED BECAUSE IT DOESN'T WORK OTHERWISE!!!! CHECK!!!!
#
#        lower_left_z = 0
    else:
        lower_left_z = ''
        
    if kwds.has_key('update_from_geomodel') and kwds['update_from_geomodel']:
        if kwds.has_key('geomodeller_dir'):
            chdir(kwds['geomodeller_dir'])
        else:
            chdir(raw_input('Please enter path of geomodel: '))
        if kwds.has_key('geomodel_filename'):
            geomodel_file = kwds['geomodel_filename']
        else:
            geomodel_file = raw_input('Please enter filename of geomodel: ')
        S1.update_model_from_geomodeller_xml_file(geomodel_file,
                                                  lower_left_x = lower_left_x,
                                                  lower_left_y = lower_left_y,
                                                  lower_left_z = lower_left_z)
    if kwds.has_key('update_from_voxet_file') and kwds['update_from_voxet_file']:
        """update shemat geology array from voxet file, exported from GeoModeller"""
        S1.update_model_from_voxet_file(kwds['voxet_filename'], **kwds)
        if kwds.has_key('geomodel_properties') and kwds['geomodel_properties'] != "":
            S1.update_properties_from_csv_list(kwds['geomodel_properties'])

    if kwds.has_key('update_from_geology_grid') and kwds['update_from_geology_grid']:
        # update model from exported geology grid, for example created with 
        # the DOS executable exportRectilinearMeshCellCenter.exe
        # This option is a lot faster than updating the model directly from the xml file
        f = open(kwds['grid_filename'])
        lines = f.readlines()
        f.close()
        geol = []
        for line in lines:
            l = line.split(',')
            for l1 in l[:-1]:
                geol.append(int(l1))
        S1.set_array("GEOLOGY", geol)
        

    # final step: update properties from csv property file, according to geology
    if kwds.has_key('update_from_property_file') and kwds['update_from_property_file']:
        if kwds.has_key('geomodel_properties') and kwds['geomodel_properties'] != "":
            S1.update_properties_from_csv_list(kwds['geomodel_properties'])
    elif kwds.has_key('geomodel_properties') and kwds['geomodel_properties'] != "":
        S1.update_properties_from_csv_list(kwds['geomodel_properties'])
        # the elif statement is required for backwards compatibility...

        
    if kwds.has_key('baset') and kwds['baset']=='TEMP':
        por = S1.get_array("POR")
        n_layer = nx*ny
        for i in range(n_layer):
            if por[i] > 0:
                por[i] = - por[i]
        S1.set_array("POR", por)

    if kwds.has_key('thermal_cond_function_of_temp') and kwds['thermal_cond_function_of_temp']:
        # set flag to calculate thermal conductivity as a function of temperature,
        # see SHEEMAT book pg. 14 for equation
        koplng = S1.get("KOPLNG")
        koplng = koplng[:3]+'P'
        S1.set("KOPLNG",koplng)
    
    if kwds.has_key('equilibrium_layer') and kwds['equilibrium_layer'] > 0:
        # add thermal equilibrium layers at bottom of model
        S1.assing_thermal_equil_layers(kwds['equilibrium_layer'])
    
    if kwds.has_key('nml_filename'):
        filename = kwds['nml_filename']
    else:
        filename = "shemat_empty_project"
    chdir(ori_dir)
    create_shemat_control_file(filename)
    S1.write_file(filename)
    if kwds.has_key('execute_shemat') and kwds['execute_shemat']:
        print "Execute SHEMAT"
        execute_shemat()
    return S1

