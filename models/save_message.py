import psycopg2
from psycopg2 import sql
from .create_db import UserDatabaseManager
9
class PjDBManager(UserDatabaseManager):
    def __init__(self, admin_config):
        super().__init__(admin_config)
        print(admin_config)

    def create_project_table(self, connection, project_name):
        """
        프로젝트별 테이블 생성
        """
        table_name = self.get_table_name(project_name)
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            project_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        try:
            self.execute_crud(connection,query)
            print(f"TABLE '{table_name}' created successfully.")
        except Exception as e:
            print(f"Error creating project table: {e}")

    def execute_project_crud(self, connection, project_name, query, params=None):
        table_name = self.get_table_name(project_name)
        formatted_query = query.format(table = table_name)
        try:
            return self.execute_crud(connection, formatted_query, params)
        except Exception as e:
            print(f"Error executing CRUD on project table'{table_name}: {e}")

    def get_table_name(self, project_name):
        return f"project_{project_name.lower().replace(' ', '_')}"
    def get_project_table(self, connection):
        """
        user_id의 데이터베이스에서 summary_로 시작하는 테이블 목록 반환
        """
        try:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'project_%'
            """
            cursor = connection.cursor()
            cursor.execute(query)
            tables = cursor.fetchall()
            cursor.close()
            return [table[0] for table in tables]  # 테이블 이름만 추출하여 리스트로 반환
        except Exception as e:
            print(f"Error retrieving summary tables: {e}")
            return []


"""    
#예시 코드드-
if __name__ == "__main__":
    file_path = 'admin_info.txt'

    with open(file_path, 'r') as file:
        lines = file.readlines()

    localhost = lines[0].strip()
    dbname = lines[1].strip()
    user = lines[2].strip()
    password = lines[3].strip()
    port = int(lines[4].strip())

    admin_config = {
        'host': localhost,
        'dbname': dbname,
        'user': user,
        'password': password,
        'port': port
    }
    
    # Initialize the PjDBManager
    manager = PjDBManager(admin_config)
    
    # Create user-specific database
    user_id = "12345"
    manager.create_user_database(user_id)
    
    # Connect to the user-specific database
    user_connection = manager.connect_user_database(user_id)
    
    # Create a table for a project
    project_name = "My First Project"
    manager.create_project_table(user_connection, project_name)
    
    # Insert data into the project table
    insert_query = "INSERT INTO {table} (name, description, project_at) VALUES (%s, %s, %s)"
    manager.execute_project_crud(
        user_connection,
        project_name,
        insert_query,
        params=("", "This is a description of the task.", "2024-11-27")
    )
    
    # Fetch data from the project table
    select_query = "SELECT * FROM {table}"
    results = manager.execute_project_crud(user_connection, project_name, select_query)
    print("Data from project table:", results)
    
    # Clean up
    manager.close_connection(user_connection)
    manager.delete_user_database(user_id)
    manager.close_admin_connection()
    """