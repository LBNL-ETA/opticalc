# Release Notes

0.0.34

- Workaround for diffuse measurements to avoid BSDF hemisphere requirement bug in Pywincal 3.7.3

0.0.33

- Update pywincalc to 3.7.3

0.0.32

- Update pywincalc to 3.7.2

0.0.31

- Bump for py_igsdb_base_data update.

0.0.30

- Update to new 'NOT_APPLICABLE' value for coated side.

0.0.29

- Improve handling of spectral data when combining specular and diffuse.

0.0.28

- Convert empty strings in measured data to None before reading and converting to Float.
- Improve logic in convert_wavelength_data

0.0.27

- Fix small bug in convert_wavelength_data().

0.0.26

- Refactor convert_wavelength_data().

0.0.25

- Add method to get version of pywincalc used internally (e.g. for summary value calculation)

0.0.24

- Update error message text

0.0.23

- Update dependencies

0.0.22

- Handle roller shade subtype as pywincalc MONOLITHIC

0.0.21

- Do not call pywincalc calc_thermal_ir if IR wavelength data is not present.

0.0.20

- Updates py_igsdb_base_data to 0.0.51

0.0.19

- Ignore emissivity results when calculating thermal IR results for SHADE_MATERIAL products.

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
