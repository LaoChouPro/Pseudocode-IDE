// A-level CS 伪代码解释器 - 前端交互脚本

// ============================
// 全局状态
// ============================

const state = {
    currentTab: 'editor',
    isRunning: false,
    inputCallback: null
};

// ============================
// 示例代码
// ============================

const examples = {
    hello: `OUTPUT "Hello, World!"
DECLARE name : STRING
name <- "Alice"
OUTPUT "Hello,", name`,

    loop: `OUTPUT "Counting from 1 to 10:"
FOR i <- 1 TO 10
    OUTPUT i
NEXT i`,

    array: `DECLARE numbers : ARRAY[1:5] OF INTEGER
FOR i <- 1 TO 5
    numbers[i] <- i * 10
NEXT i

OUTPUT "Array contents:"
FOR i <- 1 TO 5
    OUTPUT "numbers[", i, "] =", numbers[i]
NEXT i`,

    function: `DECLARE text : STRING
text <- "Hello World"

OUTPUT "String functions:"
OUTPUT "LENGTH:", LENGTH(text)
OUTPUT "LEFT 5:", LEFT(text, 5)
OUTPUT "RIGHT 5:", RIGHT(text, 5)
OUTPUT "MID:", MID(text, 7, 5)`,

    condition: `DECLARE score : INTEGER
score <- 85

IF score >= 90
THEN
    OUTPUT "Grade: A"
ELSE
    IF score >= 80
    THEN
        OUTPUT "Grade: B"
    ELSE
        IF score >= 70
        THEN
            OUTPUT "Grade: C"
        ELSE
            OUTPUT "Grade: F"
        ENDIF
    ENDIF
ENDIF`,

    average: `DECLARE numbers : ARRAY[1:5] OF INTEGER
DECLARE total : INTEGER
DECLARE average : REAL

numbers[1] <- 10
numbers[2] <- 20
numbers[3] <- 30
numbers[4] <- 40
numbers[5] <- 50

total <- 0
FOR i <- 1 TO 5
    total <- total + numbers[i]
NEXT i

average <- total / 5

OUTPUT "Total:", total
OUTPUT "Average:", average`
};

// ============================
// DOM元素
// ============================

const elements = {
    // 标签页
    navBtns: document.querySelectorAll('.nav-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // 编辑器
    codeEditor: document.getElementById('code-editor'),
    lineNumbers: document.getElementById('line-numbers'),
    syntaxHighlight: document.getElementById('syntax-highlight'),
    outputArea: document.getElementById('output-area'),
    statusBar: document.getElementById('status-bar'),

    // 按钮
    runBtn: document.getElementById('run-btn'),
    debugBtn: document.getElementById('debug-btn'),
    clearBtn: document.getElementById('clear-btn'),
    clearOutputBtn: document.getElementById('clear-output-btn'),
    loadExampleBtn: document.getElementById('load-example-btn'),

    // 复选框
    strictModeCheckbox: document.getElementById('strict-mode-checkbox'),

    // 示例卡片
    exampleCards: document.querySelectorAll('.example-card'),

    // 模态框
    inputModal: document.getElementById('input-modal'),
    inputField: document.getElementById('input-field'),
    inputSubmit: document.getElementById('input-submit'),
    inputCancel: document.getElementById('input-cancel')
};

// ============================
// 标签页切换
// ============================

elements.navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // 更新按钮状态
    elements.navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // 更新标签页内容
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    state.currentTab = tabName;
}

// ============================
// 代码编辑器
// ============================

// 伪代码关键字
const KEYWORDS = [
    'DECLARE', 'CONSTANT', 'TYPE', 'ENDTYPE',
    'IF', 'THEN', 'ELSE', 'ENDIF', 'ELSEIF',
    'CASE', 'OF', 'ENDCASE', 'OTHERWISE',
    'FOR', 'TO', 'NEXT', 'STEP',
    'WHILE', 'ENDWHILE',
    'REPEAT', 'UNTIL',
    'PROCEDURE', 'ENDPROCEDURE', 'CALL',
    'FUNCTION', 'RETURNS', 'ENDFUNCTION', 'RETURN',
    'INPUT', 'OUTPUT', 'PRINT',
    'OPENFILE', 'READFILE', 'WRITEFILE', 'CLOSEFILE',
    'BYREF', 'BYVAL', 'AND', 'OR', 'NOT', 'TRUE', 'FALSE'
];

