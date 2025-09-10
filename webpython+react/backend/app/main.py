from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .database import engine, Base
from .routers import auth, scripts, admin, amazon, proxies, gates
from .config import settings

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Script Execution Platform",
    description="Plataforma para ejecutar scripts Python y PHP con sistema de autenticación",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para hosting web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(scripts.router)
app.include_router(admin.router)
app.include_router(amazon.router)
app.include_router(proxies.router)
app.include_router(gates.router)

@app.get("/")
async def root():
    return {"message": "Script Execution Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Servir frontend estático compilado (opcional)
# Montar assets estáticos del build de React si existen
frontend_static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build", "static"))
frontend_index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build", "index.html"))

if os.path.isdir(frontend_static_dir) and os.path.isfile(frontend_index_path):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

    @app.get("/app", response_class=HTMLResponse)
    async def serve_frontend_app():
        try:
            with open(frontend_index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), media_type="text/html")
        except Exception:
            # Si falla, devolver un mensaje simple
            return HTMLResponse(content="<h1>Frontend no disponible</h1>", status_code=503)
