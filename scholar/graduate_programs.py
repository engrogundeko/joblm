from .discoveryhub import DiscoveryHubScraper
from app_write import AppwriteClient
import hashlib
from appwrite.query import Query

db = AppwriteClient()


class GraduateScraper(DiscoveryHubScraper):
    def __init__(self):
        super().__init__()  # Call parent's __init__ first
        self.base_url = "https://dixcoverhub.com.ng/category/graduate-programs/"

    async def is_new_scholarship(self, scholarship_text: dict) -> bool:
        
        """Check if a scholarship is new by looking up its hash in Appwrite"""
        try:
            title = scholarship_text.get("title", "")
            link = scholarship_text.get("link", "")
            text = f"{title}{link}"
            content_hash = hashlib.md5(text.encode()).hexdigest()
            
            result = await db.list_documents(
                collection_id="internships",
                queries=[Query.equal("content_hash", content_hash)]
            )
            
            # If no documents match the hash, the scholarship is new.
            return len(result.get("documents", [])) == 0
        except Exception as e:
            logger.error(f"Error checking scholarship history: {str(e)}")
            return True

    async def save_scholarship(self, scholarship_text: dict):
        """Save a scholarship to Appwrite database"""
        title = scholarship_text.get("title", "")
        link = scholarship_text.get("link", "")
        text = f"{title}{link}"
        content_hash = hashlib.md5(text.encode()).hexdigest()
        
        try:
            # Create document in Appwrite
            document_data = {
                    'content': scholarship_text.get("content", ""),
                    'title': title,
                    'link': link,
                    "application_link": scholarship_text.get("application_link", ""),
                    'content_hash': content_hash
                }
            db.create_document(
                collection_id="internships",
                document_id=self.generate_scholarship_id(scholarship_text),
                data=document_data
            )
            print(f"Saved scholarship: {title}")
        except Exception as e:
            print(f"Error saving scholarship: {str(e)}")

class InternshipScraper(GraduateScraper):
    def __init__(self):
        super().__init__()  # Call parent's __init__ first
        self.base_url = "https://dixcoverhub.com.ng/category/internships/"

   