// Copyright (C) 2010- Alexey Petrov
//  Copyright (C) 2009-2010 Pebble Bed Modular Reactor (Pty) Limited (PBMR)
//  
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//  
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//  
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//  See https://csrcs.pbmr.co.za/svn/nea/prototypes/reaktor/foam2med
//
//  Author : Alexey PETROV
//

#include <VISU_Vtk2MedConvertor.hxx>

#include <boost/program_options.hpp>
using namespace boost::program_options;

#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
using namespace boost;

#include <iostream>
#include <sstream>
#include <map>
using namespace std;


//---------------------------------------------------------------
#define print( MESSAGE )

//#define print_d( MESSAGE ) cout << MESSAGE << endl
#define print_d( MESSAGE )


//---------------------------------------------------------------
int main( int argc, char* argv[] )
{
    options_description desc( "Allowed options" );
    desc.add_options()
        ( "help,h", "print usage message" )
        ( "input-vtk-directory,d", value< string >(), "a directory with VTK files" )
        ( "time-stamps,t", value< string >(), "a timestamps to VTK file mapping" )
        ( "output-mesh-name,m", value< string >(), "a MED mesh name" )
        ( "output-med-file,f", value< string >(), "an output MED filename" )
	;
    
    variables_map vm;
    store( parse_command_line( argc, argv, desc ), vm );
    
    if ( vm.count( "help" ) ) {  
	cout << desc << "\n";
	return 0;
    }

    // Processing of the command line args
    string an_input_vtk_directory = vm[ "input-vtk-directory" ].as< string >();
    print_d( "--input-vtk-directory=\"" << an_input_vtk_directory << "\"" );

    string a_time_stamps = vm[ "time-stamps" ].as< string >();
    print( "--time-stamps=\"" << a_time_stamps << "\"" );

    typedef vector< string > TSplitResult;
    TSplitResult a_split_time_stamps;
    split( a_split_time_stamps, a_time_stamps, is_any_of("|"), token_compress_on );   

    typedef map< double, string > TTimeStamp2Filename;
    TTimeStamp2Filename aTimeStamp2Filename;
    {
	TSplitResult::const_iterator anIter = a_split_time_stamps.begin();
	TSplitResult::const_iterator anEnd = a_split_time_stamps.end();
	for ( ; anIter != anEnd; anIter++ ) {
	    TSplitResult a_split_time_stamp;
	    const TSplitResult::value_type& a_time_stamp = *anIter;
	    split( a_split_time_stamp, a_time_stamp, is_any_of(":"), token_compress_on );
	    
	    istringstream aStream( a_split_time_stamp[ 0 ] );
	    double aTime;
	    aStream >> aTime;
	    
	    aTimeStamp2Filename[ aTime ] = a_split_time_stamp[ 1 ];
	    print_d( aTime << " = \"" << a_split_time_stamp[ 1 ] << "\"" );
	}
    }

    string a_med_mesh_name = vm[ "output-mesh-name" ].as< string >();
    print_d( "--output-mesh-name=\"" << a_med_mesh_name << "\"" );

    string a_med_filename = vm[ "output-med-file" ].as< string >();
    print_d( "--output-med-file=\"" << a_med_filename << "\"" );

    VISU_Vtk2MedConvertor aConvertor;
    aConvertor.setMEDFileName( a_med_filename );

    TTimeStamp2Filename::const_iterator anIter = aTimeStamp2Filename.begin();
    TTimeStamp2Filename::const_iterator anEnd = aTimeStamp2Filename.end();

    VISU_Vtk2MedConvertor::TVectorDouble aTimeStamps;
    // The first VTK file need to be given separately
    {
	TTimeStamp2Filename::mapped_type aFilename = anIter->second; 
	aFilename = an_input_vtk_directory + "/" + aFilename;
	aConvertor.setFirstVTKFileName( aFilename );

	const TTimeStamp2Filename::key_type& aTime = anIter->first;  
	aTimeStamps.push_back( aTime );
    }

    VISU_Vtk2MedConvertor::TVectorString aFilenames;
    for ( ++anIter; anIter != anEnd; anIter++ ) {
	const TTimeStamp2Filename::key_type& aTime = anIter->first;  
	aTimeStamps.push_back( aTime );

	TTimeStamp2Filename::mapped_type aFilename = anIter->second;  
	aFilename = an_input_vtk_directory + "/" + aFilename;
	aFilenames.push_back( aFilename );
    }

    aConvertor.setDataVTKFileNames( aFilenames );
    aConvertor.setTimeStamps( aTimeStamps );

    aConvertor.setMeshName( a_med_mesh_name );

    aConvertor.addToIgnoringFieldList("cellID");
    aConvertor.setCellDataFieldNameIDS("cellID");

    return aConvertor.Execute();
}
