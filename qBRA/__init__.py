"""qBRA QGIS Plugin - Building Restriction Areas for ILS/LLZ."""

from typing import Any


def classFactory(iface: Any) -> "QbraPlugin":
    """QGIS plugin factory function.
    
    Args:
        iface: QGIS interface object.
        
    Returns:
        Instance of QbraPlugin.
    """
    # Import here to avoid loading QGIS dependencies during test discovery
    from .qbra_plugin import QbraPlugin
    return QbraPlugin(iface)