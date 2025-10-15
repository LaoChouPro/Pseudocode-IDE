"""
内置函数库 - 实现所有伪代码标准内置函数
支持扩展自定义函数
"""
import math
from datetime import datetime
from pseudocode_types import *
from typing import Any


def builtin_asc(char: Any) -> int:
    """ASC(char) - 返回字符的ASCII值"""
    if isinstance(char, str):
        if len(char) == 0:
            raise ValueError("ASC: Empty string")
        return ord(char[0])
    elif hasattr(char, 'value'):
        char_val = str(char.value)
        if len(char_val) == 0:
            raise ValueError("ASC: Empty string")
        return ord(char_val[0])
    else:
        raise TypeError(f"ASC: Expected string or char, got {type(char)}")


def builtin_chr(code: Any) -> str:
    """CHR(code) - 返回ASCII值对应的字符"""
    if isinstance(code, int):
        return chr(code)
    elif hasattr(code, 'value'):
        return chr(int(code.value))
    else:
        raise TypeError(f"CHR: Expected integer, got {type(code)}")


def builtin_int(value: Any) -> int:
    """INT(value) - 取整函数（向下取整）"""
    if isinstance(value, (int, float)):
        return int(value)
    elif hasattr(value, 'value'):
        return int(value.value)
    elif isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            raise ValueError(f"INT: Cannot convert '{value}' to integer")
    else:
        raise TypeError(f"INT: Cannot convert {type(value)} to integer")


def builtin_length(string: Any) -> int:
    """LENGTH(string) - 返回字符串长度"""
    if isinstance(string, str):
        return len(string)
    elif hasattr(string, 'value'):
        return len(str(string.value))
    else:
        raise TypeError(f"LENGTH: Expected string, got {type(string)}")


def builtin_left(string: Any, count: Any) -> str:
    """LEFT(string, count) - 返回字符串左侧count个字符"""
    if isinstance(string, str):
        s = string
    elif hasattr(string, 'value'):
        s = str(string.value)
    else:
        raise TypeError(f"LEFT: Expected string, got {type(string)}")

    if isinstance(count, int):
        n = count
    elif hasattr(count, 'value'):
        n = int(count.value)
    else:
        raise TypeError(f"LEFT: Expected integer for count, got {type(count)}")

    if n < 0:
        raise ValueError(f"LEFT: Count cannot be negative, got {n}")

    if n > len(s):
        raise ValueError(f"LEFT: Requested {n} characters but string only has {len(s)} characters")

    result = s[:n]
    # LEFT函数始终返回STRING类型，即使长度为1或0
    from pseudocode_types import StringType
    return StringType(result)


def builtin_right(string: Any, count: Any) -> str:
    """RIGHT(string, count) - 返回字符串右侧count个字符"""
    if isinstance(string, str):
        s = string
    elif hasattr(string, 'value'):
        s = str(string.value)
    else:
        raise TypeError(f"RIGHT: Expected string, got {type(string)}")

    if isinstance(count, int):
        n = count
    elif hasattr(count, 'value'):
        n = int(count.value)
    else:
        raise TypeError(f"RIGHT: Expected integer for count, got {type(count)}")

    if n < 0:
        raise ValueError(f"RIGHT: Count cannot be negative, got {n}")

    if n > len(s):
        raise ValueError(f"RIGHT: Requested {n} characters but string only has {len(s)} characters")

    if n == 0:
        # RIGHT函数始终返回STRING类型
        from pseudocode_types import StringType
        return StringType("")

    result = s[-n:]
    # RIGHT函数始终返回STRING类型，即使长度为1
    from pseudocode_types import StringType
    return StringType(result)


