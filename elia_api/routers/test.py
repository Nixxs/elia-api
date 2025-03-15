import logging
from elia_api.tools.data_access import list_available_tables
from typing import Dict, Any, Annotated
from elia_api.models.user import User
from fastapi import APIRouter, HTTPException, Depends
from elia_api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test/list-available-tables", response_model=Dict[str, Any])
async def test_list_available_tables(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Test route for calling the list_available_tables backend function.
    Useful for verifying BigQuery connection and schema fetching.
    """
    try:
        result = list_available_tables(map_data="")  # Call your backend tool directly
        print(result)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to run list_available_tables: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")
