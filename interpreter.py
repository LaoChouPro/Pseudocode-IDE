"""
解释器核心 - 执行AST
采用访问者模式遍历和执行AST节点
"""
from typing import Any, List
from ast_nodes import *
from environment import Environment, FileManager
import pseudocode_types as pt
from builtin_functions import is_builtin_function, call_builtin_function
import sys


class ReturnValue(Exception):
    """用于函数返回值的特殊异常"""
    def __init__(self, value):
        self.value = value


class Interpreter:
    """解释器 - 执行AST"""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.global_env = Environment(strict_mode=strict_mode)
        self.current_env = self.global_env
        self.file_manager = FileManager()

    def interpret(self, program: Program):
        """执行程序"""
        try:
            for statement in program.statements:
                self.execute_statement(statement)
        finally:
            # 确保所有文件被关闭
            self.file_manager.close_all()

    def execute_statement(self, stmt: ASTNode):
        """执行语句"""
        if isinstance(stmt, DeclareStmt):
            self.execute_declare(stmt)
        elif isinstance(stmt, ConstantStmt):
            self.execute_constant(stmt)
        elif isinstance(stmt, TypeDefStmt):
            self.execute_type_def(stmt)
        elif isinstance(stmt, AssignStmt):
            self.execute_assign(stmt)
        elif isinstance(stmt, InputStmt):
            self.execute_input(stmt)
        elif isinstance(stmt, OutputStmt):
            self.execute_output(stmt)
        elif isinstance(stmt, IfStmt):
            self.execute_if(stmt)
        elif isinstance(stmt, CaseStmt):
            self.execute_case(stmt)
        elif isinstance(stmt, ForStmt):
            self.execute_for(stmt)
        elif isinstance(stmt, WhileStmt):
            self.execute_while(stmt)
        elif isinstance(stmt, RepeatStmt):
            self.execute_repeat(stmt)
        elif isinstance(stmt, ProcedureDef):
            self.execute_procedure_def(stmt)
        elif isinstance(stmt, FunctionDef):
            self.execute_function_def(stmt)
        elif isinstance(stmt, ProcedureCall):
            self.execute_procedure_call(stmt)
        elif isinstance(stmt, ReturnStmt):
            value = self.evaluate_expression(stmt.value)
            raise ReturnValue(value)
        elif isinstance(stmt, FileOpenStmt):
            self.execute_file_open(stmt)
        elif isinstance(stmt, FileReadStmt):
            self.execute_file_read(stmt)
        elif isinstance(stmt, FileWriteStmt):
            self.execute_file_write(stmt)
        elif isinstance(stmt, FileCloseStmt):
            self.execute_file_close(stmt)

    def execute_declare(self, stmt: DeclareStmt):
        """执行声明"""
        # 创建类型实例
        value = self.create_type_instance(stmt.type_spec)
        self.current_env.define_variable(stmt.identifier, value)

    def create_type_instance(self, type_spec):
        """根据类型规格创建实例"""
        if isinstance(type_spec, SimpleType):
            type_name = type_spec.type_name
            if type_name == 'INTEGER':
                return pt.IntegerType(0)
            elif type_name == 'REAL':
                return pt.RealType(0.0)
            elif type_name == 'STRING':
                return pt.StringType("")
            elif type_name == 'CHAR':
                return pt.CharType(' ')
            elif type_name == 'BOOLEAN':
                return pt.BooleanType(False)
            elif type_name == 'DATE':
                return pt.DateType()
        elif isinstance(type_spec, ArrayType):
            # 计算维度边界
            dimensions = []
            for lower_expr, upper_expr in type_spec.dimensions:
                lower = self.evaluate_expression(lower_expr)
                upper = self.evaluate_expression(upper_expr)
                # 转换为整数
                if isinstance(lower, pt.IntegerType):
                    lower = lower.value
                if isinstance(upper, pt.IntegerType):
                    upper = upper.value
                dimensions.append((int(lower), int(upper)))

            # 获取元素类型名称
            if isinstance(type_spec.element_type, SimpleType):
                element_type = type_spec.element_type.type_name
            else:
                element_type = None

            return pt.ArrayType(dimensions, element_type)
        elif isinstance(type_spec, CustomType):
            # 自定义类型
            type_def = self.current_env.get_type(type_spec.type_name)
            return self.create_record_instance(type_def)

        return None

    def create_record_instance(self, type_def: TypeDefStmt) -> pt.RecordType:
        """创建记录类型实例"""
        fields = {}
        for field in type_def.fields:
            fields[field.identifier] = field.type_spec

        record = pt.RecordType(fields)

        # 初始化字段
        for field in type_def.fields:
            default_value = self.create_type_instance(field.type_spec)
            record.set_field(field.identifier, default_value)

        return record

    def execute_constant(self, stmt: ConstantStmt):
        """执行常量定义"""
        value = self.evaluate_expression(stmt.value)
        self.current_env.define_constant(stmt.identifier, value)

    def execute_type_def(self, stmt: TypeDefStmt):
        """执行类型定义"""
        self.current_env.define_type(stmt.name, stmt)

    def execute_assign(self, stmt: AssignStmt):
        """执行赋值"""
        value = self.evaluate_expression(stmt.value)
        self.set_identifier_value(stmt.target, value)

    def check_type_compatibility(self, declared_value, new_value, var_name: str):
        """检查赋值类型兼容性"""
        # 处理Python原生类型和伪代码类型的映射
        def normalize_type(value):
            """将值规范化为标准类型名称"""
            if isinstance(value, pt.IntegerType):
                return 'INTEGER'
            elif isinstance(value, pt.RealType):
                return 'REAL'
            elif isinstance(value, pt.StringType):
                return 'STRING'
            elif isinstance(value, pt.CharType):
                return 'CHAR'
            elif isinstance(value, pt.BooleanType):
                return 'BOOLEAN'
            elif isinstance(value, pt.DateType):
                return 'DATE'
            elif isinstance(value, pt.ArrayType):
                return 'ARRAY'
            elif isinstance(value, pt.RecordType):
                return 'RECORD'
            # Python原生类型 - 注意bool是int的子类，要先检查bool
            elif isinstance(value, bool):
                return 'BOOLEAN'
            elif isinstance(value, int):
                return 'INTEGER'
            elif isinstance(value, float):
                return 'REAL'
            elif isinstance(value, str):
                return 'STRING' if len(value) != 1 else 'CHAR'
            else:
                return type(value).__name__

        declared_type = normalize_type(declared_value)
        new_type = normalize_type(new_value)

        # 完全相同的类型 - 允许
        if declared_type == new_type:
            return

        # INTEGER 可以赋值给 REAL（隐式转换）
        if declared_type == 'REAL' and new_type == 'INTEGER':
            return

        # 其他情况都不允许
        raise TypeError(f"类型不匹配：变量 '{var_name}' 声明为 {declared_type} 类型，不能赋值 {new_type} 类型的值")

    def set_identifier_value(self, target: IdentifierAccess, value):
        """设置标识符的值"""
        if target.index1 is not None:
            # 数组赋值
            array = self.current_env.get_variable(target.name)
            index1 = self.evaluate_expression(target.index1)
            # 类型检查：数组索引必须是INTEGER类型
            if not isinstance(index1, pt.IntegerType):
                raise TypeError(f"数组索引必须是INTEGER类型，而不是{type(index1).__name__}")
            index1 = index1.value

            if target.index2 is not None:
                # 二维数组
                index2 = self.evaluate_expression(target.index2)
                # 类型检查：数组索引必须是INTEGER类型
                if not isinstance(index2, pt.IntegerType):
                    raise TypeError(f"数组索引必须是INTEGER类型，而不是{type(index2).__name__}")
                index2 = index2.value
                # 类型检查：数组元素类型
                existing_value = array.get(index1, index2)
                if existing_value is not None:
                    self.check_type_compatibility(existing_value, value, f"{target.name}[{index1}, {index2}]")
                array.set(index1, index2, value)
            else:
                # 一维数组
                # 类型检查：数组元素类型
                existing_value = array.get(index1)
                if existing_value is not None:
                    self.check_type_compatibility(existing_value, value, f"{target.name}[{index1}]")
                array.set(index1, value)

        elif target.field is not None:
            # 记录字段赋值
            record = self.current_env.get_variable(target.name)
            # 类型检查：记录字段类型
            existing_value = record.get_field(target.field)
            if existing_value is not None:
                self.check_type_compatibility(existing_value, value, f"{target.name}.{target.field}")
            record.set_field(target.field, value)
        else:
            # 简单变量赋值
            # 类型检查：只有在变量已存在时才检查类型
            try:
                existing_value = self.current_env.get_variable(target.name)
                self.check_type_compatibility(existing_value, value, target.name)
            except RuntimeError:
                # 变量不存在，允许在非严格模式下创建
                pass
            self.current_env.set_variable(target.name, value)

    def execute_input(self, stmt: InputStmt):
        """执行输入"""
        try:
            user_input = input()
            value = self.parse_input_value(user_input)
            self.set_identifier_value(stmt.target, value)
        except EOFError:
            raise RuntimeError("Unexpected end of input")

    def parse_input_value(self, input_str: str):
        """解析输入值"""
        input_str = input_str.strip()

        # 尝试解析为数字
        try:
            if '.' in input_str:
                return pt.RealType(float(input_str))
            else:
                return pt.IntegerType(int(input_str))
        except ValueError:
            pass

        # 尝试解析为布尔值
        if input_str.upper() in ['TRUE', 'FALSE']:
            return pt.BooleanType(input_str.upper() == 'TRUE')

        # 默认为字符串
        return pt.StringType(input_str)

    def execute_output(self, stmt: OutputStmt):
        """执行输出"""
        outputs = []
        for item in stmt.items:
            value = self.evaluate_expression(item)
            outputs.append(self.to_output_string(value))

        print(' '.join(outputs))

    def to_output_string(self, value) -> str:
        """将值转换为输出字符串"""
        if isinstance(value, (pt.IntegerType, pt.RealType, pt.StringType, pt.CharType, pt.BooleanType, pt.DateType)):
            return str(value)
        elif isinstance(value, (int, float, str, bool)):
            return str(value)
        else:
            return str(value)

    def execute_if(self, stmt: IfStmt):
        """执行IF语句"""
        condition = self.evaluate_expression(stmt.condition)

        if self.is_truthy(condition):
            for s in stmt.then_block:
                self.execute_statement(s)
        elif stmt.else_block:
            for s in stmt.else_block:
                self.execute_statement(s)

    def execute_case(self, stmt: CaseStmt):
        """执行CASE语句"""
        identifier_value = self.current_env.get_variable(stmt.identifier)

        # 遍历分支
        for branch in stmt.branches:
            if self.match_case_condition(identifier_value, branch.condition):
                self.execute_statement(branch.statement)
                return

        # OTHERWISE分支
        if stmt.otherwise:
            self.execute_statement(stmt.otherwise)

    def match_case_condition(self, value, condition) -> bool:
        """匹配CASE条件"""
        if isinstance(condition, RangeCondition):
            # 范围匹配
            start = self.evaluate_expression(condition.start)
            end = self.evaluate_expression(condition.end)
            return self.compare_values(value, start, '>=') and self.compare_values(value, end, '<=')
        else:
            # 值匹配
            cond_value = self.evaluate_expression(condition)
            return self.compare_values(value, cond_value, '=')

    def execute_for(self, stmt: ForStmt):
        """执行FOR循环"""
        start = self.evaluate_expression(stmt.start)
        end = self.evaluate_expression(stmt.end)

        if stmt.step:
            step = self.evaluate_expression(stmt.step)
        else:
            step = pt.IntegerType(1)

        # 类型检查：FOR循环只接受INTEGER类型
        if not isinstance(start, pt.IntegerType):
            raise TypeError(f"FOR循环的起始值必须是INTEGER类型，而不是{type(start).__name__}")
        if not isinstance(end, pt.IntegerType):
            raise TypeError(f"FOR循环的结束值必须是INTEGER类型，而不是{type(end).__name__}")
        if not isinstance(step, pt.IntegerType):
            raise TypeError(f"FOR循环的步长必须是INTEGER类型，而不是{type(step).__name__}")

        # 提取整数值
        start = start.value
        end = end.value
        step = step.value

        # 执行循环
        counter = start
        self.current_env.define_variable(stmt.variable, pt.IntegerType(counter))

        if step > 0:
            while counter <= end:
                for s in stmt.body:
                    self.execute_statement(s)
                counter += step
                self.current_env.set_variable(stmt.variable, pt.IntegerType(counter))
        else:
            while counter >= end:
                for s in stmt.body:
                    self.execute_statement(s)
                counter += step
                self.current_env.set_variable(stmt.variable, pt.IntegerType(counter))

    def execute_while(self, stmt: WhileStmt):
        """执行WHILE循环"""
        while True:
            condition = self.evaluate_expression(stmt.condition)
            # 类型检查：WHILE条件必须是BOOLEAN类型
            if not isinstance(condition, pt.BooleanType):
                raise TypeError(f"WHILE循环的条件必须是BOOLEAN类型，而不是{type(condition).__name__}")
            if not self.is_truthy(condition):
                break

            for s in stmt.body:
                self.execute_statement(s)

    def execute_repeat(self, stmt: RepeatStmt):
        """执行REPEAT循环"""
        while True:
            for s in stmt.body:
                self.execute_statement(s)

            condition = self.evaluate_expression(stmt.condition)
            # 类型检查：REPEAT-UNTIL条件必须是BOOLEAN类型
            if not isinstance(condition, pt.BooleanType):
                raise TypeError(f"REPEAT-UNTIL循环的条件必须是BOOLEAN类型，而不是{type(condition).__name__}")
            if self.is_truthy(condition):
                break

    def execute_procedure_def(self, stmt: ProcedureDef):
        """执行过程定义"""
        self.current_env.define_procedure(stmt.name, stmt)

    def execute_function_def(self, stmt: FunctionDef):
        """执行函数定义"""
        self.current_env.define_function(stmt.name, stmt)

    def execute_procedure_call(self, stmt: ProcedureCall):
        """执行过程调用"""
        proc_def = self.current_env.get_procedure(stmt.name)

        # 计算参数值
        arg_values = [self.evaluate_expression(arg) for arg in stmt.arguments]

        # 创建新的作用域
        old_env = self.current_env
        self.current_env = self.current_env.create_child()

        # 绑定参数
        for i, param in enumerate(proc_def.parameters):
            if i < len(arg_values):
                if param.by_ref:
                    # BYREF参数 - 传引用
                    # 这里需要特殊处理，直接引用原变量
                    arg_expr = stmt.arguments[i]
                    if isinstance(arg_expr, IdentifierAccess):
                        # 创建引用（简化实现）
                        self.current_env.define_variable(param.name, arg_values[i])
                    else:
                        raise RuntimeError(f"BYREF parameter must be a variable")
                else:
                    # 传值
                    self.current_env.define_variable(param.name, arg_values[i])

        # 执行过程体
        try:
            for s in proc_def.body:
                self.execute_statement(s)

            # BYREF参数需要写回
            for i, param in enumerate(proc_def.parameters):
                if param.by_ref and i < len(arg_values):
                    arg_expr = stmt.arguments[i]
                    if isinstance(arg_expr, IdentifierAccess):
                        new_value = self.current_env.get_variable(param.name)
                        self.current_env = old_env
                        self.set_identifier_value(arg_expr, new_value)
                        self.current_env = self.current_env.create_child()

        finally:
            # 恢复作用域
            self.current_env = old_env

    def execute_file_open(self, stmt: FileOpenStmt):
        """执行文件打开"""
        self.file_manager.open_file(stmt.file_id, stmt.mode)

    def execute_file_read(self, stmt: FileReadStmt):
        """执行文件读取"""
        content = self.file_manager.read_file(stmt.file_id)
        value = pt.StringType(content)
        self.set_identifier_value(stmt.target, value)

    def execute_file_write(self, stmt: FileWriteStmt):
        """执行文件写入"""
        value = self.evaluate_expression(stmt.value)
        content = self.to_output_string(value)
        self.file_manager.write_file(stmt.file_id, content)

    def execute_file_close(self, stmt: FileCloseStmt):
        """执行文件关闭"""
        self.file_manager.close_file(stmt.file_id)

    # ==================== 表达式求值 ====================

    def evaluate_expression(self, expr):
        """求值表达式"""
        if isinstance(expr, Literal):
            return self.evaluate_literal(expr)
        elif isinstance(expr, Identifier):
            return self.current_env.get_variable(expr.name)
        elif isinstance(expr, IdentifierAccess):
            return self.evaluate_identifier_access(expr)
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr)
        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr)
        else:
            raise RuntimeError(f"Unknown expression type: {type(expr)}")

    def evaluate_literal(self, literal: Literal):
        """求值字面量"""
        if literal.type_hint == 'INTEGER':
            return pt.IntegerType(literal.value)
        elif literal.type_hint == 'REAL':
            return pt.RealType(literal.value)
        elif literal.type_hint == 'STRING':
            return pt.StringType(literal.value)
        elif literal.type_hint == 'CHAR':
            return pt.CharType(literal.value)
        elif literal.type_hint == 'BOOLEAN':
            return pt.BooleanType(literal.value)
        else:
            return literal.value

    def evaluate_identifier_access(self, access: IdentifierAccess):
        """求值标识符访问"""
        if access.index1 is not None:
            # 数组访问
            array = self.current_env.get_variable(access.name)
            index1 = self.evaluate_expression(access.index1)
            # 类型检查：数组索引必须是INTEGER类型
            if not isinstance(index1, pt.IntegerType):
                raise TypeError(f"数组索引必须是INTEGER类型，而不是{type(index1).__name__}")
            index1 = index1.value

            if access.index2 is not None:
                # 二维数组
                index2 = self.evaluate_expression(access.index2)
                # 类型检查：数组索引必须是INTEGER类型
                if not isinstance(index2, pt.IntegerType):
                    raise TypeError(f"数组索引必须是INTEGER类型，而不是{type(index2).__name__}")
                index2 = index2.value
                return array.get(index1, index2)
            else:
                # 一维数组
                return array.get(index1)

        elif access.field is not None:
            # 记录字段访问
            record = self.current_env.get_variable(access.name)
            return record.get_field(access.field)
        else:
            # 简单变量
            return self.current_env.get_variable(access.name)

    def evaluate_binary_op(self, op: BinaryOp):
        """求值二元运算"""
        left = self.evaluate_expression(op.left)
        right = self.evaluate_expression(op.right)

        # 算术运算
        if op.operator == '+':
            return self.add_values(left, right)
        elif op.operator == '-':
            return self.subtract_values(left, right)
        elif op.operator == '*':
            return self.multiply_values(left, right)
        elif op.operator == '/':
            return self.divide_values(left, right)
        elif op.operator == '^':
            return self.power_values(left, right)

        # 字符串连接
        elif op.operator == '&':
            return self.concat_values(left, right)

        # 比较运算
        elif op.operator in ['=', '<>', '<', '>', '<=', '>=']:
            return pt.BooleanType(self.compare_values(left, right, op.operator))

        # 逻辑运算
        elif op.operator == 'AND':
            return pt.BooleanType(self.is_truthy(left) and self.is_truthy(right))
        elif op.operator == 'OR':
            return pt.BooleanType(self.is_truthy(left) or self.is_truthy(right))

        else:
            raise RuntimeError(f"Unknown operator: {op.operator}")

    def evaluate_unary_op(self, op: UnaryOp):
        """求值一元运算"""
        operand = self.evaluate_expression(op.operand)

        if op.operator == '-':
            if isinstance(operand, pt.IntegerType):
                return pt.IntegerType(-operand.value)
            elif isinstance(operand, pt.RealType):
                return pt.RealType(-operand.value)
        elif op.operator == '+':
            return operand
        elif op.operator == 'NOT':
            return pt.BooleanType(not self.is_truthy(operand))

        raise RuntimeError(f"Unknown unary operator: {op.operator}")

    def evaluate_function_call(self, call: FunctionCall):
        """求值函数调用"""
        # 检查是否为内置函数
        if is_builtin_function(call.name):
            arg_values = [self.evaluate_expression(arg) for arg in call.arguments]
            return call_builtin_function(call.name, arg_values, self.file_manager)

        # 用户定义的函数
        func_def = self.current_env.get_function(call.name)

        # 计算参数值
        arg_values = [self.evaluate_expression(arg) for arg in call.arguments]

        # 创建新的作用域
        old_env = self.current_env
        self.current_env = self.current_env.create_child()

        # 绑定参数
        for i, param in enumerate(func_def.parameters):
            if i < len(arg_values):
                self.current_env.define_variable(param.name, arg_values[i])

        # 执行函数体
        try:
            for s in func_def.body:
                self.execute_statement(s)
        except ReturnValue as ret:
            return ret.value
        finally:
            # 恢复作用域
            self.current_env = old_env

        raise RuntimeError(f"Function '{call.name}' did not return a value")

    # ==================== 辅助方法 ====================

    def is_truthy(self, value) -> bool:
        """判断值是否为真"""
        if isinstance(value, pt.BooleanType):
            return value.value
        elif isinstance(value, bool):
            return value
        elif isinstance(value, pt.IntegerType):
            return value.value != 0
        elif isinstance(value, int):
            return value != 0
        else:
            return bool(value)

    def add_values(self, left, right):
        """加法"""
        left_val = self.to_number(left)
        right_val = self.to_number(right)

        if isinstance(left_val, float) or isinstance(right_val, float):
            return pt.RealType(left_val + right_val)
        else:
            return pt.IntegerType(left_val + right_val)

    def subtract_values(self, left, right):
        """减法"""
        left_val = self.to_number(left)
        right_val = self.to_number(right)

        if isinstance(left_val, float) or isinstance(right_val, float):
            return pt.RealType(left_val - right_val)
        else:
            return pt.IntegerType(left_val - right_val)

    def multiply_values(self, left, right):
        """乘法"""
        left_val = self.to_number(left)
        right_val = self.to_number(right)

        if isinstance(left_val, float) or isinstance(right_val, float):
            return pt.RealType(left_val * right_val)
        else:
            return pt.IntegerType(left_val * right_val)

    def divide_values(self, left, right):
        """除法"""
        left_val = self.to_number(left)
        right_val = self.to_number(right)

        if right_val == 0:
            raise RuntimeError("Division by zero")

        return pt.RealType(left_val / right_val)

    def power_values(self, left, right):
        """幂运算"""
        left_val = self.to_number(left)
        right_val = self.to_number(right)

        result = left_val ** right_val

        if isinstance(result, float):
            return pt.RealType(result)
        else:
            return pt.IntegerType(int(result))

    def concat_values(self, left, right):
        """字符串连接"""
        left_str = self.to_string(left)
        right_str = self.to_string(right)
        return pt.StringType(left_str + right_str)

    def compare_values(self, left, right, operator: str) -> bool:
        """比较值"""
        # 尝试数值比较
        try:
            left_val = self.to_number(left)
            right_val = self.to_number(right)

            if operator == '=':
                return left_val == right_val
            elif operator == '<>':
                return left_val != right_val
            elif operator == '<':
                return left_val < right_val
            elif operator == '>':
                return left_val > right_val
            elif operator == '<=':
                return left_val <= right_val
            elif operator == '>=':
                return left_val >= right_val
        except:
            pass

        # 字符串比较
        left_str = self.to_string(left)
        right_str = self.to_string(right)

        if operator == '=':
            return left_str == right_str
        elif operator == '<>':
            return left_str != right_str
        elif operator == '<':
            return left_str < right_str
        elif operator == '>':
            return left_str > right_str
        elif operator == '<=':
            return left_str <= right_str
        elif operator == '>=':
            return left_str >= right_str

        return False

    def to_number(self, value):
        """转换为数字"""
        if isinstance(value, pt.IntegerType):
            return value.value
        elif isinstance(value, pt.RealType):
            return value.value
        elif isinstance(value, (int, float)):
            return value
        else:
            raise TypeError(f"Cannot convert {type(value)} to number")

    def to_string(self, value) -> str:
        """转换为字符串"""
        if isinstance(value, (pt.StringType, pt.CharType)):
            return str(value.value)
        elif isinstance(value, (pt.IntegerType, pt.RealType, pt.BooleanType)):
            return str(value)
        elif isinstance(value, str):
            return value
        else:
            return str(value)
