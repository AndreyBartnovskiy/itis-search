from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess
import os

PAGES_COUNT = 100

save_dir = 'pages'
index_file = 'pages/index.txt'
dump_file = 'pages/выкачка.txt'

restricted_domains = ['t.me', 'instagram.com', 'vk.com', 'm.vk.com', 'ok.ru', 'youtube.com', 'www.youtube.com',
                      'www.tiktok.com', 'viber.com', 'music.apple.com', 'rutube.ru', 'www.linkedin.com',
                      'linkedin.com', 'apps.apple.com', 'www.apple.com', 'github.com', 'account.ncbi.nlm.nih.gov',
                      'kudago.com', 'www.zoom.com']
restricted_urls = [
    'https://zen.yandex.ru/tolkosprosit',
]
start_urls = [
    'https://cuprum.media/spravochnik/f-mrt',
    'https://cuprum.media/science-answers',
    'https://cuprum.media/columns/nizkouglevodnye-diety',
    'https://cuprum.media/lifestyle/foodstagram',
    'https://cuprum.media/spravochnik/buckwheat-tea-sp',
    'https://meduza.io/feature/2020/03/20/kak-iskat-meditsinskuyu-informatsiyu-vo-vremya-pandemii-i-posle-nee',
]

class Parser(scrapy.Spider):
    name = "pages"
    start_urls = start_urls
    page_counter = 1

    def parse(self, response):
        if response.url in restricted_urls or any(domain in response.url for domain in restricted_domains):
            self.log(f'Skipping URL {response.url} due to block list')
            return

        filename = f'{self.page_counter}-{response.url.split("/")[-2]}.html'
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.body)
        
        with open(index_file, 'a') as f:
            f.write(f'{self.page_counter},{response.url}\n')
        
        with open(dump_file, 'a', encoding='utf-8') as f:
            f.write(f'FILE {self.page_counter}: {response.url}\n')
            f.write(response.text + '\n' + '='*80 + '\n')
        
        self.log(f'Saved file {filename}. Total received {self.page_counter} pages')
        
        self.page_counter += 1
        if self.page_counter > PAGES_COUNT:
            self.log(f'Reached {PAGES_COUNT} pages. Stopping crawler!')
            raise scrapy.exceptions.CloseSpider('Reached page limit')

        next_pages = set(response.css('a::attr(href)').getall() + response.xpath("//a/@href").getall())
        for next_page in next_pages:
            if next_page and self.page_allowed(next_page):
                yield response.follow(next_page, callback=self.parse)

    def page_allowed(self, next_page):
        try:
            url_domain = next_page.split('/')[2]
            if next_page in restricted_urls or url_domain in restricted_domains:
                self.log(f'Skipping URL {next_page} due to block list before visiting it')
                return False
        except:
            pass
        return True

def create_directory():
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

if __name__ == "__main__":
    create_directory()
    process = CrawlerProcess()
    process.crawl(Parser)
    process.start()
