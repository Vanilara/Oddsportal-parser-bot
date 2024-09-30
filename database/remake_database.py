import sys, os
parent_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_folder)
from database import DB


for schema in DB.get_all_schemas():
    schema.remake_schema()