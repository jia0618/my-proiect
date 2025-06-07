/**
 * 公共JavaScript功能
 * 用于所有页面的共通功能，如导航栏处理、项目选择等
 */

document.addEventListener('DOMContentLoaded', function() {
    // 不再检查登录状态，由后端控制
    // checkLoginStatus(); 
    
    // 处理导航栏高亮
    highlightCurrentNavItem();
    
    // 处理退出登录
    setupLogout();
    
    // 处理项目选择
    setupProjectSelection();
    
    // 处理菜单点击
    setupMenuNavigation();
});

/**
 * 检查用户登录状态 - 被禁用，由后端Flask-Login处理
 * 这个函数已不再使用，保留作为参考
 */
/*
function checkLoginStatus() {
    // 如果是登录页面，不需要检查
    const isLoginPage = window.location.pathname.includes('login');
    if (isLoginPage) {
        return;
    }
    
    // 检查登录状态token
    const token = localStorage.getItem('token');
    if (!token) {
        // 保存当前URL以便登录后返回
        localStorage.setItem('redirectUrl', window.location.href);
        window.location.href = '/login';
    }
}
*/

/**
 * 高亮当前页面对应的导航菜单项
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-menu a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath.endsWith(href)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * 设置退出登录功能
 */
function setupLogout() {
    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // 调用登出API
                await API.Auth.logout();
                
                // 清除本地存储的用户数据
                localStorage.removeItem('token');
                localStorage.removeItem('userId');
                localStorage.removeItem('username');
                
                // 跳转到登录页
                window.location.href = '/login';
            } catch (error) {
                console.error('登出失败:', error);
                alert('登出失败，请重试');
            }
        });
    }
}

/**
 * 设置菜单导航功能
 */
function setupMenuNavigation() {
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
}

/**
 * 设置项目选择功能
 */
function setupProjectSelection() {
    const projectSelector = document.getElementById('projectSelector');
    if (projectSelector) {
        // 加载用户的项目列表
        loadUserProjects(projectSelector);
        
        // 处理项目选择变更事件
        projectSelector.addEventListener('change', function() {
            const projectId = this.value;
            if (projectId) {
                // 保存当前选择的项目ID
                localStorage.setItem('currentProjectId', projectId);
                
                // 如果在项目相关页面，则刷新页面以显示选定项目的数据
                const projectRelatedPages = [
                    'requirement.html', 
                    'architecture.html', 
                    'database.html', 
                    'module.html', 
                    'testcase.html', 
                    'deployment.html'
                ];
                
                const currentPage = window.location.pathname.split('/').pop();
                if (projectRelatedPages.includes(currentPage)) {
                    window.location.href = `${currentPage}?project_id=${projectId}`;
                }
            }
        });
    }
}

/**
 * 加载用户项目列表
 * @param {HTMLElement} selectElement - 项目选择下拉框元素
 */
async function loadUserProjects(selectElement) {
    try {
        // 清空当前选项
        selectElement.innerHTML = '<option value="">选择项目...</option>';
        
        // 获取项目列表
        const response = await API.Project.listProjects();
        
        if (response.success && response.projects && response.projects.length > 0) {
            // 填充项目选项
            response.projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.id;
                option.textContent = project.name;
                selectElement.appendChild(option);
            });
            
            // 设置当前选中的项目
            const currentProjectId = getCurrentProjectId();
            if (currentProjectId) {
                selectElement.value = currentProjectId;
            }
        }
    } catch (error) {
        console.error('加载项目列表失败:', error);
    }
}

/**
 * 获取当前选择的项目ID
 * 优先从URL参数获取，其次从本地存储获取
 * @returns {string|null} 项目ID
 */
function getCurrentProjectId() {
    // 尝试从URL参数获取项目ID
    const urlParams = new URLSearchParams(window.location.search);
    const projectIdFromUrl = urlParams.get('project_id');
    
    if (projectIdFromUrl) {
        // 将URL中的项目ID保存到本地存储
        localStorage.setItem('currentProjectId', projectIdFromUrl);
        return projectIdFromUrl;
    }
    
    // 从本地存储获取项目ID
    return localStorage.getItem('currentProjectId');
}

/**
 * 从URL中获取项目ID
 * @returns {string|null} 项目ID
 */
function getProjectIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('project_id');
}

/**
 * 获取用户信息并显示在页面上
 */
function displayUserInfo() {
    const username = localStorage.getItem('username');
    const userElement = document.getElementById('username');
    
    if (username && userElement) {
        userElement.textContent = username;
    }
} 