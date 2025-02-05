import trafilatura
from typing import Dict, List
import re

def clean_text(text: str) -> str:
    """Clean and format scraped text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

def scrape_educational_content(url: str) -> Dict[str, str]:
    """
    Scrape educational content from given URL
    Returns a dictionary with title and content
    """
    try:
        # Download and extract content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"title": "", "content": "Failed to fetch content"}
        
        # Extract main content
        content = trafilatura.extract(downloaded, include_comments=False, 
                                    include_tables=True, no_fallback=False)
        
        # Extract title
        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata else "Educational Resource"
        
        return {
            "title": clean_text(title),
            "content": clean_text(content)
        }
    except Exception as e:
        return {
            "title": "Error",
            "content": f"Failed to scrape content: {str(e)}"
        }

def get_jee_resources() -> List[Dict[str, str]]:
    """
    Fetch content from predefined JEE preparation resources
    """
    resource_urls = [
        "https://jeemain.nta.nic.in/",
        "https://engineering.careers360.com/articles/jee-main-syllabus",
        "https://www.shiksha.com/engineering/jee-main-exam",
    ]
    
    resources = []
    for url in resource_urls:
        content = scrape_educational_content(url)
        if content["content"]:  # Only add if content was successfully scraped
            resources.append(content)
    
    return resources
