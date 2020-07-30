from selenium import webdriver

chrome_driver_path = 'C:\\Users\\Holmes\\Downloads\\chromedriver_win32\\chromedriver.exe'


class ChromeDriver:
    def __init__(self, driver_path: str = chrome_driver_path, windows_size: tuple = (1900, 1080)):
        self.driver = webdriver.Chrome(driver_path)
        self.driver.set_window_size(windows_size[0], windows_size[1])

    def get(self):
        return self.driver
