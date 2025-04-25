import os
import logging
from datetime import datetime
import hashlib
import trafilatura
from models import Document
from app import db

# Get logger
logger = logging.getLogger("pacs_assistant")

def extract_text_from_url(url):
    """
    Extract main text content from a URL using trafilatura.
    
    Args:
        url (str): URL to scrape
        
    Returns:
        str: Extracted text content
    """
    try:
        logger.info(f"Extracting content from URL: {url}")
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            logger.error(f"Failed to download content from URL: {url}")
            return None
            
        text = trafilatura.extract(downloaded)
        
        if not text:
            logger.warning(f"No meaningful text extracted from URL: {url}")
            return None
            
        logger.info(f"Successfully extracted content from URL: {url}")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting content from URL {url}: {str(e)}")
        return None


def process_document(title, content, document_type="webpage", source_url=None, description=None):
    """
    Process document content and store it in the database.
    
    Args:
        title (str): Document title
        content (str): Document content text
        document_type (str): Type of document (webpage, report, regulation, etc.)
        source_url (str): Source URL of the document
        description (str): Brief description of the document
        
    Returns:
        Document: Created document object
    """
    try:
        # Generate a unique vector ID based on content
        vector_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create a new document record
        document = Document(
            title=title,
            content=content,
            description=description or f"Document extracted from {document_type}",
            document_type=document_type,
            source_url=source_url,
            published_date=datetime.utcnow(),
            vector_id=vector_id
        )
        
        # Store in database
        db.session.add(document)
        db.session.commit()
        
        logger.info(f"Document stored in database: {title} (ID: {document.id})")
        return document
        
    except Exception as e:
        logger.error(f"Error storing document {title}: {str(e)}")
        db.session.rollback()
        raise


def process_document_from_url(url, title=None, document_type="webpage", description=None):
    """
    Process a document from a URL and store it in the database.
    
    Args:
        url (str): URL to process
        title (str): Document title (if None, will be extracted or use URL)
        document_type (str): Type of document (webpage, report, regulation, etc.)
        description (str): Brief description of the document
        
    Returns:
        Document: Created document object or None if processing failed
    """
    try:
        # Extract content from the URL
        content = extract_text_from_url(url)
        
        if not content:
            logger.error(f"No content extracted from URL: {url}")
            return None
            
        # Use URL as title if none provided
        if not title:
            # Try to extract title from content, or use URL
            try:
                # Take first line as title if it's reasonably short
                first_line = content.split('\n')[0].strip()
                if 10 <= len(first_line) <= 100:
                    title = first_line
                else:
                    title = url.split('/')[-1] or url
            except:
                title = url
        
        # Process the document
        document = process_document(
            title=title,
            content=content,
            document_type=document_type,
            source_url=url,
            description=description
        )
        
        return document
        
    except Exception as e:
        logger.error(f"Error processing document from URL {url}: {str(e)}")
        return None


def get_document_by_id(document_id):
    """
    Retrieve a document by its ID.
    
    Args:
        document_id (int): Document ID
        
    Returns:
        Document: Document object or None if not found
    """
    try:
        return Document.query.get(document_id)
    except Exception as e:
        logger.error(f"Error retrieving document ID {document_id}: {str(e)}")
        return None


def search_documents(query, limit=5):
    """
    Basic search for documents by title and content.
    
    Args:
        query (str): Search query
        limit (int): Maximum number of results
        
    Returns:
        list: List of Document objects matching the query
    """
    try:
        # Simple search by title and content
        search_term = f"%{query}%"
        documents = Document.query.filter(
            (Document.title.ilike(search_term)) | 
            (Document.content.ilike(search_term))
        ).order_by(Document.published_date.desc()).limit(limit).all()
        
        return documents
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return []