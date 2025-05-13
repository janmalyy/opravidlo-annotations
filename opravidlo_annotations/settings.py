import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

KONTEXT_TOKEN = os.getenv("KONTEXT_TOKEN")
SKETCH_ENGINE_TOKEN = os.getenv("SKETCH_ENGINE_TOKEN")
SKETCH_ENGINE_USERNAME = os.getenv("SKETCH_ENGINE_USERNAME")

OPRAVIDLO_DIR = Path(__file__).parent.parent  # \your\home\directory\opravidlo_annotations\
