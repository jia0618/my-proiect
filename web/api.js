/**
 * API接口模块
 * 用于与后端服务通信的工具函数
 */

// 基础URL，在生产环境中修改为真实的API地址
const BASE_URL = '';

/**
 * 发送API请求的通用方法
 * @param {string} url - API端点
 * @param {string} method - HTTP方法 (GET, POST, PUT, DELETE)
 * @param {object} data - 请求体数据 (可选)
 * @returns {Promise} - 返回Promise对象
 */
async function apiRequest(url, method, data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // 获取存储的token (如果有)
    const token = localStorage.getItem('token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers,
        credentials: 'include' // 包含cookies
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const fullUrl = `${BASE_URL}${url}`;
    console.log(`[API] 发送${method}请求: ${fullUrl}`, options);
    
    try {
        console.log(`[API] 开始获取: ${fullUrl}`);
        const response = await fetch(fullUrl, options);
        console.log(`[API] ${method}请求响应状态: ${response.status} ${response.statusText}`, response);
        
        // 检查响应是否为JSON格式
        const contentType = response.headers.get('content-type');
        console.log(`[API] 响应内容类型: ${contentType}`);
        
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error(`[API] 非JSON响应内容: ${textResponse}`);
            throw new Error(`服务器返回了非JSON格式的响应: ${contentType || '无内容类型'}`);
        }
        
        const responseData = await response.json();
        console.log(`[API] ${method}请求响应数据:`, responseData);
        
        // 检查响应状态
        if (!response.ok) {
            console.error(`[API] 请求失败: ${response.status} ${response.statusText}`, responseData);
            throw new Error(responseData.message || `请求失败: ${response.status} ${response.statusText}`);
        }
        
        return responseData;
    } catch (error) {
        console.error(`[API] 请求错误 (${method} ${url}):`, error);
        throw error;
    }
}

// ==== 用户认证相关 API ====
const AuthAPI = {
    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} - 返回Promise对象
     */
    login: (username, password) => {
        return apiRequest('/api/login', 'POST', { username, password });
    },
    
    /**
     * 用户注册
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @param {string} email - 邮箱
     * @returns {Promise} - 返回Promise对象
     */
    register: (username, password, email) => {
        return apiRequest('/api/register', 'POST', { username, password, email });
    },
    
    /**
     * 用户登出
     * @returns {Promise} - 返回Promise对象
     */
    logout: () => {
        return apiRequest('/api/logout', 'GET');
    }
};

// ==== 项目相关 API ====
const ProjectAPI = {
    /**
     * 获取所有项目
     * @returns {Promise} - 返回Promise对象
     */
    listProjects: () => {
        return apiRequest('/project/api/list', 'GET');
    },
    
    /**
     * 创建新项目
     * @param {string} name - 项目名称
     * @param {string} description - 项目描述
     * @returns {Promise} - 返回Promise对象
     */
    createProject: (name, description) => {
        return apiRequest('/project/api/create', 'POST', { name, description });
    },
    
    /**
     * 获取项目详情
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    getProject: (projectId) => {
        return apiRequest(`/project/api/${projectId}`, 'GET');
    },
    
    /**
     * 更新项目
     * @param {number} projectId - 项目ID
     * @param {object} data - 更新数据
     * @returns {Promise} - 返回Promise对象
     */
    updateProject: (projectId, data) => {
        return apiRequest(`/project/api/${projectId}`, 'PUT', data);
    },
    
    /**
     * 删除项目
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    deleteProject: (projectId) => {
        console.log(`API.Project.deleteProject 调用: projectId=${projectId}`);
        // 确保projectId是整数
        const id = parseInt(projectId, 10);
        
        // 检查ID是否有效
        if (isNaN(id) || id <= 0) {
            console.error('无效的项目ID:', projectId);
            return Promise.reject(new Error('无效的项目ID'));
        }
        
        // 发送删除请求
        return apiRequest(`/project/api/${id}`, 'DELETE');
    }
};

// ==== 需求相关 API ====
const RequirementAPI = {
    /**
     * 获取项目的需求列表
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    listRequirements: (projectId) => {
        return apiRequest(`/requirement/api/${projectId}`, 'GET');
    },
    
    /**
     * 创建需求
     * @param {number} projectId - 项目ID
     * @param {string} content - 需求内容
     * @param {string} requirementType - 需求类型
     * @param {number} priority - 优先级
     * @returns {Promise} - 返回Promise对象
     */
    createRequirement: (projectId, content, requirementType, priority) => {
        return apiRequest(`/requirement/api/${projectId}/create`, 'POST', {
            content,
            requirement_type: requirementType,
            priority
        });
    },
    
    /**
     * 更新需求
     * @param {number} requirementId - 需求ID
     * @param {object} data - 更新数据
     * @returns {Promise} - 返回Promise对象
     */
    updateRequirement: (requirementId, data) => {
        return apiRequest(`/requirement/api/${requirementId}`, 'PUT', data);
    },
    
    /**
     * 删除需求
     * @param {number} requirementId - 需求ID
     * @returns {Promise} - 返回Promise对象
     */
    deleteRequirement: (requirementId) => {
        return apiRequest(`/requirement/api/${requirementId}`, 'DELETE');
    }
};

