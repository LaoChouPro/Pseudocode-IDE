// ==================================================
// A-level CS 伪代码解释器 - 新版前端脚本
// ==================================================

// ==================================================
// 全局状态管理
// ==================================================
const appState = {
    currentUser: null,
    currentFile: 'default',
    files: {
        'default': {
            name: 'untitled.pseudo',
            content: `DECLARE x : INTEGER
x <- 10
OUTPUT "Hello, World!"
OUTPUT "x =", x`
        }
    },
    uploadedFiles: [],
    isRunning: false,
    inputCallback: null,
    abortController: null // 用于中断代码执行
};

// ==================================================
// DOM元素引用
// ==================================================
const elements = {
    // 顶部栏
    runBtn: document.getElementById('run-btn'),
    stopBtn: document.getElementById('stop-btn'),
    docsBtn: document.getElementById('docs-btn'),
    userBtn: document.getElementById('user-btn'),
    userName: document.getElementById('user-name'),
    userDropdown: document.getElementById('user-dropdown'),
    
    // 用户下拉菜单项
    loginItem: document.getElementById('login-item'),
    registerItem: document.getElementById('register-item'),
    logoutItem: document.getElementById('logout-item'),
    
    // 侧边栏
    newFileBtn: document.getElementById('new-file-btn'),
    fileList: document.getElementById('file-list'),
    
    // 编辑器
    codeEditor: document.getElementById('code-editor'),
    lineNumbers: document.getElementById('line-numbers'),
    syntaxHighlight: document.getElementById('syntax-highlight'),
    
    // 输出区域
    outputTabs: document.querySelectorAll('.output-tab'),
    outputPanels: document.querySelectorAll('.output-panel'),
    outputArea: document.getElementById('output-area'),
    statusText: document.getElementById('status-text'),
    clearOutputBtn: document.getElementById('clear-output-btn'),
    strictModeCheckbox: document.getElementById('strict-mode-checkbox'),
    
    // 文件上传
    uploadFileBtn: document.getElementById('upload-file-btn'),
    fileInput: document.getElementById('file-input'),
    uploadedFiles: document.getElementById('uploaded-files'),
    
    // 模态框
    loginModal: document.getElementById('login-modal'),
    registerModal: document.getElementById('register-modal'),
    inputModal: document.getElementById('input-modal'),
    docsModal: document.getElementById('docs-modal'),
    
    // 登录表单
    loginForm: document.getElementById('login-form'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    loginError: document.getElementById('login-error'),
    loginClose: document.getElementById('login-close'),
    
    // 注册表单
    registerForm: document.getElementById('register-form'),
    registerUsername: document.getElementById('register-username'),
    registerPassword: document.getElementById('register-password'),
    registerPasswordConfirm: document.getElementById('register-password-confirm'),
    registerError: document.getElementById('register-error'),
    registerClose: document.getElementById('register-close'),
    
    // INPUT模态框
    inputPrompt: document.getElementById('input-prompt'),
    inputField: document.getElementById('input-field'),
    inputSubmit: document.getElementById('input-submit'),
    inputCancel: document.getElementById('input-cancel'),
    
    // 文档模态框
    docsClose: document.getElementById('docs-close')
};

// ==================================================
// 语法高亮配置
// ==================================================
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

// ==================================================
// 语法高亮函数
// ==================================================
function highlightSyntax(code) {
    // 先转义HTML特殊字符
    code = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // 使用临时标记来保护已处理的内容
    const tokens = [];
    let tokenIndex = 0;

    // 保存token的辅助函数
    function saveToken(html) {
        const placeholder = `___TOKEN_${tokenIndex}___`;
        tokens[tokenIndex] = html;
        tokenIndex++;
        return placeholder;
    }

    // 1. 注释（优先级最高，避免注释内容被处理）
    code = code.replace(/(\/\/.*$)/gm, (match) => {
        return saveToken('<span class="syntax-comment">' + match + '</span>');
    });

    // 2. 字符串
    code = code.replace(/"([^"\\]|\\.)*"/g, (match) => {
        return saveToken('<span class="syntax-string">' + match + '</span>');
    });
    code = code.replace(/'([^'\\]|\\.)*'/g, (match) => {
        return saveToken('<span class="syntax-string">' + match + '</span>');
    });

    // 3. 数字
    code = code.replace(/\b(\d+\.?\d*)\b/g, (match) => {
        return saveToken('<span class="syntax-number">' + match + '</span>');
    });

    // 4. 内置函数
    const funcPattern = new RegExp('\\b(' + BUILTIN_FUNCTIONS.join('|') + ')(?=\\()', 'g');
    code = code.replace(funcPattern, (match) => {
        return saveToken('<span class="syntax-function">' + match + '</span>');
    });

    // 5. 关键字
    const keywordPattern = new RegExp('\\b(' + KEYWORDS.join('|') + ')\\b', 'g');
    code = code.replace(keywordPattern, (match) => {
        return saveToken('<span class="syntax-keyword">' + match + '</span>');
    });

    // 6. 类型
    const typePattern = new RegExp('\\b(' + TYPES.join('|') + ')\\b', 'g');
    code = code.replace(typePattern, (match) => {
        return saveToken('<span class="syntax-type">' + match + '</span>');
    });

    // 7. 操作符
    code = code.replace(/&lt;-/g, (match) => {
        return saveToken('<span class="syntax-operator">' + match + '</span>');
    });

    // 恢复所有token
    for (let i = 0; i < tokenIndex; i++) {
        code = code.replace(`___TOKEN_${i}___`, tokens[i]);
    }

    return code;
}

