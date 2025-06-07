import os
import pymysql
import pymysql.cursors
from typing import Dict, Any, List, Optional, Tuple, Union

class DBManager:
    """数据库管理类，负责处理MySQL数据库连接和操作"""
    
    def __init__(self, host: str = None, user: str = None, password: str = None, 
                 database: str = None, port: int = 3306):
        """
        初始化数据库管理器
        
        Args:
            host: localhost
            user: root
            password: LIUsijia123
            database: ai_software_platform
            port: 3306
        """
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.user = user or os.environ.get("DB_USER", "root")
        self.password = password or os.environ.get("DB_PASSWORD", "")
        self.database = database or os.environ.get("DB_NAME", "ai_platform")
        self.port = port or int(os.environ.get("DB_PORT", "3306"))
        self._connection = None
    
    def connect(self) -> pymysql.connections.Connection:
        """
        连接数据库
        
        Returns:
            pymysql.connections.Connection: 数据库连接
        """
        if not self._connection or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
            except pymysql.MySQLError as e:
                raise Exception(f"数据库连接失败: {str(e)}")
        
        return self._connection
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            raise Exception(f"查询执行失败: {str(e)}")
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
        """
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                conn.commit()
                return affected_rows
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"更新执行失败: {str(e)}")
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        执行批量更新
        
        Args:
            query: SQL更新语句
            params_list: 批量参数列表
            
        Returns:
            int: 受影响的行数
        """
        if not params_list:
            return 0
        
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                affected_rows = cursor.executemany(query, params_list)
                conn.commit()
                return affected_rows
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"批量更新失败: {str(e)}")
    
    def create_tables(self) -> None:
        """创建必要的数据表"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                # 创建项目表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # 创建需求表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS requirements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # 创建大纲表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS outlines (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    content JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # 创建代码表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_generations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    module_name VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # 创建提示词表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    prompt_type VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                # 创建数据库脚本表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS db_scripts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                
                conn.commit()
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"表创建失败: {str(e)}")
    
    def save_project(self, name: str, description: str = "") -> int:
        """
        保存项目
        
        Args:
            name: 项目名称
            description: 项目描述
            
        Returns:
            int: 项目ID
        """
        query = "INSERT INTO projects (name, description) VALUES (%s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, description))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存项目失败: {str(e)}")
    
    def save_requirement(self, project_id: int, content: str) -> int:
        """
        保存需求
        
        Args:
            project_id: 项目ID
            content: 需求内容
            
        Returns:
            int: 需求ID
        """
        query = "INSERT INTO requirements (project_id, content) VALUES (%s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, content))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存需求失败: {str(e)}")
    
    def save_outline(self, project_id: int, content: Dict[str, Any]) -> int:
        """
        保存大纲
        
        Args:
            project_id: 项目ID
            content: 大纲内容
            
        Returns:
            int: 大纲ID
        """
        import json
        query = "INSERT INTO outlines (project_id, content) VALUES (%s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, json.dumps(content, ensure_ascii=False)))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存大纲失败: {str(e)}")
    
    def save_code(self, project_id: int, module_name: str, content: str) -> int:
        """
        保存代码
        
        Args:
            project_id: 项目ID
            module_name: 模块名称
            content: 代码内容
            
        Returns:
            int: 代码ID
        """
        query = "INSERT INTO code_generations (project_id, module_name, content) VALUES (%s, %s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, module_name, content))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存代码失败: {str(e)}")
    
    def save_prompt(self, project_id: int, prompt_type: str, content: str) -> int:
        """
        保存提示词
        
        Args:
            project_id: 项目ID
            prompt_type: 提示词类型
            content: 提示词内容
            
        Returns:
            int: 提示词ID
        """
        query = "INSERT INTO prompts (project_id, prompt_type, content) VALUES (%s, %s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, prompt_type, content))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存提示词失败: {str(e)}")
    
    def save_db_script(self, project_id: int, content: str) -> int:
        """
        保存数据库脚本
        
        Args:
            project_id: 项目ID
            content: 脚本内容
            
        Returns:
            int: 脚本ID
        """
        query = "INSERT INTO db_scripts (project_id, content) VALUES (%s, %s)"
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, content))
                conn.commit()
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            conn.rollback()
            raise Exception(f"保存数据库脚本失败: {str(e)}")
    
    # 获取数据的方法
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        获取项目信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Dict[str, Any]]: 项目信息
        """
        query = "SELECT * FROM projects WHERE id = %s"
        results = self.execute_query(query, (project_id,))
        return results[0] if results else None
    
    def get_requirement(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        获取项目需求
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Dict[str, Any]]: 需求信息
        """
        query = "SELECT * FROM requirements WHERE project_id = %s ORDER BY created_at DESC LIMIT 1"
        results = self.execute_query(query, (project_id,))
        return results[0] if results else None
    
    def get_outline(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        获取项目大纲
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Dict[str, Any]]: 大纲信息
        """
        query = "SELECT * FROM outlines WHERE project_id = %s ORDER BY created_at DESC LIMIT 1"
        results = self.execute_query(query, (project_id,))
        if not results:
            return None
            
        import json
        outline = results[0]
        outline['content'] = json.loads(outline['content'])
        return outline 