# Runtime — PaddleOCR (Spatial OCR)

Motor de OCR espacial baseado no **PaddleOCR**, oferecendo tanto uma **API HTTP** (FastAPI) quanto um **CLI direto** para execução via terminal. As respostas são estruturadas no formato compatível com o Azure Document Intelligence (incluindo `polygons` e `confidence` reais para cada palavra e linha).

---

## Estrutura de Arquivos

| Arquivo | Descrição |
|---|---|
| `cli.py` | CLI unificado com modos `raw` e `normalized` |
| `ocr.py` | Pipeline de processamento e normalização |
| `config.py` | Singleton do motor PaddleOCR (usado pela API) |
| `models.py` | Modelos Pydantic (schema Azure-like) |
| `app.py` | API FastAPI (`/analyze`, `/health`) |
| `__main__.py` | Entrypoint para `python -m local-runtimes.paddleocr` |

---

## Instalação

```powershell
# Instalar as dependências do Paddle no ambiente virtual
# Execute a partir da raiz do repositório
poetry run pip install paddlepaddle paddleocr pypdfium2 pillow
```

> **Nota:** Na primeira execução, o PaddleOCR baixa automaticamente os modelos de detecção e reconhecimento para o idioma configurado em `~/.paddlex/` e `~/.paddleocr/`.

---

## CLI — Execução Direta via Terminal

O CLI permite executar o PaddleOCR diretamente sem precisar subir o servidor HTTP. Ideal para testar documentos, inspecionar a saída bruta do motor e experimentar parâmetros.

```powershell
# Executando a partir da raiz do repositório
python -m local-runtimes.paddleocr --input <arquivo> [opções]
```

### Modos de operação

| Modo | Flag | Descrição |
|---|---|---|
| **Raw** | `--mode raw` (padrão) | Exibe a saída bruta do motor: cada detecção com texto, confiança e polígono. Para debug e inspeção. |
| **Normalized** | `--mode normalized` | Gera JSON estruturado no formato Azure Document Intelligence. |

### Exemplos de uso

```powershell
# Modo RAW — ver exatamente o que o PaddleOCR enxerga
python -m local-runtimes.paddleocr -i documento.pdf -m raw

# Modo RAW com parâmetros customizados (alta resolução, threshold mais agressivo)
python -m local-runtimes.paddleocr -i documento.pdf -m raw --det-limit-side-len 1280 --det-db-box-thresh 0.4

# Modo NORMALIZED — salvar resultado em arquivo JSON
python -m local-runtimes.paddleocr -i planilha.png -m normalized -o resultado.json

# Apenas uma página de um PDF
python -m local-runtimes.paddleocr -i edital.pdf --pages 3

# Intervalo de páginas
python -m local-runtimes.paddleocr -i edital.pdf --pages 1-5

# Usando GPU
python -m local-runtimes.paddleocr -i documento.pdf --gpu
```

### Parâmetros disponíveis

| Parâmetro | Default | Descrição |
|---|---|---|
| `--input`, `-i` | *(obrigatório)* | Caminho do arquivo (PDF ou imagem) |
| `--mode`, `-m` | `raw` | `raw` ou `normalized` |
| `--pages` | todas | Páginas a processar (`1`, `1-2`, `1,3,5`) |
| `--output`, `-o` | stdout | Arquivo de saída (modo normalized) |
| `--lang` | `pt` | Idioma do OCR |
| `--gpu` | off | Ativar aceleração GPU |
| `--dpi` | `150` | DPI para renderização de PDFs |
| `--det-limit-side-len` | `960` | Lado máximo da imagem de detecção. Valores maiores capturam textos pequenos, porém mais lentos |
| `--det-db-thresh` | `0.3` | Limiar de binarização para detecção de caixas |
| `--det-db-box-thresh` | `0.6` | Limiar de filtragem de caixas. Valores menores retornam mais detecções (incluindo ruído) |
| `--rec-batch-num` | `6` | Tamanho do lote de reconhecimento. Aumente ao usar GPU |

### Saída do modo raw

O modo raw exibe para cada detecção:
- **Texto** reconhecido
- **Confiança** (0.0 a 1.0)
- **Polígono** com 4 pontos (coordenadas `[x, y]` em pixels)

```
============================================================
SAÍDA BRUTA — PÁGINA 1
============================================================
[Tempo de inferência: 2.34s]
Formato detectado: PaddleOCR 3.x (dict)
Total de detecções: 221
------------------------------------------------------------
Detecção #1:
  Texto:      "ANÁLISE PRELIMINAR DE LICITAÇÃO"
  Confiança:  0.9987
  Polígono:   [[584, 10], [922, 10], [922, 28], [584, 28]]
------------------------------
```

---

## API HTTP — Servidor FastAPI

### Iniciar o servidor

```powershell
# Execução nativa (porta 10001)
poetry run uvicorn local-runtimes.paddleocr.app:app --host 127.0.0.1 --port 10001 --reload
```

### Docker

```powershell
cd local-runtimes/paddleocr
docker compose up -d
```

> O Docker Compose mapeia `~/.paddleocr` do host para evitar re-download dos modelos.

### Endpoint `/analyze`

- **Método:** `POST`
- **Corpo:** `multipart/form-data` com campo `file` (PDF ou imagem) e campo opcional `pages` (ex: `1-2`)
- **Retorno:** JSON no schema `AnalyzeResult` (compatível Azure Document Intelligence)

```powershell
# Exemplo com curl
curl -X POST http://127.0.0.1:10001/analyze -F "file=@documento.pdf" -F "pages=1-2"
```

### Endpoint `/health`

- **Método:** `GET`
- **Retorno:** `{"status": "healthy", "lang": "pt", "gpu": false}`
