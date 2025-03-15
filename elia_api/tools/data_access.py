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

    This function provides a list of all tables in the BigQuery dataset, along with a description of each table's 
    schema. The AI can use this to understand what datasets are available when the user is asking to find data, 
    perform lookups, or query spatial or tabular information. This is useful when users ask questions like 
    "What data do you have?", "What datasets are available?", or "Find a dataset with XYZ fields."

    Returns:
        A dictionary containing:
            - tables: A list of available tables, where each entry includes:
                - table_name: The name of the table.
                - description: A description of the table's fields, including field names, types, and any available descriptions.

    Example response:
        {
            "tables": [
                {
                    "table_name": "parcels",
                    "description": "Table 'parcels' contains fields: id (STRING); geometry (GEOGRAPHY) - Parcel boundaries; area_ha (FLOAT64) - Area in hectares."
                },
                {
                    "table_name": "roads",
                    "description": "Table 'roads' contains fields: road_id (STRING); name (STRING); type (STRING) - Road type; geometry (GEOGRAPHY) - Road centerlines."
                }
            ]
        }

    Notes:
        - Use this function when the user asks what data is available or when selecting a table to run further spatial or attribute queries.
        - You (the AI) can use the field descriptions to guide users on what data can be queried from each table.
        - This function does not query any data itself — it only lists and describes what tables and fields are available.
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
async def query_table(table_name: str, where_clause: str = "", limit: int = 10, map_data: str = "", user_id: int = None) -> Dict[str, Any]:
    """
    Query a BigQuery table with an optional where clause, returning attribute data and spatial data as a geometry_id.

    If the table contains a 'GEOGRAPHY' column (as WKT), the geometry will be converted to GeoJSON, stored in the database, 
    and returned as a geometry_id. Use this to search for data and reference spatial features.

    Args:
        table_name: The name of the BigQuery table to query (from 'list_available_tables').
        where_clause: [Optional] A simple filter (e.g., 'column = "value"'). Case-insensitive.
        limit: [Optional] Max number of rows to return. Default is 10.
        map_data: [Provided automatically] Not used.

    Returns:
        - rows: List of records with any spatial data as geometry_id.
        - query: The SQL query that was run.

    Notes:
        - Spatial data is always returned as geometry_id, never raw geometry.
        - Use 'update_map_data' with geometry_id to display results.
    """

    project_id = "gen-lang-client-0136133024"
    dataset_id = "demo_data"
    MAX_LIMIT = 10  # Hard cap to prevent excessive querie

    try:
        # Get BigQuery client
        bigquery_client = get_bigquery_client()

        # Safely quote the table name
        full_table_name = f"`{project_id}.{dataset_id}.{table_name}`"

        # ✅ Ensure limit is an integer
        limit = min(MAX_LIMIT, max(1, int(limit)))

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

        # Get schema to check for GEOGRAPHY fields
        table_ref = bigquery_client.dataset(dataset_id, project=project_id).table(table_name)
        table_obj = bigquery_client.get_table(table_ref)
        geography_fields = [field.name for field in table_obj.schema if field.field_type.upper() == "GEOGRAPHY"]

        # Prepare rows output
        output_rows = []

        for row in results:
            row_dict = dict(row)

            # If GEOGRAPHY field exists, convert and store as GeoJSON
            for geo_field in geography_fields:
                wkt_value = row_dict.get(geo_field)
                if wkt_value:
                    try:
                        # Convert WKT to GeoJSON using Shapely
                        geom = wkt.loads(wkt_value)
                        geojson_geom = mapping(geom)

                        # Store as geometry and get ID
                        geometry_id = await store_geometry({
                            "type": "FeatureCollection",
                            "features": [
                                {
                                    "type": "Feature",
                                    "geometry": geojson_geom,
                                    "properties": {}  # Optional: you can decide to pass some properties
                                }
                            ]
                        }, user_id=user_id)

                        # Replace raw geometry with geometry_id
                        row_dict[geo_field] = geometry_id
                    except Exception as e:
                        row_dict[geo_field] = f"Error converting geometry: {str(e)}"

            output_rows.append(row_dict)

        return {
            "rows": output_rows,
            "query": query  # Let AI know what was actually run
        }

    except Exception as e:
        return {
            "error": "Failed to query BigQuery table.",
            "details": str(e),
            "query_attempted": query if 'query' in locals() else None  # Include query if it was built
        }
