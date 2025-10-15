# 版本历史

## v2.1.0 (2025-10-15)

### ✅ 库函数完整集成

根据`库函数总结.md`文档，完整集成了所有Cambridge A-level CS伪代码规范的标准库函数：

#### 字符串和字符函数 (String and character functions)
- **LEFT, RIGHT, MID**: 字符串切片函数 ✅
- **LENGTH**: 字符串长度函数 ✅
- **TO_UPPER, TO_LOWER**: 大小写转换函数 ✅
- **NUM_TO_STR, STR_TO_NUM**: 数字与字符串转换函数 ✅
- **IS_NUM**: 数字字符串验证函数 ✅
- **ASC, CHR**: ASCII码转换函数 ✅

#### 数字函数 (Numeric functions)
- **INT**: 实数取整函数 ✅
- **RAND**: 随机数生成函数 ✅

#### 日期函数 (Date functions)
- **DAY, MONTH, YEAR**: 日期分量提取函数 ✅
- **DAYINDEX**: 星期索引函数(Sunday=1, Monday=2等) ✅
- **SETDATE**: 日期创建函数 ✅
- **TODAY**: 当前日期函数 ✅

#### 文本文件函数 (Text file functions)
- **EOF**: 文件结束检测函数 ✅

#### 兼容性保证
- 保留所有旧函数名作为兼容性别名(UCASE, LCASE, DAYOF, MONTHOF, YEAROF等)
- 现有代码无需修改即可继续工作
- 新函数名严格遵循文档规范

#### 测试覆盖
- 创建了完整的测试套件验证所有函数功能
- 通过所有现有测试确保向后兼容性
- 验证函数参数类型和返回值准确性

#### 代码改进
- 修复了SETDATE函数的日期构造问题
- 为DateType添加了weekday方法支持
- 优化了CHAR类型的类型检查机制

## v1.1.6 (2025-10-01)

### ✅ 规范符合性测试

#### 测试报告
对照补充的A-level伪代码语法规范进行了全面测试，测试结果如下：

**✅ 已支持的特性：**
- 常量声明（使用 `CONSTANT x <- value`，严格要求使用 `<-`）
- 变量赋值（严格要求使用 `<-`，不接受 `=`）
- 字符串连接运算符 `&`
- CASE OF 多分支选择（包括 OTHERWISE）
- FOR循环 with STEP
- 所有基本数据类型（INTEGER, REAL, STRING, CHAR, BOOLEAN, DATE）
- 数组（一维和二维）
- 记录类型（TYPE...ENDTYPE）
- 过程和函数（PROCEDURE/FUNCTION，支持BYVAL/BYREF）

**❌ 未支持的特性（已记录）：**
- TRY...EXCEPT...ENDTRY 异常处理
- OPENFILE/READFILE/WRITEFILE/CLOSEFILE（当前使用OPEN/READ/WRITE/CLOSE）

**⚠️ 语法规则强制：**
- 常量声明、变量赋值**只能使用** `<-`，不接受 `=`
- 正确示例：`CONSTANT pi <- 3.142` ✅，`x <- 10` ✅
- 错误示例：`CONSTANT pi = 3.142` ❌，`x = 10` ❌

---

## v1.1.5 (2025-10-01)

### 🐛 修复字符串函数边界检查

#### 问题描述
LEFT、RIGHT、MID三个字符串函数缺少边界检查，导致以下问题：
- `RIGHT("SHIT", 6)` 应该报错但返回了 "SHIT"
- `LEFT("ABC", 10)` 应该报错但返回了 "ABC"
- `MID("TEST", 10, 5)` 应该报错但静默失败

#### 修复内容

**RIGHT函数：**
- ✅ 检查count是否为负数
- ✅ 检查count是否超过字符串长度
- ✅ 错误信息：`RIGHT: Requested 6 characters but string only has 4 characters`

**LEFT函数：**
- ✅ 检查count是否为负数
- ✅ 检查count是否超过字符串长度
- ✅ 错误信息：`LEFT: Requested 10 characters but string only has 3 characters`

**MID函数：**
- ✅ 检查start position是否 < 1
- ✅ 检查length是否为负数
- ✅ 检查start是否超过字符串长度
- ✅ 检查substring是否超出字符串末尾

