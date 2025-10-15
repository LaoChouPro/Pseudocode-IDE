"""
类型系统 - 支持所有伪代码数据类型
"""
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
import re


class PseudocodeType:
    """类型基类"""
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class IntegerType(PseudocodeType):
    """整数类型"""
    def __init__(self, value=0):
        if isinstance(value, str):
            value = int(value)
        elif isinstance(value, float):
            value = int(value)
        super().__init__(int(value) if value is not None else 0)

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)


class RealType(PseudocodeType):
    """实数类型"""
    def __init__(self, value=0.0):
        if isinstance(value, str):
            value = float(value)
        super().__init__(float(value) if value is not None else 0.0)

    def __float__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __str__(self):
        return str(self.value)


class StringType(PseudocodeType):
    """字符串类型"""
    def __init__(self, value=""):
        if value is None:
            value = ""
        super().__init__(str(value))

    def __str__(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def __getitem__(self, index):
        return self.value[index]


class CharType(PseudocodeType):
    """字符类型"""
    def __init__(self, value=' '):
        if value is None:
            value = ' '
        value_str = str(value)
        if len(value_str) > 1:
            value_str = value_str[0]
        super().__init__(value_str)

    def __str__(self):
        return self.value


class BooleanType(PseudocodeType):
    """布尔类型"""
    def __init__(self, value=False):
        if isinstance(value, str):
            value = value.upper() in ['TRUE', 'T', '1']
        super().__init__(bool(value))

    def __bool__(self):
        return self.value

    def __str__(self):
        return "TRUE" if self.value else "FALSE"


class DateType(PseudocodeType):
    """日期类型 - 支持扩展的日期操作"""

    # 支持多种日期格式
    DATE_FORMATS = [
        "%d/%m/%Y",  # 01/12/2024
        "%Y-%m-%d",  # 2024-12-01
        "%d-%m-%Y",  # 01-12-2024
    ]

    def __init__(self, value=None):
        if value is None:
            self.value = datetime.now()
        elif isinstance(value, str):
            parsed = False
            for fmt in self.DATE_FORMATS:
                try:
                    self.value = datetime.strptime(value, fmt)
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                raise ValueError(f"Invalid date format: {value}")
        elif isinstance(value, datetime):
            self.value = value
        else:
            raise TypeError(f"Cannot convert {type(value)} to DateType")

    def day(self):
        return self.value.day

    def month(self):
        return self.value.month

    def year(self):
        return self.value.year

    def weekday(self):
        """返回星期几(0=Monday, 6=Sunday)"""
        return self.value.weekday()

    def add_days(self, days):
        return DateType(self.value + timedelta(days=days))

    def add_months(self, months):
        new_month = self.value.month + months
        new_year = self.value.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        return DateType(self.value.replace(year=new_year, month=new_month))

    def diff_days(self, other):
        """计算两个日期之间的天数差"""
        if not isinstance(other, DateType):
            raise TypeError("Can only compare DateType with DateType")
        return (self.value - other.value).days

    def __str__(self):
        return self.value.strftime("%d/%m/%Y")

    def __eq__(self, other):
        if not isinstance(other, DateType):
            return False
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, DateType):
            raise TypeError("Can only compare DateType with DateType")
        return self.value < other.value

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


