Berkeley Lab WINDOW Calc Engine (CalcEngine) Copyright (c) 2016 - 2019, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of
Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Innovation &
Partnerships Office at IPO@lbl.gov.

NOTICE. This Software was developed under funding from the U.S. Department of Energy and the U.S. Government
consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its
behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the
public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.

# opticalc

This is a library to help generate integrated optical results for single glazing layers
using https://github.com/LBNL-ETA/pywincalc to perform the calculations. It is used primarly by Checkertool V2.

Why not include this logic directly in Pywincalc? Pywincalc is generated programmatically from wincalc and does 
not have much in the way of custom, python-based logic and classes that help a user make sense of the types and shapes
of data and the nature of various operations. This library serves as a location for that kind of python-based code.
