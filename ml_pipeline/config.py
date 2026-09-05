import os
import logging

logger = logging.getLogger(__name__)

MODEL_MODE = os.environ.get("MODEL_MODE", "mock").lower()
if MODEL_MODE not in ["mock", "local", "external"]:
    logger.warning(f"Invalid MODEL_MODE '{MODEL_MODE}'. Falling back to 'mock'.")
    MODEL_MODE = "mock"

def get_provider(module_name: str, local_class: type, external_class: type, mock_class: type):
    """
    Returns an instance of the requested provider based on MODEL_MODE.
    Implements graceful fallback to 'mock' if 'local' or 'external' fail to initialize.
    """
    if MODEL_MODE == "local":
        try:
            # Check if local requirements are installed
            import torch
            import transformers
            return local_class()
        except ImportError as e:
            logger.warning(f"[{module_name}] Local model dependencies missing ({str(e)}). Falling back to MOCK mode.")
            return mock_class()
        except Exception as e:
            logger.warning(f"[{module_name}] Failed to initialize local model ({str(e)}). Falling back to MOCK mode.")
            return mock_class()
            
    elif MODEL_MODE == "external":
        try:
            return external_class()
        except Exception as e:
            logger.warning(f"[{module_name}] Failed to initialize external model ({str(e)}). Falling back to MOCK mode.")
            return mock_class()
            
    # Default to mock
    logger.info(f"[{module_name}] Using MOCK provider.")
    return mock_class()