// ==================================================
// 行号更新
// ==================================================
function updateLineNumbers() {
    const code = elements.codeEditor.value;
    const lines = code.split('\n');
    const lineCount = lines.length;
    
    let lineNumbersHtml = '';
    for (let i = 1; i <= lineCount; i++) {
        lineNumbersHtml += i + '\n';
    }
    
    elements.lineNumbers.textContent = lineNumbersHtml;
}

// ==================================================
// 编辑器同步滚动
// ==================================================
function syncScroll() {
    const scrollTop = elements.codeEditor.scrollTop;
    const scrollLeft = elements.codeEditor.scrollLeft;
    
    elements.syntaxHighlight.style.transform = `translate(-${scrollLeft}px, -${scrollTop}px)`;
    elements.lineNumbers.scrollTop = scrollTop;
}

// ==================================================
// 文件管理
// ==================================================

// 加载用户文件列表
async function loadFileList() {
    if (!appState.currentUser) {
        // 未登录，使用本地默认文件
        renderFileList();
        return;
    }

    try {
        const response = await fetch('/api/files', {
            credentials: 'include'
        });
        const data = await response.json();

        if (data.success) {
            // 清空当前文件状态，防止未登录内容被保存
            appState.currentFile = null;

            // 清空本地文件列表
            appState.files = {};

            // 如果用户没有文件，创建一个默认文件
            if (data.files.length === 0) {
                await createNewFile();
            } else {
                // 加载文件列表
                data.files.forEach(file => {
                    appState.files[file.id] = {
                        name: file.name,
                        content: null // 内容延迟加载
                    };
                });

                // 渲染文件列表
                renderFileList();

                // 加载第一个文件（不保存当前内容）
                const firstFileId = Object.keys(appState.files)[0];
                await switchFile(firstFileId, true); // 传入 skipSave=true
            }
        }
    } catch (error) {
        console.error('加载文件列表失败', error);
    }
}

// 渲染文件列表
function renderFileList() {
    elements.fileList.innerHTML = '';

    // 未登录状态显示提示信息
    if (!appState.currentUser) {
        elements.fileList.innerHTML = `
            <div style="padding: 40px 20px; text-align: center; color: var(--color-text-secondary);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 48px; height: 48px; margin: 0 auto 16px; opacity: 0.5;">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                    <polyline points="13 2 13 9 20 9"/>
                </svg>
                <p style="font-size: 14px; margin-bottom: 8px;">登录后管理您的文件</p>
                <p style="font-size: 12px; opacity: 0.7;">文件将自动保存到云端</p>
            </div>
        `;
        return;
    }

    // 登录状态显示文件列表
    for (const [fileId, fileData] of Object.entries(appState.files)) {
        const fileItem = createFileItem(fileId, fileData.name);
        elements.fileList.appendChild(fileItem);
    }

    // 更新active状态
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.toggle('active', item.dataset.fileId === appState.currentFile);
    });
}

