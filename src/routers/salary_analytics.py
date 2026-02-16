from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import inspect, text
from src.core.database import engine
from collections import deque

router = APIRouter(prefix="/analytics", tags=["analytics"])


# -----------------------------
# Request Model
# -----------------------------
class ChartRequest(BaseModel):
    table_name: str
    value_column: str
    group_by_table: str
    group_by_column: str


# -----------------------------
# Step 1: Build Relationship Graph
# -----------------------------
def build_relationship_graph():
    inspector = inspect(engine)
    graph = {}

    for table in inspector.get_table_names():
        graph[table] = []

        fks = inspector.get_foreign_keys(table)

        for fk in fks:
            referred_table = fk["referred_table"]
            graph[table].append(referred_table)

            # Also add reverse relation
            if referred_table not in graph:
                graph[referred_table] = []
            graph[referred_table].append(table)

    return graph


# -----------------------------
# Step 2: Find Join Path (BFS)
# -----------------------------
def find_join_path(start, end, graph):
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


# -----------------------------
# Step 3: Build JOIN SQL Automatically
# -----------------------------
def build_join_chain(path):
    inspector = inspect(engine)
    join_sql = ""

    for i in range(len(path) - 1):
        table_a = path[i]
        table_b = path[i + 1]

        # Check FK from A → B
        fks = inspector.get_foreign_keys(table_a)
        matched = False

        for fk in fks:
            if fk["referred_table"] == table_b:
                local_col = fk["constrained_columns"][0]
                remote_col = fk["referred_columns"][0]

                join_sql += (
                    f" JOIN {table_b} "
                    f"ON {table_a}.{local_col} = {table_b}.{remote_col} "
                )
                matched = True
                break

        # Check reverse FK (B → A)
        if not matched:
            fks = inspector.get_foreign_keys(table_b)
            for fk in fks:
                if fk["referred_table"] == table_a:
                    local_col = fk["constrained_columns"][0]
                    remote_col = fk["referred_columns"][0]

                    join_sql += (
                        f" JOIN {table_b} "
                        f"ON {table_b}.{local_col} = {table_a}.{remote_col} "
                    )
                    break

    return join_sql


# -----------------------------
# Main Endpoint
# -----------------------------
@router.post("/analytics")
def analytics(req: ChartRequest):

    graph = build_relationship_graph()

    # Find join path
    path = find_join_path(req.table_name, req.group_by_table, graph)

    if not path:
        raise HTTPException(
            status_code=400, detail="No relationship path found between tables"
        )

    join_sql = build_join_chain(path)

    # -----------------------------
    # Grouped Query
    # -----------------------------
    grouped_sql = f"""
    SELECT
        {req.group_by_table}.{req.group_by_column} AS x,
        SUM({req.table_name}.{req.value_column}) AS sum_value,
        AVG({req.table_name}.{req.value_column}) AS avg_value,
        MIN({req.table_name}.{req.value_column}) AS min_value,
        MAX({req.table_name}.{req.value_column}) AS max_value
    FROM {req.table_name}
    {join_sql}
    GROUP BY {req.group_by_table}.{req.group_by_column}
    ORDER BY x;
    """

    # -----------------------------
    # Summary Query
    # -----------------------------
    summary_sql = f"""
    SELECT
        SUM({req.value_column}) AS sum_value,
        AVG({req.value_column}) AS avg_value,
        MIN({req.value_column}) AS min_value,
        MAX({req.value_column}) AS max_value
    FROM {req.table_name};
    """

    with engine.connect() as conn:
        grouped = conn.execute(text(grouped_sql)).mappings().all()
        summary = conn.execute(text(summary_sql)).mappings().first()
        print("Grouped SQL:", grouped_sql)
        print("Summary SQL:", summary_sql)


    return {"join_path": path, "grouped": grouped, "summary": summary}
