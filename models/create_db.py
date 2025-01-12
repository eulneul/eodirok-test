import psycopg2
from psycopg2 import sql

file_path = 'models/admin_info.txt'

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

class UserDatabaseManager:
    def __init__(self, admin_config):
        """
        초기화 함수

        입력 파라미터
        admin_config => localhost, dbname, user, password, host가 담긴 dict
        """
        self.admin_config = admin_config
        self.admin_connection = None
        self.admin_cursor = None
        self.connect_admin()
    def connect_admin(self):
        """
        admin 데이터 베이스 연결
        """
        try:
            self.admin_connection = psycopg2.connect(**self.admin_config)
            self.admin_connection.autocommit = True
            self.admin_cursor = self.admin_connection.cursor()
            print("Admin connection established")
        except Exception as e:
            print(f"Error connecting to admin database: {e}")
        
    def create_user_database(self, user_id, base_db="template1"):
        """
        사용자별 데이터베이스 생성
        
        user_id: 사용자 id
        base_db: 템플릿 데이터베이스 (기본값: 'template1')
        """
        db_name = f"user_db_{user_id}"
        try:
            self.admin_cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s;"),
                [db_name]
            )
            if self.admin_cursor.fetchone():
                print(f"Database '{db_name}' already exists")
                return
            
            self.admin_cursor.execute(
                sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier(base_db)
                )
            )
            self.admin_connection.commit()
            print(f"Database '{db_name}' created successfully")
    
        except Exception as e:
            print(f"Error while creating database: {e}")
            self.admin_connection.rollback()
        
    def execute_crud(self, connection, query, params = None):
        """
        CRUD 작업 진행
        """
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                print("Query executed successfully.")

        except Exception as e:
            print(f"Error executing query: {e}")
            connection.rollback()
        finally:
            cursor.close()

    def connect_user_database(self, user_id):
        """
        사용자별 데이터베이스 연결 생성.

        :param user_id: 사용자 ID (데이터베이스 이름으로 사용)
        :return: 사용자 DB 연결 객체
        """
        db_name = f"user_db_{user_id}"
        print(db_name)
        print(admin_config)
        try:
            user_connection = psycopg2.connect(
                host=self.admin_config['host'],
                dbname=db_name,
                user=self.admin_config['user'],
                password=self.admin_config['password'],
                port=self.admin_config['port']
            )
            print(user_connection)
            print(f"Connected to user database '{db_name}'.")
            return user_connection
        except Exception as e:
            print(f"Error connecting to user database: {e}")
            return None

    def delete_user_database(self, user_id):
        """
        사용자 데이터베이스 삭제

        :param user_id: 사용자 ID (데이터베이스 이름으로 사용)
        """
        db_name = f"user_db_{user_id}"
        try:
            self.admin_cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name))
            )
            self.admin_connection.commit()
            print(f"Database '{db_name}' deleted successfully.")
        except Exception as e:
            print(f"Error while deleting database: {e}")
            self.admin_connection.rollback()

    def close_connection(self, connection):
        """데이터베이스 연결 닫기."""
        try:
            connection.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def close_admin_connection(self):
        if self.admin_cursor:
            self.admin_cursor.close()
        if self.admin_connection:
            self.admin_connection.close()
        print("Admin connection closed.")

'''
#예제 
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
    print(admin_config)
    manager = UserDatabaseManager(admin_config)
    
    # Create a new database
    user_id = "eulneul"
    manager.create_user_database(user_id)

    # Connect to the user database
    user_conn = manager.connect_user_database(user_id)
    if user_conn:
        # Example CRUD operation
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        manager.execute_crud(user_conn, create_table_query)

        insert_query = "INSERT INTO test_table (name) VALUES (%s);"
        manager.execute_crud(user_conn, insert_query, ("Sample Name",))

        select_query = "SELECT * FROM test_table;"
        results = manager.execute_crud(user_conn, select_query)
        print("Select Results:", results)

        # Close user database connection
        manager.close_connection(user_conn)

    # Delete the user database
    manager.delete_user_database(user_id)

    # Close admin connection
    manager.close_admin_connection()
    '''