const TYPES = [
    'INTEGER', 'REAL', 'STRING', 'CHAR', 'BOOLEAN', 'DATE', 'ARRAY', 'RECORD'
];

const BUILTIN_FUNCTIONS = [
    'ASC', 'CHR', 'INT', 'RAND', 'LENGTH', 'LEFT', 'RIGHT', 'MID',
    'LCASE', 'UCASE', 'TODAY', 'NOW', 'DAYOF', 'MONTHOF', 'YEARSOF',
    'SETDATE', 'DAYINDEX', 'ABS', 'SQRT', 'MOD', 'DIV', 'EOF'
];

// 语法高亮函数
function highlightSyntax(code) {
    // 转义HTML
    code = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // 高亮注释 (// 开头的行)
    code = code.replace(/(\/\/.*$)/gm, '<span class="syntax-comment">$1</span>');

    // 高亮字符串
    code = code.replace(/"([^"\\]|\\.)*"/g, '<span class="syntax-string">$&</span>');

    // 高亮数字
    code = code.replace(/\b(\d+\.?\d*)\b/g, '<span class="syntax-number">$1</span>');

    // 高亮关键字
    const keywordPattern = new RegExp('\\b(' + KEYWORDS.join('|') + ')\\b', 'g');
    code = code.replace(keywordPattern, '<span class="syntax-keyword">$1</span>');

    // 高亮类型
    const typePattern = new RegExp('\\b(' + TYPES.join('|') + ')\\b', 'g');
    code = code.replace(typePattern, '<span class="syntax-type">$1</span>');

    // 高亮内置函数
    const builtinPattern = new RegExp('\\b(' + BUILTIN_FUNCTIONS.join('|') + ')\\b', 'g');
    code = code.replace(builtinPattern, '<span class="syntax-type">$1</span>');

    // 高亮操作符
    code = code.replace(/(<-|&lt;-)/g, '<span class="syntax-operator">$1</span>');

    return code;
}

// 更新行号和语法高亮
function updateLineNumbers() {
    const code = elements.codeEditor.value;
    const lines = code.split('\n').length;
    let lineNumbersHTML = '';

    for (let i = 1; i <= lines; i++) {
        lineNumbersHTML += `<div>${i}</div>`;
    }

    elements.lineNumbers.innerHTML = lineNumbersHTML;

    // 更新语法高亮
    elements.syntaxHighlight.innerHTML = highlightSyntax(code);
}

// 同步滚动
elements.codeEditor.addEventListener('scroll', () => {
    elements.lineNumbers.scrollTop = elements.codeEditor.scrollTop;
    elements.syntaxHighlight.scrollTop = elements.codeEditor.scrollTop;
});

// 监听输入更新行号和高亮
elements.codeEditor.addEventListener('input', updateLineNumbers);

// 初始化行号和高亮
updateLineNumbers();

// Tab键支持
elements.codeEditor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = e.target.selectionStart;
        const end = e.target.selectionEnd;
        const value = e.target.value;

        e.target.value = value.substring(0, start) + '    ' + value.substring(end);
        e.target.selectionStart = e.target.selectionEnd = start + 4;
    }
});

// 清空编辑器
elements.clearBtn.addEventListener('click', () => {
    if (confirm('确定要清空代码吗？')) {
        elements.codeEditor.value = '';
        updateLineNumbers();
    }
});

// 加载示例
elements.loadExampleBtn.addEventListener('click', () => {
    elements.codeEditor.value = examples.hello;
    updateLineNumbers();
});

// ============================
// 示例卡片
// ============================

elements.exampleCards.forEach(card => {
    card.addEventListener('click', () => {
        const exampleName = card.dataset.example;
        if (examples[exampleName]) {
            elements.codeEditor.value = examples[exampleName];
            updateLineNumbers();
            switchTab('editor');
        }
    });
});

// ============================
// 运行代码
// ============================

elements.runBtn.addEventListener('click', async () => {
    const code = elements.codeEditor.value.trim();

    if (!code) {
        showOutput('错误：代码为空', 'error');
        return;
    }

    if (state.isRunning) {
        showOutput('错误：代码正在运行中...', 'error');
        return;
    }

    await runCode(code, false);
});

