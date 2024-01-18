import json
import os

import pywincalc
from pywincalc import ThermalIRResults
from py_igsdb_base_data.product import BaseProduct

from opticalc.integrated import calc_thermal_ir_results
from opticalc.util import convert_product

OPTICAL_STANDARD_PATH_NFRC = os.path.join(os.path.dirname(__file__), "./standards/W5_NFRC_2003.std")


def test_generate_thermal_ir_values():
    """
    Create a sample MONOLITHIC product and generate
    color information.
    """

    optical_standard: pywincalc.OpticalStandard = pywincalc.load_standard(OPTICAL_STANDARD_PATH_NFRC)
    sample_monolithic_path = os.path.join(os.path.dirname(__file__), "./data/valid_monolithic_1.json")
    with open(sample_monolithic_path) as f:
        sample_monolithic_json = json.load(f)

    product = BaseProduct.from_dict(sample_monolithic_json)
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal = convert_product(product)

    values: ThermalIRResults = calc_thermal_ir_results(optical_standard=optical_standard,
                                                           pywincalc_layer=pywincalc_layer)

    assert values is not None, "calc_optical returned None"
    # TODO: Test actual values returned for known glazing system and method.
