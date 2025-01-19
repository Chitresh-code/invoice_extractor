import fitz  # PyMuPDF
from src.logger import setup_logger  # Import the logger
from typing import Optional  # Import Optional for type hinting

logger = setup_logger(__name__)  # Set up the logger

def pdf_to_image_dict(pdf_path: str) -> Optional[dict]:
    """Converts a PDF file to a dictionary of images."""
    image_dict = {}
    
    # Open the PDF file
    try:
        pdf_document = fitz.open(pdf_path)
        logger.info(f"Loaded the pdf document {pdf_path} having {len(pdf_document)} pages.")
    except Exception as e:
        logger.error(f"Error opening PDF file: {e}")  # Log the error
        return None
    
    try:
        # Loop through each page
        for page_number in range(len(pdf_document)):
            logger.info(f"Processing page number: {page_number}")
            page = pdf_document[page_number]
            # Convert the page to a pixmap (image)
            pixmap = page.get_pixmap()
            
            # Save the pixmap as an image in the dictionary
            image_dict[page_number] = pixmap.tobytes("png")  # Save as PNG bytes
            logger.info(f"Processed '{page_number}' page succesfully")
    except Exception as e:
        logger.error(f"Error processing page {page_number}: {e}")  # Log the error
    
    pdf_document.close()  # Close the PDF document
    logger.info("Closing the pdf file")
    return image_dict  # Return the dictionary of images
