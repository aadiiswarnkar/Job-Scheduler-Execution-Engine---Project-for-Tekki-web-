# In this file, we define the configuration settings for the job scheduler application, including database connection details.

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
