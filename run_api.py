"""Punto de entrada uvicorn — dev local con reload, producción vía Procfile."""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    dev = os.getenv("RAILWAY_ENVIRONMENT") is None
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=dev,
        reload_dirs=["src"] if dev else [],
    )