elements.debugBtn.addEventListener('click', async () => {
    const code = elements.codeEditor.value.trim();

    if (!code) {
        showOutput('错误：代码为空', 'error');
        return;
    }

    if (state.isRunning) {
        showOutput('错误：代码正在运行中...', 'error');
        return;
    }

    await runCode(code, true);
});

async function runCode(code, debug) {
    state.isRunning = true;
    clearOutput();
    updateStatus('运行中...', 'running');

    const startTime = performance.now();
    const strictMode = elements.strictModeCheckbox.checked;

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                debug: debug,
                strict: strictMode
            })
        });

        const result = await response.json();
        const endTime = performance.now();
        const executionTime = ((endTime - startTime) / 1000).toFixed(3);

        if (result.success) {
            if (result.output) {
                showOutput(result.output, 'success');
            }
            if (debug && result.debug_info) {
                showOutput('\n=== 调试信息 ===', 'info');
                showOutput(result.debug_info, 'info');
            }
            updateStatus(`完成 (${executionTime}s)`, 'success');
        } else {
            showOutput(result.error || '执行错误', 'error');
            updateStatus('错误', 'error');
        }

    } catch (error) {
        showOutput(`网络错误: ${error.message}`, 'error');
        updateStatus('错误', 'error');
    } finally {
        state.isRunning = false;
    }
}

// ============================
// 输出显示
// ============================

function showOutput(text, type = 'normal') {
    const placeholder = elements.outputArea.querySelector('.output-placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const line = document.createElement('div');
    line.className = `output-line ${type === 'error' ? 'output-error' : type === 'success' ? 'output-success' : ''}`;
    line.textContent = text;

    elements.outputArea.appendChild(line);
    elements.outputArea.scrollTop = elements.outputArea.scrollHeight;
}

function clearOutput() {
    elements.outputArea.innerHTML = '<div class="output-placeholder">运行代码后，输出将显示在这里...</div>';
}

elements.clearOutputBtn.addEventListener('click', clearOutput);

// ============================
// 状态栏
// ============================

function updateStatus(text, type = 'normal') {
    const statusText = elements.statusBar.querySelector('.status-text');
    statusText.textContent = text;
    statusText.className = `status-text ${type}`;
}

// ============================
// 输入模态框
// ============================

function showInputModal(prompt) {
    return new Promise((resolve, reject) => {
        const modal = elements.inputModal;
        const promptText = document.getElementById('input-prompt');

        promptText.textContent = prompt || '请输入值：';
        elements.inputField.value = '';
        modal.classList.add('active');
        elements.inputField.focus();

        state.inputCallback = { resolve, reject };
    });
}

function hideInputModal() {
    elements.inputModal.classList.remove('active');
    state.inputCallback = null;
}

elements.inputSubmit.addEventListener('click', () => {
    if (state.inputCallback) {
        const value = elements.inputField.value;
        state.inputCallback.resolve(value);
        hideInputModal();
    }
});

elements.inputCancel.addEventListener('click', () => {
    if (state.inputCallback) {
        state.inputCallback.reject(new Error('Input cancelled'));
        hideInputModal();
    }
});

elements.inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        elements.inputSubmit.click();
    } else if (e.key === 'Escape') {
        elements.inputCancel.click();
    }
});

// 点击模态框外部关闭
elements.inputModal.addEventListener('click', (e) => {
    if (e.target === elements.inputModal) {
        elements.inputCancel.click();
    }
});

// ============================
// 关于链接
// ============================

const aboutLink = document.getElementById('about-link');
if (aboutLink) {
    aboutLink.addEventListener('click', (e) => {
        e.preventDefault();
        alert('A-level CS 伪代码解释器 v1.0.0\n\n一个完整实现的伪代码解释器，支持所有A-level计算机科学伪代码语法。\n\n特性：\n- 完整的数据类型系统\n- 所有控制结构\n- 数组和自定义类型\n- 20+内置函数\n- 文件I/O操作');
    });
}

// ============================
// 初始化
// ============================

console.log('A-level CS 伪代码解释器已加载');
updateLineNumbers();
updateStatus('就绪');
