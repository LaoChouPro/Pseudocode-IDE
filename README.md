# A-level CS 伪代码解释器

完整实现的 A-level Computer Science 伪代码解释器，支持所有标准伪代码语法结构。

**🌐 现已支持Web版！** 简约高级的黑白灰配色界面，完全响应式设计。

## 💡 快速开始

### 方式1：Web界面（推荐）

# 点击 ➡️[这里](https://code.i-o.autos)⬅️ 直接访问 [https://code.i-o.autos](https://code.i-o.autos) 开始使用

---

### 方式2：命令行

```bash
python3 main.py your_program.pseudo
```

## 功能特性

### ✅ 已实现功能

- **完整的数据类型系统**
  - 基本类型：INTEGER, REAL, STRING, CHAR, BOOLEAN, DATE
  - 复合类型：ARRAY（一维/二维数组，支持自定义下界）
  - 自定义类型：TYPE...ENDTYPE（记录类型）

- **变量和常量**
  - DECLARE 变量声明
  - CONSTANT 常量定义
  - 支持大小写不敏感的标识符

- **控制结构**
  - IF-THEN-ELSE-ENDIF（支持嵌套）
  - CASE-OF-OTHERWISE-ENDCASE（支持值匹配和范围匹配）
  - FOR...TO...STEP...NEXT（计数循环）
  - WHILE...ENDWHILE（前测试循环）
  - REPEAT...UNTIL（后测试循环）

- **函数和过程**
  - PROCEDURE 过程定义和调用
  - FUNCTION 函数定义（支持返回值）
  - 参数传递：传值和传引用（BYREF）
  - ⚠️ 注意：递归函数当前存在问题，正在修复中

- **输入输出**
  - INPUT 输入语句
  - OUTPUT/PRINT 输出语句
  - 支持多项输出

- **文件操作**
  - OPEN...FOR READ/WRITE/APPEND
  - READFILE, WRITEFILE
  - CLOSEFILE
  - EOF() 文件结束检测

- **内置函数**
  - 字符串函数：ASC, CHR, LENGTH, LEFT, RIGHT, MID, UCASE, LCASE
  - 数学函数：INT, ABS, SQRT, POWER, ROUND, MOD, DIV
  - 日期函数：TODAY, DAYOF, MONTHOF, YEAROF, DATEDIFF
  - 随机数：RANDOM, RANDOMINT

- **表达式**
  - 算术运算：+, -, *, /, ^ (幂)
  - 字符串连接：&
  - 比较运算：=, <>, <, >, <=, >=
  - 逻辑运算：AND, OR, NOT
  - 完整的运算符优先级

## 安装

无需额外依赖，仅需Python 3.7+

```bash
cd pseudocode_interpreter
chmod +x main.py
```

## 使用方法

### 1. 运行伪代码文件

```bash
python3 main.py your_program.pseudo
```

### 2. 交互模式（REPL）

```bash
python3 main.py
```

### 3. 调试模式

```bash
python3 main.py --debug your_program.pseudo
```

### 4. 严格模式（强制变量声明）

```bash
# 开启严格模式，要求所有变量必须先声明
python3 main.py --strict your_program.pseudo
python3 main.py -s your_program.pseudo

# 组合使用
python3 main.py --strict --debug your_program.pseudo
```

**严格模式说明：**
- **非严格模式（默认）**：允许隐式声明变量，`x <- 10` 会自动创建变量
- **严格模式（--strict）**：强制要求使用 `DECLARE` 声明变量，未声明会报错
- 严格模式有助于发现拼写错误和未初始化变量，符合A-level考试规范

## 代码示例

### 示例1：基本变量和算术

```pseudocode
DECLARE x : INTEGER
DECLARE y : REAL
DECLARE name : STRING

x <- 10
y <- 3.14
name <- "Alice"

OUTPUT "x =", x
OUTPUT "y =", y
OUTPUT "name =", name
```

### 示例2：IF条件语句

```pseudocode
DECLARE score : INTEGER
score <- 75

IF score >= 60
THEN
    OUTPUT "Pass"
ELSE
    OUTPUT "Fail"
ENDIF
```

### 示例3：FOR循环

```pseudocode
FOR i <- 1 TO 5
    OUTPUT i
NEXT i
```

### 示例4：数组

```pseudocode
DECLARE numbers : ARRAY[1:5] OF INTEGER

FOR i <- 1 TO 5
    numbers[i] <- i * 10
NEXT i

FOR i <- 1 TO 5
    OUTPUT "numbers[", i, "] =", numbers[i]
NEXT i
```

