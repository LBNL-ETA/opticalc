import pytest

from py_igsdb_base_data.product import BaseProduct, ProductType, ProductSubtype


def test_product_dataclass():
    """
    Make sure getters and setters validate incoming strings.
    """""

    valid_type = ProductType.GLAZING.name
    valid_subtype = ProductSubtype.MONOLITHIC.name

    bad_type = "DOES_NOT_EXIST_TYPE"
    bad_subtype = "DOES_NOT_EXIST_SUBTYPE"

    with pytest.raises(ValueError):
        p = BaseProduct(type=bad_type, subtype=valid_subtype)

    with pytest.raises(ValueError):
        p = BaseProduct(type=valid_type, subtype=bad_subtype)
