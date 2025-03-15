import re
from elia_api.tools.registry import register_backend_function
from elia_api.bigquery import get_bigquery_client  # Use getter, not direct client
from typing import Dict, Any, List


@register_backend_function("list_available_tables")
def list_available_tables(map_data: str) -> Dict[str, Any]:
    """
    List and describe all BigQuery tables in the dataset for AI use.
    """
    project_id = "gen-lang-client-0136133024"
    dataset_id = "demo_data"

    tables_info: List[Dict[str, str]] = []

    try:
        # Get initialized client
        bigquery_client = get_bigquery_client()

        # Reference to dataset
        dataset_ref = bigquery_client.dataset(dataset_id, project=project_id)

        # List tables
        tables = bigquery_client.list_tables(dataset_ref)

        for table in tables:
            table_id = table.table_id

            # Get schema
            table_ref = dataset_ref.table(table_id)
            table_obj = bigquery_client.get_table(table_ref)

            # Build field descriptions
            field_descriptions = []
            for field in table_obj.schema:
                desc = (field.description or "").strip()
                field_info = f"{field.name} ({field.field_type})"
                if desc:
                    field_info += f" - {desc}"
                field_descriptions.append(field_info)

            description = (
                f"Table '{table_id}' contains fields: "
                + "; ".join(field_descriptions)
                + "."
                if field_descriptions else
                f"Table '{table_id}' has no defined fields."
            )

            tables_info.append({
                "table_name": table_id,
                "description": description
            })

        return {"tables": tables_info}

    except Exception as e:
        return {
            "error": "Failed to retrieve tables or schema from BigQuery.",
            "details": str(e)
        }

@register_backend_function("query_table")
def query_table(table_name: str, where_clause: str = "", limit: int = 10, map_data: str = "") -> Dict[str, Any]:
    """
    Query data from a specified BigQuery table with an optional case-insensitive where clause and limit.
    """

    project_id = "gen-lang-client-0136133024"
    dataset_id = "demo_data"

    try:
        # Get BigQuery client
        bigquery_client = get_bigquery_client()

        # Safely quote the table name
        full_table_name = f"`{project_id}.{dataset_id}.{table_name}`"

        # ✅ Ensure limit is an integer
        limit = int(limit)

        # Optional case-insensitive where_clause handling
        if where_clause.strip():
            # Simple pattern: column = "value" or column = 'value'
            pattern = re.compile(r'^\s*(\w+)\s*=\s*[\'"](.+)[\'"]\s*$', re.IGNORECASE)
            match = pattern.match(where_clause.strip())

            if match:
                column, value = match.groups()
                # Wrap both sides with LOWER()
                where_sql = f"WHERE LOWER({column}) = LOWER('{value}')"
            else:
                # Fallback if pattern doesn't match simple format
                where_sql = f"WHERE {where_clause}"
        else:
            where_sql = ""

        # Build final query
        query = f"SELECT * FROM {full_table_name} {where_sql} LIMIT {limit}"

        # Run query
        query_job = bigquery_client.query(query)
        results = query_job.result()

        # Extract rows as list of dicts
        rows = [dict(row) for row in results]

        return {
            "rows": rows,
            "query": query  # For AI to know what was run
        }

    except Exception as e:
        return {
            "error": "Failed to query BigQuery table.",
            "details": str(e),
            "query_attempted": query  # Helpful for AI debugging
        }
