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
        self.base_url = "https://www.scholars4dev.com/category/level-of-study/masters-scholarships"


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
        # for scholarship in scholarships:
        try:
            processed_content = await run_scholarship_list(scholarship)

            pprint(processed_content)
            return processed_content["scholarships"]
        except Exception as e:
            print(f"Error processing scholarship: {str(e)}")
            

    async def parse_scholarship(self, soup):
        scholarships = await self.parse_scholarship_list_llm(soup)

        all_detailed_scholarships = []
        for scholarship in scholarships:
            url = scholarship.get("link", "")
            
            client = await self.client
            try:
                response = await client.get(url)
            except Exception as e:
                print(f"Error fetching scholarship: {str(e)}")
                continue

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            content = self.to_markdown(soup, class_name="entry clearfix")
            if not content:
                continue

            try:
                processed_content = await run_scholarship(content)
                if processed_content and isinstance(processed_content, dict):
                    scholarship_detail = {
                        'title': scholarship['title'],
                        'link': url,
                        'content': processed_content.get('content', ''),
                        'application_link': processed_content.get('application_link', '')
                    }
                    all_detailed_scholarships.append(scholarship_detail)

            except Exception as e:
                print(f"Error processing scholarship: {str(e)}")
                continue

            all_detailed_scholarships.append(scholarship)
        return all_detailed_scholarships

        