from typing import Any, Union

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsGeometryUtils,
    QgsProject,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
    QgsLineString,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor

from ..models.bra_parameters import BRAParameters
from ..models.feature_definition import FeatureDefinition

# Keep formulas and geometry construction identical to legacy script.


def create_feature(
    definition: FeatureDefinition,
    params: BRAParameters,
    geometry: QgsGeometry,
) -> QgsFeature:
    """Create a BRA feature from a definition and parameters.
    
    This function eliminates code duplication by providing a single place
    to create features with consistent attributes.
    
    Args:
        definition: FeatureDefinition with id, area, max_elev, area_name
        params: BRAParameters with all calculation parameters
        geometry: QgsGeometry for the feature polygon
        
    Returns:
        QgsFeature with geometry and attributes set
    """
    # Facility label preferred for 'type' attribute (falls back to key)
    type_value = params.facility_label or params.facility_key or ""
    
    feature = QgsFeature()
    feature.setGeometry(geometry)
    feature.setAttributes([
        definition.id,
        definition.area,
        definition.max_elev,
        definition.area_name,
        str(round(params.a, 2)),
        str(params.b),
        str(params.h),
        str(round(params.r, 2)),
        str(params.D),
        str(params.H),
        str(params.L),
        str(params.phi),
        type_value,
    ])
    
    return feature


