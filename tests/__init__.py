"""
qBRA Plugin Test Suite

This package contains all tests for the qBRA QGIS plugin.

Test Organization:
- test_models.py: Tests for data models (dataclasses, validation)
- test_services.py: Tests for business logic services
- test_controllers.py: Tests for MVC controllers
- test_validators.py: Tests for input validation
- test_compatibility.py: Tests for Qt5/Qt6 compatibility
- test_integration.py: Integration tests for complete workflows

Test Markers:
- @pytest.mark.unit: Fast unit tests (no external dependencies)
- @pytest.mark.integration: Integration tests (may require mocks)
- @pytest.mark.slow: Slow tests (can be skipped in CI)
- @pytest.mark.qgis: Tests requiring QGIS environment

Running Tests:
    # All tests
    pytest

    # Only unit tests
    pytest -m unit

    # With coverage
    pytest --cov=qBRA --cov-report=html

    # Specific file
    pytest tests/test_models.py

    # Specific test
    pytest tests/test_models.py::TestBRAParameters::test_validation
"""
