import uuid
import time
import os

from tqdm import tqdm
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path

from scraper.utils import parse_download_link, combine_extracted_info, get_destination_path, download_file
from scraper.driver import ChromeDriver
from scraper.crawler_utils import TracePartsCrawlerUtils


class TracePartsCrawler:
    def __init__(self, destination_dir):
        self.driver = ChromeDriver().get()
        self.destination_dir = destination_dir
        self.models_urls = []
        self.description_file_name = 'descriptions.csv'
        self.description_file_path = os.path.join(self.destination_dir, self.description_file_name)
        self.utils = TracePartsCrawlerUtils(self.driver, self.description_file_path)
        if not os.path.exists(self.description_file_path):
            with open(self.description_file_path, 'w+'):
                pass

    def crawl(self):
        self._login()
        self._get_model_list()

    def _login(self):
        print('Starting logging...')
        login_info = {
            'email': 'email@email.com',
            'password': 'mypassword'
        }
        self.utils.login(login_info)

    def _get_model_list(self):
        catalogs_queue = []

        def parse_result_blocks(url):
            self.driver.get(url)
            self.utils.load_whole_result_page()
            results = self.driver.find_element_by_id('search-result-items')
            rows = results.find_elements_by_class_name('result-block')
            for row in rows:
                url = row.find_element_by_tag_name('a').get_attribute('href')
                if url.find('&Product=') == -1:
                    catalogs_queue.append(url)
                else:
                    self.models_urls.append(url)
                    print(f'Models found: {len(self.models_urls)}. Catalogs left: {len(catalogs_queue)}')
            if catalogs_queue:
                # if len(self.models_urls) > 10:
                #     return  # todo delete
                parse_result_blocks(catalogs_queue.pop(0))

        models_main_url = 'https://www.traceparts.com/en/search/traceparts-classification-mechanical-components?CatalogPath=TRACEPARTS%3ATP01'
        parse_result_blocks(models_main_url)

    def save_models(self):
        for model_index, model_url in tqdm(enumerate(self.models_urls)):
            print(f'Working on model number {model_index}, url: {model_url}')
            self.driver.get(model_url)

            try:
                _, tbody = self.utils.get_model_variations_table()  # todo: maybe change to if it's downloadable
            except NoSuchElementException:  # Can not download the model; probably it is commercial page
                continue

            self.utils.show_all_model_variations()
            _, tbody = self.utils.get_model_variations_table()
            trs = tbody.find_elements_by_tag_name('tr')
            last_downloaded_index, model_id = self.utils.restore_from_last(model_url)

            if not model_id:
                model_id = str(uuid.uuid4())
            destination_path = get_destination_path(destination_dir=self.destination_dir,
                                                    breadcrumbs=self.utils.get_model_breadcrumb(),
                                                    model_id=model_id)
            self.driver.find_element_by_id('dashboard-button').click()
            for i in range(len(trs)):
                if i < last_downloaded_index:
                    continue
                self.utils.hide_overlay_elements()
                self.utils.show_all_model_variations()
                _, tbody = self.utils.get_model_variations_table()
                trs = tbody.find_elements_by_tag_name('tr')
                if trs[i].get_attribute('class') != 'k-state-selected':
                    trs[i].click()
                    time.sleep(5)

                model_id = uuid.uuid4()
                file_path = 'test'  # self.utils.download_model(destination_path / Path(f'{model_id}.zip'))

                name = self.driver.find_element_by_id('product-items').find_element_by_tag_name('h1').text
                description = self.utils.extract_model_description()
                self.utils.save_model_description(description, model_url, model_id, file_path, name)


if __name__ == '__main__':
    crawler = TracePartsCrawler("F:\\test")
    crawler.crawl()
    crawler.save_models()
