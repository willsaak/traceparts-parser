from utils import read_urls_from_file
from crawler_utils import TracePartsCrawlerUtils
from tqdm import tqdm
from crawler import TracePartsCrawler

tp_crawler = TracePartsCrawler("F:\\test\\")
driver = tp_crawler.driver
crawler_utils = TracePartsCrawlerUtils(driver)


def get_model_urls():
    print(f'Starting crawling...')
    tp_crawler.crawl()
    model_urls = tp_crawler.models_urls

    print(f"Number of models: {len(model_urls)}")
    return model_urls


def save_model_urls(model_urls, file_path):
    print(f"Saving model_urls...")
    with open(file_path, 'w+') as file:
        for model_url in tqdm(model_urls):
            file.writelines(model_url + '\n')


def filter_models(model_urls, threshold: int = 50):
    print(f'Filtering models...')
    more_than_50_counter = 0
    for model_url in tqdm(model_urls):
        driver.get(model_url)
        try:
            crawler_utils.show_all_model_variations()
            table = driver.find_element_by_id('partConfigurationSteps')
            tbody = table.find_element_by_tag_name('tbody')
            trs = tbody.find_elements_by_tag_name('tr')
        except:
            continue
        trs_length = len(trs)
        if trs_length >= threshold:  # better parse number of variations
            name = driver.find_element_by_id('product-items').find_element_by_tag_name('h1').text
            items = driver.find_element_by_id('result-tb-category-breadcrumb').find_elements_by_tag_name('a')
            breadcrumb = [a.text for a in items[2:]]
            more_than_50_counter += 1  # todo save model_url to file
            print(f'{more_than_50_counter}: {trs_length}. {breadcrumb}. {name}. {model_url}')


if __name__ == '__main__':
    urls_file_path = 'model_urls.txt'
    # models_urls = get_model_urls()
    # save_model_urls(models_urls, urls_file_path)
    models_urls = read_urls_from_file(urls_file_path)
    filter_models(models_urls, threshold=50)
