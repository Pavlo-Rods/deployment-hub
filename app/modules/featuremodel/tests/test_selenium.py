from selenium.common.exceptions import NoSuchElementException
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_featuremodel_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}/featuremodel')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError('Test failed!')

    finally:

        # Close the browser
        close_driver(driver)


def test_rate_model():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Paso 1: Loguearse
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Paso 2: Navegar al primer dataset
        driver.maximize_window()
        dataset_url = f"{host}/doi/10.1234/dataset4/"
        driver.get(dataset_url)
        wait_for_page_to_load(driver)

        # Paso 3: Pulsar en el botón con class "btn btn-outline-warning btn-sm"
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, \"openRateModelModal('10')\")]"))
        )
        button.click()
        wait_for_page_to_load(driver)

        # Paso 4: Pulsar en el input con id model-3 (en el popup)
        popup_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "model-3"))
        )
        popup_input.click()
        wait_for_page_to_load(driver)

        # Paso 5: Pulsar en el botón con class "btn-primary"
        modal_footer = driver.find_element(By.CLASS_NAME, "modal-footer")
        submit_button = modal_footer.find_element(By.XPATH, "//button[contains(@onclick, \'submitModelRating()\')]")
        submit_button.click()

        wait_for_page_to_load(driver)

        print("Test passed!")

    finally:
        close_driver(driver)


# Call the test function
test_featuremodel_index()
test_rate_model()
