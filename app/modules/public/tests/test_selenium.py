import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def wait_for_element_to_be_clickable(driver, by, value, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


def close_modal_if_present(driver):
    try:
        modal_close_button = driver.find_element(By.CSS_SELECTOR, ".modal-close-button")
        if modal_close_button.is_displayed():
            modal_close_button.click()
            print("Modal cerrado.")
    except Exception:
        print("No se encontró un modal o no está visible.")


def test_access_dashboard():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")

        wait_for_page_to_load(driver)

        close_modal_if_present(driver)

        dashboard_button = driver.find_element(By.XPATH, "//a[text()='Ver Dashboard']")

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(dashboard_button))

        driver.execute_script("arguments[0].scrollIntoView(true);", dashboard_button)

        WebDriverWait(driver, 3).until(EC.visibility_of(dashboard_button))

        actions = ActionChains(driver)
        actions.move_to_element(dashboard_button).perform()

        time.sleep(1)

        dashboard_button.click()

        wait_for_page_to_load(driver)

        assert "/dashboard" in driver.current_url, f"Redirección fallida, URL actual: {driver.current_url}"

        print("Acceso al dashboard exitoso.")

        assert "/dashboard" in driver.current_url, "No se accedió al dashboard correctamente."

    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_access_dashboard()
