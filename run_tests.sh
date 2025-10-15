#!/bin/bash
# 运行所有测试

echo "======================================"
echo "A-level CS 伪代码解释器 - 测试套件"
echo "======================================"
echo

# 测试1：基本变量
echo "测试1: 基本变量和赋值"
echo "--------------------------------------"
python3 main.py tests/test_basic.pseudo
echo

# 测试2：算术运算
echo "测试2: 算术运算"
echo "--------------------------------------"
python3 main.py tests/test_arithmetic.pseudo
echo

# 测试3：IF语句
echo "测试3: IF条件语句"
echo "--------------------------------------"
python3 main.py tests/test_if_fixed.pseudo
echo

# 测试4：循环
echo "测试4: 循环结构"
echo "--------------------------------------"
python3 main.py tests/test_loops2.pseudo
echo

# 测试5：数组
echo "测试5: 数组操作"
echo "--------------------------------------"
python3 main.py tests/test_array.pseudo
echo

# 测试6：内置函数
echo "测试6: 内置函数"
echo "--------------------------------------"
python3 main.py tests/test_builtins.pseudo
echo

# 测试7：综合测试
echo "测试7: 综合测试（平均值计算）"
echo "--------------------------------------"
python3 main.py tests/test_comprehensive.pseudo
echo

echo "======================================"
echo "测试完成！"
echo "======================================"
