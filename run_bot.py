import asyncio
import subprocess
from dotenv import load_dotenv
import sys
import os

load_dotenv()

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Lancer Rasa dans un sous-processus
subprocess.Popen(["rasa", "run", "--enable-api"])
