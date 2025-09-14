import logging

import pywincalc
from py_igsdb_base_data.optical import (
    OpticalStandardMethodResults,
    OpticalColorResults,
    IntegratedSpectralAveragesSummaryValues,
    OpticalColorFluxResults,
    OpticalColorResult,
    ThermalIRResults,
    OpticalStandardMethodFluxResults,
    IntegratedSpectralAveragesSummaryValuesFactory,
)
from py_igsdb_base_data.product import BaseProduct, ProductSubtype
from py_igsdb_base_data.standard import CalculationStandardMethodTypes

from opticalc.exceptions import SpectralAveragesSummaryCalculationException
from opticalc.util import (
    convert_to_trichromatic_result,
    convert_to_lab_result,
    convert_to_rgb_result,
    convert_product,
)

logger = logging.getLogger(__name__)


def calc_optical(
    glazing_system: pywincalc.GlazingSystem, method_name: str
) -> OpticalStandardMethodResults:
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

    try:
        results = glazing_system.optical_method_results(method_name)
        system_results = results.system_results
    except Exception as e:
        err_message = (
            f"could not create a "
            f"pywincalc results object "
            f"with method_name: {method_name} : {str(e)}"
        )
        logger.exception(f"calc_optical() {err_message}")
        raise Exception(err_message) from e

    translated_results = OpticalStandardMethodResults()
    try:
        translated_results.transmittance_front = OpticalStandardMethodFluxResults(
            direct_direct=system_results.front.transmittance.direct_direct,
            direct_diffuse=system_results.front.transmittance.direct_diffuse,
            direct_hemispherical=system_results.front.transmittance.direct_hemispherical,
            diffuse_diffuse=system_results.front.transmittance.diffuse_diffuse,
            matrix=system_results.front.transmittance.matrix,
        )

        translated_results.transmittance_back = OpticalStandardMethodFluxResults(
            direct_direct=system_results.back.transmittance.direct_direct,
            direct_diffuse=system_results.back.transmittance.direct_diffuse,
            direct_hemispherical=system_results.back.transmittance.direct_hemispherical,
            diffuse_diffuse=system_results.back.transmittance.diffuse_diffuse,
            matrix=system_results.back.transmittance.matrix,
        )

        translated_results.reflectance_front = OpticalStandardMethodFluxResults(
            direct_direct=system_results.front.reflectance.direct_direct,
            direct_diffuse=system_results.front.reflectance.direct_diffuse,
            direct_hemispherical=system_results.front.reflectance.direct_hemispherical,
            diffuse_diffuse=system_results.front.reflectance.diffuse_diffuse,
            matrix=system_results.front.reflectance.matrix,
        )

        translated_results.reflectance_back = OpticalStandardMethodFluxResults(
            direct_direct=system_results.back.reflectance.direct_direct,
            direct_diffuse=system_results.back.reflectance.direct_diffuse,
            direct_hemispherical=system_results.back.reflectance.direct_hemispherical,
            diffuse_diffuse=system_results.back.reflectance.diffuse_diffuse,
            matrix=system_results.back.reflectance.matrix,
        )

        translated_results.absorptance_front = (
            1
            - system_results.front.transmittance.direct_hemispherical
            - system_results.front.reflectance.direct_hemispherical
        )
        translated_results.absorptance_back = (
            1
            - system_results.back.transmittance.direct_hemispherical
            - system_results.back.reflectance.direct_hemispherical
        )

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

        direct_direct_front_transmittance_trichromatic = convert_to_trichromatic_result(
            results.front.transmittance.direct_direct.trichromatic
        )
        direct_direct_front_transmittance_lab = convert_to_lab_result(
            results.front.transmittance.direct_direct.lab
        )
        direct_direct_front_transmittance_rgb = convert_to_rgb_result(
            results.front.transmittance.direct_direct.rgb
        )

        direct_diffuse_front_transmittance_trichromatic = (
            convert_to_trichromatic_result(
                results.front.transmittance.direct_diffuse.trichromatic
            )
        )
        direct_diffuse_front_transmittance_lab = convert_to_lab_result(
            results.front.transmittance.direct_diffuse.lab
        )
        direct_diffuse_front_transmittance_rgb = convert_to_rgb_result(
            results.front.transmittance.direct_diffuse.rgb
        )

        diffuse_diffuse_front_transmittance_trichromatic = (
            convert_to_trichromatic_result(
                results.front.transmittance.diffuse_diffuse.trichromatic
            )
        )
        diffuse_diffuse_front_transmittance_lab = convert_to_lab_result(
            results.front.transmittance.diffuse_diffuse.lab
        )
        diffuse_diffuse_front_transmittance_rgb = convert_to_rgb_result(
            results.front.transmittance.diffuse_diffuse.rgb
        )

        direct_hemispherical_front_transmittance_trichromatic = (
            convert_to_trichromatic_result(
                results.front.transmittance.direct_hemispherical.trichromatic
            )
        )
        direct_hemispherical_front_transmittance_lab = convert_to_lab_result(
            results.front.transmittance.direct_hemispherical.lab
        )
        direct_hemispherical_front_transmittance_rgb = convert_to_rgb_result(
            results.front.transmittance.direct_hemispherical.rgb
        )

        translated_results.transmittance_front = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_front_transmittance_trichromatic,
                lab=direct_direct_front_transmittance_lab,
                rgb=direct_direct_front_transmittance_rgb,
            ),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_front_transmittance_trichromatic,
                lab=direct_diffuse_front_transmittance_lab,
                rgb=direct_diffuse_front_transmittance_rgb,
            ),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_front_transmittance_trichromatic,
                lab=direct_hemispherical_front_transmittance_lab,
                rgb=direct_hemispherical_front_transmittance_rgb,
            ),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_front_transmittance_trichromatic,
                lab=diffuse_diffuse_front_transmittance_lab,
                rgb=diffuse_diffuse_front_transmittance_rgb,
            ),
        )

        direct_direct_front_reflectance_trichromatic = convert_to_trichromatic_result(
            results.front.reflectance.direct_direct.trichromatic
        )
        direct_direct_front_reflectance_lab = convert_to_lab_result(
            results.front.reflectance.direct_direct.lab
        )
        direct_direct_front_reflectance_rgb = convert_to_rgb_result(
            results.front.reflectance.direct_direct.rgb
        )

        direct_diffuse_front_reflectance_trichromatic = convert_to_trichromatic_result(
            results.front.reflectance.direct_diffuse.trichromatic
        )
        direct_diffuse_front_reflectance_lab = convert_to_lab_result(
            results.front.reflectance.direct_diffuse.lab
        )
        direct_diffuse_front_reflectance_rgb = convert_to_rgb_result(
            results.front.reflectance.direct_diffuse.rgb
        )

        direct_hemispherical_front_reflectance_trichromatic = (
            convert_to_trichromatic_result(
                results.front.reflectance.direct_hemispherical.trichromatic
            )
        )
        direct_hemispherical_front_reflectance_lab = convert_to_lab_result(
            results.front.reflectance.direct_hemispherical.lab
        )
        direct_hemispherical_front_reflectance_rgb = convert_to_rgb_result(
            results.front.reflectance.direct_hemispherical.rgb
        )

        diffuse_diffuse_front_reflectance_trichromatic = convert_to_trichromatic_result(
            results.front.reflectance.diffuse_diffuse.trichromatic
        )
        diffuse_diffuse_front_reflectance_lab = convert_to_lab_result(
            results.front.reflectance.diffuse_diffuse.lab
        )
        diffuse_diffuse_front_reflectance_rgb = convert_to_rgb_result(
            results.front.reflectance.diffuse_diffuse.rgb
        )

        translated_results.reflectance_front = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_front_reflectance_trichromatic,
                lab=direct_direct_front_reflectance_lab,
                rgb=direct_direct_front_reflectance_rgb,
            ),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_front_reflectance_trichromatic,
                lab=direct_diffuse_front_reflectance_lab,
                rgb=direct_diffuse_front_reflectance_rgb,
            ),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_front_reflectance_trichromatic,
                lab=direct_hemispherical_front_reflectance_lab,
                rgb=direct_hemispherical_front_reflectance_rgb,
            ),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_front_reflectance_trichromatic,
                lab=diffuse_diffuse_front_reflectance_lab,
                rgb=diffuse_diffuse_front_reflectance_rgb,
            ),
        )

        direct_direct_back_transmittance_trichromatic = convert_to_trichromatic_result(
            results.back.transmittance.direct_direct.trichromatic
        )
        direct_direct_back_transmittance_lab = convert_to_lab_result(
            results.back.transmittance.direct_direct.lab
        )
        direct_direct_back_transmittance_rgb = convert_to_rgb_result(
            results.back.transmittance.direct_direct.rgb
        )

        direct_diffuse_back_transmittance_trichromatic = convert_to_trichromatic_result(
            results.back.transmittance.direct_diffuse.trichromatic
        )
        direct_diffuse_back_transmittance_lab = convert_to_lab_result(
            results.back.transmittance.direct_diffuse.lab
        )
        direct_diffuse_back_transmittance_rgb = convert_to_rgb_result(
            results.back.transmittance.direct_diffuse.rgb
        )

        direct_hemispherical_back_transmittance_trichromatic = (
            convert_to_trichromatic_result(
                results.back.transmittance.direct_hemispherical.trichromatic
            )
        )
        direct_hemispherical_back_transmittance_lab = convert_to_lab_result(
            results.back.transmittance.direct_hemispherical.lab
        )
        direct_hemispherical_back_transmittance_rgb = convert_to_rgb_result(
            results.back.transmittance.direct_hemispherical.rgb
        )

        diffuse_diffuse_back_transmittance_trichromatic = (
            convert_to_trichromatic_result(
                results.back.transmittance.diffuse_diffuse.trichromatic
            )
        )
        diffuse_diffuse_back_transmittance_lab = convert_to_lab_result(
            results.back.transmittance.diffuse_diffuse.lab
        )
        diffuse_diffuse_back_transmittance_rgb = convert_to_rgb_result(
            results.back.transmittance.diffuse_diffuse.rgb
        )

        translated_results.transmittance_back = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_back_transmittance_trichromatic,
                lab=direct_direct_back_transmittance_lab,
                rgb=direct_direct_back_transmittance_rgb,
            ),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_back_transmittance_trichromatic,
                lab=direct_diffuse_back_transmittance_lab,
                rgb=direct_diffuse_back_transmittance_rgb,
            ),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_back_transmittance_trichromatic,
                lab=direct_hemispherical_back_transmittance_lab,
                rgb=direct_hemispherical_back_transmittance_rgb,
            ),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_back_transmittance_trichromatic,
                lab=diffuse_diffuse_back_transmittance_lab,
                rgb=diffuse_diffuse_back_transmittance_rgb,
            ),
        )

        direct_direct_back_reflectance_trichromatic = convert_to_trichromatic_result(
            results.back.reflectance.direct_direct.trichromatic
        )
        direct_direct_back_reflectance_lab = convert_to_lab_result(
            results.back.reflectance.direct_direct.lab
        )
        direct_direct_back_reflectance_rgb = convert_to_rgb_result(
            results.back.reflectance.direct_direct.rgb
        )

        direct_diffuse_back_reflectance_trichromatic = convert_to_trichromatic_result(
            results.back.reflectance.direct_diffuse.trichromatic
        )
        direct_diffuse_back_reflectance_lab = convert_to_lab_result(
            results.back.reflectance.direct_diffuse.lab
        )
        direct_diffuse_back_reflectance_rgb = convert_to_rgb_result(
            results.back.reflectance.direct_diffuse.rgb
        )

        direct_hemispherical_back_reflectance_trichromatic = (
            convert_to_trichromatic_result(
                results.back.reflectance.direct_hemispherical.trichromatic
            )
        )
        direct_hemispherical_back_reflectance_lab = convert_to_lab_result(
            results.back.reflectance.direct_hemispherical.lab
        )
        direct_hemispherical_back_reflectance_rgb = convert_to_rgb_result(
            results.back.reflectance.direct_hemispherical.rgb
        )

        diffuse_diffuse_back_reflectance_trichromatic = convert_to_trichromatic_result(
            results.back.reflectance.diffuse_diffuse.trichromatic
        )
        diffuse_diffuse_back_reflectance_lab = convert_to_lab_result(
            results.back.reflectance.diffuse_diffuse.lab
        )
        diffuse_diffuse_back_reflectance_rgb = convert_to_rgb_result(
            results.back.reflectance.diffuse_diffuse.rgb
        )

        translated_results.reflectance_back = OpticalColorFluxResults(
            direct_direct=OpticalColorResult(
                trichromatic=direct_direct_back_reflectance_trichromatic,
                lab=direct_direct_back_reflectance_lab,
                rgb=direct_direct_back_reflectance_rgb,
            ),
            direct_diffuse=OpticalColorResult(
                trichromatic=direct_diffuse_back_reflectance_trichromatic,
                lab=direct_diffuse_back_reflectance_lab,
                rgb=direct_diffuse_back_reflectance_rgb,
            ),
            direct_hemispherical=OpticalColorResult(
                trichromatic=direct_hemispherical_back_reflectance_trichromatic,
                lab=direct_hemispherical_back_reflectance_lab,
                rgb=direct_hemispherical_back_reflectance_rgb,
            ),
            diffuse_diffuse=OpticalColorResult(
                trichromatic=diffuse_diffuse_back_reflectance_trichromatic,
                lab=diffuse_diffuse_back_reflectance_lab,
                rgb=diffuse_diffuse_back_reflectance_rgb,
            ),
        )

    except Exception as e:
        logger.exception("calc_color() call failed")
        raise e

    return translated_results


