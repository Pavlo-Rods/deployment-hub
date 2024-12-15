import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_search_and_view_profile():
    """
    Prueba de búsqueda de 'doe' y visualización del perfil.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Inicia sesión
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Realizar la búsqueda de "doe"
        search_box = driver.find_element(By.ID, "search-query")
        search_box.click()
        search_box.send_keys("doe")
        search_box.send_keys(Keys.ENTER)
        wait_for_page_to_load(driver)

        # Pulsar sobre el enlace con href="/profile/view/2"
        profile_link = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, '//a[@href="/profile/view/2"]')
        )
        profile_link.click()
        wait_for_page_to_load(driver)

        # Verificar que el elemento con la clase "card-body" está presente
        card_body = driver.find_element(By.CLASS_NAME, "card-body")
        assert card_body.is_displayed(), "El perfil no se cargó correctamente o falta el 'card-body'."

        print("Prueba de búsqueda y visualización de perfil: OK")

    finally:
        close_driver(driver)


def test_edit_profile():
    """
    Prueba de la edición del perfil.
    """
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        # Inicia sesión
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")
        password_field.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        # Pulsar sobre el enlace con href="/profile/edit"
        edit_profile_link = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, '//a[@href="/profile/edit"]')
        )
        edit_profile_link.click()
        wait_for_page_to_load(driver)

        # Esperar a que el campo de nombre sea interactuable
        name_field = driver.find_element(By.ID, "name")
        name_field.click()
        name_field.clear()  # Borra el nombre actual
        name_field.send_keys("Pepe")  # Escribir "Pepe" en su lugar

        # Pulsar el botón de submit
        submit_button = driver.find_element(By.ID, "submit")
        submit_button.click()
        wait_for_page_to_load(driver)
        time.sleep(2)  # Fuerza la espera para la carga completa de la página

        # Verificar si aparece el mensaje de éxito
        success_message = driver.find_element(By.CLASS_NAME, "alert-success")
        assert success_message.is_displayed(), "El mensaje de éxito no se mostró correctamente."

        print("Prueba de edición de perfil: OK")

    finally:
        close_driver(driver)


# Llamada a los tests
if __name__ == "__main__":
    test_search_and_view_profile()
    test_edit_profile()
