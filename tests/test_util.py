"""
Test the methods from the util module.
"""
from dataclasses import dataclass
from typing import Optional, List
from unittest import TestCase

import pywincalc
from dataclasses_json import dataclass_json

from opticalc.util import convert_wavelength_data


@dataclass_json
@dataclass
class TestList:
    some_list: Optional[List[str]] = None


class TestUtil(TestCase):

    def test_convert_wavelength_data(self):
        # Test input data
        raw_wavelength_data = [
            {"w": 0.5, "specular": {"tf": 0.1, "tb": 0.2, "rf": 0.3, "rb": 0.4}},
            {"w": 0.6, "specular": {"tf": 0.2, "tb": 0.3, "rf": 0.4, "rb": 0.5}},
        ]

        # Expected output
        expected_output = [
            pywincalc.WavelengthData(0.5, pywincalc.OpticalMeasurementComponent(0.1, 0.2, 0.3, 0.4)),
            pywincalc.WavelengthData(0.6, pywincalc.OpticalMeasurementComponent(0.2, 0.3, 0.4, 0.5)),
            # Add more expected outputs for additional test cases
        ]

        # Call the method with the test data
        result: List[pywincalc.WavelengthData] = convert_wavelength_data(raw_wavelength_data)

        # Assertions to check if the actual output matches the expected output
        for index, expected_item in enumerate(expected_output):
            actual_item = result[index]
            self.assertEqual(expected_item.wavelength, actual_item.wavelength)
            self.assertEqual(expected_item.direct_component.transmittance_front, actual_item.direct_component.transmittance_front)
            self.assertEqual(expected_item.direct_component.transmittance_back, actual_item.direct_component.transmittance_back)
            self.assertEqual(expected_item.direct_component.reflectance_front, actual_item.direct_component.reflectance_front)
            self.assertEqual(expected_item.direct_component.reflectance_back, actual_item.direct_component.reflectance_back)
