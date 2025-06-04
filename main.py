from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from models import Products

config = configparser.ConfigParser()
config.read('Config.ini')

# Get API configuration
API_HOST = config.get('api', 'host', fallback='0.0.0.0')
API_PORT = config.getint('api', 'port', fallback=8585)
API_DEBUG = config.getboolean('api', 'debug', fallback=False)
API_TITLE = config.get('api', 'title', fallback='FastAPI App')
API_DESCRIPTION = config.get('api', 'description', fallback='')

# Database Config
DB_USER = config.get('mysql', 'user')
DB_PASSWORD = config.get('mysql', 'password')
DB_HOST = config.get('mysql', 'host')
DB_PORT = config.get('mysql', 'port', fallback='3306')
DB_NAME = config.get('mysql', 'database')

# Build SQLAlchemy URI
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create FastAPI app with config values
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    debug=API_DEBUG
)

# Mount static directory (for CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML Templates directory
TEMPLATE_DIR = Path("templates")

def render_template(template_name: str, request: Request, **context):
    """Flask-like template renderer"""
    with open(TEMPLATE_DIR / template_name) as f:
        content = f.read()
    # Simple template context replacement
    for key, value in context.items():
        content = content.replace("{{ " + key + " }}", str(value))
    return HTMLResponse(content)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with template rendering"""
    list_products = []

    return render_template("index.html", request, title="Home Page", message="Welcome!")


@app.get("/Add", response_class=HTMLResponse)
async def home(request: Request):
    """create a new products"""
    pass

@app.get("/Delete", response_class=HTMLResponse)
async def home(request: Request):
    """get an id and delete form db"""
    pass

# --- Start Server ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG
    )