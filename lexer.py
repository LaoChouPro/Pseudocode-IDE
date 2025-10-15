"""
词法分析器 - 处理缩进敏感的语法
将伪代码转换为token流，处理INDENT和DEDENT
"""
import re
from typing import List, Tuple


class Token:
    """Token类"""
    def __init__(self, type: str, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    """词法分析器 - 处理缩进"""

    # 关键字列表
    KEYWORDS = {
        'DECLARE', 'CONSTANT', 'TYPE', 'ENDTYPE',
        'IF', 'THEN', 'ELSE', 'ENDIF',
        'CASE', 'OF', 'OTHERWISE', 'ENDCASE',
        'FOR', 'TO', 'STEP', 'NEXT',
        'WHILE', 'ENDWHILE',
        'REPEAT', 'UNTIL',
        'PROCEDURE', 'ENDPROCEDURE', 'FUNCTION', 'ENDFUNCTION', 'RETURNS', 'RETURN',
        'CALL', 'BYREF',
        'INPUT', 'OUTPUT', 'PRINT',
        'OPENFILE', 'FOR', 'READ', 'WRITE', 'APPEND', 'READFILE', 'WRITEFILE', 'CLOSEFILE',
        'INTEGER', 'REAL', 'STRING', 'CHAR', 'BOOLEAN', 'DATE', 'ARRAY',
        'TRUE', 'FALSE',
        'AND', 'OR', 'NOT',
    }

    # Token类型
    TOKEN_PATTERNS = [
        ('COMMENT', r'//[^\n]*'),
        ('REAL', r'\d+\.\d+'),
        ('INTEGER', r'\d+'),
        ('STRING', r'"([^"\\]|\\.)*"'),
        ('CHAR', r"'([^'\\]|\\.)'"),
        ('ARROW', r'<-'),
        ('LE', r'<='),
        ('GE', r'>='),
        ('NE', r'<>'),
        ('LT', r'<'),
        ('GT', r'>'),
        ('EQ', r'='),
        ('RANGE', r'\.\.\.'),
        ('DOT', r'\.'),
        ('COLON', r':'),
        ('COMMA', r','),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('MULTIPLY', r'\*'),
        ('DIVIDE', r'/'),
        ('POWER', r'\^'),
        ('AMPERSAND', r'&'),
        ('NAME', r'[a-zA-Z][a-zA-Z0-9_]*'),
        ('NEWLINE', r'\n'),
        ('WHITESPACE', r'[ \t]+'),
    ]

    def __init__(self):
        self.compiled_patterns = [
            (name, re.compile(pattern))
            for name, pattern in self.TOKEN_PATTERNS
        ]

    def tokenize(self, code: str) -> List[Token]:
        """将代码转换为token流"""
        lines = code.split('\n')
        tokens = []
        indent_stack = [0]  # 缩进栈

        for line_num, line in enumerate(lines, 1):
            # 跳过空行
            if not line.strip():
                continue

            # 计算当前行的缩进
            indent = self._count_indent(line)
            stripped_line = line.strip()

            # 跳过注释行
            if stripped_line.startswith('//'):
                continue

            # 处理缩进变化
            if indent > indent_stack[-1]:
                # INDENT
                tokens.append(Token('INDENT', '<INDENT>', line_num, indent))
                indent_stack.append(indent)
            elif indent < indent_stack[-1]:
                # DEDENT
                while indent_stack and indent < indent_stack[-1]:
                    tokens.append(Token('DEDENT', '<DEDENT>', line_num, indent))
                    indent_stack.pop()
                if not indent_stack or indent != indent_stack[-1]:
                    raise SyntaxError(f"Indentation error at line {line_num}")

            # 行首添加NEWLINE（用于分隔语句）
            if tokens and tokens[-1].type != 'NEWLINE':
                tokens.append(Token('NEWLINE', '\\n', line_num, 0))

            # 分析该行的token
            col = 0
            while col < len(line):
                # 跳过空格
                if line[col] in ' \t':
                    col += 1
                    continue

                # 匹配token
                matched = False
                for token_name, pattern in self.compiled_patterns:
                    match = pattern.match(line, col)
                    if match:
                        value = match.group(0)

                        # 跳过空白
                        if token_name == 'WHITESPACE':
                            col = match.end()
                            matched = True
                            break

                        # 跳过注释
                        if token_name == 'COMMENT':
                            col = len(line)
                            matched = True
                            break

                        # 处理关键字
                        if token_name == 'NAME' and value.upper() in self.KEYWORDS:
                            token_name = value.upper()

                        tokens.append(Token(token_name, value, line_num, col))
                        col = match.end()
                        matched = True
                        break

                if not matched:
                    raise SyntaxError(f"Unexpected character '{line[col]}' at line {line_num}, column {col}")

        # 行尾添加NEWLINE
        if tokens and tokens[-1].type != 'NEWLINE':
            tokens.append(Token('NEWLINE', '\\n', len(lines), 0))

        # 处理剩余的DEDENT
        while len(indent_stack) > 1:
            tokens.append(Token('DEDENT', '<DEDENT>', len(lines), 0))
            indent_stack.pop()

        # 添加EOF
        tokens.append(Token('EOF', '<EOF>', len(lines), 0))

        return tokens

    def _count_indent(self, line: str) -> int:
        """计算行首缩进（空格数）"""
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += 4  # tab = 4个空格
            else:
                break
        return indent


def preprocess_pseudocode(code: str) -> str:
    """预处理伪代码 - 规范化格式"""
    lines = code.split('\n')
    processed_lines = []

    for line in lines:
        # 保留缩进和内容
        stripped = line.rstrip()
        if stripped:
            processed_lines.append(stripped)

    return '\n'.join(processed_lines)