function createFileItem(fileId, fileName) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.dataset.fileId = fileId;

    fileItem.innerHTML = `
        <div class="file-icon">📄</div>
        <div class="file-name" contenteditable="false">${fileName}</div>
        <div class="file-actions">
            <button class="file-action-btn rename-btn" title="重命名">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
            </button>
            <button class="file-action-btn delete-btn" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
    `;

    // 点击文件项切换文件
    fileItem.addEventListener('click', (e) => {
        if (e.target.closest('.file-action-btn')) return;
        switchFile(fileId);
    });

    // 重命名
    const renameBtn = fileItem.querySelector('.rename-btn');
    const fileNameEl = fileItem.querySelector('.file-name');
    renameBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        fileNameEl.contentEditable = 'true';
        fileNameEl.focus();
        const range = document.createRange();
        range.selectNodeContents(fileNameEl);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    });

    fileNameEl.addEventListener('blur', async () => {
        fileNameEl.contentEditable = 'false';
        const newName = fileNameEl.textContent.trim();
        const oldName = appState.files[fileId].name;

        if (newName && newName !== oldName) {
            // 更新到服务器
            if (appState.currentUser) {
                try {
                    const response = await fetch(`/api/files/${fileId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ name: newName })
                    });
                    const data = await response.json();

                    if (data.success) {
                        appState.files[fileId].name = newName;
                    } else {
                        fileNameEl.textContent = oldName;
                        alert('重命名失败：' + data.error);
                    }
                } catch (error) {
                    fileNameEl.textContent = oldName;
                    console.error('重命名失败', error);
                }
            } else {
                appState.files[fileId].name = newName;
            }
        } else {
            fileNameEl.textContent = oldName;
        }
    });

    fileNameEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            fileNameEl.blur();
        }
    });

    // 删除
    const deleteBtn = fileItem.querySelector('.delete-btn');
    deleteBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (Object.keys(appState.files).length === 1) {
            alert('至少需要保留一个文件');
            return;
        }
        if (confirm(`确定删除文件 "${fileName}"?`)) {
            // 从服务器删除
            if (appState.currentUser) {
                try {
                    const response = await fetch(`/api/files/${fileId}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    const data = await response.json();

                    if (!data.success) {
                        alert('删除失败：' + data.error);
                        return;
                    }
                } catch (error) {
                    console.error('删除失败', error);
                    return;
                }
            }

            // 从本地删除
            delete appState.files[fileId];
            fileItem.remove();

            // 如果删除的是当前文件，切换到其他文件
            if (appState.currentFile === fileId) {
                const firstFileId = Object.keys(appState.files)[0];
                await switchFile(firstFileId);
            }
        }
    });

    return fileItem;
}

async function switchFile(fileId, skipSave = false) {
    // 保存当前文件内容（除非明确跳过）
    if (!skipSave) {
        await saveCurrentFile();
    }

    // 切换到新文件
    appState.currentFile = fileId;

    // 加载文件内容
    if (appState.files[fileId].content === null && appState.currentUser) {
        // 从服务器加载
        try {
            const response = await fetch(`/api/files/${fileId}`, {
                credentials: 'include'
            });
            const data = await response.json();

            if (data.success) {
                appState.files[fileId].content = data.file.content;
            }
        } catch (error) {
            console.error('加载文件失败', error);
            appState.files[fileId].content = '';
        }
    }

    elements.codeEditor.value = appState.files[fileId].content || '';

    // 更新UI
    updateLineNumbers();
    elements.syntaxHighlight.innerHTML = highlightSyntax(elements.codeEditor.value);

    // 更新active状态
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.toggle('active', item.dataset.fileId === fileId);
    });
}

