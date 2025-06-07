document.addEventListener('DOMContentLoaded', function() {
    // 编辑按钮点击事件
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = row.cells[0].textContent;
            const code = row.cells[1].textContent;
            const name = row.cells[2].textContent;
            
            alert(`编辑项目: ID=${id}, 名称=${code}, 描述=${name}`);
            // 这里可以实现编辑功能，例如打开编辑对话框
        });
    });
    
    // 删除按钮点击事件
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const id = row.cells[0].textContent;
            
            if (confirm(`确定要删除ID为${id}的项目吗？`)) {
                // 这里可以实现删除功能，例如发送删除请求
                row.remove();
            }
        });
    });
    
    // 新增项目按钮点击事件
    const addButton = document.querySelector('.btn-add');
    if (addButton) {
        addButton.addEventListener('click', function() {
            // 跳转到新建项目页面
            window.location.href = 'project_new.html';
        });
    }
    
    // 新建项目表单提交
    const submitProjectButton = document.getElementById('submit-project');
    if (submitProjectButton) {
        submitProjectButton.addEventListener('click', function() {
            const projectName = document.getElementById('project-name').value;
            const projectDescription = document.getElementById('project-description').value;
            
            if (!projectName) {
                alert('请输入项目名称');
                return;
            }
            
            // 创建项目
            createNewProject(projectName, projectDescription);
        });
    }

    // 创建新项目函数
    async function createNewProject(name, description) {
        try {
            // 显示加载状态
            document.getElementById('submit-project').disabled = true;
            document.getElementById('submit-project').innerText = '创建中...';
            
            // 调用API创建项目
            const response = await API.Project.createProject(name, description);
            
            if (response.success) {
                alert(`项目"${name}"创建成功！`);
                // 跳转回首页
                window.location.href = 'index.html';
            } else {
                alert('创建项目失败: ' + (response.message || '未知错误'));
                // 恢复按钮状态
                document.getElementById('submit-project').disabled = false;
                document.getElementById('submit-project').innerText = '创建';
            }
        } catch (error) {
            console.error('创建项目失败:', error);
            alert('创建项目失败，请重试');
            // 恢复按钮状态
            document.getElementById('submit-project').disabled = false;
            document.getElementById('submit-project').innerText = '创建';
        }
    }
    
    /* 菜单项点击事件已在common.js中实现
    // 菜单项点击事件 - 实现页面跳转
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // 获取要跳转的页面URL
            const targetPage = this.getAttribute('data-page');
            
            // 如果是有效的页面链接，则进行跳转
            if (targetPage && targetPage !== '#') {
                window.location.href = targetPage;
            } else {
                // 仅更新活动状态但不跳转
                menuItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                alert('该功能页面正在开发中');
            }
        });
    });
    */
    
    /* 退出按钮点击事件已在common.js中实现
    // 退出按钮点击事件
    const logoutIcon = document.querySelector('.icons i');
    if (logoutIcon) {
        logoutIcon.addEventListener('click', function() {
            if (confirm('确定要退出系统吗？')) {
                // 模拟退出操作，实际应用中应该进行登出处理
                alert('您已退出系统');
                // 跳转到登录页面
                window.location.href = 'login.html';
            }
        });
    }
    */
    
    // 需求描述页面的特定功能
    const requirementTextarea = document.querySelector('.requirement-textarea');
    if (requirementTextarea) {
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                console.log('选择了项目:', selectedProject);
                // 这里可以加载选中项目的需求描述内容
                if (this.value) {
                    // 模拟根据项目ID加载内容
                    requirementTextarea.value = `这是${selectedProject}的需求描述示例内容，实际应用中应从服务器获取。\n\n包含以下功能点：\n1. 用户管理\n2. 权限控制\n3. 数据分析`;
                }
            });
        }
        
        // 保存按钮点击事件
        const saveButton = document.querySelector('.btn-save');
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const content = requirementTextarea.value;
                if (content.trim() === '') {
                    alert('请输入需求描述内容');
                    return;
                }
                alert('需求描述已保存');
                // 这里可以实现保存功能，例如发送保存请求
            });
        }
        
        // 取消按钮点击事件
        const cancelButton = document.querySelector('.btn-cancel');
        if (cancelButton) {
            cancelButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    return;
                }
                
                if (confirm('确定要取消编辑吗？未保存的内容将丢失')) {
                    requirementTextarea.value = '';
                    projectSelect.selectedIndex = 0; // 重置选择框
                }
            });
        }
        
        // 提交按钮点击事件
        const confirmButton = document.querySelector('.btn-confirm');
        if (confirmButton) {
            confirmButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const content = requirementTextarea.value;
                if (content.trim() === '') {
                    alert('请输入需求描述内容');
                    return;
                }
                alert('需求描述已提交成功');
                // 这里可以实现提交功能，例如发送提交请求
                window.location.href = 'index.html';
            });
        }
    }
    
    // 架构代码页面的特定功能
    const architectureTextarea = document.querySelector('.architecture-textarea');
    if (architectureTextarea) {
        // 当前选择的配置
        let currentConfig = {
            language: 'java',
            architecture: 'mvc',
            project: ''
        };
        
        // 语言选择下拉框事件
        const languageSelect = document.querySelector('.language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', function() {
                currentConfig.language = this.value;
                console.log('选择了语言:', currentConfig.language);
            });
        }
        
        // 架构类型下拉框事件
        const architectureSelect = document.querySelector('.architecture-select');
        if (architectureSelect) {
            architectureSelect.addEventListener('change', function() {
                currentConfig.architecture = this.value;
                console.log('选择了架构类型:', currentConfig.architecture);
            });
        }
        
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                currentConfig.project = selectedProject;
                console.log('选择了项目:', selectedProject);
                
                // 清空当前代码
                architectureTextarea.value = '';
                
                // 提示用户点击生成按钮
                architectureTextarea.placeholder = `请点击"生成"按钮生成${selectedProject}的${currentConfig.architecture.toUpperCase()}架构代码`;
            });
        }
        
        // 生成按钮点击事件
        const generateButton = document.querySelector('.btn-confirm');
        if (generateButton) {
            generateButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const language = currentConfig.language;
                const architecture = currentConfig.architecture;
                
                // 生成代码，根据选择的语言和架构类型
                let generatedCode = '';
                
                if (language === 'java') {
                    if (architecture === 'mvc' || architecture === 'mvvm') {
                        generatedCode = generateJavaMVCCode(selectedProject);
                    } else if (architecture === 'microservices') {
                        generatedCode = generateJavaMicroservicesCode(selectedProject);
                    } else {
                        generatedCode = generateJavaMVCCode(selectedProject); // 默认MVC
                    }
                } else if (language === 'python') {
                    generatedCode = generatePythonCode(selectedProject, architecture);
                } else if (language === 'javascript') {
                    generatedCode = generateJavaScriptCode(selectedProject, architecture);
                } else if (language === 'csharp') {
                    generatedCode = generateCSharpCode(selectedProject, architecture);
                }
                
                architectureTextarea.value = generatedCode;
                alert('代码生成成功！');
            });
        }
        
        // 下载按钮点击事件
        const downloadButton = document.getElementById('download-code');
        if (downloadButton) {
            downloadButton.addEventListener('click', function() {
                const code = architectureTextarea.value;
                if (!code || code.trim() === '') {
                    alert('没有可下载的代码');
                    return;
                }
                
                const projectSelect = document.querySelector('.project-select');
                const projectName = projectSelect.value 
                    ? projectSelect.options[projectSelect.selectedIndex].text 
                    : '未命名项目';
                
                const language = currentConfig.language;
                
                // 根据语言确定文件扩展名
                let fileExtension = '.txt';
                if (language === 'java') fileExtension = '.java';
                else if (language === 'python') fileExtension = '.py';
                else if (language === 'javascript') fileExtension = '.js';
                else if (language === 'csharp') fileExtension = '.cs';
                
                // 创建Blob对象
                const blob = new Blob([code], { type: 'text/plain' });
                
                // 创建下载链接
                const downloadLink = document.createElement('a');
                downloadLink.download = `${projectName.replace(/\s+/g, '_')}_架构代码${fileExtension}`;
                downloadLink.href = window.URL.createObjectURL(blob);
                downloadLink.style.display = 'none';
                
                // 添加到DOM并触发点击
                document.body.appendChild(downloadLink);
                downloadLink.click();
                
                // 清理
                window.URL.revokeObjectURL(downloadLink.href);
                document.body.removeChild(downloadLink);
            });
        }
    }
    
    // 数据库设计页面的特定功能
    const databaseTable = document.querySelector('.card-body .table');
    if (databaseTable && window.location.href.includes('database.html')) {
        // 当前选择的配置
        let dbConfig = {
            dbType: 'mysql',
            project: ''
        };
        
        // 数据库类型选择下拉框事件
        const dbTypeSelect = document.querySelector('.database-type-select');
        if (dbTypeSelect) {
            dbTypeSelect.addEventListener('change', function() {
                dbConfig.dbType = this.value;
                console.log('选择了数据库类型:', dbConfig.dbType);
            });
        }
        
        // 生成按钮点击事件
        const generateButton = document.querySelector('.generate-btn');
        if (generateButton) {
            generateButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const dbType = dbConfig.dbType;
                
                alert(`正在为项目 ${selectedProject} 生成 ${dbType} 数据库表结构...`);
                // 这里可以实现生成功能，例如根据选择的数据库类型生成对应的SQL语句
                
                // 模拟生成成功提示
                setTimeout(() => {
                    alert('数据库表结构生成成功！');
                }, 1000);
            });
        }
        
        // 编辑按钮点击事件
        const editButtons = document.querySelectorAll('.btn-edit');
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const tableName = row.cells[0].textContent;
                const fieldName = row.cells[1].textContent;
                const dataType = row.cells[2].textContent;
                const length = row.cells[3].textContent;
                const constraint = row.cells[4].textContent;
                const description = row.cells[5].textContent;
                
                alert(`编辑字段: 表=${tableName}, 字段=${fieldName}, 类型=${dataType}, 长度=${length}, 约束=${constraint}, 描述=${description}`);
                // 这里可以实现编辑功能，例如打开编辑对话框
            });
        });
        
        // 删除按钮点击事件
        const deleteButtons = document.querySelectorAll('.btn-delete');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const tableName = row.cells[0].textContent;
                const fieldName = row.cells[1].textContent;
                
                if (confirm(`确定要删除表 ${tableName} 中的字段 ${fieldName} 吗？`)) {
                    // 这里可以实现删除功能，例如发送删除请求
                    row.remove();
                }
            });
        });
        
        // 下载按钮点击事件
        const downloadButton = document.querySelector('.btn-download');
        if (downloadButton) {
            downloadButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const dbType = dbConfig.dbType;
                
                // 根据表格内容生成SQL文件内容
                let sqlContent = generateSQLContent(selectedProject, dbType, databaseTable);
                
                // 创建Blob对象
                const blob = new Blob([sqlContent], { type: 'text/plain' });
                
                // 创建下载链接
                const downloadLink = document.createElement('a');
                downloadLink.download = `${selectedProject}_${dbType}_schema.sql`;
                downloadLink.href = window.URL.createObjectURL(blob);
                downloadLink.style.display = 'none';
                
                // 添加到DOM并触发点击
                document.body.appendChild(downloadLink);
                downloadLink.click();
                
                // 清理
                window.URL.revokeObjectURL(downloadLink.href);
                document.body.removeChild(downloadLink);
                
                alert('表结构文件下载成功！');
            });
        }
        
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                dbConfig.project = selectedProject;
                console.log('选择了项目:', selectedProject);
                
                // 这里可以根据选择的项目加载对应的数据库表结构
                // 例如发送请求获取该项目的数据库表结构
                
                // 模拟加载完成提示
                alert(`已加载项目 ${selectedProject} 的数据库表结构`);
            });
        }
        
        // 生成SQL文件内容
        function generateSQLContent(projectName, dbType, tableElement) {
            let sql = `-- ${projectName} 数据库表结构\n`;
            sql += `-- 数据库类型: ${dbType}\n`;
            sql += `-- 生成时间: ${new Date().toLocaleString()}\n\n`;
            
            // 获取表格中的所有行
            const rows = tableElement.querySelectorAll('tbody tr');
            
            // 创建一个Map存储表结构
            const tables = new Map();
            
            // 遍历行，收集表结构信息
            rows.forEach(row => {
                const tableName = row.cells[0].textContent;
                const fieldName = row.cells[1].textContent;
                const dataType = row.cells[2].textContent;
                const length = row.cells[3].textContent;
                const constraint = row.cells[4].textContent;
                const description = row.cells[5].textContent;
                
                // 如果表不在Map中，则添加
                if (!tables.has(tableName)) {
                    tables.set(tableName, []);
                }
                
                // 添加字段信息
                tables.get(tableName).push({
                    fieldName,
                    dataType,
                    length,
                    constraint,
                    description
                });
            });
            
            // 生成SQL语句
            if (dbType === 'mysql' || dbType === 'postgresql') {
                // 遍历每个表
                tables.forEach((fields, tableName) => {
                    sql += `CREATE TABLE ${tableName} (\n`;
                    
                    // 添加字段
                    fields.forEach((field, index) => {
                        let fieldSql = `  ${field.fieldName} ${field.dataType}`;
                        
                        // 添加长度
                        if (field.length !== '-') {
                            fieldSql += `(${field.length})`;
                        }
                        
                        // 添加约束
                        if (field.constraint.includes('NOT NULL')) {
                            fieldSql += ' NOT NULL';
                        }
                        
                        // 添加注释
                        fieldSql += ` COMMENT '${field.description}'`;
                        
                        // 添加逗号
                        if (index < fields.length - 1) {
                            fieldSql += ',';
                        }
                        
                        sql += fieldSql + '\n';
                    });
                    
                    // 添加主键和外键
                    const primaryKeys = fields.filter(field => field.constraint.includes('PK'))
                        .map(field => field.fieldName);
                    
                    if (primaryKeys.length > 0) {
                        sql += `  ,PRIMARY KEY (${primaryKeys.join(', ')})\n`;
                    }
                    
                    const foreignKeys = fields.filter(field => field.constraint.includes('FK'));
                    foreignKeys.forEach(field => {
                        sql += `  ,FOREIGN KEY (${field.fieldName}) REFERENCES ${field.constraint.replace('FK', '').trim()}(id)\n`;
                    });
                    
                    sql += `);\n\n`;
                });
            } else if (dbType === 'oracle') {
                // Oracle SQL 生成逻辑
                // ...类似MySQL逻辑但使用Oracle语法
            } else if (dbType === 'sqlserver') {
                // SQL Server 生成逻辑
                // ...类似MySQL逻辑但使用SQL Server语法
            } else if (dbType === 'mongodb') {
                // MongoDB 生成逻辑 (注意MongoDB使用JSON格式而非SQL)
                sql = `// ${projectName} 数据库结构 - MongoDB\n`;
                sql += `// 生成时间: ${new Date().toLocaleString()}\n\n`;
                
                tables.forEach((fields, tableName) => {
                    sql += `db.createCollection("${tableName}", {\n`;
                    sql += `  validator: {\n`;
                    sql += `    $jsonSchema: {\n`;
                    sql += `      bsonType: "object",\n`;
                    sql += `      required: [${fields.filter(f => f.constraint.includes('NOT NULL'))
                        .map(f => `"${f.fieldName}"`).join(', ')}],\n`;
                    sql += `      properties: {\n`;
                    
                    fields.forEach((field, index) => {
                        sql += `        ${field.fieldName}: {\n`;
                        
                        // 确定BSON类型
                        let bsonType = "string";
                        if (field.dataType === 'int') bsonType = "int";
                        else if (field.dataType === 'decimal') bsonType = "decimal";
                        else if (field.dataType === 'datetime') bsonType = "date";
                        
                        sql += `          bsonType: "${bsonType}",\n`;
                        sql += `          description: "${field.description}"\n`;
                        sql += `        }${index < fields.length - 1 ? ',' : ''}\n`;
                    });
                    
                    sql += `      }\n`;
                    sql += `    }\n`;
                    sql += `  }\n`;
                    sql += `});\n\n`;
                });
            }
            
            return sql;
        }
    }
    
    // 模块代码页面的特定功能
    if (document.getElementById('download-module-code')) {
        // 当前选择的配置
        let moduleConfig = {
            language: 'java',
            moduleType: 'dao',
            project: ''
        };
        
        // 语言选择下拉框事件
        const languageSelect = document.querySelector('.language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', function() {
                moduleConfig.language = this.value;
                console.log('选择了语言:', moduleConfig.language);
            });
        }
        
        // 模块类型下拉框事件
        const moduleSelect = document.querySelector('.module-select');
        if (moduleSelect) {
            moduleSelect.addEventListener('change', function() {
                moduleConfig.moduleType = this.value;
                console.log('选择了模块类型:', moduleConfig.moduleType);
            });
        }
        
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                moduleConfig.project = selectedProject;
                console.log('选择了项目:', selectedProject);
                
                // 清空当前代码
                const moduleTextarea = document.querySelector('.architecture-textarea');
                moduleTextarea.value = '';
                
                // 提示用户点击生成按钮
                moduleTextarea.placeholder = `请点击"生成"按钮生成${selectedProject}的${moduleConfig.moduleType}模块代码`;
            });
        }
        
        // 生成按钮点击事件
        const generateButton = document.querySelector('.btn-confirm');
        if (generateButton) {
            generateButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const language = moduleConfig.language;
                const moduleType = moduleConfig.moduleType;
                
                // 生成代码，根据选择的语言和模块类型
                let generatedCode = generateModuleCode(selectedProject, language, moduleType);
                
                const moduleTextarea = document.querySelector('.architecture-textarea');
                moduleTextarea.value = generatedCode;
                alert('模块代码生成成功！');
            });
        }
        
        // 下载按钮点击事件
        const downloadButton = document.getElementById('download-module-code');
        if (downloadButton) {
            downloadButton.addEventListener('click', function() {
                const moduleTextarea = document.querySelector('.architecture-textarea');
                const code = moduleTextarea.value;
                if (!code || code.trim() === '') {
                    alert('没有可下载的代码');
                    return;
                }
                
                const projectSelect = document.querySelector('.project-select');
                const projectName = projectSelect.value 
                    ? projectSelect.options[projectSelect.selectedIndex].text 
                    : '未命名项目';
                
                const language = moduleConfig.language;
                const moduleType = moduleConfig.moduleType;
                
                // 根据语言确定文件扩展名
                let fileExtension = '.txt';
                if (language === 'java') fileExtension = '.java';
                else if (language === 'python') fileExtension = '.py';
                else if (language === 'javascript') fileExtension = '.js';
                else if (language === 'csharp') fileExtension = '.cs';
                
                // 创建Blob对象
                const blob = new Blob([code], { type: 'text/plain' });
                
                // 创建下载链接
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${projectName}_${moduleType}${fileExtension}`;
                document.body.appendChild(a);
                a.click();
                
                // 清理
                setTimeout(() => {
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }, 0);
            });
        }
    }
    
    // 测试用例页面的特定功能
    if (window.location.href.includes('testcase.html')) {
        // 当前选择的配置
        let testConfig = {
            testType: 'unit',
            project: ''
        };
        
        // 测试类型选择下拉框事件
        const testTypeSelect = document.querySelector('.test-type-select');
        if (testTypeSelect) {
            testTypeSelect.addEventListener('change', function() {
                testConfig.testType = this.value;
                console.log('选择了测试类型:', testConfig.testType);
            });
        }
        
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                testConfig.project = selectedProject;
                console.log('选择了项目:', selectedProject);
                
                // 这里可以根据选择的项目加载对应的测试用例
                alert(`已加载项目 ${selectedProject} 的测试用例`);
            });
        }
        
        // 生成按钮点击事件
        const generateButton = document.querySelector('.generate-btn');
        if (generateButton) {
            generateButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const testType = testConfig.testType;
                
                alert(`正在为项目 ${selectedProject} 生成 ${getTestTypeName(testType)} 测试用例...`);
                // 这里可以实现生成功能，例如根据选择的测试类型生成对应的测试用例
                
                // 模拟生成成功提示
                setTimeout(() => {
                    alert('测试用例生成成功！');
                }, 1000);
            });
        }
        
        // 编辑按钮点击事件
        const editButtons = document.querySelectorAll('.btn-edit');
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const testId = row.cells[0].textContent;
                const testName = row.cells[1].textContent;
                const testSteps = row.cells[2].textContent;
                const result = row.cells[3].textContent;
                
                alert(`编辑测试用例: ID=${testId}, 名称=${testName}, 步骤=${testSteps}, 测试结果=${result}`);
                // 这里可以实现编辑功能，例如打开编辑对话框
            });
        });
        
        // 删除按钮点击事件
        const deleteButtons = document.querySelectorAll('.btn-delete');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('tr');
                const testId = row.cells[0].textContent;
                const testName = row.cells[1].textContent;
                
                if (confirm(`确定要删除测试用例 ${testId}（${testName}）吗？`)) {
                    // 这里可以实现删除功能，例如发送删除请求
                    row.remove();
                }
            });
        });
        
        // 下载按钮点击事件改为执行按钮点击事件
        const executeButton = document.querySelector('.btn-execute');
        if (executeButton) {
            executeButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const testType = testConfig.testType;
                
                // 获取表格中的所有行
                const rows = document.querySelectorAll('.table tbody tr');
                
                // 显示正在执行的提示
                alert(`正在执行 ${selectedProject} 的测试用例...`);
                
                // 模拟执行测试用例
                let successCount = 0;
                let failCount = 0;
                
                // 遍历行，模拟执行测试用例
                rows.forEach((row, index) => {
                    const testId = row.cells[0].textContent;
                    const testName = row.cells[1].textContent;
                    
                    // 模拟测试执行结果（80%成功率）
                    const isSuccess = Math.random() < 0.8;
                    
                    // 根据执行结果更新测试结果单元格
                    const resultCell = row.cells[3];
                    const originalResult = resultCell.textContent;
                    
                    if (isSuccess) {
                        resultCell.textContent = "通过";
                        resultCell.style.color = "#34a853";
                        successCount++;
                    } else {
                        resultCell.textContent = "失败";
                        resultCell.style.color = "#ea4335";
                        failCount++;
                    }
                    
                    // 模拟延迟，实际应用中这里会有真实的测试执行
                    setTimeout(() => {
                        console.log(`执行测试: ${testId} - ${testName} - 结果: ${isSuccess ? '通过' : '失败'}`);
                    }, index * 100);
                });
                
                // 执行完成后显示结果统计
                setTimeout(() => {
                    alert(`测试执行完成！\n通过: ${successCount}\n失败: ${failCount}\n总计: ${rows.length}`);
                }, rows.length * 100 + 500);
            });
        }
        
        // 获取测试类型名称
        function getTestTypeName(testType) {
            const testTypeMap = {
                'unit': '单元测试',
                'integration': '集成测试',
                'functional': '功能测试',
                'performance': '性能测试',
                'security': '安全测试'
            };
            return testTypeMap[testType] || testType;
        }
        
        // 生成测试用例文本内容
        function generateTestcaseContent(projectName, testType) {
            let content = `# ${projectName} - ${getTestTypeName(testType)}测试用例\n`;
            content += `# 生成时间: ${new Date().toLocaleString()}\n\n`;
            
            // 获取表格中的所有行
            const rows = document.querySelectorAll('.table tbody tr');
            
            // 遍历行，收集测试用例信息
            rows.forEach((row, index) => {
                const testId = row.cells[0].textContent;
                const testName = row.cells[1].textContent;
                const testSteps = row.cells[2].textContent;
                const result = row.cells[3].textContent;
                
                // 生成测试用例内容
                content += `## 测试用例 ${testId}: ${testName}\n`;
                content += `- 测试步骤: ${testSteps}\n`;
                content += `- 测试类型: ${getTestTypeName(testType)}\n`;
                content += `- 测试结果: ${result}\n`;
                content += `- 详细步骤:\n`;
                content += `  1. 准备测试环境\n`;
                content += `  2. 执行测试操作\n`;
                content += `  3. 验证测试结果\n`;
                content += `  4. 清理测试环境\n\n`;
            });
            
            return content;
        }
    }
    
    // 功能部署页面的特定功能
    if (window.location.href.includes('deployment.html')) {
        // 当前选择的配置
        let deployConfig = {
            environment: 'dev',
            project: ''
        };
        
        // 部署环境选择下拉框事件
        const environmentSelect = document.querySelector('.environment-select');
        if (environmentSelect) {
            environmentSelect.addEventListener('change', function() {
                deployConfig.environment = this.value;
                console.log('选择了部署环境:', deployConfig.environment);
                updateDeploymentTable(deployConfig.environment, deployConfig.project);
            });
        }
        
        // 项目选择下拉框事件
        const projectSelect = document.querySelector('.project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const selectedProject = this.options[this.selectedIndex].text;
                deployConfig.project = selectedProject;
                console.log('选择了项目:', selectedProject);
                
                // 更新部署表格
                updateDeploymentTable(deployConfig.environment, deployConfig.project);
            });
        }
        
        // 部署按钮点击事件
        const deployButton = document.querySelector('.btn-deploy');
        if (deployButton) {
            deployButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const environment = deployConfig.environment;
                
                // 确认部署
                if (confirm(`确定要将项目 ${selectedProject} 部署到${getEnvironmentName(environment)}吗？`)) {
                    // 显示部署状态
                    const deploymentStatus = document.querySelector('.deployment-status');
                    const statusValue = document.querySelector('.status-value');
                    const progressFill = document.querySelector('.progress-fill');
                    const progressPercentage = document.querySelector('.progress-percentage');
                    
                    deploymentStatus.style.display = 'flex';
                    statusValue.textContent = '部署中...';
                    statusValue.style.color = '#fbbc05';
                    progressFill.style.width = '0%';
                    progressPercentage.textContent = '0%';
                    
                    alert(`正在部署项目 ${selectedProject} 到${getEnvironmentName(environment)}...`);
                    
                    // 模拟部署进度
                    let progress = 0;
                    const progressInterval = setInterval(() => {
                        // 增加进度
                        progress += Math.random() * 10;
                        if (progress > 100) progress = 100;
                        
                        const progressValue = Math.floor(progress);
                        progressFill.style.width = `${progressValue}%`;
                        progressPercentage.textContent = `${progressValue}%`;
                        
                        // 完成部署
                        if (progress >= 100) {
                            clearInterval(progressInterval);
                            
                            // 更新所有模块的状态
                            setTimeout(() => {
                                updateDeploymentTable(environment, selectedProject, true);
                                statusValue.textContent = '部署成功';
                                statusValue.style.color = '#34a853';
                                alert(`项目 ${selectedProject} 已成功部署到${getEnvironmentName(environment)}！`);
                            }, 500);
                        }
                    }, 500);
                    
                    // 模拟部署过程中表格状态更新
                    setTimeout(() => {
                        // 更新所有模块的状态为"部署中"
                        const rows = document.querySelectorAll('.table tbody tr');
                        rows.forEach(row => {
                            const statusCell = row.cells[2];
                            statusCell.textContent = "部署中";
                            statusCell.style.color = "#fbbc05";
                        });
                    }, 1000);
                }
            });
        }
        
        // 测试按钮点击事件(原回滚按钮)
        const testButton = document.querySelector('.btn-test');
        if (testButton) {
            testButton.addEventListener('click', function() {
                const projectSelect = document.querySelector('.project-select');
                if (!projectSelect.value) {
                    alert('请先选择项目');
                    return;
                }
                
                const selectedProject = projectSelect.options[projectSelect.selectedIndex].text;
                const environment = deployConfig.environment;
                
                // 确认测试
                if (confirm(`确定要测试项目 ${selectedProject} 在${getEnvironmentName(environment)}的部署状态吗？`)) {
                    // 显示部署状态
                    const deploymentStatus = document.querySelector('.deployment-status');
                    const statusValue = document.querySelector('.status-value');
                    const progressFill = document.querySelector('.progress-fill');
                    const progressPercentage = document.querySelector('.progress-percentage');
                    
                    deploymentStatus.style.display = 'flex';
                    statusValue.textContent = '测试中...';
                    statusValue.style.color = '#fbbc05';
                    progressFill.style.width = '0%';
                    progressPercentage.textContent = '0%';
                    
                    alert(`正在测试项目 ${selectedProject} 在${getEnvironmentName(environment)}的部署...`);
                    
                    // 模拟测试进度
                    let progress = 0;
                    const progressInterval = setInterval(() => {
                        // 增加进度
                        progress += Math.random() * 15;
                        if (progress > 100) progress = 100;
                        
                        const progressValue = Math.floor(progress);
                        progressFill.style.width = `${progressValue}%`;
                        progressPercentage.textContent = `${progressValue}%`;
                        
                        // 完成测试
                        if (progress >= 100) {
                            clearInterval(progressInterval);
                            
                            // 模拟测试完成
                            setTimeout(() => {
                                // 随机决定测试结果 (80%通过率)
                                const isTestSuccessful = Math.random() < 0.8;
                                
                                // 更新测试状态
                                const rows = document.querySelectorAll('.table tbody tr');
                                rows.forEach((row, index) => {
                                    const statusCell = row.cells[2];
                                    const errorCell = row.cells[3];
                                    
                                    // 随机确定每个用例是否通过
                                    const isTestCasePassed = Math.random() < 0.8;
                                    
                                    if (isTestCasePassed) {
                                        statusCell.textContent = "通过";
                                        statusCell.style.color = "#34a853";
                                        errorCell.textContent = "";
                                    } else {
                                        statusCell.textContent = "失败";
                                        statusCell.style.color = "#ea4335";
                                        errorCell.textContent = "测试失败，请检查日志";
                                    }
                                });
                                
                                // 更新整体状态
                                if (isTestSuccessful) {
                                    statusValue.textContent = '测试通过';
                                    statusValue.style.color = '#34a853';
                                } else {
                                    statusValue.textContent = '测试失败';
                                    statusValue.style.color = '#ea4335';
                                }
                                
                                alert(`项目 ${selectedProject} 在${getEnvironmentName(environment)}的测试已完成！`);
                            }, 500);
                        }
                    }, 300);
                    
                    // 模拟测试过程
                    setTimeout(() => {
                        // 更新所有模块的状态为"测试中"
                        const rows = document.querySelectorAll('.table tbody tr');
                        rows.forEach(row => {
                            const statusCell = row.cells[2];
                            statusCell.textContent = "测试中";
                            statusCell.style.color = "#fbbc05";
                        });
                    }, 1000);
                }
            });
        }
        
        // 更新部署表格
        function updateDeploymentTable(environment, projectName, isDeployed) {
            if (!projectName) return;
            
            const rows = document.querySelectorAll('.table tbody tr');
            
            // 模拟不同环境和项目的数据
            const testCases = [
                { id: 'TC001', failedCase: '登录验证', result: isDeployed ? '通过' : '失败', error: isDeployed ? '' : '验证失败' },
                { id: 'TC002', failedCase: '数据查询', result: isDeployed ? '通过' : '失败', error: isDeployed ? '' : '超时' },
                { id: 'TC003', failedCase: '权限检查', result: '通过', error: '' },
                { id: 'TC004', failedCase: '报表生成', result: isDeployed ? '通过' : '失败', error: isDeployed ? '' : '格式错误' },
                { id: 'TC005', failedCase: '数据导出', result: '通过', error: '' }
            ];
            
            // 更新表格内容
            rows.forEach((row, index) => {
                if (index < testCases.length) {
                    row.cells[0].textContent = testCases[index].id;
                    row.cells[1].textContent = testCases[index].failedCase;
                    row.cells[2].textContent = testCases[index].result;
                    row.cells[3].textContent = testCases[index].error;
                    
                    // 根据结果设置颜色
                    if (testCases[index].result === '通过') {
                        row.cells[2].style.color = '#34a853';
                    } else if (testCases[index].result === '失败') {
                        row.cells[2].style.color = '#ea4335';
                    } else if (testCases[index].result === '部署中' || testCases[index].result === '回滚中') {
                        row.cells[2].style.color = '#fbbc05';
                    } else if (testCases[index].result === '已回滚') {
                        row.cells[2].style.color = '#ea4335';
                    }
                }
            });
        }
        
        // 格式化日期
        function formatDate(date) {
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
        
        // 获取环境名称
        function getEnvironmentName(env) {
            const envMap = {
                'dev': '开发环境',
                'test': '测试环境',
                'staging': '预发布环境',
                'prod': '生产环境'
            };
            return envMap[env] || env;
        }
    }
    
    // 生成模块代码的函数
    function generateModuleCode(projectName, language, moduleType) {
        let code = '';
        
        if (language === 'java') {
            switch(moduleType) {
                case 'dao':
                    code = `package ${projectName.toLowerCase()}.dao;

import ${projectName.toLowerCase()}.model.User;
import java.util.List;
import java.util.Optional;

/**
 * 用户数据访问接口
 */
public interface UserDao {
    /**
     * 保存用户
     * @param user 用户信息
     * @return 保存后的用户ID
     */
    Long save(User user);
    
    /**
     * 根据ID查询用户
     * @param id 用户ID
     * @return 用户信息
     */
    Optional<User> findById(Long id);
    
    /**
     * 查询所有用户
     * @return 用户列表
     */
    List<User> findAll();
    
    /**
     * 更新用户信息
     * @param user 用户信息
     * @return 是否更新成功
     */
    boolean update(User user);
    
    /**
     * 根据ID删除用户
     * @param id 用户ID
     * @return 是否删除成功
     */
    boolean deleteById(Long id);
}`;
                    break;
                case 'service':
                    code = `package ${projectName.toLowerCase()}.service;

import ${projectName.toLowerCase()}.dao.UserDao;
import ${projectName.toLowerCase()}.model.User;
import java.util.List;
import java.util.Optional;

/**
 * 用户服务实现类
 */
public class UserServiceImpl implements UserService {
    private final UserDao userDao;
    
    public UserServiceImpl(UserDao userDao) {
        this.userDao = userDao;
    }
    
    @Override
    public User createUser(User user) {
        Long id = userDao.save(user);
        return userDao.findById(id).orElseThrow(() -> 
            new RuntimeException("Failed to create user"));
    }
    
    @Override
    public User getUserById(Long id) {
        return userDao.findById(id).orElseThrow(() -> 
            new RuntimeException("User not found with id: " + id));
    }
    
    @Override
    public List<User> getAllUsers() {
        return userDao.findAll();
    }
    
    @Override
    public User updateUser(User user) {
        boolean updated = userDao.update(user);
        if (!updated) {
            throw new RuntimeException("Failed to update user with id: " + user.getId());
        }
        return getUserById(user.getId());
    }
    
    @Override
    public void deleteUser(Long id) {
        boolean deleted = userDao.deleteById(id);
        if (!deleted) {
            throw new RuntimeException("Failed to delete user with id: " + id);
        }
    }
}`;
                    break;
                case 'controller':
                    code = `package ${projectName.toLowerCase()}.controller;

import ${projectName.toLowerCase()}.model.User;
import ${projectName.toLowerCase()}.service.UserService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 用户控制器
 */
@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User createdUser = userService.createUser(user);
        return new ResponseEntity<>(createdUser, HttpStatus.CREATED);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        User updatedUser = userService.updateUser(user);
        return ResponseEntity.ok(updatedUser);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}`;
                    break;
                case 'util':
                    code = `package ${projectName.toLowerCase()}.util;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

/**
 * 通用工具类
 */
public class CommonUtils {
    
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    
    /**
     * 生成UUID
     * @return UUID字符串
     */
    public static String generateUUID() {
        return UUID.randomUUID().toString().replace("-", "");
    }
    
    /**
     * 格式化日期
     * @param date 日期对象
     * @return 格式化后的字符串
     */
    public static String formatDate(Date date) {
        return DATE_FORMAT.format(date);
    }
    
    /**
     * 获取当前时间戳
     * @return 当前时间戳
     */
    public static long getCurrentTimestamp() {
        return System.currentTimeMillis();
    }
    
    /**
     * MD5加密
     * @param input 输入字符串
     * @return 加密后的字符串
     */
    public static String md5(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(input.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not found", e);
        }
    }
    
    /**
     * 检查字符串是否为空
     * @param str 待检查的字符串
     * @return 是否为空
     */
    public static boolean isEmpty(String str) {
        return str == null || str.trim().isEmpty();
    }
}`;
                    break;
            }
        } else if (language === 'python') {
            // Python代码生成
            switch(moduleType) {
                case 'dao':
                    code = `# ${projectName} DAO Layer
from typing import List, Optional
from models.user import User
import sqlite3

class UserDAO:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def save(self, user: User) -> int:
        """保存用户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (user.username, user.email, user.password)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
            
    def find_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, username, email, password FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return User(id=row[0], username=row[1], email=row[2], password=row[3])
            return None
        finally:
            conn.close()
            
    def find_all(self) -> List[User]:
        """查询所有用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, username, email, password FROM users")
            rows = cursor.fetchall()
            
            return [User(id=row[0], username=row[1], email=row[2], password=row[3]) for row in rows]
        finally:
            conn.close()
            
    def update(self, user: User) -> bool:
        """更新用户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?",
                (user.username, user.email, user.password, user.id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
            
    def delete_by_id(self, user_id: int) -> bool:
        """根据ID删除用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()`;
                    break;
                // 其他Python模块类型的代码实现
                // ... 可以类似Java添加更多类型
            }
        } else if (language === 'javascript') {
            // JavaScript代码生成
            switch(moduleType) {
                case 'dao':
                    code = `// ${projectName} - User Data Access Layer
const db = require('../config/database');

class UserDAO {
  /**
   * 创建用户
   * @param {Object} user - 用户信息
   * @returns {Promise<Object>} - 创建的用户
   */
  async create(user) {
    try {
      const result = await db.query(
        'INSERT INTO users (username, email, password) VALUES ($1, $2, $3) RETURNING *',
        [user.username, user.email, user.password]
      );
      return result.rows[0];
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  }

  /**
   * 根据ID查询用户
   * @param {number} id - 用户ID
   * @returns {Promise<Object>} - 用户信息
   */
  async findById(id) {
    try {
      const result = await db.query('SELECT * FROM users WHERE id = $1', [id]);
      return result.rows[0];
    } catch (error) {
      console.error('Error finding user by ID:', error);
      throw error;
    }
  }

  /**
   * 查询所有用户
   * @returns {Promise<Array>} - 用户列表
   */
  async findAll() {
    try {
      const result = await db.query('SELECT * FROM users');
      return result.rows;
    } catch (error) {
      console.error('Error finding all users:', error);
      throw error;
    }
  }

  /**
   * 更新用户
   * @param {number} id - 用户ID
   * @param {Object} user - 更新的用户信息
   * @returns {Promise<Object>} - 更新后的用户
   */
  async update(id, user) {
    try {
      const result = await db.query(
        'UPDATE users SET username = $1, email = $2, password = $3 WHERE id = $4 RETURNING *',
        [user.username, user.email, user.password, id]
      );
      return result.rows[0];
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  }

  /**
   * 删除用户
   * @param {number} id - 用户ID
   * @returns {Promise<boolean>} - 是否删除成功
   */
  async delete(id) {
    try {
      const result = await db.query('DELETE FROM users WHERE id = $1', [id]);
      return result.rowCount > 0;
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  }
}

module.exports = new UserDAO();`;
                    break;
                // 其他JavaScript模块类型的代码实现
            }
        } else if (language === 'csharp') {
            // C#代码生成
            switch(moduleType) {
                case 'dao':
                    code = `using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Threading.Tasks;
using ${projectName}.Models;

namespace ${projectName}.DataAccess
{
    /// <summary>
    /// 用户数据访问层
    /// </summary>
    public class UserRepository : IUserRepository
    {
        private readonly string _connectionString;

        public UserRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        /// <summary>
        /// 创建用户
        /// </summary>
        /// <param name="user">用户实体</param>
        /// <returns>创建后的用户ID</returns>
        public async Task<int> CreateAsync(User user)
        {
            using (var connection = new SqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SqlCommand(
                    "INSERT INTO Users (Username, Email, Password, CreatedAt) " +
                    "VALUES (@Username, @Email, @Password, @CreatedAt); " +
                    "SELECT SCOPE_IDENTITY();", connection);

                command.Parameters.AddWithValue("@Username", user.Username);
                command.Parameters.AddWithValue("@Email", user.Email);
                command.Parameters.AddWithValue("@Password", user.Password);
                command.Parameters.AddWithValue("@CreatedAt", DateTime.UtcNow);

                return Convert.ToInt32(await command.ExecuteScalarAsync());
            }
        }

        /// <summary>
        /// 获取用户信息
        /// </summary>
        /// <param name="id">用户ID</param>
        /// <returns>用户实体</returns>
        public async Task<User> GetByIdAsync(int id)
        {
            using (var connection = new SqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SqlCommand(
                    "SELECT Id, Username, Email, Password, CreatedAt FROM Users WHERE Id = @Id", connection);
                command.Parameters.AddWithValue("@Id", id);

                using (var reader = await command.ExecuteReaderAsync())
                {
                    if (await reader.ReadAsync())
                    {
                        return new User
                        {
                            Id = reader.GetInt32(0),
                            Username = reader.GetString(1),
                            Email = reader.GetString(2),
                            Password = reader.GetString(3),
                            CreatedAt = reader.GetDateTime(4)
                        };
                    }
                    return null;
                }
            }
        }

        /// <summary>
        /// 获取所有用户
        /// </summary>
        /// <returns>用户列表</returns>
        public async Task<IEnumerable<User>> GetAllAsync()
        {
            var users = new List<User>();
            using (var connection = new SqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SqlCommand(
                    "SELECT Id, Username, Email, Password, CreatedAt FROM Users", connection);

                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        users.Add(new User
                        {
                            Id = reader.GetInt32(0),
                            Username = reader.GetString(1),
                            Email = reader.GetString(2),
                            Password = reader.GetString(3),
                            CreatedAt = reader.GetDateTime(4)
                        });
                    }
                }
            }
            return users;
        }

        /// <summary>
        /// 更新用户信息
        /// </summary>
        /// <param name="user">用户实体</param>
        /// <returns>是否更新成功</returns>
        public async Task<bool> UpdateAsync(User user)
        {
            using (var connection = new SqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SqlCommand(
                    "UPDATE Users SET Username = @Username, Email = @Email, Password = @Password " +
                    "WHERE Id = @Id", connection);

                command.Parameters.AddWithValue("@Id", user.Id);
                command.Parameters.AddWithValue("@Username", user.Username);
                command.Parameters.AddWithValue("@Email", user.Email);
                command.Parameters.AddWithValue("@Password", user.Password);

                return await command.ExecuteNonQueryAsync() > 0;
            }
        }

        /// <summary>
        /// 删除用户
        /// </summary>
        /// <param name="id">用户ID</param>
        /// <returns>是否删除成功</returns>
        public async Task<bool> DeleteAsync(int id)
        {
            using (var connection = new SqlConnection(_connectionString))
            {
                await connection.OpenAsync();
                var command = new SqlCommand("DELETE FROM Users WHERE Id = @Id", connection);
                command.Parameters.AddWithValue("@Id", id);

                return await command.ExecuteNonQueryAsync() > 0;
            }
        }
    }

    // 视图
    public class UserView
    {
        public void ShowUserDetails(User user)
        {
            if (user != null)
            {
                Console.WriteLine("User Details:");
                Console.WriteLine($"ID: {user.Id}");
                Console.WriteLine($"Username: {user.Username}");
                Console.WriteLine($"Email: {user.Email}");
            }
            else
            {
                Console.WriteLine("User not found.");
            }
        }

        public void ShowAllUsers(List<User> users)
        {
            if (users.Any())
            {
                Console.WriteLine("User List:");
                foreach (var user in users)
                {
                    Console.WriteLine($"{user.Id}. {user.Username} - {user.Email}");
                }
            }
            else
            {
                Console.WriteLine("No users found.");
            }
        }

        public void ShowMessage(string message)
        {
            Console.WriteLine(message);
        }
    }

    // 控制器
    public class UserController
    {
        private readonly UserRepository _repository;
        private readonly UserView _view;

        public UserController(UserRepository repository, UserView view)
        {
            _repository = repository;
            _view = view;
        }

        public void CreateUser(int id, string username, string email)
        {
            var user = new User(id, username, email);
            _repository.Add(user);
            _view.ShowMessage($"User {username} created successfully.");
        }

        public void ShowUser(int id)
        {
            var user = _repository.GetById(id);
            _view.ShowUserDetails(user);
        }

        public void ShowAllUsers()
        {
            var users = _repository.GetAll();
            _view.ShowAllUsers(users);
        }

        public void UpdateUser(int id, string username = null, string email = null)
        {
            bool success = _repository.Update(id, username, email);
            if (success)
            {
                _view.ShowMessage($"User with ID {id} updated successfully.");
                ShowUser(id);
            }
            else
            {
                _view.ShowMessage($"Failed to update: User with ID {id} not found.");
            }
        }

        public void DeleteUser(int id)
        {
            bool success = _repository.Delete(id);
            if (success)
            {
                _view.ShowMessage($"User with ID {id} deleted successfully.");
            }
            else
            {
                _view.ShowMessage($"Failed to delete: User with ID {id} not found.");
            }
        }
    }

    // 主程序
    class Program
    {
        static void Main(string[] args)
        {
            // 初始化 MVC 组件
            var repository = new UserRepository();
            var view = new UserView();
            var controller = new UserController(repository, view);

            // 创建用户
            controller.CreateUser(1, "admin", "admin@example.com");
            controller.CreateUser(2, "user1", "user1@example.com");

            // 显示所有用户
            controller.ShowAllUsers();

            // 更新用户
            controller.UpdateUser(1, email: "newemail@example.com");

            // 显示特定用户
            controller.ShowUser(1);

            // 删除用户
            controller.DeleteUser(2);

            // 再次显示所有用户
            controller.ShowAllUsers();

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}`;
                    break;
                // 其他C#模块类型的代码实现
            }
        }
        
        return code || `// ${projectName} ${moduleType} 模块代码生成中...`;
    }
    
    // 生成Java MVC架构代码
    function generateJavaMVCCode(projectName) {
        return `/**
 * ${projectName} - 自动生成的Java MVC架构代码
 * 生成时间: ${new Date().toLocaleString()}
 */

package com.example.${projectName.toLowerCase().replace(/\s+/g, '')};

import java.util.ArrayList;
import java.util.List;

// 主应用类
public class Application {
    public static void main(String[] args) {
        System.out.println("启动 ${projectName} 应用");
        
        // 初始化组件
        DatabaseConnection db = new DatabaseConnection();
        UserService userService = new UserService(db);
        
        // 应用逻辑
        User admin = new User(1, "admin", "admin@example.com");
        userService.saveUser(admin);
        
        List<User> users = userService.getAllUsers();
        for (User user : users) {
            System.out.println(user);
        }
    }
}

// 数据库连接类
class DatabaseConnection {
    public void connect() {
        System.out.println("连接到数据库");
    }
    
    public void disconnect() {
        System.out.println("断开数据库连接");
    }
    
    public void executeQuery(String query) {
        System.out.println("执行查询: " + query);
    }
}

// 用户模型
class User {
    private int id;
    private String username;
    private String email;
    
    public User(int id, String username, String email) {
        this.id = id;
        this.username = username;
        this.email = email;
    }
    
    // Getters and Setters
    public int getId() { return id; }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    
    @Override
    public String toString() {
        return "User{id=" + id + ", username='" + username + "', email='" + email + "'}";
    }
}

// 用户服务类
class UserService {
    private DatabaseConnection db;
    private List<User> users = new ArrayList<>();
    
    public UserService(DatabaseConnection db) {
        this.db = db;
    }
    
    public void saveUser(User user) {
        users.add(user);
        db.executeQuery("INSERT INTO users VALUES (" + user.getId() + ", '" + user.getUsername() + "', '" + user.getEmail() + "')");
    }
    
    public List<User> getAllUsers() {
        return users;
    }
}`;
    }
    
    // 生成Java微服务架构代码
    function generateJavaMicroservicesCode(projectName) {
        return `/**
 * ${projectName} - 自动生成的Java微服务架构代码
 * 生成时间: ${new Date().toLocaleString()}
 */

package com.example.${projectName.toLowerCase().replace(/\s+/g, '')};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.web.bind.annotation.*;

// 服务注册中心
@SpringBootApplication
@EnableEurekaServer
public class ServiceRegistry {
    public static void main(String[] args) {
        SpringApplication.run(ServiceRegistry.class, args);
    }
}

// 用户服务
@SpringBootApplication
@EnableEurekaClient
public class UserService {
    public static void main(String[] args) {
        SpringApplication.run(UserService.class, args);
    }
}

@RestController
@RequestMapping("/users")
class UserController {
    @Autowired
    private UserRepository userRepository;
    
    @GetMapping
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userRepository.findById(id).orElseThrow(() -> new UserNotFoundException(id));
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userRepository.save(user);
    }
}

// 订单服务
@SpringBootApplication
@EnableEurekaClient
public class OrderService {
    public static void main(String[] args) {
        SpringApplication.run(OrderService.class, args);
    }
}

@RestController
@RequestMapping("/orders")
class OrderController {
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private UserServiceClient userServiceClient;
    
    @GetMapping
    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }
    
    @GetMapping("/{id}")
    public Order getOrderById(@PathVariable Long id) {
        return orderRepository.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    }
    
    @PostMapping
    public Order createOrder(@RequestBody Order order) {
        // 调用用户服务验证用户
        User user = userServiceClient.getUserById(order.getUserId());
        if (user == null) {
            throw new UserNotFoundException(order.getUserId());
        }
        
        return orderRepository.save(order);
    }
}

// API网关
@SpringBootApplication
@EnableDiscoveryClient
@EnableZuulProxy
public class ApiGateway {
    public static void main(String[] args) {
        SpringApplication.run(ApiGateway.class, args);
    }
}`;
    }
    
    // 生成Python代码
    function generatePythonCode(projectName, architecture) {
        if (architecture === 'microservices') {
            return `"""
${projectName} - 自动生成的Python微服务架构代码
生成时间: ${new Date().toLocaleString()}
"""

# 使用Flask和Flask-RESTful构建微服务

# 用户服务
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import json

app = Flask(__name__)
api = Api(app)

# 模拟数据库
users = [
    {"id": 1, "username": "admin", "email": "admin@example.com"}
]

class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = next((user for user in users if user["id"] == user_id), None)
            if user:
                return jsonify(user)
            return {"message": "User not found"}, 404
        return jsonify(users)
    
    def post(self):
        data = request.get_json()
        new_user = {
            "id": len(users) + 1,
            "username": data["username"],
            "email": data["email"]
        }
        users.append(new_user)
        return jsonify(new_user), 201

api.add_resource(UserResource, '/users', '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)`;
        } else {
            return `"""
${projectName} - 自动生成的Python MVC架构代码
生成时间: ${new Date().toLocaleString()}
"""

# 模型层
class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
    
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"

class UserModel:
    def __init__(self):
        # 模拟数据库
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
        return user
    
    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_all_users(self):
        return self.users
    
    def update_user(self, user_id, username=None, email=None):
        user = self.get_user_by_id(user_id)
        if user:
            if username:
                user.username = username
            if email:
                user.email = email
            return user
        return None
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.users.remove(user)
            return True
        return False`;
        }
    }
    
    // 生成JavaScript代码
    function generateJavaScriptCode(projectName, architecture) {
        return `/**
 * ${projectName} - 自动生成的JavaScript ${architecture.toUpperCase()} 架构代码
 * 生成时间: ${new Date().toLocaleString()}
 */

// 模型层
class UserModel {
    constructor(id, username, email) {
        this.id = id;
        this.username = username;
        this.email = email;
    }
}

// 用户数据存储
class UserStore {
    constructor() {
        this.users = [];
    }
    
    addUser(user) {
        this.users.push(user);
        return user;
    }
    
    getUserById(id) {
        return this.users.find(user => user.id === id);
    }
    
    getAllUsers() {
        return this.users;
    }
    
    updateUser(id, userData) {
        const userIndex = this.users.findIndex(user => user.id === id);
        if (userIndex !== -1) {
            this.users[userIndex] = {...this.users[userIndex], ...userData};
            return this.users[userIndex];
        }
        return null;
    }
    
    deleteUser(id) {
        const userIndex = this.users.findIndex(user => user.id === id);
        if (userIndex !== -1) {
            this.users.splice(userIndex, 1);
            return true;
        }
        return false;
    }
}`;
    }
    
    // 生成C#代码
    function generateCSharpCode(projectName, architecture) {
        return `/**
 * ${projectName} - 自动生成的C# ${architecture.toUpperCase()} 架构代码
 * 生成时间: ${new Date().toLocaleString()}
 */

using System;
using System.Collections.Generic;
using System.Linq;

namespace ${projectName.replace(/\s+/g, '')}
{
    // 模型
    public class User
    {
        public int Id { get; set; }
        public string Username { get; set; }
        public string Email { get; set; }

        public User(int id, string username, string email)
        {
            Id = id;
            Username = username;
            Email = email;
        }

        public override string ToString()
        {
            return $"User {{ Id = {Id}, Username = {Username}, Email = {Email} }}";
        }
    }

    // 数据访问层
    public class UserRepository
    {
        private List<User> _users = new List<User>();

        public void Add(User user)
        {
            _users.Add(user);
        }

        public User GetById(int id)
        {
            return _users.FirstOrDefault(u => u.Id == id);
        }

        public List<User> GetAll()
        {
            return _users;
        }

        public bool Update(int id, string username = null, string email = null)
        {
            var user = GetById(id);
            if (user == null)
                return false;

            if (username != null)
                user.Username = username;

            if (email != null)
                user.Email = email;

            return true;
        }

        public bool Delete(int id)
        {
            var user = GetById(id);
            if (user == null)
                return false;

            _users.Remove(user);
            return true;
        }
    }

    // 视图
    public class UserView
    {
        public void ShowUserDetails(User user)
        {
            if (user != null)
            {
                Console.WriteLine("User Details:");
                Console.WriteLine($"ID: {user.Id}");
                Console.WriteLine($"Username: {user.Username}");
                Console.WriteLine($"Email: {user.Email}");
            }
            else
            {
                Console.WriteLine("User not found.");
            }
        }

        public void ShowAllUsers(List<User> users)
        {
            if (users.Any())
            {
                Console.WriteLine("User List:");
                foreach (var user in users)
                {
                    Console.WriteLine($"{user.Id}. {user.Username} - {user.Email}");
                }
            }
            else
            {
                Console.WriteLine("No users found.");
            }
        }

        public void ShowMessage(string message)
        {
            Console.WriteLine(message);
        }
    }

    // 控制器
    public class UserController
    {
        private readonly UserRepository _repository;
        private readonly UserView _view;

        public UserController(UserRepository repository, UserView view)
        {
            _repository = repository;
            _view = view;
        }

        public void CreateUser(int id, string username, string email)
        {
            var user = new User(id, username, email);
            _repository.Add(user);
            _view.ShowMessage($"User {username} created successfully.");
        }

        public void ShowUser(int id)
        {
            var user = _repository.GetById(id);
            _view.ShowUserDetails(user);
        }

        public void ShowAllUsers()
        {
            var users = _repository.GetAll();
            _view.ShowAllUsers(users);
        }

        public void UpdateUser(int id, string username = null, string email = null)
        {
            bool success = _repository.Update(id, username, email);
            if (success)
            {
                _view.ShowMessage($"User with ID {id} updated successfully.");
                ShowUser(id);
            }
            else
            {
                _view.ShowMessage($"Failed to update: User with ID {id} not found.");
            }
        }

        public void DeleteUser(int id)
        {
            bool success = _repository.Delete(id);
            if (success)
            {
                _view.ShowMessage($"User with ID {id} deleted successfully.");
            }
            else
            {
                _view.ShowMessage($"Failed to delete: User with ID {id} not found.");
            }
        }
    }

    // 主程序
    class Program
    {
        static void Main(string[] args)
        {
            // 初始化 MVC 组件
            var repository = new UserRepository();
            var view = new UserView();
            var controller = new UserController(repository, view);

            // 创建用户
            controller.CreateUser(1, "admin", "admin@example.com");
            controller.CreateUser(2, "user1", "user1@example.com");

            // 显示所有用户
            controller.ShowAllUsers();

            // 更新用户
            controller.UpdateUser(1, email: "newemail@example.com");

            // 显示特定用户
            controller.ShowUser(1);

            // 删除用户
            controller.DeleteUser(2);

            // 再次显示所有用户
            controller.ShowAllUsers();

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
    }
}`;
    }
}); 