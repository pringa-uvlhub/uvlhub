from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import time
from unittest.mock import patch
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def test_login_and_check_element():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the login page
        driver.get(f'{host}/login')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, 'email')
        password_field = driver.find_element(By.NAME, 'password')

        email_field.send_keys('user1@example.com')
        password_field.send_keys('1234')

        # Send the form
        password_field.send_keys(Keys.RETURN)

        # Wait a little while to ensure that the action has been completed
        time.sleep(4)

        try:

            driver.find_element(By.XPATH, "//h1[contains(@class, 'h2 mb-3') and contains(., 'Latest datasets')]")
            print('Test passed!')

        except NoSuchElementException:
            raise AssertionError('Test failed!')

    finally:

        # Close the browser
        close_driver(driver)


def test_sign_up_and_email_confirmation():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Abrir la página de registro
        driver.get(f'{host}/signup')

        # Esperar un poco para que la página cargue
        time.sleep(4)

        # Completar el formulario de registro
        name_field = driver.find_element(By.NAME, 'name')
        surname_field = driver.find_element(By.NAME, 'surname')
        email_field = driver.find_element(By.NAME, 'email')
        password_field = driver.find_element(By.NAME, 'password')
        name_field.send_keys('Juan')
        surname_field.send_keys('Pérez')
        email_field.send_keys('juan.perez@example.com')
        password_field.send_keys('securepassword')

        # Usar patch para mockear el envío de correos
        with patch('app.modules.auth.routes.AuthenticationService.send_verification_email') as mock_send:
            # Enviar el formulario de registro
            password_field.send_keys(Keys.RETURN)

            # Esperar que el registro sea procesado y el correo de confirmación sea enviado
            time.sleep(4)

            # Verificar que la función de envío de correo fue llamada
            assert mock_send.called

            # Obtener el URL de confirmación de la llamada del mock
            args, kwargs = mock_send.call_args
            assert 'html' in kwargs
            html_content = kwargs['html']
            # Aquí deberías extraer el enlace del HTML
            confirm_url = extract_confirmation_url_from_html(html_content)
            print(f"Confirm URL: {confirm_url}")

            # Continuar con el resto de la prueba usando el URL de confirmación
            driver.get(confirm_url)
            time.sleep(4)

            # Verificar si la confirmación fue exitosa
            try:
                driver.find_element(By.XPATH, "//h1[contains(text(), 'Email Confirmed')]")
                print('Test passed! Email confirmed.')
            except NoSuchElementException:
                raise AssertionError('Email confirmation failed!')

    finally:
        # Cerrar el navegador
        close_driver(driver)


def extract_confirmation_url_from_html(html_content):
    # Aquí puedes usar expresiones regulares o una librería de análisis de HTML para extraer el enlace de confirmación
    import re
    match = re.search(r'confirm_url="([^"]+)"', html_content)
    return match.group(1) if match else None


# Call the test function
test_login_and_check_element()
test_sign_up_and_email_confirmation()