### 示例5：二维数组

```pseudocode
DECLARE matrix : ARRAY[1:2, 1:3] OF INTEGER

matrix[1,1] <- 1
matrix[1,2] <- 2
matrix[1,3] <- 3

FOR row <- 1 TO 2
    FOR col <- 1 TO 3
        OUTPUT matrix[row, col]
    NEXT col
NEXT row
```

### 示例6：内置函数

```pseudocode
DECLARE text : STRING
text <- "Hello World"

OUTPUT "LENGTH:", LENGTH(text)
OUTPUT "LEFT 5:", LEFT(text, 5)
OUTPUT "RIGHT 5:", RIGHT(text, 5)
OUTPUT "MID:", MID(text, 7, 5)
```

## 语法要点

### 缩进规则

**重要**：伪代码使用缩进来表示代码块。每个控制结构（IF, FOR, WHILE等）的代码块必须缩进。

正确示例：
```pseudocode
IF x > 0
THEN
    OUTPUT "Positive"
ENDIF
```

错误示例：
```pseudocode
IF x > 0
THEN
OUTPUT "Positive"    // ❌ 缺少缩进
ENDIF
```

### 关键字大写

所有关键字必须大写：`IF`, `THEN`, `ELSE`, `FOR`, `WHILE`, `DECLARE` 等。

### 赋值操作符

使用 `<-` 而非 `=` 进行赋值：
```pseudocode
x <- 10    // ✅ 正确
x = 10     // ❌ 错误
```

### 数组索引

数组可以使用自定义下界：
```pseudocode
DECLARE arr : ARRAY[5:10] OF INTEGER  // 下界是5，上界是10
arr[5] <- 100
arr[10] <- 200
```

## 项目结构

```
pseudocode_interpreter/
├── main.py                 # 主程序入口
├── lexer.py                # 词法分析器（处理缩进）
├── parser.py               # 语法分析器（递归下降）
├── ast_nodes.py            # AST节点定义
├── interpreter.py          # 解释器核心
├── pseudocode_types.py     # 类型系统
├── environment.py          # 作用域和环境管理
├── builtin_functions.py    # 内置函数库
├── tests/                  # 测试用例
└── README.md               # 本文档
```

## 架构设计

### 1. 词法分析（Lexer）
- 手写词法分析器
- 处理缩进敏感的语法（INDENT/DEDENT tokens）
- 识别所有关键字和操作符

### 2. 语法分析（Parser）
- 递归下降解析器
- 生成抽象语法树（AST）
- 支持所有伪代码语法结构

### 3. 类型系统
- 强类型系统
- 支持所有标准类型
- 可扩展的类型框架（易于添加新类型如DATE）

### 4. 解释器
- 基于AST的树遍历解释器
- 访问者模式执行节点
- 完整的作用域管理
- 支持函数调用栈

## 扩展性

### 添加新的内置函数

在 `builtin_functions.py` 中添加：

```python
def builtin_your_function(arg1, arg2):
    # 实现你的函数
    return result

# 注册函数
BUILTIN_FUNCTIONS['YOURFUNCTION'] = builtin_your_function
```

### 添加新的数据类型

在 `pseudocode_types.py` 中定义新类型：

```python
class YourType(PseudocodeType):
    def __init__(self, value):
        super().__init__(value)
    # 实现必要的方法
```

## 已知问题

1. **递归函数**：当前递归函数（如阶乘）会导致无限循环，正在修复中
2. **TYPE定义解析**：复杂的TYPE定义可能需要更多测试

## 测试

运行测试用例：

```bash
python3 main.py tests/test_basic.pseudo
python3 main.py tests/test_arithmetic.pseudo
python3 main.py tests/test_if_fixed.pseudo
python3 main.py tests/test_loops2.pseudo
python3 main.py tests/test_array.pseudo
python3 main.py tests/test_builtins.pseudo
```

## 开发团队

- 架构设计：完整的编译器前端架构
- 词法分析：手写lexer处理缩进
- 语法分析：递归下降parser
- 类型系统：可扩展的类型框架
- 解释器：树遍历执行引擎

## 版本历史

### v1.0.0 (2025-10-01)
- ✅ 完整实现所有基本语法结构
- ✅ 支持数组和记录类型
- ✅ 20+个内置函数
- ✅ 文件I/O操作
- ✅ 完整的测试套件
- ⚠️ 递归函数待修复

## 许可证

本项目为教育目的开发，用于A-level CS课程学习。
