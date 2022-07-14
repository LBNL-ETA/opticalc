import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from unittest import TestCase

from dataclasses_json import dataclass_json

from py_igsdb_base_data.product import BaseProduct, PhysicalProperties


@dataclass_json
@dataclass
class TestList:
    some_list: Optional[List[str]] = None


class TestDataclass(TestCase):

    def test_dataclass_library(self):
        d = '{"sports": ["soccer", "basketball"]}'
        TestList.from_json(d)

    def test_load_valid_json_file(self):
        example_product_json = Path('tests/data/valid_monolithic_1.json')
        if not example_product_json.exists():
            raise Exception(f"Cannot run test. Missing sample json file: {example_product_json}")

        with open(example_product_json, 'r') as f:
            json_content = f.read()

        # Load json string into our dataclass
        product: BaseProduct = BaseProduct.from_json(json_content)

        # Get original json properties to see if
        # they were preserved...
        original_dict = json.loads(json_content)
        expected_subtype = original_dict['subtype']

        # Check dataclass against original properties.
        self.assertEquals(product.subtype, expected_subtype)

        physical_properties = product.physical_properties
        # Makes sure nested data was transformed to dataclasses by dataclasses-json
        self.assertEquals(type(physical_properties), PhysicalProperties)
