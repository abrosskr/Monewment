from enum import Enum

class WeightUnit(str, Enum):
    G = "g"
    KG = "kg"
    ML = "ml"
    L = "l"
    OZ = "oz"  # Support for parsing, but storage might prioritize Metric
    LB = "lb"

class ManufacturingType(str, Enum):
    OWN = "Own"         # Brand owner manufactures it (e.g. Nongshim)
    OEM = "OEM"         # Contract manufacturing (e.g. Ottogi for Private Label)
    IMPORT = "Import"   # Direct import (e.g. Divella)
    UNKNOWN = "Unknown"

class ProductStatus(str, Enum):
    ACTIVE = "Active"
    DISCONTINUED = "Discontinued"
    SEASONAL = "Seasonal"

class FulfillmentType(str, Enum):
    OWNED_INVENTORY = "Owned"           # 사입/자체 재고
    DROP_SHIPPING = "DropShipping"      # 산지직송/위탁 배송
    CROSS_DOCKING = "CrossDocking"      # 크로스도킹 (입고 즉시 출고)
