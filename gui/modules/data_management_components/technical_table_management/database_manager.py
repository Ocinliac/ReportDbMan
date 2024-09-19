import sqlite3


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_log_table()
        self.create_config_table()

    def create_log_table(self):
        create_log_table_sql = '''
        CREATE TABLE IF NOT EXISTS import_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            csv_file_name TEXT NOT NULL,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.cursor.execute(create_log_table_sql)
        self.conn.commit()

    def create_config_table(self):
        create_config_table_sql = '''
        CREATE TABLE IF NOT EXISTS table_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            folder_path TEXT NOT NULL
        );
        '''
        self.cursor.execute(create_config_table_sql)
        self.conn.commit()

    def log_import(self, table_name, csv_file_name):
        insert_log_sql = '''
        INSERT INTO import_log (table_name, csv_file_name)
        VALUES (?, ?);
        '''
        self.cursor.execute(insert_log_sql, (table_name, csv_file_name))
        self.conn.commit()

    def is_csv_imported(self, table_name, csv_file_name):
        check_log_sql = '''
        SELECT COUNT(1) FROM import_log
        WHERE table_name = ? AND csv_file_name = ?;
        '''
        self.cursor.execute(check_log_sql, (table_name, csv_file_name))
        return self.cursor.fetchone()[0] > 0

    def get_table_configs(self):
        select_config_sql = '''
        SELECT table_name, folder_path FROM table_config;
        '''
        self.cursor.execute(select_config_sql)
        return self.cursor.fetchall()

    def add_table_config(self, table_name, folder_path):
        insert_config_sql = '''
        INSERT INTO table_config (table_name, folder_path)
        VALUES (?, ?);
        '''
        print(insert_config_sql)
        self.cursor.execute(insert_config_sql, (table_name, folder_path))
        self.conn.commit()

    def close(self):
        self.conn.close()