# Análisis de Bugs y Code Smells - qBRA

**Fecha**: 4 de marzo, 2026  
**Proyecto**: qBRA  
**Status**: Pre-Refactorización

---

## 🐛 Bugs Potenciales Identificados

### Bug #1: Feature ID puede no ser descriptivo

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py#L162-L171)

**Descripción**:

```python
if rwy_idx < 0:
    # Fallback: use feature id as runway label
    remark = f"RWY{feat.id()}"
else:
    remark = f"RWY{attrs[rwy_idx]}"
```

**Problema**: Si no se encuentra el campo runway, usa `feat.id()` que:

- Puede ser un número muy grande o negativo
- No es descriptivo para el usuario
- Podría cambiar si la capa se regenera

**Impacto**: 🟡 Bajo - Solo afecta naming
**Solución**: Usar un default más descriptivo como "RWY_UNKNOWN" o pedir al usuario

---

### Bug #2: Sin validación de valores numéricos

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py#L201-L208)

**Descripción**:

```python
a = float(self._widget.spnA.value())
b = float(self._widget.spnB.value())
# ... etc sin validación
```

**Problema**: No valida que:

- Valores sean positivos
- Valores estén en rangos razonables (e.g., a > 0, phi entre 0-90)
- Relaciones entre valores (e.g., a > b)

**Impacto**: 🔴 Alto - Puede causar resultados inválidos
**Solución**: Agregar validación de rangos en `get_parameters()`

---

### Bug #3: Excepción silenciada en refresh de icon

**Archivo**: [qbra_plugin.py](qBRA/qbra_plugin.py#L23-L26)

**Descripción**:

```python
try:
    self._action.setIcon(self._icon)
except Exception:
    pass
```

**Problema**:

- Excepción genérica silenciada
- No hay logging de qué falló
- Usuario no sabe si el ícono está presente o no

**Impacto**: 🟡 Bajo - Solo afecta UI visual
**Solución**: Log del error o catch específico

---

### Bug #4: División por cero potencial (no confirmado)

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py)

**Descripción**: No confirmado, pero las fórmulas geométricas podrían fallar si:

- D = 0
- r = 0
- Puntos son colineales

**Impacto**: 🟠 Medio - Causa crash
**Solución**: Validar parámetros antes de cálculos (sin cambiar fórmulas)

---

### Bug #5: Puntos insuficientes en routing

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py#L191-L196)

**Descripción**:

```python
if not pts or len(pts) < 2:
    print("QBRA ILS/LLZ: routing geometry has insufficient vertices")
    return None
```

**Problema**:

- Solo hace print (no visible al usuario)
- No lanza excepción
- Plugin se queda en estado "silencioso"

**Impacto**: 🟠 Medio - Usuario no sabe qué pasó
**Solución**: Mostrar mensaje en message bar y lanzar excepción

---

### Bug #6: Layer no agregado si no hay resultado

**Archivo**: [qbra_plugin.py](qBRA/qbra_plugin.py#L59-L65)

**Descripción**:

```python
result_layer = build_layers(self.iface, params)
# ... exception handling
if result_layer:
    QgsProject.instance().addMapLayer(result_layer)
```

**Problema**: Si `build_layers()` retorna None por error silencioso, no hay feedback

**Impacto**: 🟡 Bajo - Hay try/except arriba
**Solución**: Asegurar que build_layers siempre lanza excepción en error

---

## 💩 Code Smells

### Smell #1: Clase Dios (God Object)

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py)

**Descripción**: `IlsLlzDockWidget` hace demasiado:

- Maneja UI
- Calcula parámetros
- Valida datos
- Maneja configuración de facilities
- Extrae datos de layers

**Líneas**: 240  
**Métodos**: 8  
**Responsabilidades**: 5+

**Solución**: Separar en View, Controller, Service (Story 1.3)

---

### Smell #2: Código Duplicado (7x)

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L98-L260)

