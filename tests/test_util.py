"""
Test the methods from the util module.
"""
import json
from dataclasses import dataclass
from typing import Optional, List
from unittest import TestCase

import pywincalc
from dataclasses_json import dataclass_json
from py_igsdb_base_data.optical import LabResult, RGBResult
from py_igsdb_base_data.product import ProductSubtype, BaseProduct

from opticalc.util import convert_wavelength_data, convert_subtype, convert_coated_side, convert_product, \
    convert_to_trichromatic_result, convert_to_lab_result


@dataclass_json
@dataclass
class TestList:
    some_list: Optional[List[str]] = None


class TestUtil(TestCase):

    def test_convert_wavelength_data(self):
        raw_wavelength_data = [
            {"w": 0.5, "specular": {"tf": 0.1, "tb": 0.2, "rf": 0.3, "rb": 0.4}},
            {"w": 0.6, "specular": {"tf": 0.2, "tb": 0.3, "rf": 0.4, "rb": 0.5}},
        ]

        expected_output = [
            pywincalc.WavelengthData(0.5, pywincalc.OpticalMeasurementComponent(0.1, 0.2, 0.3, 0.4)),
            pywincalc.WavelengthData(0.6, pywincalc.OpticalMeasurementComponent(0.2, 0.3, 0.4, 0.5)),
        ]

        result: List[pywincalc.WavelengthData] = convert_wavelength_data(raw_wavelength_data)

        for index, expected_item in enumerate(expected_output):
            actual_item = result[index]
            self.assertEqual(expected_item.wavelength, actual_item.wavelength)
            self.assertEqual(expected_item.direct_component.transmittance_front,
                             actual_item.direct_component.transmittance_front)
            self.assertEqual(expected_item.direct_component.transmittance_back,
                             actual_item.direct_component.transmittance_back)
            self.assertEqual(expected_item.direct_component.reflectance_front,
                             actual_item.direct_component.reflectance_front)
            self.assertEqual(expected_item.direct_component.reflectance_back,
                             actual_item.direct_component.reflectance_back)

    def test_convert_subtype(self):
        subtype = ProductSubtype.MONOLITHIC.name
        expected_output = pywincalc.MaterialType.MONOLITHIC
        result = convert_subtype(subtype)
        self.assertEqual(expected_output, result)

    def test_convert_coated_side(self):
        coated_side = "front"
        expected_output = pywincalc.CoatedSide.FRONT
        result = convert_coated_side(coated_side)
        self.assertEqual(expected_output, result)

        coated_side = "NEITHER"
        expected_output = pywincalc.CoatedSide.NEITHER
        result = convert_coated_side(coated_side)
        self.assertEqual(expected_output, result)

        coated_side = "NOT_APPLICABLE"
        expected_output = pywincalc.CoatedSide.NEITHER
        result = convert_coated_side(coated_side)
        self.assertEqual(expected_output, result)

        coated_side = ""
        expected_output = pywincalc.CoatedSide.NEITHER
        result = convert_coated_side(coated_side)
        self.assertEqual(expected_output, result)

        coated_side = None
        expected_output = pywincalc.CoatedSide.NEITHER
        result = convert_coated_side(coated_side)
        self.assertEqual(expected_output, result)

    def test_convert_product(self):
        """
        Test that we can convert a BaseProduct dataclass instance
        to a PyWinCalc product.
        """

        with open("./tests/data/valid_monolithic_1.json") as f:
            sample_monolithic_json = json.load(f)
            sample_monolithic_dc = BaseProduct.from_dict(sample_monolithic_json)

        pywincalc_product: pywincalc.ProductDataOpticalAndThermal = convert_product(sample_monolithic_dc)

        self.assertEqual(pywincalc_product.optical_data.emissivity_front, 0.84)
        self.assertEqual(pywincalc_product.optical_data.emissivity_back, 0.85)
        self.assertEqual(pywincalc_product.optical_data.ir_transmittance_front, None)
        self.assertEqual(pywincalc_product.optical_data.ir_transmittance_back, None)
        self.assertEqual(pywincalc_product.optical_data.material_type, pywincalc.MaterialType.MONOLITHIC)
        self.assertEqual(pywincalc_product.optical_data.permeability_factor, 0.0)
        self.assertEqual(pywincalc_product.optical_data.wavelength_data[0].wavelength, 0.300)
        self.assertEqual(pywincalc_product.optical_data.wavelength_data[0].direct_component.transmittance_front, 0.0005)
        self.assertEqual(pywincalc_product.optical_data.wavelength_data[0].direct_component.transmittance_back, 0.0006)
        self.assertEqual(pywincalc_product.optical_data.wavelength_data[0].direct_component.reflectance_front, 0.0547)
        self.assertEqual(pywincalc_product.optical_data.wavelength_data[0].direct_component.reflectance_back, 0.0621)

    def test_convert_to_trichromatic_result(self):
        self.assertIsNone(convert_to_trichromatic_result(None))

        # We can't create a Pywincalc TrichromaticResult directly, so we create a
        # Pywincalc glazing system, calculate color and access the Trichromatic instance
        # for our test.

        clear_3_path = "tests/data/CLEAR_3.DAT"
        clear_3 = pywincalc.parse_optics_file(clear_3_path)
        solid_layers = [clear_3]
        glazing_system = pywincalc.GlazingSystem(solid_layers=solid_layers)
        results = glazing_system.color()
        results = results.system_results
        input_trichromatic = results.front.transmittance.direct_direct.trichromatic
        trichromatic_result = convert_to_trichromatic_result(input_trichromatic)
        self.assertEqual(input_trichromatic.X, trichromatic_result.x)
        self.assertEqual(input_trichromatic.Y, trichromatic_result.y)
        self.assertEqual(input_trichromatic.Z, trichromatic_result.z)

    def convert_to_lab_result(self):
        self.assertIsNone(convert_to_lab_result(None))

        lab = pywincalc.Lab(l=1, a=2, b=3)
        result = convert_to_lab_result(lab)
        expected_output = LabResult(l=1, a=2, b=3)
        self.assertEqual(result, expected_output)

    def convert_to_rgb_result(self):
        self.assertIsNone(convert_to_lab_result(None))

        rgb = pywincalc.RGB(r=1, g=2, b=3)
        result = convert_to_lab_result(rgb)
        expected_output = RGBResult(r=1, g=2, b=3)
        self.assertEqual(result, expected_output)
