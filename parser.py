"""
语法分析器 - 递归下降解析器
将token流转换为AST
"""
from typing import List, Optional
from lexer import Token
from ast_nodes import *


class Parser:
    """递归下降语法分析器"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[0] if tokens else None

    def error(self, message: str):
        """报错"""
        if self.current:
            raise SyntaxError(f"{message} at line {self.current.line}, column {self.current.column}")
        else:
            raise SyntaxError(f"{message} at end of file")

    def advance(self):
        """前进到下一个token"""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return self.current

    def peek(self, offset=1) -> Optional[Token]:
        """查看后续token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def expect(self, token_type: str) -> Token:
        """期望特定类型的token"""
        if self.current.type != token_type:
            self.error(f"Expected {token_type}, got {self.current.type}")
        token = self.current
        self.advance()
        return token

    def match(self, *token_types) -> bool:
        """检查当前token是否匹配给定类型之一"""
        return self.current and self.current.type in token_types

    def skip_newlines(self):
        """跳过换行符"""
        while self.match('NEWLINE'):
            self.advance()

    def parse(self) -> Program:
        """解析整个程序"""
        statements = []
        self.skip_newlines()

        while not self.match('EOF'):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        return Program(statements)

    def parse_statement(self):
        """解析语句"""
        self.skip_newlines()

        if self.match('DECLARE'):
            return self.parse_declare()
        elif self.match('CONSTANT'):
            return self.parse_constant()
        elif self.match('TYPE'):
            return self.parse_type_def()
        elif self.match('IF'):
            return self.parse_if()
        elif self.match('CASE'):
            return self.parse_case()
        elif self.match('FOR'):
            return self.parse_for()
        elif self.match('WHILE'):
            return self.parse_while()
        elif self.match('REPEAT'):
            return self.parse_repeat()
        elif self.match('PROCEDURE'):
            return self.parse_procedure_def()
        elif self.match('FUNCTION'):
            return self.parse_function_def()
        elif self.match('RETURN'):
            return self.parse_return()
        elif self.match('CALL'):
            return self.parse_procedure_call()
        elif self.match('INPUT'):
            return self.parse_input()
        elif self.match('OUTPUT', 'PRINT'):
            return self.parse_output()
        elif self.match('OPENFILE'):
            return self.parse_file_open()
        elif self.match('READFILE'):
            return self.parse_file_read()
        elif self.match('WRITEFILE'):
            return self.parse_file_write()
        elif self.match('CLOSEFILE'):
            return self.parse_file_close()
        elif self.match('NAME'):
            # 可能是赋值语句
            return self.parse_assignment_or_call()
        elif self.match('EOF'):
            # 到达文件末尾
            return None
        else:
            # 遇到无法识别的token，抛出错误
            self.error(f"Unexpected token: {self.current.type} ('{self.current.value}')")

    def parse_declare(self) -> DeclareStmt:
        """解析DECLARE语句"""
        self.expect('DECLARE')
        name = self.expect('NAME').value
        self.expect('COLON')
        type_spec = self.parse_type_spec()
        return DeclareStmt(name, type_spec)

    def parse_constant(self) -> ConstantStmt:
        """解析CONSTANT语句"""
        self.expect('CONSTANT')
        name = self.expect('NAME').value
        self.expect('ARROW')  # 只接受 <-
        value = self.parse_expression()
        return ConstantStmt(name, value)

    def parse_type_def(self) -> TypeDefStmt:
        """解析TYPE定义"""
        self.expect('TYPE')
        self.skip_newlines()
        name = self.expect('NAME').value
        self.skip_newlines()
        self.expect('INDENT')

        fields = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            if self.match('DECLARE'):
                fields.append(self.parse_declare())
            self.skip_newlines()

        self.expect('DEDENT')
        self.expect('ENDTYPE')

        return TypeDefStmt(name, fields)

    def parse_type_spec(self):
        """解析类型"""
        if self.match('INTEGER', 'REAL', 'STRING', 'CHAR', 'BOOLEAN', 'DATE'):
            type_name = self.current.type
            self.advance()
            return SimpleType(type_name)
        elif self.match('ARRAY'):
            return self.parse_array_type()
        elif self.match('NAME'):
            type_name = self.current.value
            self.advance()
            return CustomType(type_name)
        else:
            self.error("Expected type")

    def parse_array_type(self) -> ArrayType:
        """解析数组类型"""
        self.expect('ARRAY')
        self.expect('LBRACKET')

        dimensions = []
        # 第一个维度
        lower = self.parse_expression()
        self.expect('COLON')
        upper = self.parse_expression()
        dimensions.append((lower, upper))

        # 第二个维度（可选）
        if self.match('COMMA'):
            self.advance()
            lower = self.parse_expression()
            self.expect('COLON')
            upper = self.parse_expression()
            dimensions.append((lower, upper))

        self.expect('RBRACKET')
        self.expect('OF')
        element_type = self.parse_type_spec()

        return ArrayType(dimensions, element_type)

    def parse_assignment_or_call(self):
        """解析赋值或函数调用"""
        # 向前看，判断是赋值还是过程调用
        name = self.current.value
        self.advance()

        # 解析访问器（数组索引、字段访问）
        target = self.parse_identifier_access_rest(name)

        if self.match('ARROW'):
            # 赋值语句
            self.advance()
            value = self.parse_expression()
            return AssignStmt(target, value)
        else:
            self.error("Expected assignment arrow '<-'")

    def parse_identifier_access_rest(self, name: str) -> IdentifierAccess:
        """解析标识符访问的剩余部分"""
        if self.match('LBRACKET'):
            # 数组访问
            self.advance()
            index1 = self.parse_expression()

            if self.match('COMMA'):
                # 二维数组
                self.advance()
                index2 = self.parse_expression()
                self.expect('RBRACKET')
                return IdentifierAccess(name, index1, index2)
            else:
                # 一维数组
                self.expect('RBRACKET')
                return IdentifierAccess(name, index1)

        elif self.match('DOT'):
            # 记录字段访问
            self.advance()
            field = self.expect('NAME').value
            return IdentifierAccess(name, field=field)
        else:
            # 简单变量
            return IdentifierAccess(name)

    def parse_input(self) -> InputStmt:
        """解析INPUT语句"""
        self.expect('INPUT')
        target = self.parse_identifier_access()
        return InputStmt(target)

    def parse_output(self) -> OutputStmt:
        """解析OUTPUT语句"""
        self.advance()  # OUTPUT or PRINT

        items = []
        items.append(self.parse_expression())

        while self.match('COMMA'):
            self.advance()
            items.append(self.parse_expression())

        return OutputStmt(items)

    def parse_identifier_access(self) -> IdentifierAccess:
        """解析标识符访问"""
        name = self.expect('NAME').value
        return self.parse_identifier_access_rest(name)

    def parse_if(self) -> IfStmt:
        """解析IF语句"""
        self.expect('IF')
        condition = self.parse_expression()
        self.skip_newlines()

        if self.match('THEN'):
            self.advance()

        self.skip_newlines()
        self.expect('INDENT')

        then_block = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()

        # ELSE部分
        else_block = None
        if self.match('ELSE'):
            self.advance()
            self.skip_newlines()
            self.expect('INDENT')

            else_block = []
            while not self.match('DEDENT'):
                self.skip_newlines()
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
                self.skip_newlines()

            self.expect('DEDENT')
            self.skip_newlines()

        self.expect('ENDIF')

        return IfStmt(condition, then_block, else_block)

    def parse_case(self) -> CaseStmt:
        """解析CASE语句"""
        self.expect('CASE')
        self.expect('OF')
        identifier = self.expect('NAME').value
        self.skip_newlines()
        self.expect('INDENT')

        branches = []
        otherwise = None

        while not self.match('DEDENT'):
            self.skip_newlines()
            if self.match('OTHERWISE'):
                self.advance()
                self.expect('COLON')
                otherwise = self.parse_statement()
                self.skip_newlines()
            else:
                # CASE分支
                condition = self.parse_case_condition()
                self.expect('COLON')
                statement = self.parse_statement()
                branches.append(CaseBranch(condition, statement))
                self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('ENDCASE')

        return CaseStmt(identifier, branches, otherwise)

    def parse_case_condition(self):
        """解析CASE条件"""
        start = self.parse_expression()

        if self.match('RANGE'):  # ...
            self.advance()
            end = self.parse_expression()
            return RangeCondition(start, end)
        else:
            return start

    def parse_for(self) -> ForStmt:
        """解析FOR循环"""
        self.expect('FOR')
        variable = self.expect('NAME').value
        self.expect('ARROW')
        start = self.parse_expression()
        self.expect('TO')
        end = self.parse_expression()

        step = None
        if self.match('STEP'):
            self.advance()
            step = self.parse_expression()

        self.skip_newlines()
        self.expect('INDENT')

        body = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('NEXT')

        # NEXT后可选变量名
        if self.match('NAME'):
            self.advance()

        return ForStmt(variable, start, end, step, body)

    def parse_while(self) -> WhileStmt:
        """解析WHILE循环"""
        self.expect('WHILE')
        condition = self.parse_expression()
        self.skip_newlines()
        self.expect('INDENT')

        body = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('ENDWHILE')

        return WhileStmt(condition, body)

    def parse_repeat(self) -> RepeatStmt:
        """解析REPEAT循环"""
        self.expect('REPEAT')
        self.skip_newlines()
        self.expect('INDENT')

        body = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('UNTIL')
        condition = self.parse_expression()

        return RepeatStmt(body, condition)

    def parse_procedure_def(self) -> ProcedureDef:
        """解析PROCEDURE定义"""
        self.expect('PROCEDURE')
        name = self.expect('NAME').value
        self.expect('LPAREN')

        parameters = []
        if not self.match('RPAREN'):
            parameters = self.parse_parameter_list()

        self.expect('RPAREN')
        self.skip_newlines()
        self.expect('INDENT')

        body = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('ENDPROCEDURE')

        return ProcedureDef(name, parameters, body)

    def parse_function_def(self) -> FunctionDef:
        """解析FUNCTION定义"""
        self.expect('FUNCTION')
        name = self.expect('NAME').value
        self.expect('LPAREN')

        parameters = []
        if not self.match('RPAREN'):
            parameters = self.parse_parameter_list()

        self.expect('RPAREN')
        self.expect('RETURNS')
        return_type = self.parse_type_spec()
        self.skip_newlines()
        self.expect('INDENT')

        body = []
        while not self.match('DEDENT'):
            self.skip_newlines()
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.expect('DEDENT')
        self.skip_newlines()
        self.expect('ENDFUNCTION')

        return FunctionDef(name, parameters, return_type, body)

    def parse_parameter_list(self) -> List[Parameter]:
        """解析参数列表"""
        parameters = []

        # 第一个参数
        by_ref = False
        if self.match('BYREF'):
            by_ref = True
            self.advance()

        name = self.expect('NAME').value
        self.expect('COLON')
        type_spec = self.parse_type_spec()
        parameters.append(Parameter(name, type_spec, by_ref))

        # 后续参数
        while self.match('COMMA'):
            self.advance()
            by_ref = False
            if self.match('BYREF'):
                by_ref = True
                self.advance()

            name = self.expect('NAME').value
            self.expect('COLON')
            type_spec = self.parse_type_spec()
            parameters.append(Parameter(name, type_spec, by_ref))

        return parameters

    def parse_return(self) -> ReturnStmt:
        """解析RETURN语句"""
        self.expect('RETURN')
        value = self.parse_expression()
        return ReturnStmt(value)

    def parse_procedure_call(self) -> ProcedureCall:
        """解析CALL语句"""
        self.expect('CALL')
        name = self.expect('NAME').value
        self.expect('LPAREN')

        arguments = []
        if not self.match('RPAREN'):
            arguments.append(self.parse_expression())
            while self.match('COMMA'):
                self.advance()
                arguments.append(self.parse_expression())

        self.expect('RPAREN')
        return ProcedureCall(name, arguments)

    def parse_file_open(self) -> FileOpenStmt:
        """解析OPENFILE语句"""
        self.expect('OPENFILE')
        file_id = self.expect('NAME').value
        self.expect('FOR')
        mode = self.current.type  # READ, WRITE, APPEND
        self.advance()
        return FileOpenStmt(file_id, mode)

    def parse_file_read(self) -> FileReadStmt:
        """解析READFILE语句"""
        self.expect('READFILE')
        file_id = self.expect('NAME').value
        self.expect('COMMA')
        target = self.parse_identifier_access()
        return FileReadStmt(file_id, target)

    def parse_file_write(self) -> FileWriteStmt:
        """解析WRITEFILE语句"""
        self.expect('WRITEFILE')
        file_id = self.expect('NAME').value
        self.expect('COMMA')
        value = self.parse_expression()
        return FileWriteStmt(file_id, value)

    def parse_file_close(self) -> FileCloseStmt:
        """解析CLOSEFILE语句"""
        self.expect('CLOSEFILE')
        file_id = self.expect('NAME').value
        return FileCloseStmt(file_id)

    # ==================== 表达式解析 ====================

    def parse_expression(self):
        """解析表达式"""
        return self.parse_logical_or()

    def parse_logical_or(self):
        """解析逻辑OR"""
        left = self.parse_logical_and()

        while self.match('OR'):
            op = self.current.value
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(op, left, right)

        return left

    def parse_logical_and(self):
        """解析逻辑AND"""
        left = self.parse_logical_not()

        while self.match('AND'):
            op = self.current.value
            self.advance()
            right = self.parse_logical_not()
            left = BinaryOp(op, left, right)

        return left

    def parse_logical_not(self):
        """解析逻辑NOT"""
        if self.match('NOT'):
            op = self.current.value
            self.advance()
            operand = self.parse_logical_not()
            return UnaryOp(op, operand)

        return self.parse_comparison()

    def parse_comparison(self):
        """解析比较运算"""
        left = self.parse_concat()

        while self.match('EQ', 'NE', 'LT', 'GT', 'LE', 'GE'):
            if self.current.type == 'EQ':
                op = '='
            elif self.current.type == 'NE':
                op = '<>'
            elif self.current.type == 'LT':
                op = '<'
            elif self.current.type == 'GT':
                op = '>'
            elif self.current.type == 'LE':
                op = '<='
            else:
                op = '>='

            self.advance()
            right = self.parse_concat()
            left = BinaryOp(op, left, right)

        return left

    def parse_concat(self):
        """解析字符串连接"""
        left = self.parse_add_sub()

        while self.match('AMPERSAND'):
            op = '&'
            self.advance()
            right = self.parse_add_sub()
            left = BinaryOp(op, left, right)

        return left

    def parse_add_sub(self):
        """解析加减"""
        left = self.parse_mul_div()

        while self.match('PLUS', 'MINUS'):
            op = self.current.value
            self.advance()
            right = self.parse_mul_div()
            left = BinaryOp(op, left, right)

        return left

    def parse_mul_div(self):
        """解析乘除"""
        left = self.parse_power()

        while self.match('MULTIPLY', 'DIVIDE'):
            op = self.current.value
            self.advance()
            right = self.parse_power()
            left = BinaryOp(op, left, right)

        return left

    def parse_power(self):
        """解析幂运算"""
        left = self.parse_unary()

        if self.match('POWER'):
            op = self.current.value
            self.advance()
            right = self.parse_power()  # 右结合
            left = BinaryOp(op, left, right)

        return left

    def parse_unary(self):
        """解析一元运算"""
        if self.match('MINUS', 'PLUS'):
            op = self.current.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)

        return self.parse_primary()

    def parse_primary(self):
        """解析基本表达式"""
        # 字面量
        if self.match('INTEGER'):
            value = int(self.current.value)
            self.advance()
            return Literal(value, 'INTEGER')

        elif self.match('REAL'):
            value = float(self.current.value)
            self.advance()
            return Literal(value, 'REAL')

        elif self.match('STRING'):
            value = self.current.value[1:-1]  # 去掉引号
            self.advance()
            return Literal(value, 'STRING')

        elif self.match('CHAR'):
            value = self.current.value[1:-1]  # 去掉引号
            self.advance()
            return Literal(value, 'CHAR')

        elif self.match('TRUE', 'FALSE'):
            value = self.current.type == 'TRUE'
            self.advance()
            return Literal(value, 'BOOLEAN')

        # 标识符或函数调用
        elif self.match('NAME'):
            name = self.current.value
            self.advance()

            # 函数调用
            if self.match('LPAREN'):
                self.advance()
                arguments = []
                if not self.match('RPAREN'):
                    arguments.append(self.parse_expression())
                    while self.match('COMMA'):
                        self.advance()
                        arguments.append(self.parse_expression())
                self.expect('RPAREN')
                return FunctionCall(name, arguments)
            else:
                # 标识符访问
                return self.parse_identifier_access_rest(name)

        # 括号表达式
        elif self.match('LPAREN'):
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr

        else:
            self.error(f"Unexpected token in expression: {self.current.type}")