// ==== 架构代码相关 API ====
const ArchitectureAPI = {
    /**
     * 获取项目的架构代码
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    getArchitecture: (projectId) => {
        return apiRequest(`/architecture/api/${projectId}`, 'GET');
    },
    
    /**
     * 生成架构代码
     * @param {number} projectId - 项目ID
     * @param {string} language - 编程语言
     * @param {string} architectureType - 架构类型
     * @returns {Promise} - 返回Promise对象
     */
    generateArchitecture: (projectId, language, architectureType) => {
        return apiRequest(`/architecture/api/${projectId}/generate`, 'POST', {
            language,
            architecture_type: architectureType
        });
    }
};

// ==== 数据库设计相关 API ====
const DatabaseAPI = {
    /**
     * 获取项目的数据库设计
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    getDatabaseDesign: (projectId) => {
        return apiRequest(`/database/api/${projectId}`, 'GET');
    },
    
    /**
     * 生成数据库设计
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    generateDatabaseDesign: (projectId) => {
        return apiRequest(`/database/api/${projectId}/generate`, 'POST', {});
    },
    
    /**
     * 更新数据库脚本
     * @param {number} projectId - 项目ID
     * @param {string} script - 数据库脚本
     * @param {string} tables - 表结构
     * @param {string} relationships - 关系定义
     * @returns {Promise} - 返回Promise对象
     */
    updateDatabaseScript: (projectId, script, tables = '', relationships = '') => {
        return apiRequest(`/database/api/${projectId}/update`, 'PUT', {
            script,
            tables,
            relationships
        });
    },
    
    /**
     * 获取数据库表的SQL导出脚本
     * @param {number} projectId - 项目ID
     * @param {string} dbType - 数据库类型 (mysql, postgresql, oracle, sqlserver等)
     * @returns {Promise} - 返回Promise对象，包含SQL文件内容
     */
    getDatabaseSQLExport: (projectId, dbType) => {
        // 使用已有的获取数据库设计API，不再尝试调用不存在的export接口
        return apiRequest(`/database/api/${projectId}`, 'GET')
            .then(response => {
                if (response.success && response.database_design && response.database_design.script) {
                    return {
                        success: true,
                        sql_content: response.database_design.script,
                        database_type: dbType
                    };
                } else {
                    return {
                        success: false,
                        message: '无法获取SQL内容，请先生成数据库设计'
                    };
                }
            });
    },
    
    /**
     * 获取数据库SQL文件的下载URL (注：此方法生成前端下载URL，实际不调用后端)
     * @param {number} projectId - 项目ID
     * @param {string} dbType - 数据库类型
     * @returns {string} - 返回下载URL
     */
    getDownloadUrl: (projectId, dbType) => {
        // 前端不再依赖后端下载接口
        return '#'; // 返回一个占位符，实际由前端处理
    }
};

// ==== 模块代码相关 API ====
const ModuleAPI = {
    /**
     * 获取项目的模块列表
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    listModules: (projectId) => {
        return apiRequest(`/module/api/${projectId}`, 'GET');
    },
    
    /**
     * 获取模块详情
     * @param {number} moduleId - 模块ID
     * @returns {Promise} - 返回Promise对象
     */
    getModuleDetail: (moduleId) => {
        return apiRequest(`/module/api/${moduleId}/detail`, 'GET');
    },
    
    /**
     * 生成模块代码
     * @param {number} projectId - 项目ID
     * @param {string} moduleName - 模块名称
     * @param {string} moduleType - 模块类型
     * @param {string} language - 编程语言
     * @param {string} dependencies - 依赖项
     * @returns {Promise} - 返回Promise对象
     */
    generateModule: (projectId, moduleName, moduleType, language, dependencies = '') => {
        console.log(`API.Module.generateModule 调用: projectId=${projectId}, name=${moduleName}, type=${moduleType}, language=${language}`);
        return apiRequest(`/module/api/${projectId}/generate`, 'POST', {
            module_name: moduleName,
            module_type: moduleType,
            language: language,
            dependencies: dependencies
        });
    },
    
    /**
     * 更新模块
     * @param {number} moduleId - 模块ID
     * @param {object} data - 更新数据
     * @returns {Promise} - 返回Promise对象
     */
    updateModule: (moduleId, data) => {
        return apiRequest(`/module/api/${moduleId}`, 'PUT', data);
    },
    
    /**
     * 删除模块
     * @param {number} moduleId - 模块ID
     * @returns {Promise} - 返回Promise对象
     */
    deleteModule: (moduleId) => {
        return apiRequest(`/module/api/${moduleId}`, 'DELETE');
    }
};

