from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import inspect, text
from src.core.salary_database import salary_engine
from collections import deque
from typing import List, Optional, Any

router = APIRouter(prefix="/analytics", tags=["analytics"])

# -----------------------------
# Request Models
# -----------------------------

class ChartConfigInput(BaseModel):
    type: str
    x: str
    y: str
    x_table_name: str
    y_table_name: str

class AnalyticsRequest(BaseModel):
    table_name: str # The main table context from frontend
    chart: ChartConfigInput # Explicit chart config is now required

# -----------------------------
# Graph & Path Logic
# -----------------------------

def build_relationship_graph():
    inspector = inspect(salary_engine)
    graph = {}

    for table in inspector.get_table_names():
        graph[table] = []
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            referred_table = fk["referred_table"]
            graph[table].append(referred_table)
            # Reverse relation
            if referred_table not in graph:
                graph[referred_table] = []
            graph[referred_table].append(table)
    return graph

def find_join_path(start, end, graph):
    if start == end:
        return [start]
        
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current == end:
            return path
        visited.add(current)
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    return None

def build_join_chain(path):
    inspector = inspect(salary_engine)
    join_sql = ""

    for i in range(len(path) - 1):
        table_a = path[i]
        table_b = path[i + 1]

        # Check FK from A -> B
        fks = inspector.get_foreign_keys(table_a)
        matched = False
        for fk in fks:
            if fk["referred_table"] == table_b:
                local_col = fk["constrained_columns"][0]
                remote_col = fk["referred_columns"][0]
                join_sql += f" JOIN {table_b} ON {table_a}.{local_col} = {table_b}.{remote_col} "
                matched = True
                break
        
        # Check reverse FK (B -> A)
        if not matched:
            fks_b = inspector.get_foreign_keys(table_b)
            for fk in fks_b:
                if fk["referred_table"] == table_a:
                    local_col = fk["constrained_columns"][0]
                    remote_col = fk["referred_columns"][0]
                    join_sql += f" JOIN {table_b} ON {table_b}.{local_col} = {table_a}.{remote_col} "
                    matched = True
                    break
    return join_sql

# -----------------------------
# Logic Helper
# -----------------------------

def resolve_table_for_column(col_name: str, main_table: str):
    """
    Helper to map user-friendly column names to actual DB columns if needed.
    Kept for 'department' -> 'name' mapping since frontend sends 'department'.
    """
    col_lower = col_name.lower()
    if col_lower == "department":
        return "departments", "name"
    elif col_lower == "position":
        return "positions", "title"
    elif col_lower == "incentive":
        return "incentives", "amount"
    else:
        return main_table, col_name

# -----------------------------
# Endpoint
# -----------------------------

@router.post("/analytics")
def analytics(req: AnalyticsRequest):
    graph = build_relationship_graph()
    
    # Use explicit chart config
    x_col = req.chart.x
    y_col = req.chart.y
    x_table = req.chart.x_table_name
    y_table = req.chart.y_table_name
    chart_type = req.chart.type
    
    # 1. Start building SQL logic
    start_table = y_table
    target_table = x_table
    
    full_join_sql = ""
    
    if start_table != target_table:
        path = find_join_path(start_table, target_table, graph)
        if path:
            full_join_sql = build_join_chain(path)
        else:
            # Try finding path via the main table context if direct path fails?
            # Or just fail.
             raise HTTPException(status_code=400, detail=f"Cannot find join path between {start_table} and {target_table}")

    # Resolve DB column names (handling 'department' -> 'name' mapping)
    _, x_db_col = resolve_table_for_column(x_col, x_table)
    _, y_db_col = resolve_table_for_column(y_col, y_table)
    
    # Grouped Query
    grouped_sql = f"""
    SELECT 
        {x_table}.{x_db_col} as x,
        SUM({y_table}.{y_db_col}) as sum_value,
        AVG({y_table}.{y_db_col}) as avg_value,
        MIN({y_table}.{y_db_col}) as min_value,
        MAX({y_table}.{y_db_col}) as max_value
    FROM {start_table}
    {full_join_sql}
    GROUP BY {x_table}.{x_db_col}
    ORDER BY x
    """
    
    # Summary Query
    summary_sql = f"""
    SELECT 
        SUM({y_table}.{y_db_col}) as sum_value,
        AVG({y_table}.{y_db_col}) as avg_value,
        MIN({y_table}.{y_db_col}) as min_value,
        MAX({y_table}.{y_db_col}) as max_value
    FROM {start_table}
    {full_join_sql}
    """
    
    try:
        with salary_engine.connect() as conn:
            grouped_rows = conn.execute(text(grouped_sql)).mappings().all()
            summary_row = conn.execute(text(summary_sql)).mappings().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}\nQuery: {grouped_sql}")

    response = {
        "chart": {
            "type": chart_type,
            "x": x_col,
            "y": y_col,
            "x_table_name": x_table,
            "y_table_name": y_table
        },
        "grouped": grouped_rows,
        "summary": summary_row
    }
    
    return response
