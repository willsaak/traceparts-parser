import time
import csv

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait as wait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from utils import parse_download_link, combine_extracted_info, get_destination_path, download_file


class TracePartsCrawlerUtils:
    def __init__(self, driver, description_file_path):
        self.driver = driver
        self.description_file_path = description_file_path
        self._last_downloaded_file_url = ''

    def login(self, login_info):
        login_url = 'https://www.traceparts.com/en/sign-in'
        self.driver.get(login_url)
        self.driver.find_element_by_id('Email').send_keys(login_info['email'])
        self.driver.find_element_by_id('Password').send_keys(login_info['password'])
        self.driver.find_element_by_id('signin-btn').click()

    def load_whole_result_page(self):
        body_element = self.driver.find_element_by_tag_name('body')
        body_element.send_keys(Keys.END)
        time.sleep(5)  # because of auto-loading
        body_element.send_keys(Keys.END)
        time.sleep(2)
        try:
            search_more_button = self.driver.find_element_by_id('searchresult-more')
        except NoSuchElementException:  # There is no "show more" button == all results are loaded
            return
        if search_more_button.text != '':  # If == '', all results are loaded
            search_more_button.click()
            time.sleep(2)
            self.load_whole_result_page()

    def get_model_breadcrumb(self):
        items = self.driver.find_element_by_id('result-tb-category-breadcrumb').find_elements_by_tag_name('a')
        breadcrumb = [a.text for a in items]
        return breadcrumb

    def show_all_model_variations(self):
        if self.driver.find_element_by_class_name('k-pager-info').text != '':  # If there is second page
            self.driver.execute_script(
                "for(var i = 0; i < document.getElementsByTagName('select').length; i++) "
                "   document.getElementsByTagName('select')[i].style.display = 'block'")
            Select(self.driver.find_element_by_class_name('k-pager-sizes').find_element_by_tag_name(
                'select')).select_by_visible_text('All')
            time.sleep(1)

    def get_model_variations_table(self):
        table = self.driver.find_element_by_id('partConfigurationSteps')
        thead = table.find_element_by_tag_name('thead')
        tbody = table.find_element_by_tag_name('tbody')

        return thead, tbody

    def hide_overlay_elements(self):
        self.driver.execute_script("document.getElementById('header-main').style.display = 'none'")
        self.driver.execute_script("document.getElementById('cookie-consent').style.display = 'none'")

    def download_model(self, destination_path):
        print('Downloading model...')
        self.hide_overlay_elements()
        body_element = self.driver.find_element_by_tag_name('body')
        body_element.send_keys(Keys.HOME)  # because of overlaying things, for example like notify boxes

        # download_button = self.driver.find_element_by_id('direct-download')
        # wait(self.driver, 10).until(expected_conditions.element_to_be_clickable(download_button)).click()
        while True:
            try:
                select = Select(self.driver.find_element_by_id('cad-format-select'))  # todo check if can be none
                if select.first_selected_option.text != 'OBJ':
                    select.select_by_visible_text('OBJ')
                time.sleep(3)
                self.driver.find_element_by_id('direct-download').click()
                print(time.strftime("%H:%M:%S", time.localtime()), 'Clicked download button...')
                break
            except (WebDriverException, StaleElementReferenceException) as ex:
                print('Exeption', ex)
                time.sleep(1)
        time.sleep(5)

        download_url = None
        while not download_url:
            time.sleep(2)
            try:
                download_url = self.driver.find_element_by_class_name('download-item-content').get_attribute('href')
            except (NoSuchElementException, StaleElementReferenceException):
                download_url = None
        if download_url == self._last_downloaded_file_url:
            self.download_model(destination_path)
        self._last_downloaded_file_url = download_url
        download_link = parse_download_link(download_url)
        return download_file(download_link, str(destination_path))

    # class TracePartsModelDescriptionCrawler:
    #     def __init__(self, driver, output_file_path):
    #         self.driver = driver
    #         self.output_file_path = output_file_path

    def extract_model_description(self):
        print('Extracting description...')
        headers = []
        selected_model_values = []
        # thead, tbody = self.get_model_variations_table()
        # ths = thead.find_elements_by_tag_name('th')
        # for th in ths:
        #     header = th.get_attribute('data-title')
        #     if header is not None:
        #         headers.append(header)
        #
        # tr = tbody.find_element_by_class_name('k-state-selected')
        # tds = tr.find_elements_by_tag_name('td')
        # for td in tds:
        #     value = td.text
        #     if value != '':  # todo sometimes there is no value in column
        #         selected_model_values.append(value)

        description_container_tables = self.driver.find_elements_by_id('product-bomfields')
        for table in description_container_tables:
            trs = table.find_elements_by_tag_name('tr')
            for tr in trs:
                th = tr.find_element_by_tag_name('th')
                td = tr.find_element_by_tag_name('td')

                header = th.text
                if header not in headers:
                    headers.append(header)
                    selected_model_values.append(td.text)

        model_semantic = combine_extracted_info(headers, selected_model_values)
        return model_semantic

    def save_model_description(self, description, model_url, model_id, model_path, name):
        with open(self.description_file_path, 'a+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([model_path, name, model_id, self.get_model_breadcrumb(), description, model_url])

    def restore_from_last(self, model_url):
        with open(self.description_file_path) as csv_file:
            reader = csv.reader(csv_file)
            count = 0
            model_id = ''
            for line in reader:
                if line and line[-1] == model_url:
                    count += 1
                    model_id = line[0][-77:-41]  # todo clean hardcoded things

        return count, model_id
