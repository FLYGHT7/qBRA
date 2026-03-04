"""Data models for BRA feature definitions.

This module contains dataclasses for defining BRA polygon features in a declarative way,
following DRY principles to eliminate code duplication in feature creation.
"""

from dataclasses import dataclass
from typing import List, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qgis.core import QgsPoint
else:
    QgsPoint = Any


@dataclass(frozen=True)
class FeatureDefinition:
    """Definition for a single BRA feature polygon.
    
    This dataclass provides a declarative way to define polygon features,
    eliminating code duplication in the feature creation process.
    
    Attributes:
        id: Unique identifier for the feature
        area: Area type ("base", "left level", "right level", "slope", "wall")
        max_elev: Maximum elevation as string (for attribute table)
        area_name: Display name for the feature
        geometry_points: List of QgsPoint for polygon vertices
    """
    
    id: int
    area: str
    max_elev: str
    area_name: str
    geometry_points: List[QgsPoint]
    
    def __post_init__(self) -> None:
        """Validate feature definition."""
        if self.id < 1:
            raise ValueError(f"Feature id must be positive, got {self.id}")
        if not self.area:
            raise ValueError("Feature area cannot be empty")
        if not self.area_name:
            raise ValueError("Feature area_name cannot be empty")
        if len(self.geometry_points) < 3:
            raise ValueError(f"Feature geometry must have at least 3 points, got {len(self.geometry_points)}")
