from enum import Enum
from typing import List, Dict, Optional

from py_igsdb_optical_data.optical import OpticalProperties, IntegratedSpectralAveragesSummaryValues
from py_igsdb_optical_data.standard import CalculationStandardName
from pydantic.dataclasses import dataclass

from opticalc.material import MaterialBulkProperties


class TokenType(Enum):
    PUBLISHED = "PUBLISHED"
    UNDEFINED = "UNDEFINED"
    PROPOSED = "PROPOSED"
    INTRAGROUP = "INTRAGROUP"


class ProductType(Enum):
    GLAZING = "GLAZING"
    SHADING = "SHADING"
    MATERIAL = "MATERIAL"


class ProductSubtype(Enum):
    # GLAZING Subtypes
    # ----------------------------------------
    MONOLITHIC = "Monolithic"
    LAMINATE = "Laminate"
    INTERLAYER = "Interlayer"
    EMBEDDED_COATING = "Embedded coating"
    COATED = "Coated glass"
    COATING = "Coating"
    APPLIED_FILM = "Applied film"
    FILM = "Film"

    # HYBRID GLAZING / SHADING Subtypes
    # ----------------------------------------
    FRITTED_GLASS = "Fritted glass"
    SANDBLASTED_GLASS = "Sandblasted glass"
    ACID_ETCHED_GLASS = "Acid etched glass"
    CHROMOGENIC = "Chromogenic"

    # SHADING Subtypes
    # ----------------------------------------

    # These have a geometry (GeometricProperties object)
    # associated with them:
    VENETIAN_BLIND = "Venetian blind"
    VERTICAL_LOUVER = "Vertical louver"
    PERFORATED_SCREEN = "Perforated screen"
    WOVEN_SHADE = "Woven shade"

    # These must have a BSDF associated:
    ROLLER_SHADE = "Roller shade"

    # These must have a GEN_BSDF file attached
    # (and may have a THMX -- a precursor to GEN_BSDF -- file attached):
    CELLULAR_SHADE = "Cellular shade"
    PLEATED_SHADE = "Pleated Shade"
    ROMAN_SHADE = "Roman shade"

    # TODO: What qualities do these have?
    DIFFUSING_SHADE = "Diffusing shade"
    SOLAR_SCREEN = "Solar screen"

    # Shading materials:
    SHADE_MATERIAL = "Shade material"

    # other
    UNKNOWN = "Unknown"


@dataclass
class PhysicalProperties:
    # 'predefined' emissivity are values defined by the user
    # in legacy submission file headers
    predefined_emissivity_front: float = None
    predefined_emissivity_back: float = None

    # 'predefined' tir are values defined bye the user
    # in legacy submission file headers
    predefined_tir_front: float = None
    predefined_tir_back: float = None

    thickness: float = None
    permeability_factor: float = None
    optical_openness: float = None
    bulk_properties_override: dict = None
    is_specular: bool = True
    optical_properties: OpticalProperties = None


@dataclass
class IntegratedSpectralAveragesSummary:
    """
    Encapsulates summary values object containing set of integrated summary values.
    This class exists to include extra fields to qualify that data, e.g. what
    source was used to generate those values (e.g. pywincalc, legacy cgdb database, etc.)
    """
    summary_values: Optional[IntegratedSpectralAveragesSummaryValues] = None
    calculation_standard: Optional[str] = None
    source: Optional[str] = None
    # source_version helps us track changes to standards
    # if they version over time, e.g. pywincalc versions.
    source_version: Optional[str] = None


