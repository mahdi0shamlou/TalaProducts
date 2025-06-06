from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import configparser
from sqlalchemy import create_engine
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import requests
import json
from models import Products
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from fastapi import Form, File, UploadFile  # Add Form here
from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
import os
import time
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

# Initialize templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    req_url = "https://www.tala.ir/banner/?rnd=lUYlwLPFSA&ids=1001,&is-mobile=0&android=0&ios=0&rnd=1263&h=1080&w=1920"
    header = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
        "Cookie": "PHPSESSID=713ita9n0bg96lctoigkse83ih; _trc=17490238888010691083622c563813e1f1d85119d6; MEDIAAD_USER_ID=d5628e49-21e2-469c-96d1-8284ff30138d; _ga=GA1.2.815158700.1749023889; _gid=GA1.2.1498362061.1749023889"
    }
    try:
        req_response = requests.get(req_url, headers=header)
        req_response.raise_for_status()  # Raises an exception for HTTP errors
        req_response_json = req_response.json()  # Direct method to get JSON
        print(req_response_json)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    products = db.query(Products).all()
    tala = int(req_response_json['price']['geram18'].replace(',', ''))

    # Convert ORM objects to a list of dictionaries
    product_list = [
        {
            "id": product.id,
            "name_product": product.name_product,
            "profit": product.profit,
            "fee": product.fee,
            "price": round((tala * ((product.fee+100)/100) * ((product.profit+100)/100) * product.weight)),
            "weight": product.weight,
            "image_address": product.image_address,
            "text_def" : f"<br> سلام مهر بی کران اجرت: {product.fee} + {product.profit} <br> وزن : {product.weight} <br> قیمت هر عدد در این لحظه : {round((tala * ((product.fee+100)/100) * ((product.profit+100)/100) * product.weight))} تومان"
        }
        for product in products
    ]
    return templates.TemplateResponse("index.html", {"request": request, "products": product_list, "Tala": tala})


# Create upload directory if not exists
UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/Add", response_class=HTMLResponse)
async def show_add_form(request: Request):
    return templates.TemplateResponse("add_product.html", {"request": request})


@app.post("/Add", response_class=HTMLResponse)
async def create_product(
        request: Request,
        name_product: str = Form(...),  # Use Form(...) for form fields
        fee: float = Form(...),
        profit: float = Form(...),
        weight: int = Form(...),
        image: UploadFile = File(...),  # File upload remains unchanged
        db: Session = Depends(get_db)
):
    try:
        # Input Validation
        if len(name_product.strip()) < 3:
            return templates.TemplateResponse(
                "add_product.html",
                {"request": request, "error": "Product name must be at least 3 characters"},
                status_code=400
            )

        if fee < 0 or profit < 0 or weight < 1:
            return templates.TemplateResponse(
                "add_product.html",
                {"request": request, "error": "Invalid numeric values"},
                status_code=400
            )

        # Validate image
        if not image.content_type.startswith('image/'):
            return templates.TemplateResponse(
                "add_product.html",
                {"request": request, "error": "Invalid image file type"},
                status_code=400
            )

        # Generate secure filename
        file_extension = os.path.splitext(image.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
            return templates.TemplateResponse(
                "add_product.html",
                {"request": request, "error": "Unsupported image format"},
                status_code=400
            )

        safe_filename = f"{int(time.time())}_{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save image
        with open(file_path, "wb") as buffer:
            content = await image.read()
            if len(content) > 5 * 1024 * 1024:  # 5MB limit
                return templates.TemplateResponse(
                    "add_product.html",
                    {"request": request, "error": "File size exceeds 5MB limit"},
                    status_code=400
                )
            buffer.write(content)

        # Create product
        db_product = Products(
            name_product=name_product,
            fee=int(fee),  # Store as cents
            profit=int(profit),
            weight=weight,
            image_address=f"/static/images/{safe_filename}"
        )

        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Redirect using Response
        return Response(
            status_code=302,
            headers={"Location": "/"}
        )

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "add_product.html",
            {"request": request, "error": f"An error occurred: {str(e)}"},
            status_code=500
        )

@app.post("/delete")
async def delete_product(request: Request, id: int = Form(...), db: Session = Depends(get_db)):
    """Delete product by ID"""
    product = db.query(Products).filter(Products.id == id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- Start Server ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG
    )