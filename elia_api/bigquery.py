import os
import logging
import base64
from google.cloud import bigquery
from elia_api.config import config


logger = logging.getLogger(__name__)

_bigquery_client = None  # Private instance


def init_bigquery():
    """
    Initialize BigQuery client using a base64-encoded JSON key from environment variable.
    """
    global _bigquery_client

    json_key_b64 = config.BIGQUERY_JSON_KEY_B64

    if json_key_b64:
        # Decode the base64 secret and write to a temp file
        temp_path = config.SERVICE_ACCOUNT_WRITE_PATH
        try:
            json_key = base64.b64decode(json_key_b64).decode("utf-8")
            with open(temp_path, "w") as f:
                f.write(json_key)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
            logger.info(f"Decoded service account key written to {temp_path} and set as GOOGLE_APPLICATION_CREDENTIALS.")
        except Exception as e:
            logger.error(f"Failed to decode or write service account key: {e}")
            raise RuntimeError("Failed to handle service account key.")
    else:
        logger.error("No service account key found for BigQuery client.")
        raise RuntimeError("No service account key found for BigQuery client.")

    # Initialize BigQuery client
    _bigquery_client = bigquery.Client()
    logger.info("BigQuery client initialized successfully.")


def get_bigquery_client():
    """
    Safely get the initialized BigQuery client.
    Raises error if not initialized.
    """
    if _bigquery_client is None:
        raise RuntimeError("BigQuery client not initialized. Call init_bigquery() first.")
    return _bigquery_client
