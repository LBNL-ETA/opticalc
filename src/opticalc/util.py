import logging
from typing import List, Dict, Optional

import pywincalc
from py_igsdb_base_data.optical import TrichromaticResult, LabResult, RGBResult, OpticalData
from py_igsdb_base_data.product import ProductSubtype

logger = logging.getLogger(__name__)


def convert_wavelength_data(raw_wavelength_data: List[Dict], use_diffuse_as_specular: bool = False) -> List[
    pywincalc.WavelengthData]:
    """
    Converts a list of wavelength data objects into a form that can be used in Pywincalc.

    IMPORTANT: raw wavelength data must be in microns.

    TODO: The LBNL team is current discussing how to handle wavelength data with both specular and diffuse values.

    TODO: Add check for microns. Look at first value.

    Args:

        raw_wavelength_data:        A list of dictionaries in the shape of (but not necessarily
                                    actual instances of) py_igsdb_base_data.optical.WavelengthMeasurementSet.
                                    Must be in microns.
        use_diffuse_as_specular:    If True, the diffuse component will be used as the specular component.
                                    This is a temporary workaround for the fact that pywincalc cannot
                                    yet calculate both specular and diffuse components.

    Returns:
        A list of pywincalc.OpticalMeasurementComponent instances.

    """
    pywincalc_wavelength_measured_data = []
    for individual_wavelength_measurement in raw_wavelength_data:

        wavelength = individual_wavelength_measurement.get("w", None)
        if not wavelength:
            raise Exception(f"Missing wavelength property 'w' in {individual_wavelength_measurement}")

        wavelength = float(wavelength)

        if use_diffuse_as_specular:
            measurements = individual_wavelength_measurement.get("diffuse", None)
        else:
            measurements = individual_wavelength_measurement.get("specular", None)

        if not measurements:
            if use_diffuse_as_specular:
                raise Exception(f"Missing 'diffuse' property in {individual_wavelength_measurement}")
            else:
                raise Exception(f"Missing 'specular' property in {individual_wavelength_measurement}")

        direct_component = pywincalc.OpticalMeasurementComponent(
            float(measurements['tf']),
            float(measurements["tb"]),
            float(measurements["rf"]),
            float(measurements["rb"]))

        diffuse_component = None
        if not use_diffuse_as_specular:
            diffuse_measurements = individual_wavelength_measurement.get("diffuse", None)
            if diffuse_measurements:
                diffuse_component = pywincalc.OpticalMeasurementComponent(
                    float(diffuse_measurements['tf']),
                    float(diffuse_measurements["tb"]),
                    float(diffuse_measurements["rf"]),
                    float(diffuse_measurements["rb"]))

        try:
            if diffuse_component:
                if not direct_component:
                    raise Exception("Cannot have diffuse component without direct component")
                wd = pywincalc.WavelengthData(wavelength, direct_component, diffuse_component)
                pywincalc_wavelength_measured_data.append(wd)
            else:
                pywincalc_wavelength_measured_data.append(pywincalc.WavelengthData(wavelength, direct_component))
        except Exception as e:
            raise Exception(f"cannot convert wavelength data to pywincalc WavelengthData type: {e}") from e

    return pywincalc_wavelength_measured_data


def convert_subtype(subtype):
    """
    Converts a product subtype into a PyWinCalc MaterialType
    for optical calculations.

    Args:
        subtype:    A product subtype string.

    Returns:
        A PyWinCalc MaterialType enum.

    Raises:
        ValueError:     If no subtype is provided.
        Exception:   If the subtype is not supported.

    """

    if not subtype:
        raise ValueError("No subtype provided")

    subtype_mapping = {
        ProductSubtype.MONOLITHIC.name: pywincalc.MaterialType.MONOLITHIC,
        ProductSubtype.APPLIED_FILM.name: pywincalc.MaterialType.APPLIED_FILM,
        ProductSubtype.COATED.name: pywincalc.MaterialType.COATED,
        ProductSubtype.LAMINATE.name: pywincalc.MaterialType.LAMINATE,
        ProductSubtype.INTERLAYER.name: pywincalc.MaterialType.INTERLAYER,
        ProductSubtype.FILM.name: pywincalc.MaterialType.FILM,
        # This is for any shade material: fabric, monolithic, etc.
        ProductSubtype.SHADE_MATERIAL.name: pywincalc.MaterialType.MONOLITHIC,
    }

    pywincalc_material = subtype_mapping.get(subtype)
    if pywincalc_material is None:
        raise Exception("Unsupported subtype: {t}".format(t=subtype))

    return pywincalc_material