def build_layers(iface: Any, params: BRAParameters) -> QgsVectorLayer:
    """Build BRA (Building Restriction Areas) vector layer with polygons.
    
    Args:
        iface: QGIS interface object
        params: BRAParameters dataclass with all calculation parameters
    
    Returns:
        QgsVectorLayer with BRA polygon features
        
    Raises:
        ValueError: If no feature is selected on the active layer
    """
    # Extract parameters from dataclass
    layer = params.active_layer
    selection = layer.selectedFeatures()
    if not selection:
        raise ValueError("Select one feature on the active layer")
    feat = selection[0]
    p_geom = feat.geometry().asPoint()

    map_srid = iface.mapCanvas().mapSettings().destinationCrs().authid()

    # Helper to add Z
    def pz(point: Union[QgsPoint, QgsPointXY], z: float) -> QgsPoint:
        """Add Z coordinate to a point.
        
        Args:
            point: 2D or 3D point
            z: Z elevation value
            
        Returns:
            QgsPoint with Z coordinate set
        """
        cPoint = QgsPoint(point)
        cPoint.addZValue()
        cPoint.setZ(z)
        return cPoint

    a = params.a
    b = params.b
    h = params.h
    r = params.r
    D = params.D
    H = params.H
    L = params.L
    phi = params.phi
    azimuth = params.azimuth
    remark = params.remark
    display_name = params.display_name or params.remark
    site_elev = params.site_elev

    side_elev = site_elev + H

    # Points (direction is encoded solely by azimuth)
    pt_f = p_geom.project(a, azimuth)
    pt_b = p_geom.project(b, azimuth - 180)

    pt_al = pt_f.project(D, azimuth - 90)
    pt_ar = pt_f.project(D, azimuth + 90)
    pt_bl = pt_b.project(D, azimuth - 90)
    pt_br = pt_b.project(D, azimuth + 90)

    pt_Ll = pt_b.project(L, azimuth - 90)
    pt_Lr = pt_b.project(L, azimuth + 90)

    pt_rc = p_geom.project(r, azimuth)

    pt_Llp = pt_Ll.project(10000, azimuth)
    pt_alp = pt_al.project(10000, azimuth - phi)

    pt_Lrp = pt_Lr.project(10000, azimuth)
    pt_arp = pt_ar.project(10000, azimuth + phi)

    pt_rl = QgsPointXY(QgsGeometryUtils.lineCircleIntersection(p_geom, r, pt_al, pt_alp, pt_rc)[1])
    pt_rr = QgsPointXY(QgsGeometryUtils.lineCircleIntersection(p_geom, r, pt_ar, pt_arp, pt_rc)[1])

    pt_drl = QgsPointXY(
        QgsGeometryUtils.segmentIntersection(QgsPoint(pt_al), QgsPoint(pt_alp), QgsPoint(pt_Ll), QgsPoint(pt_Llp))[1]
    )
    pt_drr = QgsPointXY(
        QgsGeometryUtils.segmentIntersection(QgsPoint(pt_ar), QgsPoint(pt_arp), QgsPoint(pt_Lr), QgsPoint(pt_Lrp))[1]
    )

    # Memory layer for polygons
    z_layer = QgsVectorLayer("PolygonZ?crs=" + map_srid, f"{display_name} BRA_areas", "memory")
    fields = [
        QgsField("id", QVariant.Int),
        QgsField("area", QVariant.String),
        QgsField("max_elev", QVariant.String),
        QgsField("area_name", QVariant.String),
        QgsField("a", QVariant.String),
        QgsField("b", QVariant.String),
        QgsField("h", QVariant.String),
        QgsField("r", QVariant.String),
        QgsField("D", QVariant.String),
        QgsField("H", QVariant.String),
        QgsField("L", QVariant.String),
        QgsField("phi", QVariant.String),
        # Place 'type' as the last attribute per user request
        QgsField("type", QVariant.String),
    ]
    z_layer.dataProvider().addAttributes(fields)
    z_layer.updateFields()
    pr = z_layer.dataProvider()

    # Build all feature geometries (preserving exact calculations from legacy script)
    
    # Base geometry
    base_points = [pz(pt_bl, site_elev), pz(pt_br, site_elev), pz(pt_ar, site_elev), pz(pt_al, site_elev), pz(pt_bl, site_elev)]
    base_geom = QgsGeometry(QgsPolygon(QgsLineString(base_points), rings=[]))

    # Left level geometry
    llevel_points = [pz(pt_Ll, side_elev), pz(pt_bl, side_elev), pz(pt_al, side_elev), pz(pt_drl, side_elev), pz(pt_Ll, side_elev)]
    llevel_geom = QgsGeometry(QgsPolygon(QgsLineString(llevel_points), rings=[]))

    # Right level geometry
    rlevel_points = [pz(pt_br, side_elev), pz(pt_Lr, side_elev), pz(pt_drr, side_elev), pz(pt_ar, side_elev), pz(pt_br, side_elev)]
    rlevel_geom = QgsGeometry(QgsPolygon(QgsLineString(rlevel_points), rings=[]))

    # Slope geometry (with curve + arc)
    from qgis.core import QgsCircularString

    arc = QgsCircularString.fromTwoPointsAndCenter(
        pz(pt_rl, site_elev + h),
        pz(pt_rr, site_elev + h),
        pz(p_geom, site_elev + h),
    )
    line_start = QgsLineString(
        [pz(pt_rr, site_elev + h), pz(pt_ar, site_elev), pz(pt_al, site_elev), pz(pt_rl, site_elev + h)]
    )
    curve = line_start.toCurveType()
    curve.addCurve(arc)
    polygon = QgsPolygon()
    polygon.setExteriorRing(curve)
    slope_geom = QgsGeometry(polygon)

    # Wall geometries
    wall1_points = [pz(pt_bl, site_elev), pz(pt_bl, side_elev), pz(pt_br, side_elev), pz(pt_br, site_elev)]
    wall1_geom = QgsGeometry(QgsPolygon(QgsLineString(wall1_points), rings=[]))

    wall2_points = [pz(pt_al, site_elev), pz(pt_al, side_elev), pz(pt_bl, side_elev), pz(pt_bl, site_elev), pz(pt_al, site_elev)]
    wall2_geom = QgsGeometry(QgsPolygon(QgsLineString(wall2_points), rings=[]))

    wall3_points = [pz(pt_ar, site_elev), pz(pt_ar, side_elev), pz(pt_br, side_elev), pz(pt_br, site_elev), pz(pt_ar, site_elev)]
    wall3_geom = QgsGeometry(QgsPolygon(QgsLineString(wall3_points), rings=[]))

    # Define all features declaratively (eliminates code duplication)
    feature_definitions = [
        (FeatureDefinition(1, "base", str(site_elev), display_name, base_points), base_geom),
        (FeatureDefinition(2, "left level", str(side_elev), display_name, llevel_points), llevel_geom),
        (FeatureDefinition(3, "right level", str(side_elev), display_name, rlevel_points), rlevel_geom),
        (FeatureDefinition(4, "slope", str(site_elev + h), display_name, []), slope_geom),
        (FeatureDefinition(5, "wall", str(side_elev), display_name, wall1_points), wall1_geom),
        (FeatureDefinition(6, "wall", str(side_elev), display_name, wall2_points), wall2_geom),
        (FeatureDefinition(7, "wall", str(side_elev), remark, wall3_points), wall3_geom),
    ]

    # Create all features using generic function (DRY principle)
    features = [create_feature(definition, params, geometry) for definition, geometry in feature_definitions]
    pr.addFeatures(features)

    # Styling
    z_layer.renderer().symbol().setOpacity(0.5)
    z_layer.renderer().symbol().setColor(QColor("green"))
    z_layer.triggerRepaint()
    z_layer.updateExtents()

    return z_layer
