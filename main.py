from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

app = FastAPI()

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
    return render_template("index.html", request, title="Home Page", message="Welcome!")

# --- Start Server ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)