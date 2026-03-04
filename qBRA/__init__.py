"""qBRA QGIS Plugin - Building Restriction Areas for ILS/LLZ."""

from typing import Any
from .qbra_plugin import QbraPlugin


def classFactory(iface: Any) -> QbraPlugin:
    """QGIS plugin factory function.
    
    Args:
        iface: QGIS interface object.
        
    Returns:
        Instance of QbraPlugin.
    """
    return QbraPlugin(iface)