#### 测试结果
```pseudocode
// 现在会正确报错
OUTPUT RIGHT("SHIT", 6)     // ❌ ValueError
OUTPUT LEFT("ABC", 10)       // ❌ ValueError
OUTPUT MID("TEST", 10, 5)    // ❌ ValueError

// 正常情况仍然工作
OUTPUT RIGHT("Hello", 5)     // ✅ "Hello"
OUTPUT LEFT("World", 3)      // ✅ "Wor"
OUTPUT MID("Hello", 2, 3)    // ✅ "ell"
```

---

## v1.1.4 (2025-10-01)

### 🎨 Web编辑器增强

#### 新增功能
- ✅ **行号显示** - 左侧灰色区域显示代码行号，随编辑自动更新
- ✅ **语法高亮** - 实时高亮伪代码关键字、类型、字符串、数字、注释
- ✅ **滚动同步** - 行号与代码编辑器滚动完美同步

#### 语法高亮配色
- **关键字** (粉红色): DECLARE, IF, FOR, WHILE, OUTPUT等
- **类型** (青色): INTEGER, REAL, STRING, BOOLEAN等
- **字符串** (黄色): 双引号包围的文本
- **数字** (紫色): 整数和小数
- **注释** (灰色): // 开头的注释行
- **操作符** (粉红色): <- 赋值符号

#### 技术实现
- 使用双层结构：语法高亮层 + 透明textarea
- 实时更新，输入时即时高亮
- 完全响应式设计，适配各种屏幕

---

## v1.1.3 (2025-10-01)

### ✨ 新增严格模式（Strict Mode）

#### 功能说明
添加了"强制变量声明"开关，提供两种运行模式：

**非严格模式（默认）**
- 允许隐式声明变量
- 变量可以在未声明的情况下直接使用
- 适合快速原型开发和教学演示

**严格模式（--strict）**
- 强制要求使用 DECLARE 声明变量
- 未声明的变量会抛出错误
- 帮助发现拼写错误和未初始化变量
- 符合A-level考试规范

#### 使用方法

**命令行：**
```bash
# 非严格模式（默认）
python3 main.py program.pseudo

# 严格模式
python3 main.py --strict program.pseudo
python3 main.py -s program.pseudo
```

**Web API：**
```json
{
  "code": "x <- 10\nOUTPUT x",
  "strict": true
}
```

#### 示例

```pseudocode
// 非严格模式下可以运行
x <- 10
OUTPUT x

// 严格模式下会报错：
// Runtime Error: Variable 'x' used before declaration.
// Use DECLARE to declare variables first.

// 严格模式下需要先声明
DECLARE x : INTEGER
x <- 10
OUTPUT x
```

---

## v1.1.2 (2025-10-01)

### 🐛 修复类型检查漏洞
- **FOR循环类型检查** - 起始值、结束值、步长必须是INTEGER类型，不再静默转换REAL类型
- **WHILE循环类型检查** - 条件必须是BOOLEAN类型，不再接受INTEGER等其他类型
- **REPEAT-UNTIL类型检查** - 条件必须是BOOLEAN类型
- **数组索引类型检查** - 数组索引必须是INTEGER类型，不再静默转换

#### 修复的问题
- 之前 `FOR i <- 1 TO 10.01` 会静默转换为10并执行，现在会抛出类型错误
- 之前 `WHILE count DO` (count是INTEGER) 会被接受，现在会抛出类型错误
- 之前 `arr[2.5]` 会静默转换为索引2，现在会抛出类型错误

---

## v1.1.1 (2025-10-01)

### 🔧 配置更新
- 修改Web服务器端口从5000改为8080
- 更新相关文档中的端口信息

---

## v1.1.0 (2025-10-01)

### 🌐 Web版发布

#### 新增功能
- ✨ **Web界面** - 完整的浏览器端界面
- 🎨 **简约设计** - 黑白灰高级配色方案
- 📱 **响应式布局** - 支持桌面/平板/手机
- ⚡ **实时执行** - 在线编辑和运行代码
- 🔍 **调试模式** - 查看Token流和AST
- 📚 **内置文档** - 完整语法文档
- 💡 **示例代码** - 6个预置示例

