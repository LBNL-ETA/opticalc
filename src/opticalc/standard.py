import os
from pathlib import Path

import pywincalc


def get_optical_standard(standard_file_path: Path) -> pywincalc.OpticalStandard:
    """
    Given a file path to an optical standard .std file, create and
    return a pywincalc.OpticalStandard instance.
    """
    standard_file_path: str = os.fspath(standard_file_path.resolve())
    pwc_standard = pywincalc.load_standard(standard_file_path)
    return pwc_standard