**Descripción**: Bloque repetido 7 veces:

```python
seg = QgsFeature()
seg.setGeometry(QgsPolygon(...))
seg.setAttributes([id, area, max_elev, ...])
pr.addFeatures([seg])
```

**Duplicación**: ~140 líneas duplicadas  
**Impacto**: Si cambia estructura, hay que cambiar en 7 lugares

**Solución**: Función genérica + configuración (Story 1.4)

---

### Smell #3: Magic Numbers

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L72-L79)

**Descripción**:

```python
pt_Llp = pt_Ll.project(10000, azimuth)
pt_alp = pt_al.project(10000, azimuth - phi)
```

**Números mágicos**:

- `10000` - ¿Qué significa? (proyección al infinito?)
- `-90`, `+90` - Ángulos sin constantes
- `-180` - Azimuth reverso

**Solución**: Constantes con nombres (Story 2.4)

---

### Smell #4: Long Parameter List

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L17)

**Descripción**:

```python
def build_layers(iface, params):
    # params es dict con 12+ keys
```

**Problema**:

- Dict sin tipo
- Fácil equivocarse en key names
- No autocomplete

**Solución**: Dataclass BRAParameters (Story 1.2)

---

### Smell #5: Nombres Crípticos

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L49-L82)

**Descripción**:

```python
pt_al = pt_f.project(D, azimuth - 90)
pt_ar = pt_f.project(D, azimuth + 90)
pt_bl = pt_b.project(D, azimuth - 90)
pt_br = pt_b.project(D, azimuth + 90)
pt_Ll = pt_b.project(L, azimuth - 90)
pt_Lr = pt_b.project(L, azimuth + 90)
```

**Problema**: Sin contexto, imposible saber qué significa:

- `pt_al` - ¿ahead left?
- `pt_ar` - ¿ahead right?
- `pt_Ll` - ¿Left limit?

**Solución**: Nombres descriptivos o al menos comentarios (Story 3.2)

---

### Smell #6: Excepción Genérica

**Archivo**: Múltiples archivos

**Ocurrencias**:

```python
# qbra_plugin.py L25
except Exception:
    pass

# qbra_plugin.py L51
except Exception:
    pass

# qbra_plugin.py L62
except Exception as exc:
    self.iface.messageBar().pushMessage(...)

# dockwidgets/ils/ils_llz_dockwidget.py L82
except Exception:
    self._widget.spnA.setValue(0.0)
```

**Problema**:

- Catch Exception es muy genérico
- Algunos silencian errores
- Dificulta debugging

**Solución**: Excepciones específicas (Story 1.6)

---

### Smell #7: Print Debugging

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py)

**Ocurrencias**:

```python
# L155
print("QBRA ILS/LLZ: no navaid layer selected")
# L158
print("QBRA ILS/LLZ: no routing layer selected")
# L161
print("QBRA ILS/LLZ: no navaid feature selected")
# L187
print("QBRA ILS/LLZ: no routing feature selected")
# L195
print("QBRA ILS/LLZ: routing geometry has insufficient vertices")
# L201
print(f"QBRA ILS/LLZ: direction={direction}, azimuth={azimuth}, d0={geom.length()}")
```

**Problema**:

- 6 prints en producción
- No visible en QGIS UI
- Sin niveles (debug vs error)

**Solución**: Logger proper (Story 1.5)

---

### Smell #8: Función Dentro de Función

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L29-L33)

**Descripción**:

```python
def build_layers(iface, params):
    # ...
    def pz(point, z):
        cPoint = QgsPoint(point)
        cPoint.addZValue()
        cPoint.setZ(z)
        return cPoint
```

**Problema**:

- No reutilizable fuera de build_layers
- Dificulta testing
- Puede tener side effects no obvios

**Solución**: Función top-level o método de clase

---

### Smell #9: Feature Envy

