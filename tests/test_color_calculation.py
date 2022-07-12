import json
import os

import pywincalc
from py_igsdb_optical_data.optical import OpticalColorResults

from opticalc.integrated import calc_color
from opticalc.product import Product
from opticalc.util import convert_product

OPTICAL_STANDARD_PATH_NFRC = os.path.join(os.path.dirname(__file__), "./standards/W5_NFRC_2003.std")


def test_generate_color_values():
    """
    Create a sample MONOLITHIC product and generate
    color information.
    """

    optical_standard: pywincalc.OpticalStandard = pywincalc.load_standard(OPTICAL_STANDARD_PATH_NFRC)
    sample_monolithic_path = os.path.join(os.path.dirname(__file__), "./data/sample_monolithic.json")
    with open(sample_monolithic_path) as f:
        sample_monolithic_json = json.load(f)

    product = Product(**sample_monolithic_json)
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal = convert_product(product)
    glazing_system: pywincalc.GlazingSystem = pywincalc.GlazingSystem(optical_standard=optical_standard,
                                                                      solid_layers=[pywincalc_layer])

    values: OpticalColorResults = calc_color(glazing_system=glazing_system)

    assert values is not None, "calc_color returned None"
    # TODO: Test actual values returned for known glazing system.
