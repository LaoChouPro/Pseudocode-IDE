"""
AST节点类定义
每个节点对应一种语法结构
"""
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ASTNode:
    """AST节点基类"""
    pass


# ==================== 程序结构 ====================

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


# ==================== 声明语句 ====================

@dataclass
class DeclareStmt(ASTNode):
    identifier: str
    type_spec: Any


@dataclass
class ConstantStmt(ASTNode):
    identifier: str
    value: Any


@dataclass
class TypeDefStmt(ASTNode):
    name: str
    fields: List['DeclareStmt']


# ==================== 类型 ====================

@dataclass
class SimpleType(ASTNode):
    type_name: str  # INTEGER, REAL, STRING, CHAR, BOOLEAN, DATE


@dataclass
class ArrayType(ASTNode):
    dimensions: List[tuple]  # [(lower, upper), ...]
    element_type: Any


@dataclass
class CustomType(ASTNode):
    type_name: str


# ==================== 赋值和访问 ====================

@dataclass
class AssignStmt(ASTNode):
    target: 'IdentifierAccess'
    value: Any


@dataclass
class IdentifierAccess(ASTNode):
    name: str
    index1: Optional[Any] = None  # 数组索引
    index2: Optional[Any] = None  # 二维数组第二索引
    field: Optional[str] = None   # 记录字段


# ==================== 输入输出 ====================

@dataclass
class InputStmt(ASTNode):
    target: IdentifierAccess


@dataclass
class OutputStmt(ASTNode):
    items: List[Any]


# ==================== 控制结构 ====================

@dataclass
class IfStmt(ASTNode):
    condition: Any
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None


@dataclass
class CaseStmt(ASTNode):
    identifier: str
    branches: List['CaseBranch']
    otherwise: Optional[ASTNode] = None


@dataclass
class CaseBranch(ASTNode):
    condition: Any  # 可以是单值或范围
    statement: ASTNode


@dataclass
class RangeCondition(ASTNode):
    start: Any
    end: Any


# ==================== 循环结构 ====================

@dataclass
class ForStmt(ASTNode):
    variable: str
    start: Any
    end: Any
    step: Optional[Any]
    body: List[ASTNode]


@dataclass
class WhileStmt(ASTNode):
    condition: Any
    body: List[ASTNode]


@dataclass
class RepeatStmt(ASTNode):
    body: List[ASTNode]
    condition: Any


# ==================== 过程和函数 ====================

@dataclass
class ProcedureDef(ASTNode):
    name: str
    parameters: List['Parameter']
    body: List[ASTNode]


@dataclass
class FunctionDef(ASTNode):
    name: str
    parameters: List['Parameter']
    return_type: Any
    body: List[ASTNode]


@dataclass
class Parameter(ASTNode):
    name: str
    type_spec: Any
    by_ref: bool = False


@dataclass
class ProcedureCall(ASTNode):
    name: str
    arguments: List[Any]


@dataclass
class ReturnStmt(ASTNode):
    value: Any


# ==================== 文件操作 ====================

@dataclass
class FileOpenStmt(ASTNode):
    file_id: str
    mode: str  # READ, WRITE, APPEND


@dataclass
class FileReadStmt(ASTNode):
    file_id: str
    target: IdentifierAccess


@dataclass
class FileWriteStmt(ASTNode):
    file_id: str
    value: Any


@dataclass
class FileCloseStmt(ASTNode):
    file_id: str


# ==================== 表达式 ====================

@dataclass
class BinaryOp(ASTNode):
    operator: str
    left: Any
    right: Any


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: Any


@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[Any]


# ==================== 字面量 ====================

@dataclass
class Literal(ASTNode):
    value: Any
    type_hint: str  # INTEGER, REAL, STRING, CHAR, BOOLEAN


@dataclass
class Identifier(ASTNode):
    name: str


# ==================== 注释 ====================

@dataclass
class Comment(ASTNode):
    text: str
