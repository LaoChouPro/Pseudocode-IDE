#!/usr/bin/env python3
"""
A-level CS 伪代码解释器
主程序入口
"""
import sys
import argparse
from lexer import Lexer, preprocess_pseudocode
from parser import Parser
from interpreter import Interpreter


def run_file(filename: str, debug: bool = False, strict: bool = False):
    """运行伪代码文件"""
    try:
        # 读取文件
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()

        # 预处理
        code = preprocess_pseudocode(code)

        if debug:
            print("=== Preprocessed Code ===")
            print(code)
            print("=" * 50)

        # 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(code)

        if debug:
            print("=== Tokens ===")
            for token in tokens:
                print(token)
            print("=" * 50)

        # 语法分析
        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            print("=== AST ===")
            print(ast)
            print("=" * 50)

        # 解释执行
        interpreter = Interpreter(strict_mode=strict)
        interpreter.interpret(ast)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_repl():
    """运行交互式REPL"""
    print("A-level CS Pseudocode Interpreter")
    print("Type 'exit' or 'quit' to exit")
    print("Type 'help' for help")
    print("-" * 50)

    interpreter = Interpreter()
    lexer = Lexer()

    while True:
        try:
            # 读取输入
            print(">>> ", end="")
            line = input()

            if line.strip().lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if line.strip().lower() == 'help':
                print_help()
                continue

            if not line.strip():
                continue

            # 预处理
            code = preprocess_pseudocode(line)

            # 词法分析
            tokens = lexer.tokenize(code)

            # 语法分析
            parser = Parser(tokens)
            ast = parser.parse()

            # 解释执行
            for statement in ast.statements:
                interpreter.execute_statement(statement)

        except EOFError:
            print("\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Type 'exit' to quit.")
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
        except RuntimeError as e:
            print(f"Runtime Error: {e}")
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """打印帮助信息"""
    help_text = """
A-level CS Pseudocode Interpreter Help
======================================

Supported Features:
- Variables: DECLARE, CONSTANT
- Data Types: INTEGER, REAL, STRING, CHAR, BOOLEAN, DATE, ARRAY
- Custom Types: TYPE...ENDTYPE
- Control Flow: IF-THEN-ELSE, CASE-OF, FOR, WHILE, REPEAT-UNTIL
- Functions: PROCEDURE, FUNCTION, CALL, RETURN
- I/O: INPUT, OUTPUT, PRINT
- File Operations: OPEN, READFILE, WRITEFILE, CLOSEFILE
- Built-in Functions: ASC, CHR, INT, LENGTH, LEFT, RIGHT, MID, etc.

Examples:
    DECLARE x : INTEGER
    x <- 10
    OUTPUT x

    FOR i <- 1 TO 5
        OUTPUT i
    NEXT i

Commands:
    help  - Show this help
    exit  - Exit the interpreter
    quit  - Exit the interpreter
"""
    print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='A-level CS Pseudocode Interpreter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s program.pseudo          Run a pseudocode file
  %(prog)s --debug program.pseudo  Run with debug output
  %(prog)s                         Start interactive mode (REPL)
        """
    )

    parser.add_argument(
        'file',
        nargs='?',
        help='Pseudocode file to execute'
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output'
    )

    parser.add_argument(
        '-s', '--strict',
        action='store_true',
        help='Enable strict mode (require variable declarations)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='A-level CS Pseudocode Interpreter v1.1.3'
    )

    args = parser.parse_args()

    if args.file:
        # 运行文件
        run_file(args.file, args.debug, args.strict)
    else:
        # 交互模式
        run_repl()


if __name__ == '__main__':
    main()
