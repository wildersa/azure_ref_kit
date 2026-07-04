import io
import re
import time
import numpy as np
from PIL import Image
import pypdfium2 as pdfium

try:
    from .config import get_ocr_instance
    from .models import AnalyzeResult, Page, Line, Word, Paragraph, Span
except ImportError:
    from config import get_ocr_instance
    from models import AnalyzeResult, Page, Line, Word, Paragraph, Span

def get_page_indices(pages_str: str | None, total_pages: int) -> list[int]:
    """Parseia a string de páginas (ex: '1-2', '1,3') para índices 0-indexed."""
    if not pages_str:
        return list(range(total_pages))
    
    indices = []
    parts = pages_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start_str, end_str = part.split("-")
                start = int(start_str) - 1
                end = int(end_str) - 1
                start = max(0, min(start, total_pages - 1))
                end = max(0, min(end, total_pages - 1))
                indices.extend(list(range(start, end + 1)))
            except ValueError:
                pass
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < total_pages:
                    indices.append(idx)
            except ValueError:
                pass
    seen = set()
    return [x for x in indices if not (x in seen or seen.add(x))]

def process_document_bytes(
    file_bytes: bytes, 
    filename: str, 
    pages_str: str | None = None
) -> AnalyzeResult:
    """Executa o pipeline do PaddleOCR na imagem/PDF e normaliza para o formato do Azure."""
    start_time = time.perf_counter()
    filename_lower = filename.lower()
    
    images_to_process: list[tuple[int, Image.Image]] = []
    
    try:
        if filename_lower.endswith(".pdf"):
            doc = pdfium.PdfDocument(file_bytes)
            total_pages = len(doc)
            target_indices = get_page_indices(pages_str, total_pages)
            
            for idx in target_indices:
                page = doc[idx]
                bitmap = page.render(scale=150 / 72)
                pil_img = bitmap.to_pil()
                images_to_process.append((idx + 1, pil_img))
        else:
            pil_img = Image.open(io.BytesIO(file_bytes))
            images_to_process.append((1, pil_img))
    except Exception as exc:
        raise ValueError(f"Erro ao ler arquivo de entrada: {exc}")

    # Obtém singleton do OCR de forma lazy
    ocr = get_ocr_instance()
    
    global_content = ""
    normalized_pages: list[Page] = []
    paragraphs: list[Paragraph] = []
    
    for page_number, pil_img in images_to_process:
        img_np = np.array(pil_img.convert("RGB"))
        width, height = pil_img.size
        
        try:
            ocr_result = ocr.ocr(img_np)
        except Exception as exc:
            print(f"Erro na execução do PaddleOCR na página {page_number}: {exc}")
            ocr_result = None

        page_lines: list[Line] = []
        page_words: list[Word] = []
        page_text_blocks: list[str] = []
        
        page_start_offset = len(global_content)
        
        if ocr_result and ocr_result[0]:
            if isinstance(ocr_result[0], dict):
                # PaddleOCR 3.x (PaddleX API)
                page_res = ocr_result[0]
                rec_texts = page_res.get("rec_texts", [])
                rec_scores = page_res.get("rec_scores", [])
                rec_polys = page_res.get("dt_polys", [])
                
                detections = []
                for i in range(len(rec_texts)):
                    poly = rec_polys[i]
                    poly_points = poly.tolist() if hasattr(poly, "tolist") else poly
                    if len(poly_points) >= 4:
                        detections.append((poly_points[:4], (rec_texts[i], rec_scores[i])))
            else:
                # PaddleOCR 2.x
                detections = ocr_result[0]
            
            for detection in detections:
                poly_points = detection[0]
                text_content = detection[1][0]
                confidence = float(detection[1][1])
                
                line_polygon = [coord for pt in poly_points for coord in pt]
                
                if page_text_blocks:
                    global_content += "\n"
                
                line_offset = len(global_content)
                global_content += text_content
                line_length = len(text_content)
                
                line_span = Span(offset=line_offset, length=line_length)
                
                page_lines.append(
                    Line(
                        content=text_content,
                        polygon=line_polygon,
                        spans=[line_span]
                    )
                )
                page_text_blocks.append(text_content)
                
                pt0, pt1, pt2, pt3 = poly_points
                line_char_count = len(text_content)
                
                for word_match in re.finditer(r"\S+", text_content):
                    word_str = word_match.group()
                    start_char = word_match.start()
                    end_char = word_match.end()
                    
                    word_global_offset = line_offset + start_char
                    word_length = end_char - start_char
                    
                    t1 = start_char / line_char_count
                    t2 = end_char / line_char_count
                    
                    top_left = [pt0[0] + t1 * (pt1[0] - pt0[0]), pt0[1] + t1 * (pt1[1] - pt0[1])]
                    top_right = [pt0[0] + t2 * (pt1[0] - pt0[0]), pt0[1] + t2 * (pt1[1] - pt0[1])]
                    bottom_right = [pt3[0] + t2 * (pt2[0] - pt3[0]), pt3[1] + t2 * (pt2[1] - pt3[1])]
                    bottom_left = [pt3[0] + t1 * (pt2[0] - pt3[0]), pt3[1] + t1 * (pt2[1] - pt3[1])]
                    
                    word_polygon = [
                        top_left[0], top_left[1],
                        top_right[0], top_right[1],
                        bottom_right[0], bottom_right[1],
                        bottom_left[0], bottom_left[1]
                    ]
                    
                    page_words.append(
                        Word(
                            content=word_str,
                            polygon=word_polygon,
                            confidence=confidence,
                            span=Span(offset=word_global_offset, length=word_length)
                        )
                    )
                    
        if len(images_to_process) > 1 and page_number < images_to_process[-1][0]:
            global_content += "\n\n"
            
        page_end_offset = len(global_content)
        
        # Cria a página estruturada
        normalized_pages.append(
            Page(
                pageNumber=page_number,
                width=float(width),
                height=float(height),
                words=page_words,
                lines=page_lines,
                spans=[Span(offset=page_start_offset, length=page_end_offset - page_start_offset)]
            )
        )
        
        # Agrupa parágrafos heuristicamente
        page_text = "\n".join(page_text_blocks)
        for para_match in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", page_text, re.S):
            para_text = para_match.group()
            para_start_rel = para_match.start()
            para_end_rel = para_match.end()
            
            para_global_offset = page_start_offset + para_start_rel
            para_length = para_end_rel - para_start_rel
            
            paragraphs.append(
                Paragraph(
                    content=para_text,
                    spans=[Span(offset=para_global_offset, length=para_length)]
                )
            )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(f"Processamento concluído em {elapsed_ms:.2f} ms")
    
    return AnalyzeResult(
        apiVersion="local-2026-01-01",
        modelId="paddleocr-local",
        stringIndexType="unicodeCodePoint",
        contentFormat="text",
        content=global_content,
        pages=normalized_pages,
        paragraphs=paragraphs,
    )
