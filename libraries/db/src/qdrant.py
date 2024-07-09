# Retrieval module for chatbot using qdrant for similarity search
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional

from qdrant_client import QdrantClient, conversions
from qdrant_client.fastembed_common import QueryResponse
from qdrant_client.models import PointIdsList

from src.model import ContextDocument, ContextDocumentList

logger = logging.getLogger(__name__)


class ContextRetriever:
    """
    A class to manage retrieval of data using QdrantClient.
    Attributes:
        collection (str): The name of the collection in the QdrantClient.
        models_dir (str): Directory to store embedding models.
        device (str): Device to run the embedding model on.
    Methods:
        initialize(): Initialize the QdrantClient and collection.
        load(document): Load a document into the vectorstore.
        query(question, threshold): Query the vector store for a question.
        delete(uuid): Delete a document by uuid.
    """

    def __init__(
        self,
        models_dir: str = ".cache",
        device: str = "cpu",
        collection: str = "documents",
        url: str = "http://qdrant:6333",
    ):
        """
        Initialize the ContextRetriever instance.
        Args:
            models_dir (str): Directory to store embedding models. Defaults to ".cache".
            device (str): Device to run the embedding model on. Defaults to "cpu".
            collection (str): The name of the collection in the QdrantClient. Defaults to "documents".
            url (str): Url to client server.
        This uses FastEmbedding's default model (BAAI/bge-small-en-v1.5), which built for speed and efficiency.
        """
        # embedding settings
        self.models_dir = models_dir
        self.device = device

        # client and collection
        self.url = url
        self.client: QdrantClient = None
        self.collection = None
        self.collection_name = collection

        self.initialize()  # Initialize client and collection

    def __init_client(self):
        """Initialize QdrantClient."""
        self.client = QdrantClient(url=self.url)
        logger.debug("Initialized Qdrant Client")

    def __init_collection(self, collection_name: str):
        """Check if collection exists, if not, create it."""
        if self.client.collection_exists(collection_name=collection_name) == False:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=self.client.get_fastembed_vector_params(),
                sparse_vectors_config=self.client.get_fastembed_sparse_vector_params(),
            )
            logger.info(f"Created new collection for retrieval {self.collection_name}")

    def __load_documents(
        self, documents: list, metadata: list, collection_name: str
    ) -> list:
        """Load documents into the vectorstore collection.
        Args:
            documents (list): List of documents
            metadata (list): List of metadata for each document
            collection_name (str): Name of the collection to load the documents into.

        Returns:
            id (list): List of ids of the documents just added.
        """
        ids = self.client.add(
            collection_name=collection_name, documents=documents, metadata=metadata
        )  # creates a collection if it does not already exist

        return ids

    def __query(
        self, question: str, threshold: float, limit: int, collection_name: str = None
    ) -> List[QueryResponse]:
        """Query the vector store by question."""
        hits = self.client.query(
            collection_name=collection_name,
            query_text=question,
            limit=limit,
            score_threshold=threshold,
        )

        logger.info(f"Found relevant documents for question: {question}")
        logger.debug(
            "\n".join(
                [
                    f"[{i}] Content: {hit.document} | Metadata: {hit.metadata} | Score: {hit.score}"
                    for i, hit in enumerate(hits)
                ]
            )
        )
        return hits

    def __delete_documents(self, document_ids: List[str], collection_name: str):
        res = self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(
                points=document_ids,
            ),
        )
        logger.info(f"Deleted document with id {document_ids}. Operation result: {res}")

    def __generate_metadata(
        self, collection_name: str, documents: List[str], metadata: Optional[List[Dict]]
    ) -> List[Dict]:
        internal_metadata = [
            {"timestamp": datetime.now().timestamp(), "collection": collection_name}
            for i in range(len(documents))
        ]
        # Add internal metadata to the metadata if it exists
        if metadata:
            assert len(metadata) == len(
                documents
            )  # check if metadata is same length as documents

            logger.debug(f"Adding metadata to documents: {metadata}")
            metadata = [
                {**metadata[i], **internal_metadata[i]} for i in range(len(metadata))
            ]
        else:
            metadata = internal_metadata

        # check if metadata is same length as documents
        assert len(metadata) == len(metadata)
        return metadata

    def initialize(self, collection_name: str = None):
        """Initialize the ContextRetriever."""
        try:
            collection_name = collection_name or self.collection_name

            self.__init_client()
            self.__init_collection(collection_name=collection_name)
        except Exception as e:
            logger.error(
                f"Qdrant server could not be reached. {traceback.format_exc()}"
            )

    def create_index(self, name: str):
        self.__init_collection(collection_name=name)

    def add_documents(
        self,
        chunks: List[str],
        metadata: Optional[List[dict]] = None,
        index: Optional[str] = None,
    ) -> List[str]:
        """Add documents to the collection
        Args:
            chunks (List[str]): List of documents
            metadata (Optional[List[dict]]): List of metadata for each document
            index (Optional[str]): Name of the collection to load the documents into. Defaults to the collection_name set during initialization.
        """
        collection_name = index or self.collection_name

        # Generate metadata
        metadata = self.__generate_metadata(collection_name, chunks, metadata)

        # Load documents
        ids = self.__load_documents(
            documents=chunks, metadata=metadata, collection_name=collection_name
        )
        logger.debug("Stored documents in vectorstore.")
        return ids

    def search(
        self,
        text: str,
        threshold: Optional[float] = 0.95,
        limit: Optional[int] = 3,
        indexes: Optional[List[str]] = [],
    ) -> List[ContextDocumentList]:
        """Query the vectorstore.
        Args:
            text (str): The query text.
            threshold (Optional[float]): Maximum score. Defaults to 0.95.
            limit (Optional[int]): Maximum number of results to return. Defaults to 3.
            indexes (Optional[List[str]]): List of collection names to query. Defaults to the collection_name set during initialization.
        """
        collection_names = indexes or [self.collection_name]
        results = []
        for collection in collection_names:
            metadata = {"collection": collection}
            if not self.client.collection_exists(collection_name=collection):
                logger.error(f"Collection {collection} does not exist.")
                continue

            hits = self.__query(
                text, threshold=threshold, limit=limit, collection_name=collection
            )
            if hits:
                # Convert hits to ContextDocument
                documents = [ContextDocument(**hit.model_dump()) for hit in hits]
                # Remove docuement from docs's metadata
                for doc in documents:
                    doc.metadata.pop("document", None)
                # Add collection hits to the results
                results.extend(documents)
                logger.info(
                    f"Found {len(documents)} relevant documents in collection {collection}"
                )
            else:
                logger.info(f"No relevant documents found in collection {collection}")
        return results

    def delete_documents(self, document_ids: List[str], index: Optional[str] = None):
        """Delete a document fron the vectorstore by it's uuid.
        Args:
            document_ids (List[str]): List of UUID of the document to delete
            index (Optional[str]): Name of the collection to delete the document from. Defaults to the collection_name set during initialization.
        """
        collection_name = index or self.collection_name
        self.__delete_documents(document_ids, collection_name)
        logger.debug(
            f"Deleted documents with ids {document_ids} from {collection_name}"
        )
