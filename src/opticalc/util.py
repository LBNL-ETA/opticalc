from py_igsdb_base_data.optical import TrichromaticResult, LabResult, RGBResult

from opticalc.product import ProductSubtype


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


import pywincalc


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


def convert_trichromatic_result(trichromatic):
    return TrichromaticResult(x=trichromatic.X, y=trichromatic.Y, z=trichromatic.Z)


def convert_lab_result(lab):
    return LabResult(l=lab.L, a=lab.a, b=lab.b)


def convert_rgb_result(rgb):
    return RGBResult(r=rgb.R, g=rgb.G, b=rgb.B)
