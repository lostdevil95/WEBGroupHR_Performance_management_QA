import time
from termcolor import colored

from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class WebElement:

    _locator = ('', '')
    _web_driver = None
    _page = None
    _timeout = 10
    _wait_after_click = False

    def __init__(self, timeout=10, wait_after_click=False, **kwargs):
        self._timeout = timeout
        self._wait_after_click = wait_after_click

        for attr in kwargs:
            self._locator = (str(attr).replace('_', ' '), str(kwargs.get(attr)))

    def find(self, timeout=10):
        """ Ищет элемент на странице. """

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_element_located(self._locator)
            )
        except:
            print(colored('Элемент не найден на странице!', 'red'))

        return element

    def wait_to_be_clickable(self, timeout=10, check_visibility=True):
        """ Ждет пока элемент не станет доступным для клика. """

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
                EC.element_to_be_clickable(self._locator)
            )
        except:
            print(colored('Элемент не кликабелен!', 'red'))

        if check_visibility:
            self.wait_until_not_visible()

        return element

    def is_clickable(self):
        """ Проверяет можно ли кликать элемент или нет. """

        element = self.wait_to_be_clickable(timeout=1)
        return element is not None

    def is_presented(self):
        """ Проверяет появился ли элемент на странице. """

        element = self.find(timeout=1)
        return element is not None

    def is_visible(self):
        """ Проверяет видим ли элемент. """

        element = self.find(timeout=1)

        if element:
            return element.is_displayed()

        return False

    def wait_until_not_visible(self, timeout=10):

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
                EC.visibility_of_element_located(self._locator)
            )
        except:
            print(colored('Элемент не видим!', 'red'))

        if element:
            js = ('return (!(arguments[0].offsetParent === null) && '
                  '!(window.getComputedStyle(arguments[0]) === "none") &&'
                  'arguments[0].offsetWidth > 0 && arguments[0].offsetHeight > 0'
                  ');')
            visibility = self._web_driver.execute_script(js, element)
            iteration = 0

            while not visibility and iteration < 10:
                time.sleep(0.5)

                iteration += 1

                visibility = self._web_driver.execute_script(js, element)
                print('Element {0} visibility: {1}'.format(self._locator, visibility))

        return element

    def send_keys(self, keys, wait=2):
        """ Отправляет ключи элементу. """

        keys = keys.replace('\n', '\ue007')

        element = self.find()

        if element:
            element.click()
            element.clear()
            element.send_keys(keys)
            time.sleep(wait)
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def get_text(self):
        """ Получает текст элемента. """

        element = self.find()
        text = ''

        try:
            text = str(element.text)
        except Exception as e:
            print('Error: {0}'.format(e))

        return text

    def get_attribute(self, attr_name):
        """ Получает атрибуи элемента. """

        element = self.find()

        if element:
            return element.get_attribute(attr_name)

    def _set_value(self, web_driver, value, clear=True):
        """ Ставит значение вводимому элементу. """

        element = self.find()

        if clear:
            element.clear()

        element.send_keys(value)

    def click(self, hold_seconds=0, x_offset=1, y_offset=1):
        """ Ждет и кликает по элементу. """

        element = self.wait_to_be_clickable()

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset).\
                pause(hold_seconds).click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

        if self._wait_after_click:
            self._page.wait_page_loaded()

    def right_mouse_click(self, x_offset=0, y_offset=0, hold_seconds=0):
        """ Кликает правой кнопкой мыши по элементу. """

        element = self.wait_to_be_clickable()

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset). \
                pause(hold_seconds).context_click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Подсвечивает элемент и делает скриншот всей страницы. """

        element = self.find()

        # Скроллит страницу к элементу:
        self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

        # Добавляет красную линию к стилю:
        self._web_driver.execute_script("arguments[0].style.border='3px solid red'", element)

        # Делает скриншот страницы:
        self._web_driver.save_screenshot(file_name)

    def scroll_to_element(self):
        """ Скроллит страницу к элементу. """

        element = self.find()

        # Скроллит страницу к элементу:
        # Способ #1 проскролить до элемента:
        self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

        # Способ #2:
        try:
            element.send_keys(Keys.DOWN)
        except Exception as e:
            pass  # Просто игнорирует ошибку если мы не может отправить ключи

    def delete(self):
        """ Удаляет элемент со страницы. """

        element = self.find()

        # Удаляет  элемент:
        self._web_driver.execute_script("arguments[0].remove();", element)


class ManyWebElements(WebElement):

    def __getitem__(self, item):
        """ Получает список элементОВ и пытается вернуть требуемый элемент. """

        elements = self.find()
        return elements[item]

    def find(self, timeout=10):
        """ Ищет элементЫ на странице. """

        elements = []

        try:
            elements = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_all_elements_located(self._locator)
            )
        except:
            print(colored('Elements not found on the page!', 'red'))

        return elements

    def count(self):
        """ Считает элементЫ. """

        elements = self.find()
        return len(elements)

    def get_text(self):
        """ Получает тексты элементОВ. """

        elements = self.find()
        result = []

        for element in elements:
            text = ''

            try:
                text = str(element.text)
            except Exception as e:
                print('Error: {0}'.format(e))

            result.append(text)

        return result

    def get_attribute(self, attr_name):
        """ Получает атрибуты элементОВ. """

        results = []
        elements = self.find()

        for element in elements:
            results.append(element.get_attribute(attr_name))

        return results

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Подсвеивает элементЫ и делает скрин страницы. """

        elements = self.find()

        for element in elements:
            # Скроллит до элемента:
            self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

            # Добавляет красную обводку:
            self._web_driver.execute_script("arguments[0].style.border='3px solid red'", element)

        # Делает скрин страницы:
        self._web_driver.save_screenshot(file_name)
