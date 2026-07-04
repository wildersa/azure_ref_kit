from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

try:
    from .config import OCR_LANG, USE_GPU
    from .models import AnalyzeResult
    from .ocr import process_document_bytes
except ImportError:
    from config import OCR_LANG, USE_GPU
    from models import AnalyzeResult
    from ocr import process_document_bytes

app = FastAPI(
    title="PaddleOCR Local Microservice",
    description="Microserviço local de OCR que expõe a API do PaddleOCR no formato compatível com o Azure Document Intelligence",
    version="1.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "lang": OCR_LANG, "gpu": USE_GPU}

@app.post("/analyze", response_model=AnalyzeResult)
async def analyze_document(
    file: UploadFile = File(...),
    pages: str | None = Form(None),
):
    try:
        file_bytes = await file.read()
        return process_document_bytes(
            file_bytes=file_bytes, 
            filename=file.filename or "document.bin", 
            pages_str=pages
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro inesperado no servidor: {exc}")
