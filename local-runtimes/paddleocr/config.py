import os

# Configurações do ambiente para o microserviço PaddleOCR
OCR_LANG = os.getenv("OCR_LANG", "pt")
USE_GPU = os.getenv("OCR_USE_GPU", "false").lower() in ("true", "1", "yes")

_ocr_instance = None

def get_ocr_instance():
    """Inicializa e retorna a instância única (Singleton) do PaddleOCR de forma lazy."""
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR
        device_str = "gpu" if USE_GPU else "cpu"
        print(f"Inicializando PaddleOCR (lang={OCR_LANG}, GPU={USE_GPU}, device={device_str})...")
        # Inicializa o PaddleOCR com MKLDNN desabilitado para evitar conflitos conhecidos com oneDNN/PIR no CPU
        _ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang=OCR_LANG,
            device=device_str,
            enable_mkldnn=False
        )
        print("PaddleOCR inicializado com sucesso!")
    return _ocr_instance