def calc_thermal_ir_results(
    optical_standard: pywincalc.OpticalStandard,
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal,
    ignore_emissivity: bool = False,
) -> ThermalIRResults:
    """
    Uses pywincalc to generate thermal IR information for a given layer and standard.

    Args:
        optical_standard:       Instance of a pywincalc OpticalStandard class.
        pywincalc_layer:        Instance of a pywincalc ProductDataOpticalAndThermal class.
        ignore_emissivity:      There are times we don't want to store the generated emissivity, for example
                                when calculating summary values for SHADE_MATERIAL subtype products.

    Returns:
        An instance of ThermalIRResults dataclass populated with results.


    """

    if not optical_standard:
        raise ValueError("optical_standard is None")
    if not pywincalc_layer:
        raise ValueError("pywincalc_layer is None")

    # TODO: Ignore emissivity_front_hemispheric and emissivity_back_hemispheric for SHADE_MATERIAL subtype.

    try:
        translated_results = ThermalIRResults()
        pywincalc_results = pywincalc.calc_thermal_ir(optical_standard, pywincalc_layer)
        translated_results.transmittance_front_diffuse_diffuse = (
            pywincalc_results.transmittance_front_diffuse_diffuse
        )
        translated_results.transmittance_back_diffuse_diffuse = (
            pywincalc_results.transmittance_back_diffuse_diffuse
        )
        if ignore_emissivity:
            logger.info(
                "Ignoring emissivity_front_hemispheric and emissivity_back_hemispheric from ThermalIRResults()"
            )
        else:
            translated_results.emissivity_front_hemispheric = (
                pywincalc_results.emissivity_front_hemispheric
            )
            translated_results.emissivity_back_hemispheric = (
                pywincalc_results.emissivity_back_hemispheric
            )
    except Exception as e:
        logger.exception("calc_thermal_ir_results() call failed")
        raise e

    return translated_results