// ==== 测试用例相关 API ====
const TestAPI = {
    /**
     * 获取项目的测试用例列表
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    listTestCases: (projectId) => {
        return apiRequest(`/test/api/${projectId}`, 'GET');
    },
    
    /**
     * 获取测试用例详情
     * @param {number} testId - 测试用例ID
     * @returns {Promise} - 返回Promise对象
     */
    getTestDetail: (testId) => {
        return apiRequest(`/test/api/${testId}/detail`, 'GET');
    },
    
    /**
     * 生成测试用例
     * @param {number} projectId - 项目ID
     * @param {string} testName - 测试名称
     * @param {string} testType - 测试类型
     * @param {number} testCount - 生成的测试用例数量
     * @param {number} moduleId - 模块ID (可选)
     * @returns {Promise} - 返回Promise对象
     */
    generateTestCase: (projectId, testName, testType, testCount = 3, moduleId = null) => {
        return apiRequest(`/test/api/${projectId}/generate`, 'POST', {
            test_name: testName,
            test_type: testType,
            test_count: testCount,
            module_id: moduleId
        });
    },
    
    /**
     * 更新测试用例
     * @param {number} testId - 测试用例ID
     * @param {object} data - 更新数据
     * @returns {Promise} - 返回Promise对象
     */
    updateTestCase: (testId, data) => {
        return apiRequest(`/test/api/${testId}/update`, 'PUT', data);
    },
    
    /**
     * 执行测试用例
     * @param {number} testId - 测试用例ID
     * @returns {Promise} - 返回Promise对象
     */
    executeTestCase: (testId) => {
        return apiRequest(`/test/api/${testId}/execute`, 'POST');
    },
    
    /**
     * 删除测试用例
     * @param {number} testId - 测试用例ID
     * @returns {Promise} - 返回Promise对象
     */
    deleteTestCase: (testId) => {
        return apiRequest(`/test/api/${testId}`, 'DELETE');
    }
};

// ==== 部署相关 API ====
const DeploymentAPI = {
    /**
     * 获取项目的部署信息
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    getDeployment: (projectId) => {
        return apiRequest(`/deployment/api/${projectId}`, 'GET');
    },
    
    /**
     * 生成部署步骤
     * @param {number} projectId - 项目ID
     * @param {string} environment - 部署环境
     * @returns {Promise} - 返回Promise对象
     */
    generateDeployment: (projectId, environment) => {
        return apiRequest(`/deployment/api/${projectId}/generate`, 'POST', {
            environment
        });
    },
    
    /**
     * 执行部署
     * @param {number} projectId - 项目ID
     * @returns {Promise} - 返回Promise对象
     */
    executeDeployment: (projectId) => {
        return apiRequest(`/deployment/api/${projectId}/execute`, 'POST');
    },
    
    /**
     * 更新部署配置
     * @param {number} projectId - 项目ID
     * @param {object} data - 更新数据
     * @returns {Promise} - 返回Promise对象
     */
    updateDeployment: (projectId, data) => {
        return apiRequest(`/deployment/api/${projectId}/update`, 'PUT', data);
    }
};

// ==== 系统配置相关 API ====
const SystemConfigAPI = {
    /**
     * 获取指定类型的系统配置项列表
     * @param {string} configType - 配置类型
     * @returns {Promise} - 返回Promise对象
     */
    getConfigItems: (configType) => {
        return apiRequest(`/system/api/configs/${configType}`, 'GET');
    },
    
    /**
     * 获取所有类型的默认配置项
     * @returns {Promise} - 返回Promise对象
     */
    getDefaultConfigs: () => {
        return apiRequest('/system/api/configs/defaults', 'GET');
    }
};

// 将API对象导出为全局变量
const API = {
    Auth: AuthAPI,
    Project: ProjectAPI,
    Requirement: RequirementAPI,
    Architecture: ArchitectureAPI,
    Database: DatabaseAPI,
    Module: ModuleAPI,
    Test: TestAPI,
    Deployment: DeploymentAPI,
    SystemConfig: SystemConfigAPI
};

// 确保在浏览器环境中API对象可用
if (typeof window !== 'undefined') {
    window.API = API;
}

// 如果是在Node.js环境中，则导出API对象
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
} 