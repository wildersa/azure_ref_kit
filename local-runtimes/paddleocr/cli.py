"""
CLI unificado do PaddleOCR.

Permite executar a análise OCR diretamente via terminal com controle total
sobre os parâmetros do motor, exibindo o processo e o resultado bruto.

Uso:
    python -m runtimes.paddleocr --input <arquivo> [opções]

Modos:
    --mode raw          Mostra a saída bruta do PaddleOCR (para debug/inspeção)
    --mode normalized   Gera o JSON normalizado no formato Azure Document Intelligence
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_page_indices(pages_str: str | None, total_pages: int) -> list[int]:
    """Parseia a string de páginas (ex: '1-2', '1,3') para índices 0-indexed."""
    if not pages_str:
        return list(range(total_pages))

    indices: list[int] = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start_str, end_str = part.split("-")
                start = max(0, min(int(start_str) - 1, total_pages - 1))
                end = max(0, min(int(end_str) - 1, total_pages - 1))
                indices.extend(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < total_pages:
                    indices.append(idx)
            except ValueError:
                pass

    seen: set[int] = set()
    return [x for x in indices if not (x in seen or seen.add(x))]


def _load_images(
    input_path: Path,
    pages_str: str | None,
    dpi: int,
) -> list[tuple[int, Image.Image]]:
    """Carrega as imagens a partir de um PDF ou arquivo de imagem."""
    import pypdfium2 as pdfium

    images: list[tuple[int, Image.Image]] = []

    if input_path.suffix.lower() == ".pdf":
        doc = pdfium.PdfDocument(str(input_path))
        total_pages = len(doc)
        target_indices = _parse_page_indices(pages_str, total_pages)
        print(
            f"  PDF com {total_pages} página(s), processando: "
            f"{[i + 1 for i in target_indices]}",
            file=sys.stderr,
        )
        for idx in target_indices:
            page = doc[idx]
            bitmap = page.render(scale=dpi / 72)
            images.append((idx + 1, bitmap.to_pil()))
    else:
        img = Image.open(str(input_path))
        images.append((1, img))

    return images


def _create_ocr_engine(args: argparse.Namespace):
    """Cria uma instância do PaddleOCR com os parâmetros informados no CLI."""
    from paddleocr import PaddleOCR

    device_str = "gpu" if args.gpu else "cpu"

    ocr = PaddleOCR(
        use_angle_cls=True,
        lang=args.lang,
        device=device_str,
        enable_mkldnn=False,
        det_limit_side_len=args.det_limit_side_len,
        det_db_thresh=args.det_db_thresh,
        det_db_box_thresh=args.det_db_box_thresh,
        rec_batch_num=args.rec_batch_num,
    )
    return ocr


# ---------------------------------------------------------------------------
# Modo RAW — saída bruta do motor para inspeção/debug
# ---------------------------------------------------------------------------


def _run_raw(args: argparse.Namespace) -> None:
    """Executa o OCR e imprime a saída bruta do PaddleOCR sem normalização."""
    input_path = Path(args.input).resolve()

    print("=" * 60, file=sys.stderr)
    print("PADDLEOCR CLI  —  MODO RAW (saída bruta)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    device_str = "gpu" if args.gpu else "cpu"
    print(f"  Arquivo:          {input_path.name}", file=sys.stderr)
    print(f"  Device:           {device_str}", file=sys.stderr)
    print(f"  Idioma:           {args.lang}", file=sys.stderr)
    print(f"  DPI renderização: {args.dpi}", file=sys.stderr)
    print(f"  det-limit-side:   {args.det_limit_side_len}", file=sys.stderr)
    print(f"  det-db-thresh:    {args.det_db_thresh}", file=sys.stderr)
    print(f"  det-db-box-thresh:{args.det_db_box_thresh}", file=sys.stderr)
    print(f"  rec-batch-num:    {args.rec_batch_num}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    print("\nInicializando motor PaddleOCR...", file=sys.stderr)
    try:
        ocr = _create_ocr_engine(args)
    except Exception as exc:
        print(f"\nErro ao inicializar PaddleOCR: {exc}", file=sys.stderr)
        if args.gpu:
            print(
                "\nDICA: Certifique-se de que 'paddlepaddle-gpu' e o CUDA "
                "estejam instalados.",
                file=sys.stderr,
            )
        sys.exit(1)

    print("Carregando imagens...", file=sys.stderr)
    images = _load_images(input_path, args.pages, args.dpi)
    print(
        f"Iniciando inferência em {len(images)} página(s)...\n", file=sys.stderr
    )

    for page_num, pil_img in images:
        print("=" * 60)
        print(f"SAÍDA BRUTA — PÁGINA {page_num}")
        print("=" * 60)

        img_np = np.array(pil_img.convert("RGB"))
        started = time.perf_counter()

        try:
            result = ocr.ocr(img_np)
        except Exception as exc:
            print(f"Erro na inferência da página {page_num}: {exc}", file=sys.stderr)
            continue

        elapsed = time.perf_counter() - started
        print(f"[Tempo de inferência: {elapsed:.2f}s]")
        print(f"DEBUG — Tipo do resultado: {type(result)}")

        if not result or not result[0]:
            print("Nenhum texto detectado na página.")
            print("-" * 60)
            continue

        page_data = result[0]

        # ----- PaddleOCR 3.x (PaddleX API): resultado é um dict -----
        if isinstance(page_data, dict):
            rec_texts = page_data.get("rec_texts", [])
            rec_scores = page_data.get("rec_scores", [])
            dt_polys = page_data.get("dt_polys", [])

            print(f"Formato detectado: PaddleOCR 3.x (dict)")
            print(f"Total de detecções: {len(rec_texts)}")
            print("-" * 60)

            for idx in range(len(rec_texts)):
                text = rec_texts[idx]
                confidence = float(rec_scores[idx]) if idx < len(rec_scores) else 0.0
                poly_np = dt_polys[idx] if idx < len(dt_polys) else []
                polygon = poly_np.tolist() if hasattr(poly_np, "tolist") else list(poly_np)

                print(f"Detecção #{idx + 1}:")
                print(f'  Texto:      "{text}"')
                print(f"  Confiança:  {confidence:.4f}")
                print(f"  Polígono:   {polygon}")
                print("-" * 30)

        # ----- PaddleOCR 2.x: resultado é lista de [polígono, (texto, score)] -----
        elif isinstance(page_data, list):
            print(f"Formato detectado: PaddleOCR 2.x (list)")
            print(f"Total de detecções: {len(page_data)}")
            print("-" * 60)

            for idx, detection in enumerate(page_data):
                poly_points = detection[0]
                text = detection[1][0]
                confidence = float(detection[1][1])

                polygon = (
                    [pt.tolist() if hasattr(pt, "tolist") else pt for pt in poly_points]
                    if poly_points
                    else []
                )

                print(f"Detecção #{idx + 1}:")
                print(f'  Texto:      "{text}"')
                print(f"  Confiança:  {confidence:.4f}")
                print(f"  Polígono:   {polygon}")
                print("-" * 30)

        else:
            print(f"Formato desconhecido: {type(page_data)}")
            print(f"Conteúdo: {page_data}")

    print("\n" + "=" * 60, file=sys.stderr)
    print("Processamento RAW concluído.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Modo NORMALIZED — saída no formato Azure Document Intelligence
# ---------------------------------------------------------------------------


def _run_normalized(args: argparse.Namespace) -> None:
    """Executa o OCR e gera o JSON normalizado no formato Azure-like."""
    input_path = Path(args.input).resolve()

    print("=" * 60, file=sys.stderr)
    print("PADDLEOCR CLI  —  MODO NORMALIZED (formato Azure)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"  Arquivo:  {input_path.name}", file=sys.stderr)
    print(f"  DPI:      {args.dpi}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # No modo normalized usamos o pipeline existente do módulo
    try:
        from .ocr import process_document_bytes
    except ImportError:
        from ocr import process_document_bytes

    print(f"\nProcessando '{input_path.name}'...", file=sys.stderr)

    file_bytes = input_path.read_bytes()
    started = time.perf_counter()
    result = process_document_bytes(
        file_bytes=file_bytes,
        filename=input_path.name,
        pages_str=args.pages,
    )
    elapsed = time.perf_counter() - started

    json_str = result.model_dump_json(by_alias=True, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_str, encoding="utf-8")
        print(
            f"Resultado salvo em: {out_path}  ({elapsed:.2f}s)",
            file=sys.stderr,
        )
    else:
        print(json_str)
        print(
            f"\n[Tempo total: {elapsed:.2f}s]",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paddleocr-cli",
        description=(
            "Executa o PaddleOCR diretamente via terminal.\n\n"
            "Dois modos de operação:\n"
            "  raw        — Exibe a saída bruta do motor (para inspeção/debug)\n"
            "  normalized — Gera JSON no formato Azure Document Intelligence"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Obrigatórios ---
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Caminho do arquivo de entrada (PDF ou imagem).",
    )

    # --- Modo de operação ---
    parser.add_argument(
        "--mode", "-m",
        choices=["raw", "normalized"],
        default="raw",
        help="Modo de saída: 'raw' para debug bruto, 'normalized' para JSON Azure-like. (default: raw)",
    )

    # --- Opções gerais ---
    parser.add_argument(
        "--pages",
        default=None,
        help="Páginas a processar (ex: '1', '1-2', '1,3'). Padrão: todas.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Caminho do arquivo JSON de saída (modo normalized). Se omitido, imprime no stdout.",
    )

    # --- Parâmetros do motor PaddleOCR ---
    engine = parser.add_argument_group("Parâmetros do Motor PaddleOCR")
    engine.add_argument(
        "--lang",
        default="pt",
        help="Idioma do OCR (default: pt).",
    )
    engine.add_argument(
        "--gpu",
        action="store_true",
        help="Forçar uso de GPU (requer paddlepaddle-gpu + CUDA).",
    )
    engine.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI para renderização de PDFs (default: 150).",
    )
    engine.add_argument(
        "--det-limit-side-len",
        type=int,
        default=960,
        help="Lado máximo da imagem de detecção. Valores maiores capturam textos pequenos, porém mais lentos. (default: 960)",
    )
    engine.add_argument(
        "--det-db-thresh",
        type=float,
        default=0.3,
        help="Limiar de binarização para detecção de caixas (default: 0.3).",
    )
    engine.add_argument(
        "--det-db-box-thresh",
        type=float,
        default=0.6,
        help="Limiar de filtragem de caixas (default: 0.6).",
    )
    engine.add_argument(
        "--rec-batch-num",
        type=int,
        default=6,
        help="Tamanho do lote de reconhecimento. Aumente se estiver usando GPU. (default: 6)",
    )

    return parser


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erro: Arquivo '{input_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    if args.mode == "raw":
        _run_raw(args)
    else:
        _run_normalized(args)


if __name__ == "__main__":
    main()
