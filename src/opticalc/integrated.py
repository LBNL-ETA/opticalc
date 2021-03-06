import logging

import pywincalc
from py_igsdb_base_data.optical import OpticalStandardMethodResults, OpticalColorResults, \
    IntegratedSpectralAveragesSummaryValues, OpticalColorFluxResults, OpticalColorResult, ThermalIRResults, \
    OpticalStandardMethodFluxResults, \
    IntegratedSpectralAveragesSummaryValuesFactory
from py_igsdb_base_data.product import BaseProduct
from py_igsdb_base_data.standard import CalculationStandardMethodTypes

from opticalc.exceptions import SpectralAveragesSummaryCalculationException
from opticalc.util import convert_trichromatic_result, convert_lab_result, convert_rgb_result, convert_product

logger = logging.getLogger(__name__)


def calc_optical(glazing_system: pywincalc.GlazingSystem, method_name: str) -> OpticalStandardMethodResults:
    try:
        CalculationStandardMethodTypes[method_name]
    except KeyError:
        raise ValueError(f"Invalid method: {method_name}")

    translated_results = OpticalStandardMethodResults()
    try:
        results = glazing_system.optical_method_results(method_name)
        system_results = results.system_results
        translated_results.transmittance_front = OpticalStandardMethodFluxResults(
            direct_direct=system_results.front.transmittance.direct_direct,
            direct_diffuse=system_results.front.transmittance.direct_diffuse,
            direct_hemispherical=system_results.front.transmittance.direct_hemispherical,
            diffuse_diffuse=system_results.front.transmittance.diffuse_diffuse,
            matrix=system_results.front.transmittance.matrix)

        translated_results.transmittance_back = OpticalStandardMethodFluxResults(
            direct_direct=system_results.back.transmittance.direct_direct,
            direct_diffuse=system_results.back.transmittance.direct_diffuse,
            direct_hemispherical=system_results.back.transmittance.direct_hemispherical,
            diffuse_diffuse=system_results.back.transmittance.diffuse_diffuse,
            matrix=system_results.back.transmittance.matrix)

        translated_results.reflectance_front = OpticalStandardMethodFluxResults(
            direct_direct=system_results.front.reflectance.direct_direct,
            direct_diffuse=system_results.front.reflectance.direct_diffuse,
            direct_hemispherical=system_results.front.reflectance.direct_hemispherical,
            diffuse_diffuse=system_results.front.reflectance.diffuse_diffuse,
            matrix=system_results.front.reflectance.matrix)

        translated_results.reflectance_back = OpticalStandardMethodFluxResults(
            direct_direct=system_results.back.reflectance.direct_direct,
            direct_diffuse=system_results.back.reflectance.direct_diffuse,
            direct_hemispherical=system_results.back.reflectance.direct_hemispherical,
            diffuse_diffuse=system_results.back.reflectance.diffuse_diffuse,
            matrix=system_results.back.reflectance.matrix)

        translated_results.absorptance_front_direct = results.layer_results[0].front.absorptance.direct
        translated_results.absorptance_back_direct = results.layer_results[0].back.absorptance.direct
        translated_results.absorptance_front_hemispheric = results.layer_results[0].front.absorptance.diffuse
        translated_results.absorptance_back_hemispheric = results.layer_results[0].back.absorptance.diffuse

    except Exception as e:
        translated_results.error = e

    return translated_results


