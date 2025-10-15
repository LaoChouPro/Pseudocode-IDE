# 快速入门指南

## 5分钟上手A-level伪代码解释器

### 第一步：运行你的第一个程序

创建文件 `hello.pseudo`：

```pseudocode
OUTPUT "Hello, World!"
```

运行：

```bash
python3 main.py hello.pseudo
```

输出：
```
Hello, World!
```

### 第二步：使用变量

创建文件 `variables.pseudo`：

```pseudocode
DECLARE name : STRING
DECLARE age : INTEGER

name <- "Alice"
age <- 15

OUTPUT "Name:", name
OUTPUT "Age:", age
```

### 第三步：使用循环

创建文件 `loop.pseudo`：

```pseudocode
FOR i <- 1 TO 10
    OUTPUT "Number", i
NEXT i
```

### 第四步：使用数组

创建文件 `array.pseudo`：

```pseudocode
DECLARE scores : ARRAY[1:3] OF INTEGER
DECLARE total : INTEGER
DECLARE average : REAL

scores[1] <- 85
scores[2] <- 90
scores[3] <- 78

total <- scores[1] + scores[2] + scores[3]
average <- total / 3

OUTPUT "Total:", total
OUTPUT "Average:", average
```

### 第五步：使用函数（内置）

创建文件 `functions.pseudo`：

```pseudocode
DECLARE text : STRING
text <- "Hello"

OUTPUT "Length:", LENGTH(text)
OUTPUT "Upper:", UCASE(text)
OUTPUT "First 3:", LEFT(text, 3)
```

### 第六步：条件判断

创建文件 `condition.pseudo`：

```pseudocode
DECLARE score : INTEGER
score <- 85

IF score >= 90
THEN
    OUTPUT "Grade: A"
ELSE
    IF score >= 80
    THEN
        OUTPUT "Grade: B"
    ELSE
        OUTPUT "Grade: C"
    ENDIF
ENDIF
```

## 交互模式

直接输入 `python3 main.py` 进入交互模式，可以逐行输入代码测试：

```bash
python3 main.py
>>> DECLARE x : INTEGER
>>> x <- 42
>>> OUTPUT x
42
>>> exit
```

## 常见错误

### 错误1：忘记缩进

❌ 错误：
```pseudocode
IF x > 0
THEN
OUTPUT "Positive"
ENDIF
```

✅ 正确：
```pseudocode
IF x > 0
THEN
    OUTPUT "Positive"
ENDIF
```

### 错误2：使用等号赋值

❌ 错误：
```pseudocode
x = 10
```

✅ 正确：
```pseudocode
x <- 10
```

### 错误3：关键字小写

❌ 错误：
```pseudocode
declare x : integer
```

✅ 正确：
```pseudocode
DECLARE x : INTEGER
```

## 调试技巧

使用 `--debug` 标志查看详细信息：

```bash
python3 main.py --debug your_program.pseudo
```

这会显示：
- 预处理后的代码
- Token流
- AST结构

## 下一步

- 查看 `tests/` 目录中的更多示例
- 阅读 `README.md` 了解完整功能
- 运行 `./run_tests.sh` 查看所有测试

## 需要帮助？

在交互模式下输入 `help` 查看帮助信息。
