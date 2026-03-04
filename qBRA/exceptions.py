"""Custom exceptions for qBRA plugin.

This module defines domain-specific exceptions for the qBRA plugin,
providing clear error messages and structured error handling.

Exceptions follow a hierarchy:
- BRAError: Base exception for all qBRA errors
  - BRAValidationError: Input validation failures
  - BRACalculationError: Calculation/geometry processing errors
  - LayerNotFoundError: Layer discovery or access errors
  - UIOperationError: UI-related operations that fail gracefully
"""

from typing import Optional


class BRAError(Exception):
    """Base exception for all qBRA plugin errors.
    
    All custom exceptions in qBRA inherit from this base class,
    allowing for broad exception handling when needed while
    maintaining specific exception types for different error scenarios.
    """
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        """Initialize BRA error.
        
        Args:
            message: Primary error message for the user
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return string representation of the error.
        
        Returns:
            Error message with optional details
        """
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class BRAValidationError(BRAError):
    """Exception raised when input validation fails.
    
    Use this exception when:
    - User inputs are invalid (out of range, wrong type)
    - Required layers are not selected
    - Required features are not selected
    - Geometry validation fails (insufficient vertices, invalid geometry)
    
    Example:
        >>> if not layer:
        ...     raise BRAValidationError(
        ...         "No navaid layer selected",
        ...         "User must select a point layer with navaid features"
        ...     )
    """
    pass


class BRACalculationError(BRAError):
    """Exception raised when BRA calculation or geometry processing fails.
    
    Use this exception when:
    - Geometry calculations fail (distance, azimuth, buffer)
    - Feature creation fails
    - Coordinate transformation errors
    - Mathematical operations produce invalid results
    
    Example:
        >>> try:
        ...     azimuth = point1.azimuth(point2)
        ... except Exception as e:
        ...     raise BRACalculationError(
        ...         "Failed to calculate azimuth between points",
        ...         f"Points: {point1}, {point2}, Error: {e}"
        ...     )
    """
    pass


class LayerNotFoundError(BRAError):
    """Exception raised when a required layer cannot be found or accessed.
    
    Use this exception when:
    - Layer lookup by name fails
    - Layer has incorrect geometry type
    - Layer has no features
    - Active layer is not set
    
    Example:
        >>> point_layers = [l for l in layers if l.geometryType() == QgsWkbTypes.PointGeometry]
        >>> if not point_layers:
        ...     raise LayerNotFoundError(
        ...         "No point layers found in project",
        ...         f"Project has {len(layers)} layers, but none with point geometry"
        ...     )
    """
    pass


class UIOperationError(BRAError):
    """Exception raised when a UI operation fails gracefully.
    
    Use this exception for non-critical UI operations that can fail
    without breaking the plugin (e.g., setting icons, cosmetic features).
    These exceptions should typically be caught and logged, not propagated.
    
    Example:
        >>> try:
        ...     action.setIcon(icon)
        ... except Exception as e:
        ...     raise UIOperationError(
        ...         "Failed to set action icon",
        ...         f"Icon path: {icon_path}, Error: {e}"
        ...     )
    """
    pass