def calc_color(glazing_system: pywincalc.GlazingSystem) -> OpticalColorResults:
    """
    Uses pywincalc to generate color information for a given glazing system.
    Returns information in a populated instance of the OpticalColorResults dataclass

    Args:
        glazing_system: Instance of a pywincalc GlazingSystem

    Returns:
        An instance of OpticalColorResults dataclass populated with results.

    Raises:
        SpectralAveragesSummaryCalculationException if an error is encountered when generating or parsing
        results.
    """

    translated_results = OpticalColorResults()
    try:
        results = glazing_system.color()
        results = results.system_results
        direct_direct_front_transmittance_trichromatic = convert_trichromatic_result(
            results.front.transmittance.direct_direct.trichromatic)
        direct_direct_front_transmittance_lab = convert_lab_result(results.front.transmittance.direct_direct.lab)
        direct_direct_front_transmittance_rgb = convert_rgb_result(results.front.transmittance.direct_direct.rgb)

        direct_diffuse_front_transmittance_trichromatic = convert_trichromatic_result(
            results.front.transmittance.direct_diffuse.trichromatic)
        direct_diffuse_front_transmittance_lab = convert_lab_result(results.front.transmittance.direct_diffuse.lab)
        direct_diffuse_front_transmittance_rgb = convert_rgb_result(results.front.transmittance.direct_diffuse.rgb)

        direct_hemispherical_front_transmittance_trichromatic = convert_trichromatic_result(
            results.front.transmittance.direct_hemispherical.trichromatic)
        direct_hemispherical_front_transmittance_lab = convert_lab_result(
            results.front.transmittance.direct_hemispherical.lab)
        direct_hemispherical_front_transmittance_rgb = convert_rgb_result(
            results.front.transmittance.direct_hemispherical.rgb)

        diffuse_diffuse_front_transmittance_trichromatic = convert_trichromatic_result(
            results.front.transmittance.diffuse_diffuse.trichromatic)
        diffuse_diffuse_front_transmittance_lab = convert_lab_result(results.front.transmittance.diffuse_diffuse.lab)
        diffuse_diffuse_front_transmittance_rgb = convert_rgb_result(results.front.transmittance.diffuse_diffuse.rgb)

        translated_results.transmittance_front = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_front_transmittance_trichromatic,
                lab=direct_direct_front_transmittance_lab,
                rgb=direct_direct_front_transmittance_rgb),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_front_transmittance_trichromatic,
                lab=direct_diffuse_front_transmittance_lab,
                rgb=direct_diffuse_front_transmittance_rgb),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_front_transmittance_trichromatic,
                lab=direct_hemispherical_front_transmittance_lab,
                rgb=direct_hemispherical_front_transmittance_rgb),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_front_transmittance_trichromatic,
                lab=diffuse_diffuse_front_transmittance_lab,
                rgb=diffuse_diffuse_front_transmittance_rgb))

        direct_direct_front_reflectance_trichromatic = convert_trichromatic_result(
            results.front.reflectance.direct_direct.trichromatic)
        direct_direct_front_reflectance_lab = convert_lab_result(results.front.reflectance.direct_direct.lab)
        direct_direct_front_reflectance_rgb = convert_rgb_result(results.front.reflectance.direct_direct.rgb)

        direct_diffuse_front_reflectance_trichromatic = convert_trichromatic_result(
            results.front.reflectance.direct_diffuse.trichromatic)
        direct_diffuse_front_reflectance_lab = convert_lab_result(results.front.reflectance.direct_diffuse.lab)
        direct_diffuse_front_reflectance_rgb = convert_rgb_result(results.front.reflectance.direct_diffuse.rgb)

        direct_hemispherical_front_reflectance_trichromatic = convert_trichromatic_result(
            results.front.reflectance.direct_hemispherical.trichromatic)
        direct_hemispherical_front_reflectance_lab = convert_lab_result(
            results.front.reflectance.direct_hemispherical.lab)
        direct_hemispherical_front_reflectance_rgb = convert_rgb_result(
            results.front.reflectance.direct_hemispherical.rgb)

        diffuse_diffuse_front_reflectance_trichromatic = convert_trichromatic_result(
            results.front.reflectance.diffuse_diffuse.trichromatic)
        diffuse_diffuse_front_reflectance_lab = convert_lab_result(results.front.reflectance.diffuse_diffuse.lab)
        diffuse_diffuse_front_reflectance_rgb = convert_rgb_result(results.front.reflectance.diffuse_diffuse.rgb)

        translated_results.reflectance_front = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_front_reflectance_trichromatic,
                lab=direct_direct_front_reflectance_lab,
                rgb=direct_direct_front_reflectance_rgb),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_front_reflectance_trichromatic,
                lab=direct_diffuse_front_reflectance_lab,
                rgb=direct_diffuse_front_reflectance_rgb),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_front_reflectance_trichromatic,
                lab=direct_hemispherical_front_reflectance_lab,
                rgb=direct_hemispherical_front_reflectance_rgb),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_front_reflectance_trichromatic,
                lab=diffuse_diffuse_front_reflectance_lab,
                rgb=diffuse_diffuse_front_reflectance_rgb))

        direct_direct_back_transmittance_trichromatic = convert_trichromatic_result(
            results.back.transmittance.direct_direct.trichromatic)
        direct_direct_back_transmittance_lab = convert_lab_result(results.back.transmittance.direct_direct.lab)
        direct_direct_back_transmittance_rgb = convert_rgb_result(results.back.transmittance.direct_direct.rgb)

        direct_diffuse_back_transmittance_trichromatic = convert_trichromatic_result(
            results.back.transmittance.direct_diffuse.trichromatic)
        direct_diffuse_back_transmittance_lab = convert_lab_result(results.back.transmittance.direct_diffuse.lab)
        direct_diffuse_back_transmittance_rgb = convert_rgb_result(results.back.transmittance.direct_diffuse.rgb)

        direct_hemispherical_back_transmittance_trichromatic = convert_trichromatic_result(
            results.back.transmittance.direct_hemispherical.trichromatic)
        direct_hemispherical_back_transmittance_lab = convert_lab_result(
            results.back.transmittance.direct_hemispherical.lab)
        direct_hemispherical_back_transmittance_rgb = convert_rgb_result(
            results.back.transmittance.direct_hemispherical.rgb)

        diffuse_diffuse_back_transmittance_trichromatic = convert_trichromatic_result(
            results.back.transmittance.diffuse_diffuse.trichromatic)
        diffuse_diffuse_back_transmittance_lab = convert_lab_result(results.back.transmittance.diffuse_diffuse.lab)
        diffuse_diffuse_back_transmittance_rgb = convert_rgb_result(results.back.transmittance.diffuse_diffuse.rgb)

        translated_results.transmittance_back = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_back_transmittance_trichromatic,
                lab=direct_direct_back_transmittance_lab,
                rgb=direct_direct_back_transmittance_rgb),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_back_transmittance_trichromatic,
                lab=direct_diffuse_back_transmittance_lab,
                rgb=direct_diffuse_back_transmittance_rgb),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_back_transmittance_trichromatic,
                lab=direct_hemispherical_back_transmittance_lab,
                rgb=direct_hemispherical_back_transmittance_rgb),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_back_transmittance_trichromatic,
                lab=diffuse_diffuse_back_transmittance_lab,
                rgb=diffuse_diffuse_back_transmittance_rgb))

        direct_direct_back_reflectance_trichromatic = convert_trichromatic_result(
            results.back.reflectance.direct_direct.trichromatic)
        direct_direct_back_reflectance_lab = convert_lab_result(results.back.reflectance.direct_direct.lab)
        direct_direct_back_reflectance_rgb = convert_rgb_result(results.back.reflectance.direct_direct.rgb)

        direct_diffuse_back_reflectance_trichromatic = convert_trichromatic_result(
            results.back.reflectance.direct_diffuse.trichromatic)
        direct_diffuse_back_reflectance_lab = convert_lab_result(results.back.reflectance.direct_diffuse.lab)
        direct_diffuse_back_reflectance_rgb = convert_rgb_result(results.back.reflectance.direct_diffuse.rgb)

        direct_hemispherical_back_reflectance_trichromatic = convert_trichromatic_result(
            results.back.reflectance.direct_hemispherical.trichromatic)
        direct_hemispherical_back_reflectance_lab = convert_lab_result(
            results.back.reflectance.direct_hemispherical.lab)
        direct_hemispherical_back_reflectance_rgb = convert_rgb_result(
            results.back.reflectance.direct_hemispherical.rgb)

        diffuse_diffuse_back_reflectance_trichromatic = convert_trichromatic_result(
            results.back.reflectance.diffuse_diffuse.trichromatic)
        diffuse_diffuse_back_reflectance_lab = convert_lab_result(results.back.reflectance.diffuse_diffuse.lab)
        diffuse_diffuse_back_reflectance_rgb = convert_rgb_result(results.back.reflectance.diffuse_diffuse.rgb)

        translated_results.reflectance_back = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_back_reflectance_trichromatic,
                lab=direct_direct_back_reflectance_lab,
                rgb=direct_direct_back_reflectance_rgb),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_back_reflectance_trichromatic,
                lab=direct_diffuse_back_reflectance_lab,
                rgb=direct_diffuse_back_reflectance_rgb),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_back_reflectance_trichromatic,
                lab=direct_hemispherical_back_reflectance_lab,
                rgb=direct_hemispherical_back_reflectance_rgb),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_back_reflectance_trichromatic,
                lab=diffuse_diffuse_back_reflectance_lab,
                rgb=diffuse_diffuse_back_reflectance_rgb))

    except Exception as e:
        translated_results.error = e

    return translated_results