def builtin_mid(string: Any, start: Any, length: Any) -> str:
    """MID(string, start, length) - 返回从start位置开始的length个字符"""
    if isinstance(string, str):
        s = string
    elif hasattr(string, 'value'):
        s = str(string.value)
    else:
        raise TypeError(f"MID: Expected string, got {type(string)}")

    if isinstance(start, int):
        start_pos = start
    elif hasattr(start, 'value'):
        start_pos = int(start.value)
    else:
        raise TypeError(f"MID: Expected integer for start, got {type(start)}")

    if isinstance(length, int):
        len_val = length
    elif hasattr(length, 'value'):
        len_val = int(length.value)
    else:
        raise TypeError(f"MID: Expected integer for length, got {type(length)}")

    # 参数验证
    if start_pos < 1:
        raise ValueError(f"MID: Start position must be >= 1, got {start_pos}")

    if len_val < 0:
        raise ValueError(f"MID: Length cannot be negative, got {len_val}")

    if start_pos > len(s):
        raise ValueError(f"MID: Start position {start_pos} is beyond string length {len(s)}")

    # 检查是否超出字符串末尾
    end_pos = start_pos - 1 + len_val
    if end_pos > len(s):
        raise ValueError(f"MID: Requested substring from position {start_pos} with length {len_val} exceeds string length {len(s)}")

    # 伪代码通常使用1-based索引
    result = s[start_pos - 1:start_pos - 1 + len_val]
    # MID函数始终返回STRING类型，即使长度为1
    from pseudocode_types import StringType
    return StringType(result)


def builtin_to_upper(string: Any) -> str:
    """TO_UPPER(string) - 转换为大写"""
    if isinstance(string, str):
        return string.upper()
    elif hasattr(string, 'value'):
        return str(string.value).upper()
    else:
        raise TypeError(f"TO_UPPER: Expected string or char, got {type(string)}")


def builtin_to_lower(string: Any) -> str:
    """TO_LOWER(string) - 转换为小写"""
    if isinstance(string, str):
        return string.lower()
    elif hasattr(string, 'value'):
        return str(string.value).lower()
    else:
        raise TypeError(f"TO_LOWER: Expected string or char, got {type(string)}")


# 兼容性别名
def builtin_ucase(string: Any) -> str:
    """UCASE(string) - 转换为大写（兼容性别名）"""
    return builtin_to_upper(string)


def builtin_lcase(string: Any) -> str:
    """LCASE(string) - 转换为小写（兼容性别名）"""
    return builtin_to_lower(string)


def builtin_num_to_str(number: Any) -> str:
    """NUM_TO_STR(number) - 将数字转换为字符串"""
    if isinstance(number, (int, float)):
        return str(number)
    elif hasattr(number, 'value'):
        return str(number.value)
    else:
        raise TypeError(f"NUM_TO_STR: Expected REAL or INTEGER, got {type(number)}")


def builtin_str_to_num(string: Any) -> float:
    """STR_TO_NUM(string) - 将字符串转换为数字"""
    if isinstance(string, str):
        try:
            # 检查是否为整数
            if '.' in string:
                return float(string)
            else:
                return int(string)
        except ValueError:
            raise ValueError(f"STR_TO_NUM: Cannot convert '{string}' to number")
    elif hasattr(string, 'value'):
        return builtin_str_to_num(str(string.value))
    else:
        raise TypeError(f"STR_TO_NUM: Expected CHAR or STRING, got {type(string)}")


def builtin_is_num(string: Any) -> bool:
    """IS_NUM(string) - 检查字符串是否为有效数字"""
    if isinstance(string, str):
        try:
            float(string)
            return True
        except ValueError:
            return False
    elif hasattr(string, 'value'):
        return builtin_is_num(str(string.value))
    else:
        raise TypeError(f"IS_NUM: Expected CHAR or STRING, got {type(string)}")


# ==================== 数学函数 ====================

def builtin_abs(value: Any) -> Any:
    """ABS(value) - 绝对值"""
    if isinstance(value, (int, float)):
        return abs(value)
    elif hasattr(value, 'value'):
        return abs(value.value)
    else:
        raise TypeError(f"ABS: Expected number, got {type(value)}")


def builtin_sqrt(value: Any) -> float:
    """SQRT(value) - 平方根"""
    if isinstance(value, (int, float)):
        return math.sqrt(value)
    elif hasattr(value, 'value'):
        return math.sqrt(float(value.value))
    else:
        raise TypeError(f"SQRT: Expected number, got {type(value)}")


def builtin_power(base: Any, exponent: Any) -> Any:
    """POWER(base, exponent) - 幂运算"""
    if isinstance(base, (int, float)):
        b = base
    elif hasattr(base, 'value'):
        b = float(base.value)
    else:
        raise TypeError(f"POWER: Expected number for base, got {type(base)}")

    if isinstance(exponent, (int, float)):
        e = exponent
    elif hasattr(exponent, 'value'):
        e = float(exponent.value)
    else:
        raise TypeError(f"POWER: Expected number for exponent, got {type(exponent)}")

    return b ** e


