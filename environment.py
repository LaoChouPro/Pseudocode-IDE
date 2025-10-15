"""
环境和作用域管理 - 管理变量、常量、函数的作用域
"""
from typing import Any, Dict, Optional


class Environment:
    """环境类 - 管理变量和函数的作用域链"""

    def __init__(self, parent: Optional['Environment'] = None, strict_mode: bool = False):
        self.parent = parent
        self.strict_mode = strict_mode  # 严格模式：要求变量必须先声明
        self.variables: Dict[str, Any] = {}
        self.constants: Dict[str, Any] = {}
        self.types: Dict[str, Any] = {}  # 自定义类型定义
        self.procedures: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}

    def define_variable(self, name: str, value: Any):
        """定义变量"""
        name_upper = name.upper()
        if name_upper in self.constants:
            raise RuntimeError(f"Cannot redefine constant '{name}'")
        self.variables[name_upper] = value

    def define_constant(self, name: str, value: Any):
        """定义常量"""
        name_upper = name.upper()
        if name_upper in self.constants:
            raise RuntimeError(f"Constant '{name}' already defined")
        if name_upper in self.variables:
            raise RuntimeError(f"Cannot define constant '{name}': variable with same name exists")
        self.constants[name_upper] = value

    def define_type(self, name: str, type_def: Any):
        """定义自定义类型"""
        name_upper = name.upper()
        self.types[name_upper] = type_def

    def define_procedure(self, name: str, proc_def: Any):
        """定义过程"""
        name_upper = name.upper()
        self.procedures[name_upper] = proc_def

    def define_function(self, name: str, func_def: Any):
        """定义函数"""
        name_upper = name.upper()
        self.functions[name_upper] = func_def

    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        name_upper = name.upper()

        # 先检查常量
        if name_upper in self.constants:
            return self.constants[name_upper]

        # 再检查变量
        if name_upper in self.variables:
            return self.variables[name_upper]

        # 向父作用域查找
        if self.parent:
            return self.parent.get_variable(name)

        raise RuntimeError(f"Undefined variable '{name}'")

    def set_variable(self, name: str, value: Any):
        """设置变量值"""
        name_upper = name.upper()

        # 不能修改常量
        if name_upper in self.constants:
            raise RuntimeError(f"Cannot modify constant '{name}'")

        # 在当前作用域或父作用域中查找变量
        if name_upper in self.variables:
            self.variables[name_upper] = value
            return

        # 向父作用域查找
        if self.parent:
            try:
                self.parent.set_variable(name, value)
                return
            except RuntimeError:
                pass

        # 严格模式：变量未声明则报错
        if self.strict_mode or (self.parent and self.parent.strict_mode):
            raise RuntimeError(f"Variable '{name}' used before declaration. Use DECLARE to declare variables first.")

        # 非严格模式：如果找不到，就在当前作用域创建（隐式声明）
        self.variables[name_upper] = value

    def get_type(self, name: str) -> Any:
        """获取类型定义"""
        name_upper = name.upper()

        if name_upper in self.types:
            return self.types[name_upper]

        if self.parent:
            return self.parent.get_type(name)

        raise RuntimeError(f"Undefined type '{name}'")

    def get_procedure(self, name: str) -> Any:
        """获取过程定义"""
        name_upper = name.upper()

        if name_upper in self.procedures:
            return self.procedures[name_upper]

        if self.parent:
            return self.parent.get_procedure(name)

        raise RuntimeError(f"Undefined procedure '{name}'")

    def get_function(self, name: str) -> Any:
        """获取函数定义"""
        name_upper = name.upper()

        if name_upper in self.functions:
            return self.functions[name_upper]

        if self.parent:
            return self.parent.get_function(name)

        raise RuntimeError(f"Undefined function '{name}'")

    def has_variable(self, name: str) -> bool:
        """检查变量是否存在"""
        name_upper = name.upper()
        if name_upper in self.variables or name_upper in self.constants:
            return True
        if self.parent:
            return self.parent.has_variable(name)
        return False

    def create_child(self) -> 'Environment':
        """创建子作用域"""
        return Environment(parent=self)

    def __repr__(self):
        return f"Environment(vars={list(self.variables.keys())}, consts={list(self.constants.keys())})"


