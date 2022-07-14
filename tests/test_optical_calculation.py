import json
import os

import pywincalc
from py_igsdb_base_data.optical import OpticalStandardMethodResults
from py_igsdb_base_data.standard import CalculationStandardMethodTypes

from opticalc.integrated import calc_optical
from py_igsdb_base_data.product import BaseProduct
from opticalc.util import convert_product

OPTICAL_STANDARD_PATH_NFRC = os.path.join(os.path.dirname(__file__), "./standards/W5_NFRC_2003.std")


def test_generate_optical_values():
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
    glazing_system: pywincalc.GlazingSystem = pywincalc.GlazingSystem(optical_standard=optical_standard,
                                                                      solid_layers=[pywincalc_layer])

    for method_name in [item.name for item in CalculationStandardMethodTypes]:
        # Only calculate results for a method if it's supported in the current optical standard...
        if method_name in optical_standard.methods:
            values: OpticalStandardMethodResults = calc_optical(glazing_system=glazing_system,
                                                                method_name=method_name)

            assert values is not None, "calc_optical returned None"
            # TODO: Test actual values returned for known glazing system and method.
