from .utils.connector import Int, Str, Bool, Field as F
from .utils.funcs import SchemaBase



class Data:
    class Filters(SchemaBase):
        table_name = 'filters'
        fields = [
            F('type', Str),
            F('player_id', Int),
            F('keyword', Str),
            F('is_positive', Bool)
        ]

    class Messages(SchemaBase):
        table_name = 'messages'
        fields = [
            F('text', Str),
        ]

    class Players(SchemaBase):
        table_name = 'players'
        fields = [
            F('name', Str),
        ]

    class Users(SchemaBase):
        table_name = 'users'
        fields = [
            F('user_id', Int),
            F('username', Str),
            F('is_admin', Bool),
            F('name', Str),
            F('to_notice', Bool),
        ]

class DB:
    @staticmethod
    def get_all_schemas():
        return [getattr(DB, attr) for attr in dir(DB) if isinstance(getattr(DB, attr), type) and issubclass(getattr(DB, attr), SchemaBase)]
    
    Filters = Data.Filters
    Messages = Data.Messages
    Players = Data.Players
    Users = Data.Users

