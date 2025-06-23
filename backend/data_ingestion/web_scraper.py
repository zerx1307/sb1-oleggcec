import scrapy
import json
import os
from urllib.parse import urljoin, urlparse
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import PyPDF2
import requests
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MOSDACSpider(scrapy.Spider):
    name = 'mosdac_spider'
    allowed_domains = ['mosdac.gov.in']
    start_urls = [
        'https://www.mosdac.gov.in/',
        'https://www.mosdac.gov.in/faq',
        'https://www.mosdac.gov.in/products',
        'https://www.mosdac.gov.in/missions',
        'https://www.mosdac.gov.in/documentation'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
    }
    
    def __init__(self, output_dir='./data/scraped', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def parse(self, response):
        # Extract page content
        page_data = self.extract_page_content(response)
        
        # Save page data
        filename = self.get_filename(response.url)
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        # Follow links to other pages
        links = response.css('a::attr(href)').getall()
        for link in links:
            if link and not link.startswith('#'):
                absolute_url = urljoin(response.url, link)
                if self.is_valid_url(absolute_url):
                    yield response.follow(absolute_url, self.parse)
        
        # Download PDFs and documents
        doc_links = response.css('a[href$=".pdf"], a[href$=".doc"], a[href$=".docx"]::attr(href)').getall()
        for doc_link in doc_links:
            absolute_url = urljoin(response.url, doc_link)
            yield response.follow(absolute_url, self.parse_document)
    
    def extract_page_content(self, response) -> Dict[str, Any]:
        """Extract structured content from web page"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract metadata
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description.get('content', '') if meta_description else ""
        
        # Extract main content
        content_selectors = [
            'main', '.content', '#content', '.main-content',
            'article', '.article', '.post-content'
        ]
        
        main_content = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                main_content = content_elem.get_text(separator=' ', strip=True)
                break
        
        if not main_content:
            # Fallback to body content
            body = soup.find('body')
            main_content = body.get_text(separator=' ', strip=True) if body else ""
        
        # Extract structured data
        tables = []
        for table in soup.find_all('table'):
            table_data = self.extract_table_data(table)
            if table_data:
                tables.append(table_data)
        
        # Extract FAQ sections
        faqs = self.extract_faq_content(soup)
        
        # Extract navigation and breadcrumbs
        nav_items = [a.get_text().strip() for a in soup.select('nav a, .breadcrumb a')]
        
        return {
            'url': response.url,
            'title': title_text,
            'description': description,
            'content': main_content,
            'tables': tables,
            'faqs': faqs,
            'navigation': nav_items,
            'links': [urljoin(response.url, a.get('href', '')) for a in soup.find_all('a', href=True)],
            'timestamp': response.headers.get('Date', '').decode('utf-8') if response.headers.get('Date') else "",
            'content_type': 'webpage'
        }
    
    def extract_table_data(self, table) -> Dict[str, Any]:
        """Extract structured data from HTML tables"""
        headers = []
        rows = []
        
        # Extract headers
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
        
        # Extract data rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            row_data = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
            if row_data:
                rows.append(row_data)
        
        return {
            'headers': headers,
            'rows': rows,
            'row_count': len(rows)
        } if headers or rows else None
    
    def extract_faq_content(self, soup) -> List[Dict[str, str]]:
        """Extract FAQ question-answer pairs"""
        faqs = []
        
        # Common FAQ patterns
        faq_patterns = [
            ('.faq-item', '.question', '.answer'),
            ('.qa-pair', '.q', '.a'),
            ('dt', 'dt', 'dd'),  # Definition list format
        ]
        
        for container_sel, q_sel, a_sel in faq_patterns:
            containers = soup.select(container_sel)
            for container in containers:
                question_elem = container.select_one(q_sel)
                answer_elem = container.select_one(a_sel)
                
                if question_elem and answer_elem:
                    faqs.append({
                        'question': question_elem.get_text().strip(),
                        'answer': answer_elem.get_text().strip()
                    })
        
        return faqs
    
    def parse_document(self, response):
        """Parse PDF and document files"""
        filename = self.get_filename(response.url)
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.pdf':
            content = self.extract_pdf_content(response.body)
        else:
            # For other document types, save raw content
            content = response.text
        
        doc_data = {
            'url': response.url,
            'filename': filename,
            'content': content,
            'content_type': 'document',
            'file_type': file_extension,
            'size': len(response.body)
        }
        
        filepath = os.path.join(self.output_dir, f"doc_{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
    
    def extract_pdf_content(self, pdf_bytes) -> str:
        """Extract text content from PDF"""
        try:
            from io import BytesIO
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return ""
    
    def get_filename(self, url: str) -> str:
        """Generate filename from URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        return path.replace('/', '_').replace('?', '_').replace('&', '_')
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        parsed = urlparse(url)
        
        # Skip external domains
        if parsed.netloc and 'mosdac.gov.in' not in parsed.netloc:
            return False
        
        # Skip certain file types and patterns
        skip_patterns = [
            '.jpg', '.jpeg', '.png', '.gif', '.css', '.js',
            '.zip', '.tar', '.gz', 'mailto:', 'tel:', 'javascript:'
        ]
        
        return not any(pattern in url.lower() for pattern in skip_patterns)

class DataIngestionPipeline:
    def __init__(self, output_dir: str = './data/scraped'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run_scraper(self):
        """Run the web scraper"""
        process = CrawlerProcess({
            'USER_AGENT': 'MOSDAC-AI-Bot/1.0',
            'ROBOTSTXT_OBEY': True,
            'FEEDS': {
                os.path.join(self.output_dir, 'scraped_urls.json'): {
                    'format': 'json',
                    'overwrite': True,
                },
            },
        })
        
        process.crawl(MOSDACSpider, output_dir=self.output_dir)
        process.start()
    
    def process_scraped_data(self) -> List[Dict[str, Any]]:
        """Process and consolidate scraped data"""
        all_data = []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.json') and filename != 'scraped_urls.json':
                filepath = os.path.join(self.output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.append(data)
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
        
        return all_data

if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    pipeline.run_scraper()