#### Web技术栈
- Flask Web服务器
- 原生JavaScript (无框架)
- CSS3 Grid/Flexbox响应式布局
- REST API接口

#### 文件新增
- `web/index.html` - Web主页
- `web/style.css` - 样式表（600+行）
- `web/script.js` - 交互逻辑
- `web_server.py` - Flask后端
- `start_web.sh` - 启动脚本
- `WEB_README.md` - Web版文档

---

## v1.0.0 (2025-10-01)

### 🎉 命令行版首次发布

#### 核心功能
- ✅ 完整的词法分析器（支持缩进敏感语法）
- ✅ 递归下降语法分析器
- ✅ AST（抽象语法树）构建
- ✅ 基于树遍历的解释器

#### 数据类型
- ✅ INTEGER（整数）
- ✅ REAL（实数）
- ✅ STRING（字符串）
- ✅ CHAR（字符）
- ✅ BOOLEAN（布尔值）
- ✅ DATE（日期类型，可扩展）
- ✅ ARRAY（一维/二维数组，支持自定义下界）
- ✅ TYPE...ENDTYPE（自定义记录类型）

#### 控制结构
- ✅ IF-THEN-ELSE-ENDIF
- ✅ CASE-OF-OTHERWISE-ENDCASE（支持值匹配和范围匹配）
- ✅ FOR...TO...STEP...NEXT
- ✅ WHILE...DO...ENDWHILE
- ✅ REPEAT...UNTIL

#### 函数和过程
- ✅ PROCEDURE 定义和调用
- ✅ FUNCTION 定义（支持RETURN）
- ✅ 参数传递（传值和BYREF传引用）
- ⚠️ 递归函数存在问题（待修复）

#### 输入输出
- ✅ INPUT 输入语句
- ✅ OUTPUT/PRINT 输出语句
- ✅ 文件操作（OPEN, READFILE, WRITEFILE, CLOSEFILE, EOF）

#### 内置函数（21个）

**字符串函数：**
- ASC(), CHR()
- LENGTH(), LEFT(), RIGHT(), MID()
- UCASE(), LCASE()

**数学函数：**
- INT(), ABS(), SQRT()
- POWER(), ROUND()
- MOD(), DIV()

**日期函数：**
- TODAY(), DAYOF(), MONTHOF(), YEAROF()
- DATEDIFF()

**随机数函数：**
- RANDOM(), RANDOMINT()

#### 表达式和运算符
- ✅ 算术：+, -, *, /, ^
- ✅ 字符串连接：&
- ✅ 比较：=, <>, <, >, <=, >=
- ✅ 逻辑：AND, OR, NOT
- ✅ 完整的运算符优先级

#### 特性
- ✅ 大小写不敏感的标识符
- ✅ 作用域管理（全局/局部）
- ✅ 常量定义（CONSTANT）
- ✅ 变量声明（DECLARE）
- ✅ 注释支持（//）

#### 测试
- ✅ 基本变量和赋值测试
- ✅ 算术运算测试
- ✅ IF条件语句测试
- ✅ 循环结构测试
- ✅ 数组操作测试
- ✅ 内置函数测试
- ✅ 综合测试用例

#### 已知问题
- ⚠️ 递归函数会导致无限循环
- ⚠️ 复杂的嵌套FUNCTION定义可能有问题

#### 架构优势
- 🎯 模块化设计，易于维护
- 🎯 可扩展的类型系统
- 🎯 清晰的错误报告
- 🎯 支持调试模式
- 🎯 交互式REPL模式

#### 文件统计
- 源代码文件：9个
- 测试文件：7个
- 总代码行数：约2500行
- 文档：README.md, VERSIONS.md

---

## 未来计划

### v1.1.0（计划中）
- 🔧 修复递归函数问题
- 🔧 优化错误消息
- ✨ 添加更多内置函数
- ✨ 支持更多日期格式
- 📝 增加更多示例代码

### v1.2.0（计划中）
- ✨ 指针和链表支持
- ✨ 更复杂的数据结构（栈、队列）
- ✨ 性能优化
- 📊 添加性能分析工具

### v2.0.0（远期规划）
- 🚀 编译到字节码
- 🚀 JIT编译优化
- 🚀 图形化调试器
- 🚀 IDE插件
