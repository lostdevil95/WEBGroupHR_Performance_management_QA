from pages.base import BasePage
from pages.elements import WebElement


class AuthPage(BasePage):

    def __init__(self, web_driver, url=''):
        url = 'http://hrbn.dnc.su/'
        super().__init__(web_driver, url)

    email = WebElement(id='name')

    password = WebElement(id='password')

    remember_me = WebElement(id='checkbox')