@dataclass
class Product:
    type: ProductType
    subtype: ProductSubtype
    product_id: int = None
    token: str = None
    token_type: TokenType = None
    data_file_name: str = None
    data_file_type: str = None
    # This product can be decomposed into parts
    deconstructable: bool = False
    # This product is a 'reference' product, meaning it's sole purpose is
    # to get a child product into the IGSDB using reference substrates.
    # This is method of submittal is only valid for APPLIED_FILM and LAMINATE products.
    reference: bool = False
    igsdb_version: str = None
    coated_side: str = None
    coating_name: str = None
    owner: str = None
    manufacturer: str = None
    coating_id: int = None
    product_description: Dict = None
    igsdb_checksum: int = None
    material: str = None
    published_date: str = None
    hidden: bool = None
    active: bool = True
    appearance: str = None
    acceptance: str = None
    nfrc_id: str = None
    composition: list = None
    material_bulk_properties: MaterialBulkProperties = None
    integrated_spectral_averages_summaries: List[IntegratedSpectralAveragesSummary] = None
    physical_properties: PhysicalProperties = None
    extra_data: dict = None
    created_at: str = None
    updated_at: str = None

    @property
    def emissivity_front(self, calculation_standard_name: str = CalculationStandardName.NFRC.name) \
            -> Optional[float]:
        """
        Emissivity (front) is defined in IntegratedSpectralAveragesSummaryValues summary objects
        contained in the integrated_spectral_averages_summaries List.

        Args:
            calculation_standard_name:      Calculation standard name to use when searching
                                            for a spectral averages integrated summary values object
                                            amongst those generated for this product.


        Returns:
            This property will return a 'calculated' value if one was generated by pywincalc.
            Otherwise, it returns the calculated value from WinCalc, if available.
            If neither value is available, it returns None.

        """

        # If we have a calculated value for the given standard, return that...
        if self.integrated_spectral_averages_summaries:
            for summary in self.integrated_spectral_averages_summaries:
                if summary.calculation_standard == calculation_standard_name:
                    value = summary.summary_values.thermal_ir.emissivity_front_hemispheric
                    if value:
                        return value
        # If we don't have a calculated value, we might have a 'user defined' value (from
        # a header line in submission file). If so, return that...
        if self.physical_properties and self.physical_properties.predefined_emissivity_front:
            return self.physical_properties.predefined_emissivity_front
        return None

    @property
    def emissivity_back(self, calculation_standard_name: str = CalculationStandardName.NFRC.name) \
            -> Optional[float]:
        """
        Emissivity (front) is defined in IntegratedSpectralAveragesSummaryValues summary objects
        contained in the integrated_spectral_averages_summaries List.

        Args:
            calculation_standard_name:      Calculation standard name to use when searching
                                            for a spectral averages integrated summary values object
                                            amongst those generated for this product.


        Returns:
            This property will return a 'calculated' value if one was generated by pywincalc.
            Otherwise, it returns the calculated value from WinCalc, if available.
            If neither value is available, it returns None.

        """
        # If we have a calculated value for the given standard, return that...
        if self.integrated_spectral_averages_summaries:
            for summary in self.integrated_spectral_averages_summaries:
                if summary.calculation_standard == calculation_standard_name:
                    value = summary.summary_values.thermal_ir.emissivity_back_hemispheric
                    if value:
                        return value
            # If we don't have a calculated value, we might have a 'user defined' value (from
            # a header line in submission file). If so, return that...
        if self.physical_properties and self.physical_properties.predefined_emissivity_front:
            return self.physical_properties.predefined_emissivity_back
        return None

    @property
    def tir_front(self, calculation_standard_name: str = CalculationStandardName.NFRC.name) \
            -> Optional[float]:
        """
        TIR (front) is defined in IntegratedSpectralAveragesSummaryValues summary objects
        contained in the integrated_spectral_averages_summaries List.

        Args:
            calculation_standard_name:      Calculation standard name to use when searching
                                            for a spectral averages integrated summary values object
                                            amongst those generated for this product.

        Returns:
            This property will return a 'calculated' value if one was generated by pywincalc.
            Otherwise, it returns the calculated value from WinCalc, if available.
            If neither value is available, it returns None.

        """

        # If we have a calculated value for the given standard, return that...
        if self.integrated_spectral_averages_summaries:
            for summary in self.integrated_spectral_averages_summaries:
                if summary.calculation_standard == calculation_standard_name:
                    value = summary.summary_values.thermal_ir.transmittance_front
                    if value:
                        return value
        # If we don't have a calculated value, we might have a 'user defined' value (from
        # a header line in submission file). If so, return that...
        if self.physical_properties and self.physical_properties.predefined_emissivity_front:
            return self.physical_properties.predefined_tir_front
        return None

    @property
    def tir_back(self, calculation_standard_name: str = CalculationStandardName.NFRC.name) -> Optional[float]:
        """
        TIR (back) is defined in IntegratedSpectralAveragesSummaryValues summary objects
        contained in the integrated_spectral_averages_summaries List.

        Args:
            calculation_standard_name:      Calculation standard name to use when searching
                                            for a spectral averages integrated summary values object
                                            amongst those generated for this product.


        Returns:
            This property will return a 'calculated' value if one was generated by pywincalc.
            Otherwise, it returns the calculated value from WinCalc, if available.
            If neither value is available, it returns None.

        """
        # If we have a calculated value for the given standard, return that...
        if self.integrated_spectral_averages_summaries:
            for summary in self.integrated_spectral_averages_summaries:
                if summary.calculation_standard == calculation_standard_name:
                    value = summary.summary_values.thermal_ir.transmittance_back
                    if value:
                        return value
        # If we don't have a calculated value, we might have a 'user defined' value (from
        # a header line in submission file). If so, return that...
        if self.physical_properties and self.physical_properties.predefined_tir_back:
            return self.physical_properties.predefined_emissivity_back
        return None
