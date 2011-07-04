#!/usr/bin/env python

"""
This utility provides functionality to convert OpenFOAM data the MED format. 
To obtain more detail information on this account it is possible to
run this script with '--help' command line option.
"""

## Copyright (C) 2010- Alexey Petrov
## Copyright (C) 2009-2010 Pebble Bed Modular Reactor (Pty) Limited (PBMR)
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
## 
## See https://csrcs.pbmr.co.za/svn/nea/prototypes/reaktor/foam2med
##
## Author : Alexey PETROV
##


#--------------------------------------------------------------------------------------
def print_d( the_message, the_debug_mode = False ):
    """
    Helper function to control output debug information
    """
    if the_debug_mode :
        print the_message
        pass
    pass


#--------------------------------------------------------------------------------------
def execute( the_case_dir, the_output_med_file, the_output_mesh_name, the_foam_time = None ):
    """
    This function defines procedure like Python API for this utility
    """
    import os, os.path   

    #  To identify the canonical pathes of the specified filenames
    the_case_dir = os.path.realpath( the_case_dir )
    print_d( "the_case_dir = \"%s\"" % the_case_dir )

    the_output_med_file = os.path.realpath( the_output_med_file )
    print_d( "the_output_med_file = \"%s\"" % the_output_med_file )

    # Definiton of the "root" and OpenFOAM "case"
    a_root_dir, a_case = os.path.split( the_case_dir )
    print_d( "a_root_dir = \"%s\", case = \"%s\"" % ( a_root_dir, a_case ) )

    # Remove all existing VTK data files
    import shutil
    a_vtk_folder = os.path.join( the_case_dir, "VTK" )
    if os.path.exists( a_vtk_folder ) :
        shutil.rmtree( a_vtk_folder )
        pass

    # Assembling command line arguments for execution of the foamToVTK utility
    a_command_line = "\"foamToVTK\""
    print_d( "${WM_PROJECT_VERSION} = %s" % os.environ[ "WM_PROJECT_VERSION" ] )
    if os.environ[ "WM_PROJECT_VERSION" ] < "1.5" :
        a_command_line += " \"%s\"" % ( os.path.join( a_root_dir ) )
        a_command_line += " \"%s\"" % ( os.path.basename( the_case_dir ) )
    else:
        a_command_line += " -case \"%s\"" % the_case_dir
        pass        

    # check, whether there will be data for particular time will should extracted only 
    if the_foam_time != None :
        print_d( "the_foam_time = %g" % the_foam_time )
        a_command_line += " -time %g" % the_foam_time
        pass                

    # Running of the foamToVTK utility
    print_d( "a_command_line = %s" % a_command_line )
    os.system( a_command_line )

    # Definition of the regular expression describing every number 
    import re
    a_number_expression = re.compile( "^[-+]?[0-9]+[\.]?[0-9]*([eE][-+]?[0-9]+)?$" )

    # Collecting of the timestamps
    a_time_stamps = []
    a_list_dir = os.listdir( the_case_dir )
    for a_dir_name in a_list_dir :
        if a_number_expression.match( a_dir_name ) != None :
            a_time_stamps.append( a_dir_name )
            pass
        pass

    a_time_stamps.sort()
    print_d( "a_time_stamps = %s" % a_time_stamps )

    # Collecting of the timestamp related VTK files
    a_vtk_files = {}
    a_list_dir = os.listdir( a_vtk_folder )
    a_vtk_file_expression = a_case + "_([0-9]+).vtk"
    a_vtk_expression = re.compile( a_vtk_file_expression )
    for a_dir_name in a_list_dir :
        if a_vtk_expression.match( a_dir_name ) != None :
            an_ordered_number = a_vtk_expression.sub( r"\1", a_dir_name )
            a_vtk_files[ an_ordered_number ] = a_dir_name
            pass
        pass
    print_d( "a_vtk_files = %s" % a_vtk_files )

    # To sort the obtained VTK files by its number
    a_vtk_keys = [ int( a_number ) for a_number in a_vtk_files.keys() ]
    a_vtk_keys.sort()
    print_d( "a_vtk_keys = %s" % a_vtk_keys )

    # To collect the VTK files according to the Foam time 
    a_time2file_list = []
    if the_foam_time == None :
        # The case when all existing time data are collected 
        a_vtk_files_number = len( a_vtk_files )
        a_time_stamps_number = len( a_time_stamps )
        for an_id in range( a_time_stamps_number ) :
            # It is necessary to walk in a reverse order
            # to support Foam time and VTK file consistency
            an_time_stamps_id = a_time_stamps_number - an_id - 1
            a_time_stamp = a_time_stamps[ an_time_stamps_id ]
            print_d( "a_time_stamp = %s" % a_time_stamp )
            
            a_vtk_file_id = a_vtk_files_number - an_id - 1
            a_vtk_key = str( a_vtk_keys[ a_vtk_file_id ] )
            print_d( "a_vtk_key = %s" % a_vtk_key )
            
            a_vtk_file = a_vtk_files[ a_vtk_key ]
            a_time2file = a_time_stamp + ":" + a_vtk_file
            a_time2file_list.append( a_time2file )
            pass
        pass
    else:
        # The case when only precise Foam time data is collected 
        a_time_stamp = "%g" % the_foam_time
        a_vtk_file = a_vtk_files.values()[ 0 ]
        a_time2file = a_time_stamp + ":" + a_vtk_file
        a_time2file_list.append( a_time2file )
        pass
    print_d( "a_time2file_list = %s" % a_time2file_list )

    # Remove an existing MED file to be able to create a new one with the same name
    if os.path.exists( the_output_med_file ) :
        os.remove( the_output_med_file )
        pass

    # Assembling command line arguments for execution of the vtk2med utility
    a_command_line = "\"%s\"" % ( "vtk2med" )
    a_command_line += " --input-vtk-directory=\"%s\"" % ( a_vtk_folder )
    a_command_line += " --time-stamps=\"%s\"" % ( "|".join( a_time2file_list ) )
    a_command_line += " --output-mesh-name=\"%s\"" % ( the_output_mesh_name )
    a_command_line += " --output-med-file=\"%s\"" % ( the_output_med_file )

    # Running of the vtk2med utility
    print_d( "a_command_line = %s" % a_command_line, False )

    return os.system( a_command_line ) == os.EX_OK