def generate_thermal_ir_results(optical_standard: pywincalc.OpticalStandard,
                                pywincalc_layer: pywincalc.ProductDataOpticalAndThermal) -> ThermalIRResults:
    translated_results = ThermalIRResults()
    pywincalc_results = pywincalc.calc_thermal_ir(optical_standard, pywincalc_layer)
    translated_results.transmittance_front_diffuse_diffuse = pywincalc_results.transmittance_front_diffuse_diffuse
    translated_results.transmittance_back_diffuse_diffuse = pywincalc_results.transmittance_back_diffuse_diffuse
    translated_results.absorptance_front_hemispheric = pywincalc_results.emissivity_front_hemispheric
    translated_results.absorptance_back_hemispheric = pywincalc_results.emissivity_back_hemispheric
    return translated_results


def generate_integrated_spectral_averages_summary(product: BaseProduct,
                                                  optical_standard: pywincalc.OpticalStandard) \
        -> IntegratedSpectralAveragesSummaryValues:
    """
    Uses pywincalc to generate an integrated spectral averages summary for a given product
    and standard.

    Args:
        product:            Instance of a product dataclass
        optical_standard:   Instance of a pywincalc OpticalStandard class.

    Returns:
        An instance of IntegratedSpectralAveragesSummaryValues dataclass populated with results.

    Raises:
        SpectralAveragesSummaryCalculationException if an error is encountered when generating or parsing
        results.
    """

    summary_results: IntegratedSpectralAveragesSummaryValues = IntegratedSpectralAveragesSummaryValuesFactory.create()
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal = convert_product(product)
    glazing_system: pywincalc.GlazingSystem = pywincalc.GlazingSystem(optical_standard=optical_standard,
                                                                      solid_layers=[pywincalc_layer])

    for method_name in [item.name for item in CalculationStandardMethodTypes]:
        # Only calculate results for a method if it's supported in the current optical standard...
        if method_name in optical_standard.methods:
            try:
                results: OpticalStandardMethodResults = calc_optical(glazing_system, method_name)
                setattr(summary_results, method_name.lower(), results)
            except Exception as e:
                error_msg = f"calc_optical() call failed for method {method_name}"
                logger.error(f"OptiCalc : {error_msg} : {e}")
                raise SpectralAveragesSummaryCalculationException(error_msg) from e
        else:
            logger.info(f"generate_integrated_spectral_averages_summary() skipping method {method_name} as its not "
                        f"present in the methods for optical standard {optical_standard} "
                        f"( methods : {optical_standard.methods} )")

    try:
        summary_results.color = calc_color(glazing_system)
    except Exception as e:
        error_msg = f"calc_color() call failed for product: {product} " \
                    f"optical_standard : {optical_standard} " \
                    f"glazing_system {glazing_system}"
        logger.error(f"OptiCalc : {error_msg}  error : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    try:
        summary_results.thermal_ir = generate_thermal_ir_results(optical_standard, pywincalc_layer)
    except Exception as e:
        error_msg = f"generate_thermal_ir_results() call failed for " \
                    f"layer: {pywincalc_layer} " \
                    f"optical_standard: {optical_standard} "
        logger.error(f"OptiCalc : {error_msg} : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    return summary_results
