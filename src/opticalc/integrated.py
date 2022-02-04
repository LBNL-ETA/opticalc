from functools import partial

import logging
import pywincalc
from opticalc.product import Product, ProductSubtype
from py_igsdb_optical_data.optical import OpticalStandardMethodResults, OpticalColorResults, \
    IntegratedSpectralAveragesSummaryValues, OpticalColorFluxResults, OpticalColorResult, RGBResult, \
    LabResult, TrichromaticResult, ThermalIRResults, OpticalStandardMethodFluxResults, \
    IntegratedSpectralAveragesSummaryValuesFactory

logger = logging.getLogger(__name__)


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
    subtype_mapping = {ProductSubtype.MONOLITHIC: pywincalc.MaterialType.MONOLITHIC,
                       ProductSubtype.APPLIED_FILM: pywincalc.MaterialType.APPLIED_FILM,
                       ProductSubtype.COATED: pywincalc.MaterialType.COATED,
                       ProductSubtype.LAMINATE: pywincalc.MaterialType.LAMINATE,
                       ProductSubtype.INTERLAYER: pywincalc.MaterialType.INTERLAYER,
                       ProductSubtype.FILM: pywincalc.MaterialType.FILM}

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


def convert_product(product):
    wavelength_data = convert_wavelength_data(
        product.physical_properties.optical_properties.optical_data["angle_blocks"][0]["wavelength_data"])
    material_type = convert_subtype(product.subtype)
    material_thickness = product.physical_properties.thickness
    emissivity_front = product.physical_properties.emissivity_front
    emissivity_back = product.physical_properties.emissivity_back
    ir_transmittance_front = product.physical_properties.tir_front
    ir_transmittance_back = product.physical_properties.tir_back
    coated_side = convert_coated_side(product.coated_side)

    optical_data = pywincalc.ProductDataOpticalNBand(material_type, material_thickness, wavelength_data, coated_side,
                                                     ir_transmittance_front, ir_transmittance_back,
                                                     emissivity_front, emissivity_back)

    layer = pywincalc.ProductDataOpticalAndThermal(optical_data, None)
    return layer


def calc_optical(glazing_system, method, result_setter_f):
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

    result_setter_f(translated_results)


def convert_trichromatic_result(trichromatic):
    return TrichromaticResult(x=trichromatic.X, y=trichromatic.Y, z=trichromatic.Z)


def convert_lab_result(lab):
    return LabResult(l=lab.L, a=lab.a, b=lab.b)


def convert_rgb_result(rgb):
    return RGBResult(r=rgb.R, g=rgb.G, b=rgb.B)


def calc_color(glazing_system, results_setter_f):
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

    results_setter_f(translated_results)


def generate_thermal_ir_results(pywincalc_layer, optical_standard, result_setter_f):
    converted_results = ThermalIRResults()
    thermal_results = pywincalc.calc_thermal_ir(optical_standard, pywincalc_layer)
    converted_results.transmittance_front_diffuse_diffuse = thermal_results.transmittance_front_diffuse_diffuse
    converted_results.transmittance_back_diffuse_diffuse = thermal_results.transmittance_back_diffuse_diffuse
    converted_results.absorptance_front_hemispheric = thermal_results.emissivity_front_hemispheric
    converted_results.absorptance_back_hemispheric = thermal_results.emissivity_back_hemispheric
    result_setter_f(converted_results)


class SpectralAveragesSummaryCalculationException(Exception):
    """
    Capture info about which part of integrated spectral averages
    calculation process went bad.
    """
    pass


def generate_integrated_spectral_averages_summary(product: Product,
                                                  optical_standard: pywincalc.OpticalStandard) \
        -> IntegratedSpectralAveragesSummaryValues:
    """
    Generate integrated spectral averages summary for a given product and standard.
    """

    # TODO: Business logic that generates integrated spectral averages summary
    # TODO: for the given product and calculation standard.

    results: IntegratedSpectralAveragesSummaryValues = IntegratedSpectralAveragesSummaryValuesFactory.create()

    method_to_result_setter = {
        "SOLAR": partial(setattr, results, "solar"),
        "PHOTOPIC": partial(setattr, results, "photopic"),
        "TUV": partial(setattr, results, "tuv"),
        "SPF": partial(setattr, results, "spf"),
        "TDW": partial(setattr, results, "tdw"),
        "TKR": partial(setattr, results, "tkr")}

    pywincalc_layer = convert_product(product)
    glazing_system = pywincalc.GlazingSystem(optical_standard=optical_standard, solid_layers=[pywincalc_layer])

    for method, f in method_to_result_setter.items():
        if method in optical_standard.methods:
            try:
                calc_optical(glazing_system, method, f)
            except Exception as e:
                error_msg = f"calc_optical() call failed for method {method}"
                logger.error(f"OptiCalc : {error_msg} : {e}")
                raise SpectralAveragesSummaryCalculationException(error_msg) from e

    color_kwargs = partial(setattr, results, "color")
    try:
        calc_color(glazing_system, color_kwargs)
    except Exception as e:
        error_msg = f"calc_color() call failed with color_kwargs : {color_kwargs}"
        logger.error(f"OptiCalc : {error_msg}  error : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    thermal_ir_kwargs = partial(setattr, results, "thermal_ir")
    try:
        generate_thermal_ir_results(pywincalc_layer, optical_standard, thermal_ir_kwargs)
    except Exception as e:
        error_msg = f"generate_thermal_ir_results() call failed for " \
                    f"layer: {pywincalc_layer} " \
                    f"optical_standard: {optical_standard} " \
                    f"thermal_ir_kwargs : {thermal_ir_kwargs}. "
        logger.error(f"OptiCalc : {error_msg} : {e}")
        raise SpectralAveragesSummaryCalculationException(error_msg) from e

    return results