def builtin_round(value: Any, decimals: Any = 0) -> Any:
    """ROUND(value, decimals) - 四舍五入"""
    if isinstance(value, (int, float)):
        v = value
    elif hasattr(value, 'value'):
        v = float(value.value)
    else:
        raise TypeError(f"ROUND: Expected number, got {type(value)}")

    if isinstance(decimals, int):
        d = decimals
    elif hasattr(decimals, 'value'):
        d = int(decimals.value)
    else:
        d = 0

    return round(v, d)


def builtin_mod(dividend: Any, divisor: Any) -> Any:
    """MOD(dividend, divisor) - 取模运算"""
    if isinstance(dividend, (int, float)):
        a = dividend
    elif hasattr(dividend, 'value'):
        a = dividend.value
    else:
        raise TypeError(f"MOD: Expected number for dividend, got {type(dividend)}")

    if isinstance(divisor, (int, float)):
        b = divisor
    elif hasattr(divisor, 'value'):
        b = divisor.value
    else:
        raise TypeError(f"MOD: Expected number for divisor, got {type(divisor)}")

    return a % b


def builtin_div(dividend: Any, divisor: Any) -> int:
    """DIV(dividend, divisor) - 整除"""
    if isinstance(dividend, (int, float)):
        a = dividend
    elif hasattr(dividend, 'value'):
        a = dividend.value
    else:
        raise TypeError(f"DIV: Expected number for dividend, got {type(dividend)}")

    if isinstance(divisor, (int, float)):
        b = divisor
    elif hasattr(divisor, 'value'):
        b = divisor.value
    else:
        raise TypeError(f"DIV: Expected number for divisor, got {type(divisor)}")

    return int(a // b)


def builtin_rand(upper: Any) -> float:
    """RAND(upper) - 返回0到upper之间的随机实数(不包括upper)"""
    import random

    if isinstance(upper, (int, float)):
        u = float(upper)
    elif hasattr(upper, 'value'):
        u = float(upper.value)
    else:
        raise TypeError(f"RAND: Expected INTEGER for upper bound, got {type(upper)}")

    if u <= 0:
        raise ValueError(f"RAND: Upper bound must be positive, got {u}")

    return random.random() * u


# ==================== 日期函数（扩展功能） ====================

def builtin_today() -> 'DateType':
    """TODAY() - 返回当前日期"""
    from types import DateType
    return DateType(datetime.now())


def builtin_day(date: Any) -> int:
    """DAY(date) - 返回日期的天"""
    if hasattr(date, 'day'):
        return date.day()
    else:
        raise TypeError(f"DAY: Expected DATE type, got {type(date)}")


def builtin_month(date: Any) -> int:
    """MONTH(date) - 返回日期的月"""
    if hasattr(date, 'month'):
        return date.month()
    else:
        raise TypeError(f"MONTH: Expected DATE type, got {type(date)}")


def builtin_year(date: Any) -> int:
    """YEAR(date) - 返回日期的年"""
    if hasattr(date, 'year'):
        return date.year()
    else:
        raise TypeError(f"YEAR: Expected DATE type, got {type(date)}")


def builtin_dayindex(date: Any) -> int:
    """DAYINDEX(date) - 返回日期的星期索引(Sunday=1, Monday=2等)"""
    if hasattr(date, 'weekday'):
        # datetime的weekday(): Monday=0, Sunday=6
        # 转换为伪代码规范: Sunday=1, Monday=2, ..., Saturday=7
        py_weekday = date.weekday()
        return py_weekday + 2 if py_weekday != 6 else 1
    else:
        raise TypeError(f"DAYINDEX: Expected DATE type, got {type(date)}")


def builtin_setdate(day: Any, month: Any, year: Any) -> 'DateType':
    """SETDATE(day, month, year) - 创建指定日期"""
    from pseudocode_types import DateType
    from datetime import datetime
    try:
        d = int(day.value if hasattr(day, 'value') else day)
        m = int(month.value if hasattr(month, 'value') else month)
        y = int(year.value if hasattr(year, 'value') else year)
        # 使用datetime创建日期对象，然后传递给DateType
        date_obj = datetime(y, m, d)
        return DateType(date_obj)
    except ValueError as e:
        raise ValueError(f"SETDATE: Invalid date values - {e}")


# 兼容性别名
def builtin_dayof(date: Any) -> int:
    """DAYOF(date) - 返回日期的天（兼容性别名）"""
    return builtin_day(date)


def builtin_monthof(date: Any) -> int:
    """MONTHOF(date) - 返回日期的月（兼容性别名）"""
    return builtin_month(date)


def builtin_yearof(date: Any) -> int:
    """YEAROF(date) - 返回日期的年（兼容性别名）"""
    return builtin_year(date)


def builtin_datediff(date1: Any, date2: Any) -> int:
    """DATEDIFF(date1, date2) - 计算两个日期之间的天数差"""
    if hasattr(date1, 'diff_days') and hasattr(date2, 'value'):
        return date1.diff_days(date2)
    else:
        raise TypeError(f"DATEDIFF: Expected DATE types")


# ==================== 文件函数 ====================

def builtin_eof(file_manager: Any, file_id: str) -> bool:
    """EOF(file) - 检查文件是否到达末尾"""
    if hasattr(file_manager, 'is_eof'):
        return file_manager.is_eof(file_id)
    else:
        raise RuntimeError("EOF: File manager not available")


# ==================== 随机数函数（扩展功能） ====================

def builtin_random() -> float:
    """RANDOM() - 返回0到1之间的随机数"""
    import random
    return random.random()


def builtin_randomint(lower: Any, upper: Any) -> int:
    """RANDOMINT(lower, upper) - 返回lower到upper之间的随机整数"""
    import random

    if isinstance(lower, int):
        l = lower
    elif hasattr(lower, 'value'):
        l = int(lower.value)
    else:
        raise TypeError(f"RANDOMINT: Expected integer for lower, got {type(lower)}")

    if isinstance(upper, int):
        u = upper
    elif hasattr(upper, 'value'):
        u = int(upper.value)
    else:
        raise TypeError(f"RANDOMINT: Expected integer for upper, got {type(upper)}")

    return random.randint(l, u)


# ==================== 内置函数映射表 ====================

BUILTIN_FUNCTIONS = {
    # 字符串和字符函数（文档规范）
    'LEFT': builtin_left,
    'RIGHT': builtin_right,
    'MID': builtin_mid,
    'LENGTH': builtin_length,
    'TO_UPPER': builtin_to_upper,
    'TO_LOWER': builtin_to_lower,
    'NUM_TO_STR': builtin_num_to_str,
    'STR_TO_NUM': builtin_str_to_num,
    'IS_NUM': builtin_is_num,
    'ASC': builtin_asc,
    'CHR': builtin_chr,

    # 数字函数（文档规范）
    'INT': builtin_int,
    'RAND': builtin_rand,

    # 日期函数（文档规范）
    'DAY': builtin_day,
    'MONTH': builtin_month,
    'YEAR': builtin_year,
    'DAYINDEX': builtin_dayindex,
    'SETDATE': builtin_setdate,
    'TODAY': builtin_today,

    # 文本文件函数（文档规范）
    'EOF': builtin_eof,

    # 兼容性别名
    'UCASE': builtin_ucase,
    'LCASE': builtin_lcase,
    'DAYOF': builtin_dayof,
    'MONTHOF': builtin_monthof,
    'YEAROF': builtin_yearof,

    # 扩展数学函数
    'ABS': builtin_abs,
    'SQRT': builtin_sqrt,
    'POWER': builtin_power,
    'ROUND': builtin_round,
    'MOD': builtin_mod,
    'DIV': builtin_div,

    # 扩展随机数函数
    'RANDOM': builtin_random,
    'RANDOMINT': builtin_randomint,

    # 扩展日期函数
    'DATEDIFF': builtin_datediff,
}


def is_builtin_function(name: str) -> bool:
    """检查是否为内置函数"""
    return name.upper() in BUILTIN_FUNCTIONS


def call_builtin_function(name: str, args: list, file_manager=None) -> Any:
    """调用内置函数"""
    name_upper = name.upper()

    if name_upper not in BUILTIN_FUNCTIONS:
        raise RuntimeError(f"Unknown builtin function '{name}'")

    func = BUILTIN_FUNCTIONS[name_upper]

    # 特殊处理EOF函数
    if name_upper == 'EOF' and file_manager:
        return builtin_eof(file_manager, args[0])

    try:
        return func(*args)
    except TypeError as e:
        raise RuntimeError(f"Error calling builtin function '{name}': {e}")
