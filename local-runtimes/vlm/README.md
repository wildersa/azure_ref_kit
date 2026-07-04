# Runtime — VLM (Vision Language Model)

Microserviço que lê documentos através de um **modelo de linguagem com visão (VLM)**, como o **GLM-OCR**. O modelo recebe a imagem de uma página e retorna o texto extraído em formato plain text ou markdown.

A API exposta é compatível com o padrão **OpenAI Chat Completions** (`/v1/chat/completions`), podendo ser consumida por qualquer client OpenAI-compatible.

---

## Backends Disponíveis

Este runtime oferece **dois backends alternativos** para servir o mesmo modelo. Escolha o que faz sentido para o seu ambiente:

| Backend | Quando usar | Requisitos |
|---|---|---|
| **llama.cpp** | Máquina local com GPU NVIDIA e modelo GGUF | Docker + NVIDIA Container Toolkit |
| **vLLM** | Servidor com GPU NVIDIA e modelo HuggingFace | Docker + NVIDIA Container Toolkit |

Ambos expõem a API na **porta 10000**.

---

## Como Executar

### Opção 1: llama.cpp (modelos GGUF)

Ideal para rodar localmente com modelos quantizados.

**Pré-requisitos:**
- Arquivos GGUF do modelo na pasta configurada (default: `E:\ollamamodels`):
  - `GLM-OCR-Q8_0.gguf` (modelo principal)
  - `mmproj-GLM-OCR-Q8_0.gguf` (projetor de visão)

```powershell
cd local-runtimes/vlm
docker compose -f docker-compose.llama.yml up -d

# Verificar logs de carregamento
docker compose -f docker-compose.llama.yml logs -f
```

> **Nota:** Edite o volume em `docker-compose.llama.yml` para apontar para o caminho real dos seus modelos GGUF.

### Opção 2: vLLM (modelos HuggingFace)

Ideal para rodar em servidores com download direto do HuggingFace.

```powershell
cd local-runtimes/vlm

# Definir token HuggingFace (se necessário)
$env:HF_TOKEN = "seu-token-aqui"

docker compose -f docker-compose.vllm.yml up -d

# Verificar logs de carregamento
docker compose -f docker-compose.vllm.yml logs -f
```

---

## Endpoint

- **URL:** `http://127.0.0.1:10000/v1/chat/completions`
- **Formato:** OpenAI Chat Completions API
- **Modelo:** `zai-org/GLM-OCR` (ou o nome configurado no compose)

### Exemplo de chamada

```powershell
# Testar com uma imagem (base64)
$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("documento.png"))

$body = @{
    model = "zai-org/GLM-OCR"
    messages = @(@{
        role = "user"
        content = @(
            @{ type = "text"; text = "Text Recognition:" },
            @{ type = "image_url"; image_url = @{ url = "data:image/png;base64,$base64" } }
        )
    })
    temperature = 0
    max_tokens = 8192
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:10000/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body
```

---

## Estrutura de Arquivos

| Arquivo | Descrição |
|---|---|
| `docker-compose.llama.yml` | Deploy via llama.cpp (modelos GGUF locais) |
| `docker-compose.vllm.yml` | Deploy via vLLM (modelos HuggingFace) |
| `README.md` | Esta documentação |
