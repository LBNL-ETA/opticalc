Release Notes:

0.0.18
- upgrade to pywincalc 3.3.1

0.0.17
- use pywincalc 3.2.0 in requirements

0.0.16
- Refactored error handling in calc_optical
- Added check when creating Wavelength data with direct and diffuse component

0.0.15

- Added a get_optical_standard method for creating a pywincalc optical standard from a pywincalc optical standard file.

0.0.14

- Updated pydantic dependency to 2.5.2
- Updated py_igsdb_base_data dependency to 0.0.44

0.0.13

- Updated pydantic dependency to 2.2.1
- Updated py_igsdb_base_data dependency to 0.0.34
- Update pywincalc to 3.2.0

0.0.5

- Updated pywincalc to 2.4.2
    - This pywincalc version has improved calculation of integrated spectral averages for shading layers with BSDF

0.0.6

- Updates integrated summary values models to reflect changes in how Checkertool structures these values.
- Updates ProductSubtype dataclass to match Checkertool.
- Update Product dataclass to use strings rather than enums, but validate those string values against values defined in
  enums.
- Add tests.

0.0.7

- Update pywincalc dependency
- Use py_igsdb_base_data for product dataclasses