async function createNewFile() {
    if (!appState.currentUser) {
        // 未登录，本地创建
        const fileId = 'file_' + Date.now();
        const fileName = `untitled_${Object.keys(appState.files).length}.pseudo`;

        appState.files[fileId] = {
            name: fileName,
            content: '// 新文件\n'
        };

        const fileItem = createFileItem(fileId, fileName);
        elements.fileList.appendChild(fileItem);

        await switchFile(fileId);
        return;
    }

    // 登录用户，从服务器创建
    try {
        const fileName = `untitled_${Object.keys(appState.files).length}.pseudo`;
        const response = await fetch('/api/files', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: fileName })
        });
        const data = await response.json();

        if (data.success) {
            const file = data.file;
            appState.files[file.id] = {
                name: file.name,
                content: file.content
            };

            const fileItem = createFileItem(file.id, file.name);
            elements.fileList.insertBefore(fileItem, elements.fileList.firstChild);

            await switchFile(file.id);
        } else {
            alert('创建文件失败：' + data.error);
        }
    } catch (error) {
        console.error('创建文件失败', error);
        alert('创建文件失败');
    }
}

// 保存当前文件
async function saveCurrentFile() {
    if (!appState.currentFile || !appState.files[appState.currentFile]) {
        return;
    }

    const currentContent = elements.codeEditor.value;
    const fileId = appState.currentFile;

    // 更新本地内容
    appState.files[fileId].content = currentContent;

    // 如果已登录，保存到服务器
    if (appState.currentUser) {
        try {
            await fetch(`/api/files/${fileId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ content: currentContent })
            });
        } catch (error) {
            console.error('保存文件失败', error);
        }
    }
}

// 自动保存定时器
let autoSaveTimer = null;

function startAutoSave() {
    if (autoSaveTimer) {
        clearInterval(autoSaveTimer);
    }

    autoSaveTimer = setInterval(async () => {
        if (appState.currentUser && appState.currentFile) {
            await saveCurrentFile();
        }
    }, 5000); // 每5秒保存一次
}

// ==================================================
// 输出区标签页切换
// ==================================================
function switchOutputTab(tabName) {
    elements.outputTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    elements.outputPanels.forEach(panel => {
        panel.classList.toggle('active', panel.id === tabName + '-panel');
    });
}

// ==================================================
// 代码运行
// ==================================================

// 重置运行状态
function resetRunState() {
    appState.isRunning = false;
    appState.abortController = null;
    elements.runBtn.style.display = 'flex';
    elements.stopBtn.style.display = 'none';
}

// 停止代码执行
function stopCode() {
    if (appState.abortController) {
        appState.abortController.abort();
    }
    elements.statusText.textContent = '已停止';
    elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot';
    displayError('代码执行已被用户中断');
    resetRunState();
}

async function runCode() {
    if (appState.isRunning) return;

    const code = elements.codeEditor.value.trim();
    if (!code) {
        alert('请输入代码');
        return;
    }

    // 清空输出
    elements.outputArea.innerHTML = '';
    elements.statusText.textContent = '运行中...';
    elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot running';
    appState.isRunning = true;

    // 创建AbortController用于中断请求
    appState.abortController = new AbortController();

    // 显示停止按钮，隐藏运行按钮
    elements.runBtn.style.display = 'none';
    elements.stopBtn.style.display = 'flex';

    // 切换到输出结果标签页
    switchOutputTab('result');

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                debug: false,
                strict: elements.strictModeCheckbox.checked
            }),
            signal: appState.abortController.signal
        });
        
        const data = await response.json();

        if (data.status === 'success') {
            displayOutput(data.output);
            elements.statusText.textContent = '运行成功';
            elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot success';
            resetRunState();
        } else if (data.status === 'input_required') {
            // 需要用户输入
            const userInput = await promptInput(data.prompt);
            if (userInput !== null) {
                continueExecution(data.execution_id, userInput);
            } else {
                elements.statusText.textContent = '已取消';
                elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot';
                resetRunState();
            }
        } else {
            displayError(data.error);
            elements.statusText.textContent = '运行错误';
            elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot error';
            resetRunState();
        }
    } catch (error) {
        // 检查是否是用户主动中断
        if (error.name === 'AbortError') {
            return; // stopCode() 已经处理了状态重置
        }
        displayError('网络错误: ' + error.message);
        elements.statusText.textContent = '网络错误';
        elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot error';
        resetRunState();
    }
}

async function continueExecution(executionId, input) {
    try {
        const response = await fetch('/api/input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                execution_id: executionId,
                input: input
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayOutput(data.output);
            elements.statusText.textContent = '运行成功';
            elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot success';
            appState.isRunning = false;
        } else if (data.status === 'input_required') {
            const userInput = await promptInput(data.prompt);
            if (userInput !== null) {
                continueExecution(executionId, userInput);
            } else {
                elements.statusText.textContent = '已取消';
                elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot';
                appState.isRunning = false;
            }
        } else {
            displayError(data.error);
            elements.statusText.textContent = '运行错误';
            elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot error';
            appState.isRunning = false;
        }
    } catch (error) {
        displayError('网络错误: ' + error.message);
        elements.statusText.textContent = '网络错误';
        elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot error';
        appState.isRunning = false;
    }
}

function displayOutput(output) {
    elements.outputArea.innerHTML = '';
    output.forEach(line => {
        const lineEl = document.createElement('div');
        lineEl.className = 'output-line';
        lineEl.textContent = line;
        elements.outputArea.appendChild(lineEl);
    });
}

function displayError(error) {
    elements.outputArea.innerHTML = '';
    const errorEl = document.createElement('div');
    errorEl.className = 'output-line error';
    errorEl.textContent = error;
    elements.outputArea.appendChild(errorEl);
}

function promptInput(prompt) {
    return new Promise((resolve) => {
        elements.inputPrompt.textContent = prompt;
        elements.inputField.value = '';
        showModal('input-modal');
        elements.inputField.focus();
        
        const submitHandler = () => {
            const value = elements.inputField.value;
            hideModal('input-modal');
            cleanup();
            resolve(value);
        };
        
        const cancelHandler = () => {
            hideModal('input-modal');
            cleanup();
            resolve(null);
        };
        
        const keyHandler = (e) => {
            if (e.key === 'Enter') {
                submitHandler();
            }
        };
        
        const cleanup = () => {
            elements.inputSubmit.removeEventListener('click', submitHandler);
            elements.inputCancel.removeEventListener('click', cancelHandler);
            elements.inputField.removeEventListener('keydown', keyHandler);
        };
        
        elements.inputSubmit.addEventListener('click', submitHandler);
        elements.inputCancel.addEventListener('click', cancelHandler);
        elements.inputField.addEventListener('keydown', keyHandler);
    });
}

// ==================================================
// 模态框管理
// ==================================================
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// ==================================================
// 用户认证
// ==================================================
async function login(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            appState.currentUser = data.user;
            updateUserUI();
            hideModal('login-modal');
            elements.loginError.textContent = '';
            return true;
        } else {
            elements.loginError.textContent = data.error || '登录失败';
            return false;
        }
    } catch (error) {
        elements.loginError.textContent = '网络错误';
        return false;
    }
}

async function register(username, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            appState.currentUser = data.user;
            updateUserUI();
            hideModal('register-modal');
            elements.registerError.textContent = '';
            return true;
        } else {
            elements.registerError.textContent = data.error || '注册失败';
            return false;
        }
    } catch (error) {
        elements.registerError.textContent = '网络错误';
        return false;
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        appState.currentUser = null;
        updateUserUI();
    } catch (error) {
        console.error('退出登录失败', error);
    }
}

async function updateUserUI() {
    if (appState.currentUser) {
        elements.userName.textContent = appState.currentUser.username;
        elements.loginItem.style.display = 'none';
        elements.registerItem.style.display = 'none';
        elements.logoutItem.style.display = 'block';

        // 显示新建文件按钮
        elements.newFileBtn.style.display = 'block';

        // 加载用户文件列表
        await loadFileList();

        // 启动自动保存
        startAutoSave();
    } else {
        elements.userName.textContent = '登录 / 注册';
        elements.loginItem.style.display = 'block';
        elements.registerItem.style.display = 'block';
        elements.logoutItem.style.display = 'none';

        // 隐藏新建文件按钮
        elements.newFileBtn.style.display = 'none';

        // 停止自动保存
        if (autoSaveTimer) {
            clearInterval(autoSaveTimer);
            autoSaveTimer = null;
        }

        // 显示未登录提示
        renderFileList();
    }
}

// ==================================================
// 文件上传
// ==================================================
function handleFileUpload(file) {
    if (!file.name.endsWith('.txt')) {
        alert('只能上传 .txt 文件');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const fileData = {
            id: 'upload_' + Date.now(),
            name: file.name,
            size: file.size,
            content: e.target.result
        };
        
        appState.uploadedFiles.push(fileData);
        renderUploadedFiles();
    };
    reader.readAsText(file);
}

function renderUploadedFiles() {
    elements.uploadedFiles.innerHTML = '';
    
    if (appState.uploadedFiles.length === 0) {
        elements.uploadedFiles.innerHTML = `
            <div class="no-files">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                    <polyline points="13 2 13 9 20 9"/>
                </svg>
                <p>暂无上传文件</p>
                <p class="hint">上传的 .txt 文件可在伪代码中通过 OPENFILE 读取</p>
            </div>
        `;
        return;
    }
    
    appState.uploadedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'uploaded-file-item';
        fileItem.innerHTML = `
            <div class="file-item-icon">📄</div>
            <div class="file-item-info">
                <div class="file-item-name">${file.name}</div>
                <div class="file-item-size">${(file.size / 1024).toFixed(2)} KB</div>
            </div>
            <div class="file-item-actions">
                <button class="btn btn-small btn-secondary delete-upload-btn" data-file-id="${file.id}">删除</button>
            </div>
        `;
        
        const deleteBtn = fileItem.querySelector('.delete-upload-btn');
        deleteBtn.addEventListener('click', () => {
            appState.uploadedFiles = appState.uploadedFiles.filter(f => f.id !== file.id);
            renderUploadedFiles();
        });
        
        elements.uploadedFiles.appendChild(fileItem);
    });
}

// ==================================================
// 事件监听器
// ==================================================
function initializeEventListeners() {
    // 编辑器事件
    elements.codeEditor.addEventListener('input', () => {
        updateLineNumbers();
        elements.syntaxHighlight.innerHTML = highlightSyntax(elements.codeEditor.value);
    });

    elements.codeEditor.addEventListener('scroll', syncScroll);

    // Tab键处理：插入4个空格而不是切换焦点
    elements.codeEditor.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();

            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const value = e.target.value;

            // 插入4个空格
            e.target.value = value.substring(0, start) + '    ' + value.substring(end);

            // 设置光标位置
            e.target.selectionStart = e.target.selectionEnd = start + 4;

            // 触发input事件以更新行号和语法高亮
            e.target.dispatchEvent(new Event('input'));
        }

        // Enter键自动缩进
        if (e.key === 'Enter') {
            e.preventDefault();

            const start = e.target.selectionStart;
            const value = e.target.value;

            // 获取当前行的开始位置
            const lineStart = value.lastIndexOf('\n', start - 1) + 1;
            const currentLine = value.substring(lineStart, start);

            // 计算当前行的缩进
            const indentMatch = currentLine.match(/^(\s*)/);
            let indent = indentMatch ? indentMatch[1] : '';

            // 检测是否需要增加缩进的关键字
            const increaseIndentKeywords = [
                'THEN', 'ELSE', 'DO', 'REPEAT',
                'PROCEDURE', 'FUNCTION', 'TYPE', 'CASE', 'OF'
            ];

            // 检测是否需要减少缩进的关键字（在当前行）
            const decreaseIndentKeywords = [
                'ENDIF', 'ENDWHILE', 'ENDPROCEDURE', 'ENDFUNCTION',
                'ENDTYPE', 'ENDCASE', 'UNTIL', 'NEXT', 'ELSE', 'ELSEIF', 'OTHERWISE'
            ];

            // 检查当前行是否以需要增加缩进的关键字结尾
            const trimmedLine = currentLine.trim();
            const shouldIncreaseIndent = increaseIndentKeywords.some(keyword =>
                trimmedLine.endsWith(keyword) ||
                new RegExp('\\b' + keyword + '\\s*$').test(trimmedLine)
            );

            // 如果当前行以增加缩进的关键字结尾，下一行增加缩进
            if (shouldIncreaseIndent) {
                indent += '    ';
            }

            // 插入换行和缩进
            const newText = '\n' + indent;
            e.target.value = value.substring(0, start) + newText + value.substring(start);

            // 设置光标位置
            const newCursorPos = start + newText.length;
            e.target.selectionStart = e.target.selectionEnd = newCursorPos;

            // 触发input事件
            e.target.dispatchEvent(new Event('input'));
        }

        // Backspace键智能删除缩进
        if (e.key === 'Backspace') {
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const value = e.target.value;

            // 只在没有选中文本且光标不在开头时处理
            if (start === end && start > 0) {
                // 获取当前行的开始位置
                const lineStart = value.lastIndexOf('\n', start - 1) + 1;
                const beforeCursor = value.substring(lineStart, start);

                // 检查光标前是否只有空格，且数量是4的倍数
                if (/^( +)$/.test(beforeCursor) && beforeCursor.length % 4 === 0) {
                    e.preventDefault();

                    // 删除4个空格（一个缩进级别）
                    const newValue = value.substring(0, start - 4) + value.substring(start);
                    e.target.value = newValue;

                    // 设置光标位置
                    e.target.selectionStart = e.target.selectionEnd = start - 4;

                    // 触发input事件
                    e.target.dispatchEvent(new Event('input'));
                }
            }
        }
    });

    // 运行按钮
    elements.runBtn.addEventListener('click', runCode);
    elements.stopBtn.addEventListener('click', stopCode);
    
    // 文档按钮
    elements.docsBtn.addEventListener('click', () => showModal('docs-modal'));
    elements.docsClose.addEventListener('click', () => hideModal('docs-modal'));
    
    // 用户菜单
    elements.userBtn.addEventListener('click', () => {
        elements.userDropdown.classList.toggle('show');
    });
    
    // 点击外部关闭下拉菜单
    document.addEventListener('click', (e) => {
        if (!elements.userBtn.contains(e.target) && !elements.userDropdown.contains(e.target)) {
            elements.userDropdown.classList.remove('show');
        }
    });
    
    elements.loginItem.addEventListener('click', () => {
        elements.userDropdown.classList.remove('show');
        showModal('login-modal');
    });
    
    elements.registerItem.addEventListener('click', () => {
        elements.userDropdown.classList.remove('show');
        showModal('register-modal');
    });
    
    elements.logoutItem.addEventListener('click', () => {
        elements.userDropdown.classList.remove('show');
        logout();
    });
    
    // 登录表单
    elements.loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await login(elements.loginUsername.value, elements.loginPassword.value);
    });
    
    elements.loginClose.addEventListener('click', () => hideModal('login-modal'));
    
    // 注册表单
    elements.registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const password = elements.registerPassword.value;
        const confirm = elements.registerPasswordConfirm.value;
        
        if (password !== confirm) {
            elements.registerError.textContent = '两次输入的密码不一致';
            return;
        }
        
        await register(elements.registerUsername.value, password);
    });
    
    elements.registerClose.addEventListener('click', () => hideModal('register-modal'));
    
    // 模态框背景点击关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.querySelector('.modal-overlay')?.addEventListener('click', () => {
            hideModal(modal.id);
        });
    });
    
    // 新建文件
    elements.newFileBtn.addEventListener('click', createNewFile);
    
    // 输出区标签页切换
    elements.outputTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchOutputTab(tab.dataset.tab);
        });
    });
    
    // 清空输出
    elements.clearOutputBtn.addEventListener('click', () => {
        elements.outputArea.innerHTML = '<div class="output-placeholder">运行代码后，输出将显示在这里...</div>';
        elements.statusText.textContent = '就绪';
        elements.statusText.parentElement.querySelector('.status-dot').className = 'status-dot';
    });
    
    // 文件上传
    elements.uploadFileBtn.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
            e.target.value = '';
        }
    });
}

// ==================================================
// 初始化
// ==================================================
function initialize() {
    // 初始化行号和语法高亮
    updateLineNumbers();
    elements.syntaxHighlight.innerHTML = highlightSyntax(elements.codeEditor.value);

    // 初始化事件监听器
    initializeEventListeners();

    // 检查登录状态（会自动调用updateUserUI）
    checkLoginStatus();

    console.log('伪代码解释器已初始化');
}

async function checkLoginStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        if (data.logged_in) {
            appState.currentUser = data.user;
        }
        // 无论是否登录，都调用updateUserUI更新界面
        await updateUserUI();
    } catch (error) {
        console.error('检查登录状态失败', error);
        // 即使出错也调用updateUserUI显示未登录状态
        await updateUserUI();
    }
}

// ==================== 可拖动分隔条功能 ====================

function initResizers() {
    const sidebarResizer = document.getElementById('sidebar-resizer');
    const outputResizer = document.getElementById('output-resizer');
    const sidebar = document.getElementById('sidebar');
    const editorWrapper = document.getElementById('editor-wrapper');
    const outputContainer = document.getElementById('output-container');

    // 左右拖动（侧边栏宽度）
    let isResizingX = false;
    let startX = 0;
    let startWidth = 0;

    sidebarResizer.addEventListener('mousedown', (e) => {
        isResizingX = true;
        startX = e.clientX;
        startWidth = sidebar.offsetWidth;
        sidebarResizer.classList.add('dragging');
        document.body.classList.add('resizing');
        e.preventDefault();
    });

    // 上下拖动（输出面板高度）
    let isResizingY = false;
    let startY = 0;
    let startHeight = 0;

    outputResizer.addEventListener('mousedown', (e) => {
        isResizingY = true;
        startY = e.clientY;
        startHeight = outputContainer.offsetHeight;
        outputResizer.classList.add('dragging');
        document.body.classList.add('resizing-y');
        e.preventDefault();
    });

    // 全局鼠标移动事件
    document.addEventListener('mousemove', (e) => {
        if (isResizingX) {
            const deltaX = e.clientX - startX;
            const newWidth = startWidth + deltaX;

            // 限制宽度范围：最小200px，最大窗口宽度的50%
            const minWidth = 200;
            const maxWidth = window.innerWidth * 0.5;

            if (newWidth >= minWidth && newWidth <= maxWidth) {
                sidebar.style.width = newWidth + 'px';
            }
        }

        if (isResizingY) {
            const deltaY = e.clientY - startY;
            const newHeight = startHeight - deltaY; // 注意是减，因为从下往上拖

            // 限制高度范围：最小150px，最大容器高度的80%
            const minHeight = 150;
            const maxHeight = (window.innerHeight - 50) * 0.8; // 50是顶部栏高度

            if (newHeight >= minHeight && newHeight <= maxHeight) {
                outputContainer.style.height = newHeight + 'px';
                // 同时调整编辑器高度
                const remainingHeight = window.innerHeight - 50 - newHeight - 4; // 4是分隔条高度
                editorWrapper.style.height = remainingHeight + 'px';
            }
        }
    });

    // 全局鼠标释放事件
    document.addEventListener('mouseup', () => {
        if (isResizingX) {
            isResizingX = false;
            sidebarResizer.classList.remove('dragging');
            document.body.classList.remove('resizing');
        }

        if (isResizingY) {
            isResizingY = false;
            outputResizer.classList.remove('dragging');
            document.body.classList.remove('resizing-y');
        }
    });
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initialize();
        initResizers();
    });
} else {
    initialize();
    initResizers();
}
