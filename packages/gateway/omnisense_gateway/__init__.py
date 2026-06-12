"""FastAPI gateway for OmniSense Runtime."""

from omnisense_gateway.app import create_app
from omnisense_gateway.state import GatewayState

__all__ = ["GatewayState", "create_app"]
