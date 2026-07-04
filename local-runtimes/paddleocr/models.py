from typing import Literal
from pydantic import BaseModel, Field

# Modelos Pydantic baseados no esquema do Azure Document Intelligence

class Span(BaseModel):
    offset: int
    length: int

class Word(BaseModel):
    content: str
    polygon: list[float] | None = None
    confidence: float | None = None
    span: Span

class Line(BaseModel):
    content: str
    polygon: list[float] | None = None
    spans: list[Span]

class Page(BaseModel):
    page_number: int = Field(alias="pageNumber")
    angle: float = 0.0
    width: float
    height: float
    unit: Literal["pixel", "inch"] = "pixel"
    words: list[Word] = Field(default_factory=list)
    lines: list[Line] = Field(default_factory=list)
    spans: list[Span] = Field(default_factory=list)

class Paragraph(BaseModel):
    content: str
    spans: list[Span]

class AnalyzeResult(BaseModel):
    api_version: str = Field(default="local-2026-01-01", alias="apiVersion")
    model_id: str = Field(default="paddleocr-local", alias="modelId")
    string_index_type: str = Field(default="unicodeCodePoint", alias="stringIndexType")
    content_format: str = Field(default="text", alias="contentFormat")
    content: str
    pages: list[Page] = Field(default_factory=list)
    paragraphs: list[Paragraph] = Field(default_factory=list)
