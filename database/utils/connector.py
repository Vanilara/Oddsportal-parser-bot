import sqlite3
import os


def decorator(func):
    def wrapper(cls, *args, db='easysql', **kwargs):
        abs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = f'{abs_path}/store/{db}.db'
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            result = func(cls, cur, *args, **kwargs)
            conn.commit()
        return result
    return wrapper


class YourTableModel:
    "Таблицы представление"
    def __init__(self, row, schema):
        self.schema = schema
        for field, value in zip(schema.get_fields(), row):
            setattr(self, field.name, field.from_sql(value))

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.schema.get_fields()}
    
    def __repr__(self):
        attributes = ', '.join(f"{field.name}={getattr(self, field.name, None)}" 
                               for field in self.schema.get_fields())
        return f"<YourTableModel({attributes})>"
    
class Field:
    "Представление столбца таблицы"
    def __init__(self, name, sql_type, extra = None, default=None):
        self.name = name
        self.sql_type = sql_type.name
        self.extra = extra
        self.default = default
        self.to_sql = lambda x: x
        self.from_sql = lambda x: x
        if sql_type == Bool:
            self.to_sql = lambda x: 1 if x else 0
            self.from_sql = lambda x: bool(x)

    def __str__(self):
        extra = f' {self.extra}' if self.extra is not None else ""
        default_part = f" DEFAULT {self.default}" if self.default is not None else ""
        return f"{self.name} {self.sql_type}{extra}{default_part}"

class DataType:
    name = None

class Int(DataType):
    name = 'INTEGER'

class Str(DataType):
    name = 'VARCHAR'

class Bool(DataType):
    name = 'BOOLEAN'