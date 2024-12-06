from bs4 import BeautifulSoup
from .scraper import ScholarshipScraper



class DiscoveryHubScraper(ScholarshipScraper):
    def __init__(self):
        super().__init__()  # Call parent's __init__ first
        # Override base_url if needed, but it's already set in parent class
        # self.base_url = "https://dixcoverhub.com.ng/category/scholarship"

    async def parse_scholarship(self, soup: BeautifulSoup):
        scholarships = []
        main_tag = soup.find("main")
        if main_tag:  # Check if a <main> tag is found
            for li in main_tag.find_all("li"):
                title = li.find("h2")
                # date = li.find("time")
                link = li.find("a")
                if title and link:
                    # Convert HTML to markdown and clean
                    content = self.to_md(str(li))
                    # First remove unwanted sections
                    content = self.remove_string(content)
                    # Then clean up formatting
                    cleaned_content = self.clean_content(content)

                    scholarship = {
                        "title": title.text.strip(),
                        # "date": date.text.strip(),
                        "link": link["href"],
                        "content": cleaned_content
                    }
                    scholarships.append(scholarship)
        return scholarships

    # @override
    def remove_string(self, content: str) -> str:
        """Remove 'Also Apply:' section and everything after it"""
        if not content:
            return ""
            
        # List of variations to check
        variations = [
            "Also Apply:",
            "Also apply:",
            "ALSO APPLY:",
            "Also Apply For:",
            "Also Apply for:",
            "Also Check:",
            "ALSO CHECK:",
            "Also check:",
            "Apply Here:",
            "APPLY HERE:",
            "Apply here:"
        ]
        
        # Find the earliest occurrence of any variation
        earliest_pos = len(content)
        for variant in variations:
            pos = content.find(variant)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                
        # If any variation was found, truncate the content
        if earliest_pos < len(content):
            content = content[:earliest_pos].strip()
            
        return content
