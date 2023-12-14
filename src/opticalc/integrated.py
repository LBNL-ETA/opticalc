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
    """
    Uses pywincalc to generate optical information for a given glazing system.

    Args:
        glazing_system: Instance of a pywincalc GlazingSystem
        method_name:    Name of the optical method to use. Must be a valid method name in pywincalc.

    Returns:
        An instance of OpticalStandardMethodResults dataclass populated with results.

    Raises:
        ValueError if method_name is not a valid method name in pywincalc.
        Exception if an error is encountered when generating or parsing results.

    """
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
        logger.exception(f"calc_optical() call failed for method {method_name}")
        raise e

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
        ValueError if glazing_system is None.
        Exception if an error is encountered when generating or parsing results.
    """

    if not glazing_system:
        raise ValueError("glazing_system is None")

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
        logger.exception(f"calc_color() call failed")
        raise e

    return translated_results


def generate_thermal_ir_results(optical_standard: pywincalc.OpticalStandard,
                                pywincalc_layer: pywincalc.ProductDataOpticalAndThermal) -> ThermalIRResults:
    """
    Uses pywincalc to generate thermal IR information for a given layer and standard.

    Args:
        optical_standard:   Instance of a pywincalc OpticalStandard class.
        pywincalc_layer:    Instance of a pywincalc ProductDataOpticalAndThermal class.

    Returns:
        An instance of ThermalIRResults dataclass populated with results.


    """

    if not optical_standard:
        raise ValueError("optical_standard is None")
    if not pywincalc_layer:
        raise ValueError("pywincalc_layer is None")

    try:
        translated_results = ThermalIRResults()
        pywincalc_results = pywincalc.calc_thermal_ir(optical_standard, pywincalc_layer)
        translated_results.transmittance_front_diffuse_diffuse = pywincalc_results.transmittance_front_diffuse_diffuse
        translated_results.transmittance_back_diffuse_diffuse = pywincalc_results.transmittance_back_diffuse_diffuse
        translated_results.absorptance_front_hemispheric = pywincalc_results.emissivity_front_hemispheric
        translated_results.absorptance_back_hemispheric = pywincalc_results.emissivity_back_hemispheric
    except Exception as e:
        logger.exception(f"generate_thermal_ir_results() call failed")
        raise e

    return translated_results


def generate_integrated_spectral_averages_summary(product: BaseProduct,
                                                  optical_standard: pywincalc.OpticalStandard) \
        -> IntegratedSpectralAveragesSummaryValues:
    """
    Uses pywincalc to generate an integrated spectral averages summary for a given product
    and standard. Returns information in a populated instance of the IntegratedSpectralAveragesSummaryValues dataclass.

    Note: some optical calculations may be skipped if the optical_standard passed in does not support them.

    Args:
        product:            Instance of a BaseProduct dataclass.
        optical_standard:   Instance of a pywincalc OpticalStandard class.

    Returns:
        An instance of IntegratedSpectralAveragesSummaryValues dataclass populated with results.

    Raises:
        ValueError if product or optical_standard is None.
        SpectralAveragesSummaryCalculationException if an error is encountered when generating or parsing
        results.
    """

    if not product:
        raise ValueError("product is None")
    if not optical_standard:
        raise ValueError("optical_standard is None")

    summary_results: IntegratedSpectralAveragesSummaryValues = IntegratedSpectralAveragesSummaryValuesFactory.create()
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal = convert_product(product)
    glazing_system: pywincalc.GlazingSystem = pywincalc.GlazingSystem(optical_standard=optical_standard,
                                                                      solid_layers=[pywincalc_layer])

    # Iterate through optical methods and add the calculated results to the
    # summary_results instance. Note that we may skip one or more methods, if
    # they are not supported by the optical_standard passed in.
    optical_methods = [
        CalculationStandardMethodTypes.PHOTOPIC.name,
        CalculationStandardMethodTypes.SOLAR.name,
        CalculationStandardMethodTypes.TDW.name,
        CalculationStandardMethodTypes.TKR.name,
        CalculationStandardMethodTypes.TUV.name
        # We do not include THERMAL_IR and SPF.
    ]
    for method_name in optical_methods:
        if method_name in optical_standard.methods:
            try:
                results: OpticalStandardMethodResults = calc_optical(glazing_system, method_name)
                setattr(summary_results, method_name.lower(), results)
            except Exception as e:
                error_msg = f"calc_optical() call failed for method {method_name}"
                logger.error(f"OptiCalc : {error_msg} : {e}")
                raise SpectralAveragesSummaryCalculationException(error_msg) from e
        else:
            logger.warning(f"generate_integrated_spectral_averages_summary() skipping method {method_name} as its not "
                           f"present in the methods for optical standard {optical_standard} "
                           f"( methods : {optical_standard.methods} )")

    # Add color results to summary_results
    try:
        summary_results.color = calc_color(glazing_system)
    except Exception as e:
        error_msg = f"calc_color() call failed for product: {product} " \
                    f"optical_standard : {optical_standard} " \
                    f"glazing_system {glazing_system}"
        logger.error(f"OptiCalc : {error_msg}  error : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    # TODO:
    #   Check explicitly for IR wavelength values and existence of ir_transmittance_front
    #   and ir_transmittance_back and emissivity front / back

    # Add thermal IR results to summary_results
    try:
        summary_results.thermal_ir = generate_thermal_ir_results(optical_standard, pywincalc_layer)
    except Exception as e:
        error_msg = f"generate_thermal_ir_results() call failed for " \
                    f"layer: {pywincalc_layer} " \
                    f"optical_standard: {optical_standard} "
        logger.error(f"OptiCalc : {error_msg} : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    return summary_results
