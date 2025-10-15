# A-level Computer Science 伪代码完整语法规范

本文档详细描述了当前实现的Cambridge A-level Computer Science伪代码解释器的完整语法规则、类型系统和库函数规范。

## 目录

1. [词法规则](#词法规则)
2. [语法结构](#语法结构)
3. [类型系统](#类型系统)
4. [表达式和运算符](#表达式和运算符)
5. [控制结构](#控制结构)
6. [函数和过程](#函数和过程)
7. [文件操作](#文件操作)
8. [内置库函数](#内置库函数)
9. [缩进规则](#缩进规则)
10. [错误处理](#错误处理)

---

## 词法规则

### 关键字 (Keywords)

```
DECLARE, CONSTANT, TYPE, ENDTYPE
IF, THEN, ELSE, ENDIF
CASE, OF, OTHERWISE, ENDCASE
FOR, TO, STEP, NEXT
WHILE, ENDWHILE
REPEAT, UNTIL
PROCEDURE, ENDPROCEDURE, FUNCTION, ENDFUNCTION, RETURNS, RETURN
CALL, BYREF
INPUT, OUTPUT, PRINT
OPENFILE, READ, WRITE, APPEND, READFILE, WRITEFILE, CLOSEFILE
INTEGER, REAL, STRING, CHAR, BOOLEAN, DATE, ARRAY
TRUE, FALSE
AND, OR, NOT
```

### 标识符 (Identifiers)

- **格式**: `[a-zA-Z][a-zA-Z0-9_]*`
- **规则**: 以字母开头，可包含字母、数字和下划线
- **大小写**: 不敏感
- **示例**: `count`, `student_name`, `tempValue`

### 字面量 (Literals)

#### 数字字面量
```
整数: 123, -45, 0
实数: 3.14, -2.5, 0.0
```

#### 字符串字面量
```
格式: "双引号包围的文本"
示例: "Hello World", "Student Name", ""
```

#### 字符字面量
```
格式: '单引号包围的单个字符'
示例: 'A', 'b', '0', '?'
```

#### 布尔字面量
```
TRUE, FALSE
```

### 运算符和分隔符

#### 赋值运算符
```
<-  // 赋值符号
```

#### 算术运算符
```
+   // 加法
-   // 减法
*   // 乘法
/   // 除法
^   // 幂运算
```

#### 比较运算符
```
=   // 等于
<>  // 不等于
<   // 小于
>   // 大于
<=  // 小于等于
>=  // 大于等于
```

#### 逻辑运算符
```
AND // 逻辑与
OR  // 逻辑或
NOT // 逻辑非
```

#### 其他分隔符
```
:   // 类型声明
,   // 分隔符
;   // 语句分隔符(可选)
.   // 小数点/字段访问
..  // 范围运算符
[]  // 数组索引
()  // 函数调用/表达式分组
&   // 字符串连接
```

### 注释
```
// 单行注释，从双斜杠到行尾
```

---

## 语法结构

### 程序结构
```
程序由一系列语句组成，支持缩进表示代码块
```

### 变量声明
```
DECLARE <identifier> : <type>
DECLARE <identifier> : ARRAY[<lower>:<upper>] OF <type>
DECLARE <identifier> : ARRAY[<lower1>:<upper1>, <lower2>:<upper2>] OF <type>
```

**示例:**
```pseudo
DECLARE count : INTEGER
DECLARE name : STRING
DECLARE scores : ARRAY[1:10] OF INTEGER
DECLARE matrix : ARRAY[1:3, 1:3] OF REAL
```

### 常量声明
```
CONSTANT <identifier> : <type> = <value>
```

**示例:**
```pseudo
CONSTANT PI : REAL = 3.14159
CONSTANT MAX_SIZE : INTEGER = 100
```

### 自定义类型
```
TYPE <TypeName>
    <field1> : <type1>
    <field2> : <type2>
    ...
ENDTYPE
```

**示例:**
```pseudo
TYPE Student
    name : STRING
    age : INTEGER
    grade : REAL
ENDTYPE

DECLARE student1 : Student
```

### 赋值语句
```
<identifier> <- <expression>
```

**示例:**
```pseudo
x <- 10
name <- "John"
average <- (score1 + score2) / 2
```

---

## 类型系统

### 基本数据类型

#### INTEGER (整数类型)
- **范围**: 任意精度整数
- **字面量**: `123`, `-45`, `0`
- **运算**: `+`, `-`, `*`, `/`, `^`, `MOD`, `DIV`

#### REAL (实数类型)
- **范围**: IEEE 754 双精度浮点数
- **字面量**: `3.14`, `-2.5`, `0.0`
- **运算**: `+`, `-`, `*`, `/`, `^`

#### STRING (字符串类型)
- **长度**: 可变长度
- **字面量**: `"Hello"`, `""`
- **运算**: `&` (连接)
- **注意**: 长度为1的字符串可以与CHAR类型互换

#### CHAR (字符类型)
- **长度**: 固定长度1
- **字面量**: `'A'`, `'b'`, `'0'`
- **转换**: 可以赋值给STRING类型

#### BOOLEAN (布尔类型)
- **值**: `TRUE`, `FALSE`
- **运算**: `AND`, `OR`, `NOT`

#### DATE (日期类型)
- **格式**: DD/MM/YYYY (内部存储为datetime对象)
- **支持**: 日期比较、日期运算

### 复合数据类型

#### ARRAY (数组类型)
```
一维数组: ARRAY[<lower>:<upper>] OF <type>
二维数组: ARRAY[<lower1>:<upper1>, <lower2>:<upper2>] OF <type>
```

**特性:**
- 支持自定义下界
- 下界可以是任意整数
- 数组索引从下界开始

**示例:**
```pseudo
DECLARE numbers : ARRAY[5:10] OF INTEGER  // 6个元素，索引5,6,7,8,9,10
DECLARE matrix : ARRAY[0:2, 0:2] OF REAL  // 3x3矩阵
```

#### RECORD (记录类型)
通过TYPE定义的自定义复合类型

**示例:**
```pseudo
TYPE Person
    name : STRING
    age : INTEGER
    address : STRING
ENDTYPE

DECLARE p : Person
p.name <- "Alice"
p.age <- 25
```

---

## 表达式和运算符

### 算术表达式
```
<expr> + <expr>    // 加法
<expr> - <expr>    // 减法
<expr> * <expr>    // 乘法
<expr> / <expr>    // 除法
<expr> ^ <expr>    // 幂运算
- <expr>           // 负号
```

**优先级 (从高到低):**
1. `()` 括号
2. `^` 幂运算
3. `*`, `/` 乘除法
4. `+`, `-` 加减法

### 比较表达式
```
<expr> = <expr>     // 等于
<expr> <> <expr>    // 不等于
<expr> < <expr>     // 小于
<expr> > <expr>     // 大于
<expr> <= <expr>    // 小于等于
<expr> >= <expr>    // 大于等于
```

### 逻辑表达式
```
NOT <expr>          // 逻辑非
<expr> AND <expr>    // 逻辑与
<expr> OR <expr>     // 逻辑或
```

**优先级 (从高到低):**
1. `NOT`
2. `AND`
3. `OR`

### 字符串表达式
```
<string_expr> & <string_expr>  // 字符串连接
```

### 数组访问
```
<array_identifier>[<index>]                    // 一维数组
<array_identifier>[<index1>, <index2>]         // 二维数组
<record_identifier>.<field_name>               // 记录字段访问
```

---

## 控制结构

### 条件语句

#### IF语句
```pseudo
IF <condition> THEN
    <statements>
ELSE
    <statements>
ENDIF
```

#### CASE语句
```pseudo
CASE <expression> OF
    <value1> : <statements>
    <value2> : <statements>
    OTHERWISE : <statements>
ENDCASE
```

**支持范围匹配:**
```pseudo
CASE score OF
    90..100 : OUTPUT "A"
    80..89  : OUTPUT "B"
    OTHERWISE : OUTPUT "C"
ENDCASE
```

### 循环语句

#### FOR循环
```pseudo
FOR <counter> <- <start> TO <end> [STEP <step>]
    <statements>
NEXT <counter>
```

**特性:**
- STEP默认为1
- 支持负步长
- 包含边界值

#### WHILE循环
```pseudo
WHILE <condition>
    <statements>
ENDWHILE
```

**特性:**
- 前测试循环
- 条件为假时跳过循环体

#### REPEAT循环
```pseudo
REPEAT
    <statements>
UNTIL <condition>
```

**特性:**
- 后测试循环
- 至少执行一次循环体

---

## 函数和过程

### 过程定义
```pseudo
PROCEDURE <procedure_name>([<parameters>])
    [DECLARE <local_variables>]
    <statements>
ENDPROCEDURE
```

### 函数定义
```pseudo
FUNCTION <function_name>([<parameters>]) RETURNS <return_type>
    [DECLARE <local_variables>]
    <statements>
    RETURN <expression>
ENDFUNCTION
```

### 参数传递

#### 传值调用 (默认)
```pseudo
PROCEDURE Example(x : INTEGER)
    x <- x + 1  // 不影响实际参数
ENDPROCEDURE
```

#### 传引用调用 (BYREF)
```pseudo
PROCEDURE Example(BYREF x : INTEGER)
    x <- x + 1  // 影响实际参数
ENDPROCEDURE
```

### 函数/过程调用
```pseudo
CALL <procedure_name>([<arguments>])
<variable> <- <function_name>([<arguments>])
```

---

## 文件操作

### 文件打开
```pseudo
OPENFILE <filename> FOR <mode>
```

**模式:**
- `READ` - 读取模式
- `WRITE` - 写入模式
- `APPEND` - 追加模式

### 文件读取
```pseudo
READFILE <filename>, <variable>
```

### 文件写入
```pseudo
WRITEFILE <filename>, <expression>
```

### 文件关闭
```pseudo
CLOSEFILE <filename>
```

### 文件结束检测
```pseudo
EOF(<filename>)  // 返回BOOLEAN
```

**示例:**
```pseudo
OPENFILE "data.txt" FOR READ
WHILE NOT EOF("data.txt")
    READFILE "data.txt", line
    OUTPUT line
ENDWHILE
CLOSEFILE "data.txt"
```

---

## 内置库函数

### 字符串和字符函数

| 函数 | 语法 | 返回类型 | 描述 |
|------|------|----------|------|
| LEFT | `LEFT(string, count)` | STRING | 返回字符串左侧count个字符 |
| RIGHT | `RIGHT(string, count)` | STRING | 返回字符串右侧count个字符 |
| MID | `MID(string, start, length)` | STRING | 从位置start开始返回length个字符 |
| LENGTH | `LENGTH(string)` | INTEGER | 返回字符串长度 |
| TO_UPPER | `TO_UPPER(string)` | STRING | 转换为大写 |
| TO_LOWER | `TO_LOWER(string)` | STRING | 转换为小写 |
| NUM_TO_STR | `NUM_TO_STR(number)` | STRING | 数字转字符串 |
| STR_TO_NUM | `STR_TO_NUM(string)` | REAL/INTEGER | 字符串转数字 |
| IS_NUM | `IS_NUM(string)` | BOOLEAN | 检查字符串是否为有效数字 |
| ASC | `ASC(char)` | INTEGER | 返回字符的ASCII值 |
| CHR | `CHR(code)` | CHAR | 返回ASCII码对应的字符 |

### 数字函数

| 函数 | 语法 | 返回类型 | 描述 |
|------|------|----------|------|
| INT | `INT(real_number)` | INTEGER | 返回实数的整数部分 |
| RAND | `RAND(upper_bound)` | REAL | 返回0到upper_bound之间的随机数 |

### 日期函数

| 函数 | 语法 | 返回类型 | 描述 |
|------|------|----------|------|
| DAY | `DAY(date)` | INTEGER | 返回日期的天数 |
| MONTH | `MONTH(date)` | INTEGER | 返回日期的月份 |
| YEAR | `YEAR(date)` | INTEGER | 返回日期的年份 |
| DAYINDEX | `DAYINDEX(date)` | INTEGER | 返回星期索引(Sunday=1) |
| SETDATE | `SETDATE(day, month, year)` | DATE | 创建指定日期 |
| TODAY | `TODAY()` | DATE | 返回当前日期 |

### 文件函数

| 函数 | 语法 | 返回类型 | 描述 |
|------|------|----------|------|
| EOF | `EOF(filename)` | BOOLEAN | 检查文件是否到达末尾 |

---

## 缩进规则

### 基本规则
- 使用缩进表示代码块结构
- 缩进字符转换为INDENT/DEDENT token
- 支持制表符或空格缩进

### 语法结构
```pseudo
IF condition THEN          // IF语句开始
    statement1              // 缩进增加 - INDENT token
    statement2
ELSE                       // ELSE同级别
    statement3
    statement4
ENDIF                      // IF语句结束 - DEDENT token
```

### 支持缩进的语法
- IF-THEN-ELSE-ENDIF
- CASE-OF-OTHERWISE-ENDCASE
- FOR-TO-STEP-NEXT
- WHILE-ENDWHILE
- REPEAT-UNTIL
- PROCEDURE-ENDPROCEDURE
- FUNCTION-ENDFUNCTION
- TYPE-ENDTYPE

---

## 错误处理

### 词法错误
- 未识别的字符
- 不匹配的字符串字面量
- 无效的数字格式

### 语法错误
- 缺少必需的关键字
- 不匹配的括号或分隔符
- 无效的语句结构

### 运行时错误
- 类型不匹配
- 数组越界访问
- 除零错误
- 未定义变量或函数
- 文件操作错误

### 类型检查错误
- 赋值类型不匹配
- 函数参数类型错误
- 数组索引类型错误
- 返回值类型不匹配

---

## 示例程序

### 基本输入输出
```pseudo
// 计算平均值的程序
DECLARE score1, score2, score3 : INTEGER
DECLARE average : REAL

OUTPUT "请输入三个分数:"
INPUT score1
INPUT score2
INPUT score3

average <- (score1 + score2 + score3) / 3
OUTPUT "平均分: ", average
```

### 数组处理
```pseudo
// 查找数组中的最大值
DECLARE numbers : ARRAY[1:5] OF INTEGER
DECLARE max_value, i : INTEGER

numbers[1] <- 23
numbers[2] <- 56
numbers[3] <- 12
numbers[4] <- 89
numbers[5] <- 34

max_value <- numbers[1]
FOR i <- 2 TO 5
    IF numbers[i] > max_value THEN
        max_value <- numbers[i]
    ENDIF
NEXT i

OUTPUT "最大值: ", max_value
```

### 函数定义
```pseudo
// 阶乘函数
FUNCTION Factorial(n : INTEGER) RETURNS INTEGER
    DECLARE result : INTEGER
    IF n <= 1 THEN
        result <- 1
    ELSE
        result <- n * Factorial(n - 1)
    ENDIF
    RETURN result
ENDFUNCTION

DECLARE num, fact : INTEGER
num <- 5
fact <- Factorial(num)
OUTPUT num, "! = ", fact
```

---

## 版本信息

**当前版本**: v2.1.0
**最后更新**: 2025-10-15
**兼容性**: Cambridge A-level Computer Science (9618) 伪代码规范

本实现完全支持Cambridge International AS & A Level Computer Science (9618)考试大纲中规定的所有伪代码语法特性，包括变量声明、控制结构、数组、函数、文件操作和所有标准库函数。