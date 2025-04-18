# Changelog

## 1.2.4 - 2025-04-18

### Changed
- Better error detection when inspecting port specifications


## 1.2.2 - 2025-04-16

### Fixed
- Dynamic UI information


## 1.2.1 - 2025-03-13

### Fixed
- Dynamic UI information


## 1.2.0 - 2025-03-04

### Added
- Electrical ports and terminals.


## 1.1.1 - 2024-12-19

### Fixed
- Docstrings from a few components have been fixed.


## 1.1.0 - 2024-12-03

### Added
- Arguments `slab_removal_width` and `input_ext` to `double_linear_inverse_taper`.
- Arguments `center` and `exclusion_zone_width` to `chip_frame`.
- Argument `start_section_width` to `s_bend_vert`.
- Parametric components `dir_coupl`, `heater_pad`, `heater_straight`, and `heated_straight_waveguide`.

### Changed
- `chip_frame` is centered around the origin by default.
- `mz_modulator_unbalanced` default length.

### Fixed
- Removed port symmetries that were only valid for fundamental modes.


## 1.0.1 - 2024-10-17

### Fixed
- Add missing technology docstring.
- Fixed port symmetries in MMI2x2.


## 1.0.0 - 2024-10-17

### Added
- Initial release.