def convert_coated_side(coated_side: str) -> pywincalc.CoatedSide:
    """
    Converts a coated side string into a PyWinCalc CoatedSide
    instance.

    Args:
        coated_side:    A coated side string.

    Returns:
        A PyWinCalc CoatedSide enum.

    Raises:


    """

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
        raise Exception(f"Unsupported coated side: {coated_side}")


def convert_product(product, use_diffuse_as_specular: bool = False) -> pywincalc.ProductDataOpticalAndThermal:
    """
    Converts a product.Product dataclass instance into a
    dataclass instance that PyWinCalc can work with.

    This method provides a 'use_diffuse_as_specular' argument to allow the user to
    use diffuse measurements in the wavelength data in place of specular measurements.

    This is a temporary workaround for the fact that pywincalc cannot yet calculate both
    specular and diffuse components. In the meantime, it's expected a user will run two calculations,
    one with specular and one with diffuse-as-specular, and then combine those into a single
    result with specular and diffuse components.

    If the use_diffuse_as_specular arg is False, the standard procedure will be to use both
    the specular and diffuse measurements if they are present, otherwise only use specular.

    Args:
        product:                    Instance of a populated product.Product dataclass
        use_diffuse_as_specular:    If True, the diffuse component will be used as the specular component.

    Returns:
        Instance of pywincalc.ProductDataOpticalAndThermal

    Raises:
        ValueError:     If no product is provided.
        Exception:      If the product does not have optical data, or if
                        the wavelength data cannot be converted.
    """

    if not product:
        raise ValueError("No product provided")

    optical_data: OpticalData = product.physical_properties.optical_properties.optical_data
    if not optical_data:
        raise Exception(f"No optical_data is defined on product: {product}")

    try:
        wavelength_data = optical_data.angle_blocks[0].wavelength_data
        if not wavelength_data:
            raise Exception("No wavelength data")
    except Exception as e:
        raise Exception("Could not find wavelength data in product : {product}") from e

    try:
        wavelength_data = convert_wavelength_data(wavelength_data, use_diffuse_as_specular=use_diffuse_as_specular)
    except Exception as e:
        logger.exception(f"Could not convert wavelength data : {e}")
        raise e

    material_type = convert_subtype(product.subtype)
    material_thickness = product.physical_properties.thickness

    # We use the top-level properties on 'product' to get emissivity and TIR.
    # These property methods will return a predefined value if one exists,
    # otherwise will return a calculated value if one exists.
    emissivity_front = product.get_emissivity_front()
    if emissivity_front is not None:
        emissivity_front = float(emissivity_front)

    emissivity_back = product.get_emissivity_back()
    if emissivity_back is not None:
        emissivity_back = float(emissivity_back)

    ir_transmittance_front = product.get_tir_front()
    if ir_transmittance_front is not None:
        ir_transmittance_front = float(ir_transmittance_front)

    ir_transmittance_back = product.get_tir_back()
    if ir_transmittance_back is not None:
        ir_transmittance_back = float(ir_transmittance_back)

    coated_side = convert_coated_side(product.coated_side)

    optical_data = pywincalc.ProductDataOpticalNBand(material_type,
                                                     float(material_thickness),
                                                     wavelength_data,
                                                     coated_side,
                                                     ir_transmittance_front,
                                                     ir_transmittance_back,
                                                     emissivity_front,
                                                     emissivity_back)

    layer = pywincalc.ProductDataOpticalAndThermal(optical_data, None)
    return layer


def convert_to_trichromatic_result(trichromatic) -> Optional[TrichromaticResult]:
    """
    Converts a pywincalc.TrichromaticResult instance into
    a py_igsdb_base_data.optical.TrichromaticResult instance.
    
    If None is provided, None is returned.
    
    """
    if not trichromatic:
        return None
    return TrichromaticResult(x=trichromatic.X, y=trichromatic.Y, z=trichromatic.Z)


def convert_to_lab_result(lab) -> Optional[LabResult]:
    """
    Converts a pywincalc.LabResult instance into
    a py_igsdb_base_data.optical.LabResult instance.
    """
    if not lab:
        return None
    return LabResult(l=lab.L, a=lab.a, b=lab.b)


def convert_to_rgb_result(rgb) -> Optional[RGBResult]:
    """
    Converts a pywincalc.RGBResult instance into
    a py_igsdb_base_data.optical.RGBResult instance.
    """
    if not rgb:
        return None
    return RGBResult(r=rgb.R, g=rgb.G, b=rgb.B)
