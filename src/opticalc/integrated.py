import logging

import pywincalc
from py_igsdb_optical_data.optical import OpticalStandardMethodResults, OpticalColorResults, \
    IntegratedSpectralAveragesSummaryValues, OpticalColorFluxResults, OpticalColorResult, RGBResult, \
    LabResult, TrichromaticResult, ThermalIRResults, OpticalStandardMethodFluxResults, \
    IntegratedSpectralAveragesSummaryValuesFactory
from py_igsdb_optical_data.standard import CalculationStandardMethodTypes

from opticalc.product import Product, ProductSubtype

logger = logging.getLogger(__name__)


class SpectralAveragesSummaryCalculationException(Exception):
    """
    Capture info about which part of integrated spectral averages
    summary calculation process went bad.
    """
    pass


def convert_wavelength_data(raw_wavelength_data):
    pywincalc_wavelength_measured_data = []
    for individual_wavelength_measurement in raw_wavelength_data:
        wavelength = individual_wavelength_measurement["w"]
        # In this case the raw data only has the direct component measured
        # Diffuse measured data is also not yet supported in the calculations
        direct_component = pywincalc.OpticalMeasurementComponent(
            individual_wavelength_measurement["specular"]["tf"],
            individual_wavelength_measurement["specular"]["tb"],
            individual_wavelength_measurement["specular"]["rf"],
            individual_wavelength_measurement["specular"]["rb"])
        pywincalc_wavelength_measured_data.append(pywincalc.WavelengthData(wavelength, direct_component))

    return pywincalc_wavelength_measured_data


def convert_subtype(subtype):
    subtype_mapping = {ProductSubtype.MONOLITHIC.name: pywincalc.MaterialType.MONOLITHIC,
                       ProductSubtype.APPLIED_FILM.name: pywincalc.MaterialType.APPLIED_FILM,
                       ProductSubtype.COATED.name: pywincalc.MaterialType.COATED,
                       ProductSubtype.LAMINATE.name: pywincalc.MaterialType.LAMINATE,
                       ProductSubtype.INTERLAYER.name: pywincalc.MaterialType.INTERLAYER,
                       ProductSubtype.FILM.name: pywincalc.MaterialType.FILM}

    pywincalc_material = subtype_mapping.get(subtype)
    if pywincalc_material is None:
        raise RuntimeError("Unsupported subtype: {t}".format(t=subtype))
    return pywincalc_material


def convert_coated_side(coated_side: str) -> pywincalc.CoatedSide:
    if not coated_side:
        return pywincalc.CoatedSide.NEITHER
    coated_side = coated_side.upper()
    mapping = {
        "FRONT": pywincalc.CoatedSide.FRONT,
        "BACK": pywincalc.CoatedSide.BACK,
        "BOTH": pywincalc.CoatedSide.BOTH,
        "NEITHER": pywincalc.CoatedSide.NEITHER,
        "NA": pywincalc.CoatedSide.NEITHER
    }
    try:
        return mapping.get(coated_side)
    except KeyError:
        raise RuntimeError(f"Unsupported coated side: {coated_side}")


def convert_product(product) -> pywincalc.ProductDataOpticalAndThermal:
    """
    Converts a product.Product dataclass instance into a
    dataclass instance that PyWinCalc can work with.

    :param product:     Instance of a populated product.Product dataclass

    :return:
    Instance of pywincalc.ProductDataOpticalAndThermal
    """

    optical_data = product.physical_properties.optical_properties.optical_data
    if not optical_data:
        raise Exception(f"No optical_data is defined on product: {product}")

    try:
        wavelength_data = optical_data["angle_blocks"][0]["wavelength_data"]
        if not wavelength_data:
            raise Exception("No wavelength data")
    except Exception as e:
        raise Exception("Could not find wavelength data in product : {product}") from e

    wavelength_data = convert_wavelength_data(wavelength_data)
    material_type = convert_subtype(product.subtype)
    material_thickness = product.physical_properties.thickness

    # We use the top-level properties on 'product' to get emissivity and TIR.
    # These property methods will return a predefined value if one exists,
    # otherwise will return a calculated value if one exists.
    emissivity_front = product.emissivity_front
    emissivity_back = product.emissivity_back
    ir_transmittance_front = product.tir_front
    ir_transmittance_back = product.tir_back

    coated_side = convert_coated_side(product.coated_side)

    optical_data = pywincalc.ProductDataOpticalNBand(material_type, material_thickness, wavelength_data, coated_side,
                                                     ir_transmittance_front, ir_transmittance_back,
                                                     emissivity_front, emissivity_back)

    layer = pywincalc.ProductDataOpticalAndThermal(optical_data, None)
    return layer


def calc_optical(glazing_system, method) -> OpticalStandardMethodResults:
    translated_results = OpticalStandardMethodResults()
    try:
        results = glazing_system.optical_method_results(method)
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


def convert_trichromatic_result(trichromatic):
    return TrichromaticResult(x=trichromatic.X, y=trichromatic.Y, z=trichromatic.Z)


def convert_lab_result(lab):
    return LabResult(l=lab.L, a=lab.a, b=lab.b)


def convert_rgb_result(rgb):
    return RGBResult(r=rgb.R, g=rgb.G, b=rgb.B)


def calc_color(glazing_system) -> OpticalColorResults:
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


def generate_thermal_ir_results(pywincalc_layer, optical_standard) -> ThermalIRResults:
    translated_results = ThermalIRResults()
    pywincalc_results = pywincalc.calc_thermal_ir(optical_standard, pywincalc_layer)
    translated_results.transmittance_front_diffuse_diffuse = pywincalc_results.transmittance_front_diffuse_diffuse
    translated_results.transmittance_back_diffuse_diffuse = pywincalc_results.transmittance_back_diffuse_diffuse
    translated_results.absorptance_front_hemispheric = pywincalc_results.emissivity_front_hemispheric
    translated_results.absorptance_back_hemispheric = pywincalc_results.emissivity_back_hemispheric
    return translated_results


def generate_integrated_spectral_averages_summary(product: Product,
                                                  optical_standard: pywincalc.OpticalStandard) \
        -> IntegratedSpectralAveragesSummaryValues:
    """
    Generate integrated spectral averages summary for a given product and standard.
    """

    summary_results: IntegratedSpectralAveragesSummaryValues = IntegratedSpectralAveragesSummaryValuesFactory.create()
    pywincalc_layer = convert_product(product)
    glazing_system = pywincalc.GlazingSystem(optical_standard=optical_standard, solid_layers=[pywincalc_layer])

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
        summary_results.thermal_ir = generate_thermal_ir_results(pywincalc_layer, optical_standard)
    except Exception as e:
        error_msg = f"generate_thermal_ir_results() call failed for " \
                    f"layer: {pywincalc_layer} " \
                    f"optical_standard: {optical_standard} "
        logger.error(f"OptiCalc : {error_msg} : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    return summary_results
