import json
import os
from math import isclose

import pywincalc
from py_igsdb_base_data.optical import IntegratedSpectralAveragesSummaryValues

from opticalc.integrated import generate_integrated_spectral_averages_summary
from opticalc.product import Product

OPTICAL_STANDARD_PATH_NFRC = os.path.join(os.path.dirname(__file__), "./standards/W5_NFRC_2003.std")


def test_generate_integrated_spectral_averages_summary():
    """
    Create a sample MONOLITHIC product and generate
    integrated spectral averages summary.
    :return:
    """

    optical_standard = pywincalc.load_standard(OPTICAL_STANDARD_PATH_NFRC)
    sample_monolithic_path = os.path.join(os.path.dirname(__file__), "./data/sample_monolithic.json")
    with open(sample_monolithic_path) as f:
        sample_monolithic_json = json.load(f)

    product = Product(**sample_monolithic_json)
    
    values: IntegratedSpectralAveragesSummaryValues = generate_integrated_spectral_averages_summary(
        product=product,
        optical_standard=optical_standard)        
    
    assert isclose(values.solar.transmittance_front.direct_hemispherical, 0.847468218237298, abs_tol=1e-6)
    assert isclose(values.thermal_ir.absorptance_front_hemispheric, 0.839999974, abs_tol=1e-8)
    assert isclose(values.thermal_ir.absorptance_back_hemispheric, 0.839999974, abs_tol=1e-8)
    assert values.thermal_ir.emissivity_front_hemispheric == values.thermal_ir.absorptance_front_hemispheric
    assert values.thermal_ir.emissivity_back_hemispheric == values.thermal_ir.absorptance_back_hemispheric
    assert values.thermal_ir.transmittance_front_diffuse_diffuse == 0
    assert values.thermal_ir.transmittance_back_diffuse_diffuse == 0
    

def test_calculate_emissivity_from_wavelengths():
    """
    Create a sample product with measurements into the IR range and generate
    integrated spectral averages summary.
    :return:
    """

    optical_standard = pywincalc.load_standard(OPTICAL_STANDARD_PATH_NFRC)
    sample_path = os.path.join(os.path.dirname(__file__), "./data/sample_with_measured_ir.json")
    with open(sample_path) as f:
        sample_json = json.load(f)

    product = Product(**sample_json)
    
    values: IntegratedSpectralAveragesSummaryValues = generate_integrated_spectral_averages_summary(
        product=product,
        optical_standard=optical_standard)        
    assert isclose(values.thermal_ir.absorptance_front_hemispheric, 0.8402627824166977, abs_tol=1e-8)
    assert isclose(values.thermal_ir.absorptance_back_hemispheric, 0.0077240385089490824, abs_tol=1e-8)
    assert values.thermal_ir.emissivity_front_hemispheric == values.thermal_ir.absorptance_front_hemispheric
    assert values.thermal_ir.emissivity_back_hemispheric == values.thermal_ir.absorptance_back_hemispheric
    assert values.thermal_ir.transmittance_front_diffuse_diffuse == 0
    assert values.thermal_ir.transmittance_back_diffuse_diffuse == 0
    