class ArrayType(PseudocodeType):
    """数组类型 - 支持自定义下界"""
    def __init__(self, dimensions, element_type, default_value=None):
        """
        dimensions: [(lower, upper), ...] 每个维度的下界和上界
        element_type: 元素类型
        """
        self.dimensions = dimensions
        self.element_type = element_type
        self.lower_bounds = [d[0] for d in dimensions]
        self.upper_bounds = [d[1] for d in dimensions]

        # 计算实际存储大小
        sizes = [upper - lower + 1 for lower, upper in dimensions]

        # 创建多维数组
        if len(dimensions) == 1:
            self.data = [self._create_default(default_value) for _ in range(sizes[0])]
        elif len(dimensions) == 2:
            self.data = [[self._create_default(default_value) for _ in range(sizes[1])]
                         for _ in range(sizes[0])]
        else:
            raise ValueError("Only 1D and 2D arrays are supported")

        super().__init__(self.data)

    def _create_default(self, default_value):
        """创建默认值"""
        if default_value is not None:
            return default_value

        # 根据类型创建默认值
        if self.element_type == "INTEGER":
            return 0
        elif self.element_type == "REAL":
            return 0.0
        elif self.element_type == "STRING":
            return ""
        elif self.element_type == "CHAR":
            return ' '
        elif self.element_type == "BOOLEAN":
            return False
        else:
            return None

    def get(self, *indices):
        """获取数组元素"""
        if len(indices) != len(self.dimensions):
            raise IndexError(f"Array requires {len(self.dimensions)} indices, got {len(indices)}")

        # 转换为实际索引
        actual_indices = []
        for i, idx in enumerate(indices):
            if not (self.lower_bounds[i] <= idx <= self.upper_bounds[i]):
                raise IndexError(f"Index {idx} out of bounds [{self.lower_bounds[i]}:{self.upper_bounds[i]}]")
            actual_indices.append(idx - self.lower_bounds[i])

        if len(actual_indices) == 1:
            return self.data[actual_indices[0]]
        else:
            return self.data[actual_indices[0]][actual_indices[1]]

    def set(self, *args):
        """设置数组元素 - 最后一个参数是值"""
        indices = args[:-1]
        value = args[-1]

        if len(indices) != len(self.dimensions):
            raise IndexError(f"Array requires {len(self.dimensions)} indices, got {len(indices)}")

        # 转换为实际索引
        actual_indices = []
        for i, idx in enumerate(indices):
            if not (self.lower_bounds[i] <= idx <= self.upper_bounds[i]):
                raise IndexError(f"Index {idx} out of bounds [{self.lower_bounds[i]}:{self.upper_bounds[i]}]")
            actual_indices.append(idx - self.lower_bounds[i])

        if len(actual_indices) == 1:
            self.data[actual_indices[0]] = value
        else:
            self.data[actual_indices[0]][actual_indices[1]] = value

    def __repr__(self):
        return f"ArrayType({self.dimensions}, {self.element_type})"


class RecordType(PseudocodeType):
    """记录类型（结构体）"""
    def __init__(self, fields: Dict[str, Any]):
        """
        fields: {field_name: field_type}
        """
        self.fields = fields
        self.values = {name: None for name in fields.keys()}
        super().__init__(self.values)

    def get_field(self, field_name: str):
        if field_name not in self.fields:
            raise AttributeError(f"Record has no field '{field_name}'")
        return self.values[field_name]

    def set_field(self, field_name: str, value):
        if field_name not in self.fields:
            raise AttributeError(f"Record has no field '{field_name}'")
        self.values[field_name] = value

    def __repr__(self):
        return f"RecordType({self.values})"


# 类型转换工具
def to_python_value(value):
    """将伪代码类型转换为Python原生类型"""
    if isinstance(value, PseudocodeType):
        if isinstance(value, (IntegerType, RealType)):
            return value.value
        elif isinstance(value, (StringType, CharType)):
            return str(value.value)
        elif isinstance(value, BooleanType):
            return bool(value.value)
        elif isinstance(value, DateType):
            return value.value
        elif isinstance(value, ArrayType):
            return value.data
        elif isinstance(value, RecordType):
            return value.values
    return value


def from_python_value(value, type_hint=None):
    """将Python原生类型转换为伪代码类型"""
    if isinstance(value, PseudocodeType):
        return value

    if type_hint:
        if type_hint == "INTEGER":
            return IntegerType(value)
        elif type_hint == "REAL":
            return RealType(value)
        elif type_hint == "STRING":
            return StringType(value)
        elif type_hint == "CHAR":
            return CharType(value)
        elif type_hint == "BOOLEAN":
            return BooleanType(value)
        elif type_hint == "DATE":
            return DateType(value)

    # 自动推断类型
    if isinstance(value, bool):
        return BooleanType(value)
    elif isinstance(value, int):
        return IntegerType(value)
    elif isinstance(value, float):
        return RealType(value)
    elif isinstance(value, str):
        if len(value) == 1:
            return CharType(value)
        return StringType(value)
    elif isinstance(value, datetime):
        return DateType(value)

    return value
