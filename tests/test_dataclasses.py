import pytest

from opticalc.product import Product, ProductType, ProductSubtype


def test_product_dataclass():
    """
    Make sure getters and setters validate incoming strings.
    """""

    valid_type = ProductType.GLAZING.name
    valid_subtype = ProductSubtype.MONOLITHIC.name

    bad_type = "DOES_NOT_EXIST_TYPE"
    bad_subtype = "DOES_NOT_EXIST_SUBTYPE"

    with pytest.raises(ValueError):
        p = Product(type=bad_type, subtype=valid_subtype)

    with pytest.raises(ValueError):
        p = Product(type=valid_type, subtype=bad_subtype)
