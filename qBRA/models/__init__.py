"""Models package for qBRA plugin.

Imports are wrapped in try/except to allow testing without QGIS installed.
"""

__all__ = [
    "BRAParameters",
    "FacilityConfig",
    "FacilityDefaults",
    "FeatureDefinition",
]

# Lazy imports to avoid QGIS dependency during test discovery
def __getattr__(name: str):
    """Lazy import of models to avoid QGIS dependency during test collection."""
    if name == "BRAParameters":
        from .bra_parameters import BRAParameters
        return BRAParameters
    elif name == "FacilityConfig":
        from .bra_parameters import FacilityConfig
        return FacilityConfig
    elif name == "FacilityDefaults":
        from .bra_parameters import FacilityDefaults
        return FacilityDefaults
    elif name == "FeatureDefinition":
        from .feature_definition import FeatureDefinition
        return FeatureDefinition
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
