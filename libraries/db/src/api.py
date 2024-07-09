# FastAPI to access qdrant database
import logging
import sys
from pathlib import Path
from typing import Dict, List, Union

from fastapi import FastAPI

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.model import ContextDocument, ContextDocumentList, ContextRequest
from src.qdrant import ContextRetriever

logger = logging.getLogger(__name__)

db_manager = ContextRetriever(url="http://qdrant:6333", collection="documents")

db = FastAPI()  # Set up server


@db.post("/add_documents", tags=["db"])
async def add_documents(request: ContextDocumentList) -> List[str]:
    """Add documents to the database.
    Args:
        request (ContextDocumentList): List of documents to add.
    Returns:
        List[str]: List of document ids added to the database.
    """
    # Load documents
    documents, metadata = zip(
        *[(doc.document, doc.metadata) for doc in request.documents]
    )
    # make sure metadata is not None
    ids = db_manager.add_documents(documents, metadata, index=request.index)
    logger.info(f"Loaded {len(request.documents)} documents: {ids}")
    return ids


@db.post("/search", tags=["db"])
async def search(request: ContextRequest) -> List[ContextDocument]:
    # Retrieve documents
    response = db_manager.search(
        request.text,
        threshold=request.threshold,
        limit=request.limit,
        indexes=request.indexes,
    )
    logger.info(f"Retrieved {len(response)} documents.")
    return response


@db.delete("/delete_documents", tags=["db"])
async def delete_documents(request: ContextDocumentList):
    # Retrieve documents
    documents = [
        db_manager.search(text, threshold=1, limit=1, index=request.index)[0]
        for text in request.documents
    ]
    document_ids = [doc.id for doc in documents]
    # Delete documents
    db_manager.delete_documents(document_ids=document_ids, index=request.index)
    return