class FileHandle:
    """文件句柄类 - 管理文件操作状态"""

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode.upper()
        self.handle = None
        self.is_open = False
        self.at_eof = False

    def open(self):
        """打开文件"""
        if self.is_open:
            raise RuntimeError(f"File '{self.filename}' is already open")

        mode_map = {
            'READ': 'r',
            'WRITE': 'w',
            'APPEND': 'a'
        }

        try:
            self.handle = open(self.filename, mode_map[self.mode], encoding='utf-8')
            self.is_open = True
            self.at_eof = False
        except Exception as e:
            raise RuntimeError(f"Cannot open file '{self.filename}': {e}")

    def read_line(self) -> str:
        """读取一行"""
        if not self.is_open:
            raise RuntimeError(f"File '{self.filename}' is not open")
        if self.mode != 'READ':
            raise RuntimeError(f"File '{self.filename}' is not open for reading")

        try:
            line = self.handle.readline()
            if line:
                # 移除换行符
                return line.rstrip('\n\r')
            else:
                self.at_eof = True
                return ""
        except Exception as e:
            raise RuntimeError(f"Error reading from file '{self.filename}': {e}")

    def write_line(self, content: str):
        """写入一行"""
        if not self.is_open:
            raise RuntimeError(f"File '{self.filename}' is not open")
        if self.mode not in ['WRITE', 'APPEND']:
            raise RuntimeError(f"File '{self.filename}' is not open for writing")

        try:
            self.handle.write(content + '\n')
        except Exception as e:
            raise RuntimeError(f"Error writing to file '{self.filename}': {e}")

    def is_at_eof(self) -> bool:
        """检查是否到达文件末尾"""
        return self.at_eof

    def close(self):
        """关闭文件"""
        if self.is_open and self.handle:
            try:
                self.handle.close()
                self.is_open = False
                self.at_eof = False
            except Exception as e:
                raise RuntimeError(f"Error closing file '{self.filename}': {e}")

    def __del__(self):
        """析构函数 - 确保文件被关闭"""
        if self.is_open:
            self.close()


class FileManager:
    """文件管理器 - 管理所有打开的文件"""

    def __init__(self):
        self.files: Dict[str, FileHandle] = {}

    def open_file(self, file_id: str, mode: str):
        """打开文件"""
        file_id_upper = file_id.upper()

        # 如果已经打开，先关闭
        if file_id_upper in self.files:
            self.files[file_id_upper].close()

        # 创建新的文件句柄
        file_handle = FileHandle(file_id, mode)
        file_handle.open()
        self.files[file_id_upper] = file_handle

    def read_file(self, file_id: str) -> str:
        """从文件读取一行"""
        file_id_upper = file_id.upper()
        if file_id_upper not in self.files:
            raise RuntimeError(f"File '{file_id}' is not open")
        return self.files[file_id_upper].read_line()

    def write_file(self, file_id: str, content: str):
        """向文件写入一行"""
        file_id_upper = file_id.upper()
        if file_id_upper not in self.files:
            raise RuntimeError(f"File '{file_id}' is not open")
        self.files[file_id_upper].write_line(content)

    def is_eof(self, file_id: str) -> bool:
        """检查文件是否到达末尾"""
        file_id_upper = file_id.upper()
        if file_id_upper not in self.files:
            raise RuntimeError(f"File '{file_id}' is not open")
        return self.files[file_id_upper].is_at_eof()

    def close_file(self, file_id: str):
        """关闭文件"""
        file_id_upper = file_id.upper()
        if file_id_upper in self.files:
            self.files[file_id_upper].close()
            del self.files[file_id_upper]

    def close_all(self):
        """关闭所有文件"""
        for file_handle in self.files.values():
            file_handle.close()
        self.files.clear()

    def __del__(self):
        """析构函数 - 确保所有文件被关闭"""
        self.close_all()
