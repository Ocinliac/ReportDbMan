import os
import pandas as pd
from .utils import archive_file


class CSVImporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_latest_csv_file(self, folder_path):
        files = os.listdir(folder_path)
        csv_files = [f for f in files if f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the specified folder.")
        full_paths = [os.path.join(folder_path, f) for f in csv_files]
        latest_file = max(full_paths, key=os.path.getmtime)
        return latest_file

    def create_table_from_csv(self, csv_file_path, table_name):
        df = pd.read_csv(csv_file_path)
        columns = df.columns
        column_types = []

        for column in columns:
            if df[column].dtype == 'int64':
                column_type = 'INTEGER'
            elif df[column].dtype == 'float64':
                column_type = 'REAL'
            else:
                column_type = 'TEXT'
            column_types.append(f"{column} {column_type}")

        columns_schema = ", ".join(column_types)
        # print(columns_schema.replace("(","").replace(")", ""))
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_schema});"
        # print(create_table_sql)
        self.db_manager.cursor.execute(create_table_sql)
        self.db_manager.conn.commit()

        df.to_sql(table_name, self.db_manager.conn, if_exists='append', index=False)

    def import_latest_csv_to_sqlite(self):
        table_configs = self.db_manager.get_table_configs()

        for table_name, folder_path in table_configs:
            try:
                latest_csv_file = self.get_latest_csv_file(folder_path)
                csv_file_name = os.path.basename(latest_csv_file)
                print(csv_file_name)
                if self.db_manager.is_csv_imported(table_name, csv_file_name):
                    print(f"CSV file '{csv_file_name}' has already been imported into '{table_name}'.")
                    continue

                self.create_table_from_csv(latest_csv_file, table_name)
                self.db_manager.log_import(table_name, csv_file_name)
                archive_file(latest_csv_file, folder_path)
                print(f"Data from '{csv_file_name}' imported into table '{table_name}' successfully.")
            except FileNotFoundError as e:
                print(e)
            except Exception as e:
                print(f"An error occurred while importing data to '{table_name}': {e}")
