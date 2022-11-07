import psycopg2
import json

class Database:
    def __init__(self, username, password, hostname, port):
        self.connection = self.connect(username, password, hostname, port)
        self.table_name = None

    def connect(self, username, password, hostname, port):
        print(f"Attempting to connect to db: {hostname}:{password} with username: {username}")
        connection = psycopg2.connect(user=username,
                                    password=password,
                                    host=hostname,
                                    port=port,
                                    database="postgresdb")
        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        cursor.close()
        return connection

    def table_exists(self):
        cursor = self.connection.cursor()
        cursor.execute("select exists(select relname from pg_class where relname='" + self.table_name + "')")
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists

    def execute_query(self, query, return_value=False):
        record=None
        cursor = self.connection.cursor()
        cursor.execute(query)
        if return_value: record=cursor.fetchall()
        cursor.close()
        return record

    def create_table(self, table_name):
        self.table_name = table_name
        if self.table_exists(): 
            print(f"table {self.table_name} already exists")
            return
        create_table_query = f'''CREATE TABLE {self.table_name}
            (SYSTEM_ID TEXT PRIMARY KEY     NOT NULL,
            AGENTS           TEXT    NOT NULL,
            LEADER           TEXT    NOT NULL,
            MAP              TEXT    NOT NULL,
            PATHS            TEXT    NOT NULL); '''
        # Execute a command: this creates a new table
        self.execute_query(create_table_query)
        print("Table created successfully in PostgreSQL")

    def insert_data(self, system_id, table_name, key, value):
        return

    def update_data(self, system_id, data):
        agents = json.dumps(data['agents'])
        leader = data['leader']
        cur_map = json.dumps(data['map'])
        paths = json.dumps(data['paths'])

        update_or_insert_query = f'''
        INSERT INTO {self.table_name} (SYSTEM_ID, AGENTS, LEADER, MAP, PATHS)
        VALUES ('{system_id}', '{agents}', '{leader}', '{cur_map}', '{paths}')
        ON CONFLICT (SYSTEM_ID) DO UPDATE
        SET AGENTS = excluded.AGENTS,
            LEADER = excluded.LEADER,
            MAP = excluded.MAP,
            PATHS = excluded.PATHS;
        '''
        self.execute_query(update_or_insert_query)
        return True

    def get_data(self, system_id):
        query = f'''
        SELECT * FROM {self.table_name} WHERE SYSTEM_ID = '{system_id}'
        '''
        raw_data=self.execute_query(query, return_value=True)
        if not raw_data: return None, None, None, None
        raw_data=raw_data[0]
        system=raw_data[0]
        agents=json.loads(raw_data[1])
        leader=raw_data[2]
        print(leader)
        cur_map=json.loads(raw_data[3])
        paths = json.loads(raw_data[4])
        return agents, leader, cur_map, paths

    def get_systems(self):
        query = f'''
        SELECT SYSTEM_ID FROM {self.table_name}
        '''
        raw_data=self.execute_query(query, return_value=True)
        print(raw_data)
        if not raw_data: return None
        return raw_data[0]