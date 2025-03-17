import re
from elia_api.tools.registry import register_backend_function
from elia_api.bigquery import get_bigquery_client  # Use getter, not direct client
from typing import Dict, Any, List
from elia_api.utils.database_ops import store_geometry
from shapely import wkt
from shapely.geometry import mapping


@register_backend_function("list_available_tables")
def list_available_tables() -> Dict[str, Any]:
    """
    List and describe all available BigQuery tables for use in data analysis or spatial operations.

    This function returns fully qualified table names, along with a description of each table's fields.
    You (the AI) can use this to understand what datasets are available when the user is asking you to do things,
    perform lookups, or query spatial or tabular information.

    Returns:
        A dictionary containing:
            - tables: A list of available tables, where each entry includes:
                - table_name: The fully qualified name of the table (e.g., `gen-lang-client-0136133024.demo_data.table_name`).
                - description: A description of the table's fields, including field names, types, and any available descriptions.

    Notes:
        - Always use these fully qualified table names when building SQL queries.
        - You can use this function when a user asks "What data do you have?", "What datasets are available?", or similar.
        - This function does not query data — it only lists available tables and fields for your reference.
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
            full_table_name = f"`{project_id}.{dataset_id}.{table_id}`"  # Fully qualified name

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
                f"Table {full_table_name} contains fields: "
                + "; ".join(field_descriptions)
                + "."
                if field_descriptions else
                f"Table {full_table_name} has no defined fields."
            )

            tables_info.append({
                "table_name": full_table_name,  # Fully qualified name provided here
                "description": description
            })

        return {"tables": tables_info}

    except Exception as e:
        return {
            "error": "Failed to retrieve tables or schema from BigQuery.",
            "details": str(e)
        }

@register_backend_function("query_table")
async def query_table(
    table_name: str,
    where_clause: str = "",
    limit: int = 10,
    user_id: int = None,
    full_query: str = ""
) -> Dict[str, Any]:
    """
    Query a BigQuery table and return rows based on either a simple WHERE clause or a full custom SQL query.
    Automatically handles spatial data if present (GEOGRAPHY columns).

    Workflow for AI:
    1. First, call 'list_available_tables' to see which tables and fields are available.
    2. Then, call 'query_table' to query a selected table.

    Important:
    - BigQuery requires fully qualified table names in the format: `gen-lang-client-0136133024.demo_data.table_name`.
    - You must use the full table name in any SQL query, including in the 'full_query' parameter.
    - If unsure of table names, always call 'list_available_tables' first and choose from the result.
    - Do not invent or guess table names — always refer to listed tables.

    Query Options:
    - You can provide a simple WHERE clause for filtering, or
    - You can write a full custom BigQuery SQL query (e.g., with joins, aggregations, ordering, spatial filtering).
    - If 'full_query' is provided, 'where_clause' and 'limit' will be ignored.

    Spatial Data Handling:
    - If a table contains a GEOGRAPHY column (spatial data in WKT format), it will be automatically converted to GeoJSON and stored as a 'geometry_id'.
    - You do NOT need to handle spatial data yourself.
    - 'geometry_id' can be used with 'update_map_data' to show results on a map, but should never be shown or mentioned directly to the user.

    Args:
        table_name (str): Fully qualified table name (from 'list_available_tables').
        where_clause (str, optional): Optional WHERE clause to filter rows. Example: "POSTCODE = '6000'".
        limit (int, optional): Maximum number of rows to return (default 10, max 50).
        user_id (int, optional): Used internally for storing spatial data.
        full_query (str, optional): A full BigQuery SQL query. Must use fully qualified table names.

    Returns:
        dict:
            rows (list): List of records. Spatial data (GEOGRAPHY) will be returned as 'geometry_id'.
            query (str): The exact SQL query that was executed.
    """

    project_id = "gen-lang-client-0136133024"
    dataset_id = "demo_data"
    MAX_LIMIT = 50  # Adjust this to your acceptable max load

    try:
        bigquery_client = get_bigquery_client()

        # Strip backticks for internal API use
        raw_table_name = table_name.strip("`")
        table_id = raw_table_name.split(".")[-1]  # Extract table_id part for dataset ref

        # Enforce row limit cap
        limit = min(MAX_LIMIT, max(1, int(limit)))

        # ----------------------------
        # Build SQL query
        # ----------------------------
        if full_query.strip():
            query = full_query.strip()  # Use full query directly (AI writes this)
        else:
            where_sql = ""
            if where_clause.strip():
                # Simple case-insensitive column matching
                pattern = re.compile(r'^\s*(\w+)\s*=\s*[\'"](.+)[\'"]\s*$', re.IGNORECASE)
                match = pattern.match(where_clause.strip())
                if match:
                    column, value = match.groups()
                    where_sql = f"WHERE LOWER({column}) = LOWER('{value}')"
                else:
                    where_sql = f"WHERE {where_clause.strip()}"
            # Use fully qualified table name for SQL
            query = f"SELECT * FROM {table_name} {where_sql} LIMIT {limit}"

        # ----------------------------
        # Execute the query
        # ----------------------------
        query_job = bigquery_client.query(query)
        results = query_job.result()

        # ----------------------------
        # Get schema to identify spatial (GEOGRAPHY) fields
        # ----------------------------
        table_ref = bigquery_client.dataset(dataset_id, project=project_id).table(table_id)
        table_obj = bigquery_client.get_table(table_ref)
        geography_fields = [field.name for field in table_obj.schema if field.field_type.upper() == "GEOGRAPHY"]

        # ----------------------------
        # Process rows & handle spatial data
        # ----------------------------
        output_rows = []
        for row in results:
            row_dict = dict(row)
            for geo_field in geography_fields:
                wkt_value = row_dict.get(geo_field)
                if wkt_value:
                    try:
                        # Convert WKT to GeoJSON
                        geom = wkt.loads(wkt_value)
                        geojson_geom = mapping(geom)
                        # Store GeoJSON as geometry_id
                        geometry_id = await store_geometry({
                            "type": "FeatureCollection",
                            "features": [{
                                "type": "Feature",
                                "geometry": geojson_geom,
                                "properties": {}
                            }]
                        }, user_id=user_id)
                        row_dict[geo_field] = geometry_id  # Replace raw WKT with ID
                    except Exception as e:
                        row_dict[geo_field] = f"Error converting geometry: {str(e)}"

            output_rows.append(row_dict)

        return {
            "rows": output_rows,
            "query": query
        }

    except Exception as e:
        return {
            "error": "Failed to query BigQuery table.",
            "details": str(e),
            "query_attempted": query if 'query' in locals() else None
        }
