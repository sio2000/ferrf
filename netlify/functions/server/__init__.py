import sys
import os

# Add project root to path to import app
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from mangum import Mangum
from app import app

handler = Mangum(app)

