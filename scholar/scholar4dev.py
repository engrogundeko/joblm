import pprint

from sqlalchemy.sql.ddl import exc
from .scraper import ScholarshipScraper
from .agent import run_scholarship, run_scholarship_list
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from pprint import pprint


class Scholarship4Dev(ScholarshipScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.scholars4dev.com/category/level-of-study/masters-scholarships/"


    def to_markdown(self, html_content: BeautifulSoup, class_name="post clearfix"):
        # if isinstance(html_content, BeautifulSoup):
        main_div = html_content.find_all('div', class_=class_name)
        if main_div:
            html_content = str(main_div)
            content = md(html_content)
            return self.clean_content(content)
        return ""

    async def parse_scholarship_list_llm(self, soup):
        scholarship = self.to_markdown(soup)
        if not scholarship:
            return []
        try:
            processed_content = await run_scholarship_list(scholarship)
            if not processed_content or not isinstance(processed_content, dict):
                return []
            return processed_content.get("scholarships", [])
        except Exception as e:
            print(f"Error processing scholarship list: {str(e)}")
            return []
            

    async def parse_scholarship(self, soup):
        scholarships = await self.parse_scholarship_list_llm(soup)
        if not scholarships:
            return []

        all_detailed_scholarships = []
        for scholarship in scholarships:
            if not isinstance(scholarship, dict):
                continue
                
            url = scholarship.get("link", "")
            if not url:
                continue
            
            client = await self.client
            try:
                response = await client.get(url)
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                content = self.to_markdown(soup, class_name="entry clearfix")
                if not content:
                    continue

                processed_content = await run_scholarship(content)
                if processed_content and isinstance(processed_content, dict):
                    scholarship_detail = {
                        'title': scholarship.get('title', ''),
                        'link': url,
                        'content': processed_content.get('content', ''),
                        'application_link': processed_content.get('application_link', '')
                    }
                    if all(scholarship_detail.values()):
                        all_detailed_scholarships.append(scholarship_detail)

            except Exception as e:
                print(f"Error processing scholarship detail: {str(e)}")
                continue

        return all_detailed_scholarships

        