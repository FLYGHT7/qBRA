"""Tests for custom exceptions in qBRA plugin.

This module tests the exception hierarchy and behavior of custom exceptions.
"""

import pytest

from qBRA.exceptions import (
    BRAError,
    BRAValidationError,
    BRACalculationError,
    LayerNotFoundError,
    UIOperationError,
)


class TestBRAError:
    """Test base BRAError exception."""
    
    def test_base_error_with_message_only(self):
        """Test that BRAError can be created with just a message."""
        error = BRAError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.details is None
        assert str(error) == "Something went wrong"
    
    def test_base_error_with_details(self):
        """Test that BRAError can include optional details."""
        error = BRAError(
            "Calculation failed",
            "Missing required parameter 'azimuth'"
        )
        assert error.message == "Calculation failed"
        assert error.details == "Missing required parameter 'azimuth'"
        assert "Calculation failed" in str(error)
        assert "Missing required parameter" in str(error)
    
    def test_base_error_is_exception(self):
        """Test that BRAError inherits from Exception."""
        error = BRAError("test")
        assert isinstance(error, Exception)
    
    def test_base_error_can_be_raised(self):
        """Test that BRAError can be raised and caught."""
        with pytest.raises(BRAError) as exc_info:
            raise BRAError("test error", "test details")
        
        assert exc_info.value.message == "test error"
        assert exc_info.value.details == "test details"


class TestBRAValidationError:
    """Test BRAValidationError for input validation failures."""
    
    def test_validation_error_inherits_from_base(self):
        """Test that BRAValidationError inherits from BRAError."""
        error = BRAValidationError("Invalid input")
        assert isinstance(error, BRAError)
        assert isinstance(error, BRAValidationError)
    
    def test_validation_error_message(self):
        """Test validation error message formatting."""
        error = BRAValidationError("Layer not selected")
        assert error.message == "Layer not selected"
    
    def test_validation_error_with_details(self):
        """Test validation error with technical details."""
        error = BRAValidationError(
            "Invalid geometry",
            "Polygon must have at least 3 vertices, got 2"
        )
        assert "Invalid geometry" in str(error)
        assert "at least 3 vertices" in str(error)
    
    def test_validation_error_catching(self):
        """Test that validation errors can be caught specifically."""
        with pytest.raises(BRAValidationError):
            raise BRAValidationError("Field 'azimuth' out of range")
    
    def test_validation_error_catching_as_base(self):
        """Test that BRAValidationError can be caught as BRAError."""
        with pytest.raises(BRAError):
            raise BRAValidationError("Invalid input")


class TestBRACalculationError:
    """Test BRACalculationError for calculation failures."""
    
    def test_calculation_error_inherits_from_base(self):
        """Test that BRACalculationError inherits from BRAError."""
        error = BRACalculationError("Calculation failed")
        assert isinstance(error, BRAError)
        assert isinstance(error, BRACalculationError)
    
    def test_calculation_error_with_geometry_context(self):
        """Test calculation error with geometry context."""
        error = BRACalculationError(
            "Failed to compute azimuth",
            "Points are identical: (0, 0) and (0, 0)"
        )
        assert error.message == "Failed to compute azimuth"
        assert "Points are identical" in str(error)
    
    def test_calculation_error_catching(self):
        """Test that calculation errors can be caught specifically."""
        with pytest.raises(BRACalculationError):
            raise BRACalculationError("Buffer operation failed")
    
    def test_calculation_error_as_base(self):
        """Test that BRACalculationError can be caught as BRAError."""
        with pytest.raises(BRAError):
            raise BRACalculationError("Transform error")


class TestLayerNotFoundError:
    """Test LayerNotFoundError for layer access failures."""
    
    def test_layer_not_found_inherits_from_base(self):
        """Test that LayerNotFoundError inherits from BRAError."""
        error = LayerNotFoundError("Layer 'navaid' not found")
        assert isinstance(error, BRAError)
        assert isinstance(error, LayerNotFoundError)
    
    def test_layer_not_found_with_context(self):
        """Test layer not found error with search context."""
        error = LayerNotFoundError(
            "No point layers available",
            "Searched 5 layers, found 0 with point geometry"
        )
        assert "No point layers" in str(error)
        assert "Searched 5 layers" in str(error)
    
    def test_layer_not_found_catching(self):
        """Test that layer errors can be caught specifically."""
        with pytest.raises(LayerNotFoundError):
            raise LayerNotFoundError("Active layer is None")


class TestUIOperationError:
    """Test UIOperationError for non-critical UI failures."""
    
    def test_ui_error_inherits_from_base(self):
        """Test that UIOperationError inherits from BRAError."""
        error = UIOperationError("Icon load failed")
        assert isinstance(error, BRAError)
        assert isinstance(error, UIOperationError)
    
    def test_ui_error_with_file_context(self):
        """Test UI error with file path context."""
        error = UIOperationError(
            "Failed to set icon",
            "Icon file not found: /icons/missing.svg"
        )
        assert "Failed to set icon" in str(error)
        assert "missing.svg" in str(error)
    
    def test_ui_error_non_critical_semantics(self):
        """Test that UIOperationError semantics indicate non-critical failure."""
        # UIOperationError should be used for operations that can fail
        # without breaking the plugin
        error = UIOperationError("Font loading failed")
        # Should be catchable and logged, but not stop execution
        assert error.message == "Font loading failed"


