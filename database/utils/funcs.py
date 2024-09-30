from .connector import Field, decorator, YourTableModel, Int

class SchemaBase:
    table_name = ""
    fields = []

    @classmethod
    def get_fields(cls):
        "Получить поля таблицы"
        return [Field('id', Int, extra='PRIMARY KEY NOT NULL')] + cls.fields

    @classmethod
    @decorator
    def make(cls, cur, db = 'easysql'):
        fields_query = ', '.join(str(field) for field in cls.get_fields())
        cur.execute(f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({fields_query})")

    @classmethod
    @decorator
    def drop(cls, cur, db='easysql'):
        cur.execute(f"DROP TABLE {cls.table_name}")

    @classmethod
    def _construct_where_clause(cls, by):
        "Создать where для query"
        where_clauses = []
        params = []
        for key, values in (by or {}).items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                if isinstance(value, tuple):
                    val, op = value[1], value[0]
                    if op == 'IN':
                        where_clauses.append(f"{key} IN ({','.join(['?' for _ in val])})")
                        params.extend(val)
                    else:
                        where_clauses.append(f"{key} {op} ?")
                        params.append(val)
                else:
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
        return " AND ".join(where_clauses), params

    @classmethod
    @decorator
    def select(cls, cur, by=None, fields='*', order_by=None, limit=None, output_format='object', db='easysql', count_only=False):
        if count_only:
            base_query = f"SELECT COUNT(*) FROM {cls.table_name}"
        else:
            base_query = f"SELECT {fields} FROM {cls.table_name}"

        where_clause, params = cls._construct_where_clause(by)
        query = f"{base_query} WHERE {where_clause}" if where_clause else base_query

        if not count_only:
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        if count_only:
            return rows[0][0]  # Возвращаем сразу количество записей

        if output_format == 'json':
            columns = [column[0] for column in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        elif output_format == 'array':
            if ',' in fields or fields == '*':  # Check if more than one field is being fetched
                raise ValueError("array output format requires exactly one field to be specified")
            return [row[0] for row in rows]
        else:
            return [YourTableModel(row, cls) for row in rows]


    @classmethod
    @decorator
    def insert(cls, cur, data, db='easysql'):
        if isinstance(data, dict):
            data = [data]
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['?' for _ in data[0]])
        query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
        params = [tuple(item.values()) for item in data]
        if len(data) > 1:
            cur.executemany(query, params)
        else:
            cur.execute(query, params[0])
            return cur.lastrowid


    @classmethod
    @decorator
    def update(cls, cur, updates, by=None, all=False, db='easysql'):
        if not updates:
            raise ValueError("No update data provided.")
        if not by and not all:
            raise ValueError("No conditions specified for update.")
        set_clauses = ', '.join(f"{key} = ?" for key in updates)
        params = list(updates.values())
        where_clause, where_params = cls._construct_where_clause(by)
        query = f"UPDATE {cls.table_name} SET {set_clauses} WHERE {where_clause}" if where_clause else f"UPDATE {cls.table_name} SET {set_clauses}"
        params.extend(where_params)
        cur.execute(query, tuple(params))

    @classmethod
    @decorator
    def delete(cls, cur, by=None, all=False, db='easysql'):
        if not by and not all:
            raise ValueError("No conditions specified for deletion.")
        where_clause, params = cls._construct_where_clause(by)
        query = f"DELETE FROM {cls.table_name} WHERE {where_clause}" if where_clause else f"DELETE FROM {cls.table_name}"
        cur.execute(query, tuple(params))

    @classmethod
    def remake_schema(cls, db='easysql'):
        try:
            cls.drop(db = db)
        except Exception as e:
            pass
        cls.make(db = db)