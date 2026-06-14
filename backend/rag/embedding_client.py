import os
from typing import List, Optional

import numpy as np
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from settings.paths import BACKEND_DIR

load_dotenv()