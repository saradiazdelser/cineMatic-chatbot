# Context retrieval models
from typing import List, Optional, Union

from pydantic import BaseModel


class ContextRequest(BaseModel):
    """Request model for context retrieval."""

    text: str
    threshold: Optional[float] = None
    limit: Optional[int] = None
    indexes: List[Optional[str]] = []


class ContextDocument(BaseModel):
    """Document model for context retrieval."""

    document: str
    id: Optional[Union[str, int]] = None
    metadata: Optional[dict] = {}
    score: Optional[float] = None


class ContextDocumentList(BaseModel):
    """List of documents model for context retrieval."""

    documents: List[ContextDocument] = []
    index: Optional[str] = None