class TestExceptionHierarchy:
    """Test exception hierarchy and polymorphism."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from BRAError."""
        validation_error = BRAValidationError("test")
        calculation_error = BRACalculationError("test")
        layer_error = LayerNotFoundError("test")
        ui_error = UIOperationError("test")
        
        assert isinstance(validation_error, BRAError)
        assert isinstance(calculation_error, BRAError)
        assert isinstance(layer_error, BRAError)
        assert isinstance(ui_error, BRAError)
    
    def test_catch_all_with_base_exception(self):
        """Test that base exception can catch all custom exceptions."""
        errors = [
            BRAValidationError("validation"),
            BRACalculationError("calculation"),
            LayerNotFoundError("layer"),
            UIOperationError("ui"),
        ]
        
        for error in errors:
            with pytest.raises(BRAError):
                raise error
    
    def test_specific_exception_catching(self):
        """Test that specific exceptions can be caught individually."""
        # This pattern allows for granular error handling
        try:
            raise BRAValidationError("Validation failed")
        except BRAValidationError as e:
            assert e.message == "Validation failed"
        except BRAError:
            pytest.fail("Should have caught BRAValidationError specifically")
    
    def test_exception_type_discrimination(self):
        """Test that exception types can be discriminated."""
        def classify_error(error: BRAError) -> str:
            if isinstance(error, BRAValidationError):
                return "validation"
            elif isinstance(error, BRACalculationError):
                return "calculation"
            elif isinstance(error, LayerNotFoundError):
                return "layer"
            elif isinstance(error, UIOperationError):
                return "ui"
            else:
                return "unknown"
        
        assert classify_error(BRAValidationError("test")) == "validation"
        assert classify_error(BRACalculationError("test")) == "calculation"
        assert classify_error(LayerNotFoundError("test")) == "layer"
        assert classify_error(UIOperationError("test")) == "ui"


class TestExceptionUsagePatterns:
    """Test real-world exception usage patterns."""
    
    def test_validation_error_in_factory_pattern(self):
        """Test validation error raised during object creation."""
        def create_params(azimuth: float) -> dict:
            if not (0 <= azimuth <= 360):
                raise BRAValidationError(
                    f"Azimuth must be between 0 and 360 degrees",
                    f"Got azimuth={azimuth}"
                )
            return {"azimuth": azimuth}
        
        # Valid input
        assert create_params(180.0) == {"azimuth": 180.0}
        
        # Invalid input
        with pytest.raises(BRAValidationError) as exc_info:
            create_params(400.0)
        assert "between 0 and 360" in str(exc_info.value)
    
    def test_calculation_error_in_geometry_operation(self):
        """Test calculation error raised during geometry processing."""
        def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
            try:
                import math
                return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            except Exception as e:
                raise BRACalculationError(
                    "Distance calculation failed",
                    f"Points: ({x1}, {y1}), ({x2}, {y2}), Error: {e}"
                )
        
        # Valid calculation
        assert calculate_distance(0, 0, 3, 4) == 5.0
        
        # Type error would be wrapped
        with pytest.raises(BRACalculationError):
            calculate_distance("a", 0, 3, 4)  # type: ignore
    
    def test_layer_error_in_layer_lookup(self):
        """Test layer error raised during layer discovery."""
        def find_layer_by_name(layers: list, name: str):
            matching = [l for l in layers if l == name]
            if not matching:
                raise LayerNotFoundError(
                    f"Layer '{name}' not found",
                    f"Available layers: {', '.join(layers)}"
                )
            return matching[0]
        
        layers = ["roads", "buildings", "rivers"]
        
        # Found
        assert find_layer_by_name(layers, "roads") == "roads"
        
        # Not found
        with pytest.raises(LayerNotFoundError) as exc_info:
            find_layer_by_name(layers, "airports")
        assert "airports" in str(exc_info.value)
        assert "Available layers" in str(exc_info.value)
    
    def test_ui_error_logged_but_not_fatal(self):
        """Test UI error pattern where failure is logged but not fatal."""
        errors_logged = []
        
        def set_window_icon(icon_path: str) -> bool:
            try:
                # Simulate icon loading failure
                if not icon_path.endswith(".svg"):
                    raise UIOperationError(
                        "Invalid icon format",
                        f"Expected .svg, got {icon_path}"
                    )
                return True
            except UIOperationError as e:
                errors_logged.append(e)
                return False  # Continue despite failure
        
        # Failure is handled gracefully
        result = set_window_icon("icon.png")
        assert result is False
        assert len(errors_logged) == 1
        assert "Invalid icon format" in errors_logged[0].message
