from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("KEY")
algorithm = os.getenv("ALGORITHM")