#--------------------------------------------------------------------------------------
def get_option_parser() :
    """
    This function defines command line options parser for this utility
    """

    an_usage = \
    """
    %prog \\
          --case-dir=${WM_PROJECT_USER_DIR}/run/tutorials/icoFoam/cavity \\
          --foam-time=0.3 \\
          --output-med-file=${WM_PROJECT_USER_DIR}/run/tutorials/icoFoam/cavity/cavity.med \\
          --output-mesh-name=foo 
    """

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    a_parser = OptionParser( usage = an_usage, version="%prog 2.1", formatter = a_help_formatter )
    
    # Definition of the command line arguments
    a_parser.add_option( "--case-dir",
                         metavar = "< OpenFOAM case directory >",
                         action = "store",
                         dest = "case_dir",
                         help = "location of OpenFOAM case directory" +
                         " (\"%default\", by default)",
                         default = "." )
    
    a_parser.add_option( "--foam-time",
                         metavar = "< time value to be taken into account >",
                         action = "store",
                         type = "float",
                         dest = "foam_time",
                         help = "time value to be taken into account" +
                         " (%default, by default)",
                         default = None )
    
    a_parser.add_option( "--output-mesh-name",
                         metavar = "< MED mesh name >",
                         action = "store",
                         dest = "mesh_name",
                         help = "name of mesh in the output MED file" +
                         " (\"%default\", by default)",
                         default = None )
    
    a_parser.add_option( "--output-med-file",
                         metavar = "< output MED file >",
                         action = "store",
                         dest = "med_file",
                         help = "name of the output MED file" +
                         " (\"%default\", by default)",
                         default = None )
    
    return a_parser


#--------------------------------------------------------------------------------------
class TFilePostProcessor :
    """
    This class defines object oriented Python API for this utility
    """
    def __init__( self, the_option_parser = get_option_parser() ) :
        """
        Constructs instance of this class
        """
        self.option_parser = the_option_parser
        self.output_mesh_name = None
        self.output_med_file = None
        pass

    def process_args( self ) :
        """
        Gets command line arguments and starts execution of the utility
        """
        an_options, an_args = self.option_parser.parse_args() 
        print_d( "an_options = %s" % an_options )
        
        return self.run( an_options.case_dir, 
                         an_options.med_file, 
                         an_options.mesh_name, 
                         an_options.foam_time )

    def run( self, the_case_dir, the_output_med_file, the_output_mesh_name, the_foam_time ) :
        """
        Runs the main functionality
        """
        import os, os.path   

        # If name for the mesh is not defined it will be the same one as for the case 
        self.output_mesh_name = the_output_mesh_name
        if the_output_mesh_name == None :
            self.output_mesh_name = os.path.basename( the_case_dir )
            pass
        print_d( "self.output_mesh_name = \"%s\"" % self.output_mesh_name )

        self.output_med_file = the_output_med_file
        if  self.output_med_file == None :
            # Generate a proper name for the output MED file
            self.output_med_file = "%s" % self.output_mesh_name

            if the_foam_time != None :
                self.output_med_file = "%s-%g" % ( self.output_mesh_name, the_foam_time )
                pass

            self.output_med_file += ".med"
            self.output_med_file = os.path.join( the_case_dir, self.output_med_file )
            pass
        print_d( "self.output_med_file = \"%s\"" % self.output_med_file )
        
        return execute( the_case_dir,
                        self.output_med_file, 
                        self.output_mesh_name, 
                        the_foam_time )

    def get_output_mesh_name( self ) :
        return self.output_mesh_name

    def get_output_med_file( self ) :
        return self.output_med_file

    pass


#--------------------------------------------------------------------------------------
# This piece of code will be perfomed only in case of invoking this script directly from shell
if __name__ == '__main__' :
    import os

    if TFilePostProcessor().process_args() == True :
        os._exit( os.EX_OK )
        pass

    os._exit( os.EX_USAGE )
    pass


#--------------------------------------------------------------------------------------
