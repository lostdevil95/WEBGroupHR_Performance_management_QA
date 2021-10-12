import pytest
import allure
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    # Параметр выбора браузера для тестов из комм. строки. По умолчанию Chrome
    parser.addoption('--browser_name', action='store', default='chrome',
                     help="Choose browser: chrome or firefox")
    # Параметр выбора языка из комм. строки. По умолчанию Русский
    parser.addoption('--language', action='store', default='ru',
                     help='choose language - en, ru, fr of etc...')


@pytest.fixture
def chrome_options(chrome_options):
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--log-level=DEBUG')

    return chrome_options


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Эта функция помогает определить, что какой-то тест
    # не удался и передает эту информацию

    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture
def browser(request):
    browser_name = request.config.getoption("browser_name")
    user_language = request.config.getoption('language')
    if browser_name == "chrome":
        print("\nЗапускаем Chrome для теста..")
        options = Options()
        options.add_experimental_option('prefs', {'intl.accept_languages': user_language})
        browser = webdriver.Chrome(options=options)
        browser.implicitly_wait(10)
    elif browser_name == "firefox":
        print("\nЗапускаем Firefox для теста..")
        fp = webdriver.FirefoxProfile()
        fp.set_preference("intl.accept_languages", user_language)
        browser = webdriver.Firefox(firefox_profile=fp)
        browser.implicitly_wait(10)
    else:
        raise pytest.UsageError("--browser_name должен быть chrome или firefox")
    yield browser

    if request.node.rep_call.failed:
        # Делает скриншот, если тест падает
        try:
            browser.execute_script("document.body.bgColor = 'white';")

            # Делает и сохраняет скриншот в локаль:
            browser.save_screenshot('screenshots/' + str(uuid.uuid4()) + '.png')

            # Прикрепляет скрин к отчету Allure:
            allure.attach(browser.get_screenshot_as_png(),
                          name=request.function.__name__,
                          attachment_type=allure.attachment_type.PNG)

            # принтует логи
            print('URL: ', browser.current_url)
            print('Browser logs:')
            for log in browser.get_log('browser'):
                print(log)

        except:
            pass  # просто игнорирует все ошибки


def get_test_case_docstring(item):
    """ Эта функция получает строку документа из тестового набора и форматирует ее,
        чтобы показать ее вместо имени самого теста """

    full_name = ''

    if item._obj.__doc__:
        # Убирает лишние пробелы:
        name = str(item._obj.__doc__.split('.')[0]).strip()
        full_name = ' '.join(name.split())

        # Генериует список параметром для параметризированных тестов:
        if hasattr(item, 'callspec'):
            params = item.callspec.params

            res_keys = sorted([k for k in params])
            # Создает словарь:
            res = ['{0}_"{1}"'.format(k, params[k]) for k in res_keys]
            full_name += ' Parameters ' + str(', '.join(res))
            full_name = full_name.replace(':', '')

    return full_name


def pytest_itemcollected(item):
    if item._obj.__doc__:
        item._nodeid = get_test_case_docstring(item)


def pytest_collection_finish(session):
    if session.config.option.collectonly is True:
        for item in session.items:
            if item._obj.__doc__:
                full_name = get_test_case_docstring(item)
                print(full_name)

        pytest.exit('Готово!')
