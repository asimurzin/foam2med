dnl confFlu - pythonFlu configuration package
dnl Copyright (C) 2010- Alexey Petrov
dnl Copyright (C) 2009-2010 Pebble Bed Modular Reactor (Pty) Limited (PBMR)
dnl 
dnl This program is free software: you can redistribute it and/or modify
dnl it under the terms of the GNU General Public License as published by
dnl the Free Software Foundation, either version 3 of the License, or
dnl (at your option) any later version.
dnl
dnl This program is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl GNU General Public License for more details.
dnl 
dnl You should have received a copy of the GNU General Public License
dnl along with this program.  If not, see <http://www.gnu.org/licenses/>.
dnl 
dnl See http://sourceforge.net/projects/pythonflu
dnl
dnl Author : Alexey PETROV
dnl


dnl --------------------------------------------------------------------------------
AC_DEFUN([FOAM2MED_CHECK_FOAM2MED],
[
AC_CHECKING(for foam2med package)

AC_REQUIRE([CONFFLU_CHECK_SALOME_KERNEL])
AC_REQUIRE([CONFFLU_CHECK_SALOME_MED])
AC_REQUIRE([CONFFLU_CHECK_SALOME_GUI])
AC_REQUIRE([CONFFLU_CHECK_SALOME_VISU])

AC_REQUIRE([CONFFLU_CHECK_PYTHON])

AC_REQUIRE([CONFFLU_CHECK_HDF5])
AC_REQUIRE([CONFFLU_CHECK_VTK])
AC_REQUIRE([CONFFLU_CHECK_BOOST_PROGRAM_OPTIONS])

AC_SUBST(ENABLE_FOAM2MED)

foam2med_ok=no


dnl --------------------------------------------------------------------------------
AC_CHECK_PROG( [foam2med_exe], [vtk2med], [yes], [no] )


dnl --------------------------------------------------------------------------------
AC_MSG_CHECKING( foam2med python module )
foam2med_python_module=[`python -c "import foam2med; print \"yes\"" 2>/dev/null`]
AC_MSG_RESULT( ${foam2med_python_module} )


dnl --------------------------------------------------------------------------------
if test "x${foam2med_exe}" = "xyes" && test "x${foam2med_python_module}" = "xyes"; then
   foam2med_ok=yes
else
   AC_MSG_WARN([install or sourced foam2med package])
fi


dnl --------------------------------------------------------------------------------
ENABLE_FOAM2MED=${foam2med_ok}
])


dnl --------------------------------------------------------------------------------
