from scraper.crawler import TracePartsCrawler
from scraper.utils import read_urls_from_file

if __name__ == "__main__":
    while True:
        # crawler = TracePartsCrawler('F:\\dataset')
        crawler = TracePartsCrawler('F:\\test')
        try:
            model_urls = read_urls_from_file('model_urls1.txt')
            crawler._login()
            crawler.models_urls = model_urls
            crawler.save_models()
            break
        except Exception as e:
            print(e)
            crawler.driver.close()