def generate_integrated_spectral_averages_summary(
    product: BaseProduct,
    optical_standard: pywincalc.OpticalStandard,
    use_diffuse_as_specular: bool = False,
) -> IntegratedSpectralAveragesSummaryValues:
    """
    Uses pywincalc to generate an integrated spectral averages summary for a given product
    and standard. Returns information in a populated instance of the IntegratedSpectralAveragesSummaryValues dataclass.

    Note: some optical calculation methods may be skipped if the optical_standard passed in does not support them.

    This method provides a 'use_diffuse_as_specular' argument to allow the user to
    use diffuse measurements in the wavelength data in place of specular measurements.

    This is a temporary workaround for the fact that pywincalc cannot yet calculate both
    specular and diffuse components. In the meantime, it's expected Checkertool will run two calculations,
    one with specular and one with diffuse-as-specular, and then combine those into a single
    result with specular and diffuse components.

    If the use_diffuse_as_specular arg is False, the standard procedure will be to use both
    the specular and diffuse measurements if they are present, otherwise only use specular.

    Args:
        product:                    Instance of a py_igsdb_base_data BaseProduct dataclass.
        optical_standard:           Instance of a pywincalc OpticalStandard class.
        use_diffuse_as_specular:    If True, the diffuse measurements will be used as the specular measurements
                                    when building pywincalc WavelengthData objects.

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

    # Create an empty summary_results instance. We'll populate it below and then return it.
    summary_results: IntegratedSpectralAveragesSummaryValues = (
        IntegratedSpectralAveragesSummaryValuesFactory.create()
    )

    # Convert product from a BaseData object into a format that pywincalc understands.
    pywincalc_layer: pywincalc.ProductDataOpticalAndThermal = convert_product(
        product,
        use_diffuse_as_specular=use_diffuse_as_specular,
    )

    glazing_system: pywincalc.GlazingSystem = pywincalc.GlazingSystem(
        optical_standard=optical_standard,
        solid_layers=[pywincalc_layer],
    )

    # Iterate through optical methods and add the calculated results to the
    # summary_results instance. Note that we skip a method if
    # it is not supported by the optical_standard passed in.
    optical_methods = [
        CalculationStandardMethodTypes.PHOTOPIC.name,
        CalculationStandardMethodTypes.SOLAR.name,
        CalculationStandardMethodTypes.TDW.name,
        CalculationStandardMethodTypes.TKR.name,
        CalculationStandardMethodTypes.TUV.name,
        # NOTE:
        #   We do not include THERMAL_IR here as we do it further below.
        # NOTE:
        #   We skip SPF during optical calcs because of the following reasons
        #   provided by JJ and SC:
        #       -   SC: we need measured values down to .28 to calculated SPF, but almost all IGDB and CGDB records only have
        #           down to .3.
        #       -   JJ: there is also a fundamental difference in SPF in that it is inversely proportional to the
        #           transmittance that prevents it from being directly calculated with the function used for all
        #           other spectral average metrics. (IIRC you get a T_spf using the spectral averaging routine and
        #           then report SPF as 1/T_spf).
        # CalculationStandardMethodTypes.SPF.name
    ]
    for method_name in optical_methods:
        if method_name in optical_standard.methods:
            try:
                results: OpticalStandardMethodResults = calc_optical(
                    glazing_system, method_name
                )
                setattr(summary_results, method_name.lower(), results)
            except Exception as e:
                error_msg = f"calc_optical() call failed for method {method_name} : {e}"
                logger.error(f"OptiCalc : {error_msg} ")
                raise SpectralAveragesSummaryCalculationException(error_msg) from e
        else:
            logger.warning(
                f"generate_integrated_spectral_averages_summary() skipping method {method_name} as its not "
                f"present in the methods for optical standard {optical_standard} "
                f"( methods : {optical_standard.methods} )"
            )

    # Add color results to summary_results
    try:
        summary_results.color = calc_color(glazing_system)
    except Exception as e:
        error_msg = (
            f"calc_color() call failed for product: {product} "
            f"optical_standard : {optical_standard} "
            f"glazing_system {glazing_system}"
        )
        logger.error(f"OptiCalc : {error_msg}  error : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    if not product.has_thermal_ir_wavelengths:
        # Don't run thermal IR calculations if the product
        # doesn't have thermal IR wavelength data.
        return summary_results

    # Add thermal IR results to summary_results
    # Per meeting in late Jan 2024, we will ignore emissivity for SHADE_MATERIAL subtype products.
    # We only want to refer to header value emissivity for products of this subtype.
    ignore_emissivity = product.subtype == ProductSubtype.SHADE_MATERIAL.name
    try:
        summary_results.thermal_ir = calc_thermal_ir_results(
            optical_standard, pywincalc_layer, ignore_emissivity=ignore_emissivity
        )
    except Exception as e:
        error_msg = (
            f"calc_thermal_ir_results() call failed for "
            f"layer: {pywincalc_layer} "
            f"optical_standard: {optical_standard} "
        )
        logger.error(f"OptiCalc : {error_msg} : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    return summary_results