**Archivo**: [dockwidgets/ils/ils_llz_dockwidget.py](qBRA/dockwidgets/ils/ils_llz_dockwidget.py#L69-L85)

**Descripción**: DockWidget accede profundamente a facility_defs:

```python
key = self._widget.cboFacility.currentData()
defs = self._facility_defs.get(key, (None, False, {}))[2]
r_expr = defs.get("r_expr")
```

**Problema**: Necesita conocer estructura interna de facility_defs

**Solución**: Encapsular en FacilityService (Story 1.3)

---

### Smell #10: Hardcoded Strings

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L96-L108)

**Descripción**:

```python
fields = [
    QgsField("id", QVariant.Int),
    QgsField("area", QVariant.String),
    QgsField("max_elev", QVariant.String),
    # ... 10 more
]
```

**Problema**: Nombres de campos repetidos en:

- Definición de fields
- setAttributes() (7 veces)
- No hay constantes

**Solución**: Enum o constantes (Story 2.4)

---

### Smell #11: Falta de Inmutabilidad

**Archivo**: Todos

**Descripción**:

- params es dict mutable
- Configuraciones son dicts mutables
- No hay frozen dataclasses

**Problema**: Puede mutarse accidentalmente
**Solución**: Frozen dataclasses (Story 1.2)

---

### Smell #12: Sin Validación de Precondiciones

**Archivo**: [modules/ils_llz_logic.py](qBRA/modules/ils_llz_logic.py#L17-L46)

**Descripción**:

```python
def build_layers(iface, params):
    layer = params["active_layer"]
    selection = layer.selectedFeatures()
    if not selection:
        raise ValueError("Select one feature on the active layer")
```

**Problema**:

- Solo valida selection
- No valida que params tenga todas las keys
- No valida rangos de valores

**Solución**: Validación completa (Story 1.6)

---

## 📊 Resumen de Severidad

| Categoría        | Count  | Severidad Media |
| ---------------- | ------ | --------------- |
| 🔴 Bugs Críticos | 1      | Alta            |
| 🟠 Bugs Medios   | 3      | Media           |
| 🟡 Bugs Menores  | 2      | Baja            |
| 💩 Code Smells   | 12     | -               |
| **Total Issues** | **18** |                 |

---

## 🎯 Prioridades de Corrección

### Urgente (Sprint 1)

1. Bug #2 - Validación de valores numéricos
2. Smell #1 - Clase Dios
3. Smell #2 - Código duplicado
4. Smell #6 - Excepciones genéricas
5. Smell #7 - Print debugging

### Importante (Sprint 2)

6. Smell #3 - Magic numbers
7. Smell #4 - Long parameter list
8. Smell #10 - Hardcoded strings
9. Smell #11 - Falta inmutabilidad
10. Smell #12 - Sin validación

### Nice to Have (Sprint 3)

11. Bug #1 - Feature ID
12. Bug #5 - Puntos insuficientes (ya tiene check)
13. Smell #5 - Nombres crípticos
14. Smell #8 - Función dentro de función
15. Smell #9 - Feature envy

---

## ✅ Validation Checklist

### Pre-Cálculo

- [ ] active_layer existe y es válido
- [ ] Layer tiene features seleccionados
- [ ] Routing layer existe
- [ ] Routing tiene geometría válida (≥2 puntos)
- [ ] a > 0
- [ ] b > 0
- [ ] h > 0
- [ ] r > 0
- [ ] D > 0
- [ ] H > 0
- [ ] L > 0
- [ ] 0 < phi < 90
- [ ] site_elev es razonable (-1000 < elev < 10000)

### Post-Cálculo

- [ ] Layer creado no es None
- [ ] Layer tiene ≥4 features (base, left, right, slope mínimo)
- [ ] Todas las geometrías son válidas
- [ ] CRS coincide con canvas

---

**Fin del Análisis de Bugs y Code Smells**
