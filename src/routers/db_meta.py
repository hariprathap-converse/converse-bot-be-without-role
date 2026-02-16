from sqlalchemy import MetaData, Table
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from functools import lru_cache

from src.core.database import get_db, engine

router = APIRouter()


# @router.get("/schema")
# def get_schema():
#     inspector = inspect(engine)

#     schema = {}

#     for table_name in inspector.get_table_names():
#         columns = inspector.get_columns(table_name)
#         foreign_keys = inspector.get_foreign_keys(table_name)

#         schema[table_name] = {
#             "columns": inspector.get_columns(table_name),
#             "primary_key": inspector.get_pk_constraint(table_name),
#             "foreign_keys": inspector.get_foreign_keys(table_name),
#         }
#     return schema


# @router.get("/schema")
# def get_schema():
#     inspector = inspect(engine)

#     schema = {"tables": {}}

#     for table_name in inspector.get_table_names():
#         columns = inspector.get_columns(table_name)
#         pk = inspector.get_pk_constraint(table_name)
#         fks = inspector.get_foreign_keys(table_name)

#         table_info = {
#             "primary_key": pk.get("constrained_columns", []),
#             "columns": {},
#             "relationships": [],
#         }

#         # Columns
#         for col in columns:
#             print(col)
#             table_info["columns"][col["name"]] = {
#                 "type": str(col["type"]),
#                 "nullable": col["nullable"],
#             }

#         # Relationships (foreign keys)
#         for fk in fks:
#             for local_col, remote_col in zip(
#                 fk["constrained_columns"],
#                 fk["referred_columns"],
#             ):
#                 table_info["relationships"].append(
#                     {
#                         # "type": "many_to_one",
#                         "local_column": local_col,
#                         "target_table": fk["referred_table"],
#                         "target_column": remote_col,
#                     }
#                 )

#         schema["tables"][table_name] = table_info

#     return schema


# @router.get("/schema")
# def get_schema():
#     inspector = inspect(engine)
#     tables = inspector.get_table_names()

#     schema = {"tables": {}}

#     # First pass: collect table metadata
#     table_data = {}

#     for table in tables:
#         columns = inspector.get_columns(table)
#         pk = inspector.get_pk_constraint(table)
#         fks = inspector.get_foreign_keys(table)
#         uniques = inspector.get_unique_constraints(table)

#         table_data[table] = {
#             "columns": columns,
#             "primary_key": pk.get("constrained_columns", []),
#             "foreign_keys": fks,
#             "unique_constraints": uniques,
#         }

#     # Second pass: build structured schema
#     for table, data in table_data.items():
#         schema["tables"][table] = {
#             "primary_key": data["primary_key"],
#             "columns": {
#                 col["name"]: {
#                     "type": str(col["type"]),
#                     "nullable": col["nullable"],
#                 }
#                 for col in data["columns"]
#             },
#             "relationships": [],
#         }

#     # Third pass: detect relationships
#     for table, data in table_data.items():
#         fks = data["foreign_keys"]
#         pk = set(data["primary_key"])
#         uniques = [
#             set(u["column_names"]) for u in data["unique_constraints"]
#         ]

#         # Detect many-to-many
#         if (
#             len(fks) == 2
#             and len(data["columns"]) <= 3
#             and set(data["primary_key"]) ==
#             set(fks[0]["constrained_columns"] + fks[1]["constrained_columns"])
#         ):
#             t1 = fks[0]["referred_table"]
#             t2 = fks[1]["referred_table"]

#             schema["tables"][t1]["relationships"].append({
#                 "type": "many_to_many",
#                 "target_table": t2,
#                 "through": table,
#             })

#             schema["tables"][t2]["relationships"].append({
#                 "type": "many_to_many",
#                 "target_table": t1,
#                 "through": table,
#             })

#             continue

#         # Detect one-to-one or many-to-one
#         for fk in fks:
#             local_cols = set(fk["constrained_columns"])
#             target = fk["referred_table"]

#             relationship_type = "many_to_one"

#             # one-to-one detection
#             if (
#                 local_cols == pk
#                 or any(local_cols == u for u in uniques)
#             ):
#                 relationship_type = "one_to_one"

#             schema["tables"][table]["relationships"].append({
#                 "type": relationship_type,
#                 "local_columns": list(local_cols),
#                 "target_table": target,
#                 "target_columns": fk["referred_columns"],
#             })

#             # Add reverse relationship
#             reverse_type = (
#                 "one_to_one"
#                 if relationship_type == "one_to_one"
#                 else "one_to_many"
#             )

#             schema["tables"][target]["relationships"].append({
#                 "type": reverse_type,
#                 "target_table": table,
#                 "via_columns": list(local_cols),
#             })

#     return schema


# @lru_cache()
# def build_llm_schema():
#     inspector = inspect(engine)
#     tables = sorted(inspector.get_table_names())

#     schema = {}

#     for table in tables:
#         columns = inspector.get_columns(table)
#         fks = inspector.get_foreign_keys(table)

#         column_names = sorted([col["name"] for col in columns])

#         table_schema = {
#             "c": column_names,  # columns
#             "f": [],  # foreign keys (join map)
#         }

#         for fk in fks:
#             for local, remote in zip(fk["constrained_columns"], fk["referred_columns"]):
#                 table_schema["f"].append([local, fk["referred_table"], remote])

#         # Keep only tables that have columns
#         # (all real tables will have columns)
#         if table_schema["c"]:
#             schema[table] = table_schema

#     return schema


# @router.get("/schema-llm")
# def get_schema_llm():
#     return build_llm_schema()


@lru_cache()
def build_schema():
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    schema = {}

    for table in tables:
        columns = inspector.get_columns(table)
        pk = inspector.get_pk_constraint(table)
        fks = inspector.get_foreign_keys(table)

        table_schema = {
            "columns": sorted([col["name"] for col in columns]),
            "pk": pk.get("constrained_columns", []),
            "foreign_keys": [],
        }

        for fk in fks:
            for local, remote in zip(fk["constrained_columns"], fk["referred_columns"]):
                table_schema["foreign_keys"].append(
                    {
                        "column": local,
                        "ref_table": fk["referred_table"],
                        "ref_column": remote,
                    }
                )

        # Only include tables that actually have columns
        if table_schema["columns"]:
            schema[table] = table_schema

    return schema


@router.get("/schema-llm")
def get_schema_llm():
    return build_schema()
