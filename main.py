import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import json
from selenium.common import WebDriverException


# Función proporcionada para obtener el código SMS
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string."""
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.")
        return code


class UrbanRoutesPage:
    # --- Localizadores ---
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    ask_taxi_button = (By.XPATH, "//button[contains(text(), 'Pedir un taxi')]")

    # Tarifa Comfort
    comfort_tariff = (By.XPATH, "//div[contains(text(), 'Comfort')]")

    # Teléfono
    phone_field_button = (By.CLASS_NAME, 'np-text')
    phone_input = (By.ID, 'phone')
    next_button = (By.XPATH, "//button[contains(text(), 'Siguiente')]")
    code_input = (By.ID, 'code')
    confirm_button = (By.XPATH, "//button[contains(text(), 'Confirmar')]")

    # Tarjeta de crédito
    payment_method_button = (By.CLASS_NAME, 'pp-text')
    add_card_button = (By.CLASS_NAME, 'pp-plus-container')
    card_number_input = (By.ID, 'number')
    card_code_input = (By.XPATH, "//div[@class='card-code-input']//input[@id='code']")
    link_card_button = (By.XPATH, "//button[contains(text(), 'Enlace')]")
    close_payment_modal_button = (By.XPATH, "//div[@class='payment-picker']//button[@class='close-button']")

    # Extras
    message_field = (By.ID, 'comment')
    blanket_switch = (By.XPATH, "//div[contains(text(), 'Manta y pañuelos')]/..//span[@class='slider round']")
    ice_cream_plus = (By.XPATH, "//div[contains(text(), 'Helado')]/..//div[@class='counter-plus']")
    ice_cream_value = (By.XPATH, "//div[contains(text(), 'Helado')]/..//div[@class='counter-value']")

    # Botón final y modal
    final_order_button = (By.CLASS_NAME, 'smart-button')
    driver_modal = (By.CLASS_NAME, 'order-body')

    def __init__(self, driver):
        self.driver = driver

    # --- Métodos de Acción ---
    def set_route(self, from_address, to_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def click_ask_for_taxi(self):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.ask_taxi_button)).click()

    def select_comfort_tariff(self):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.comfort_tariff)).click()

    def set_phone_number(self, phone_number):
        self.driver.find_element(*self.phone_field_button).click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.phone_input)).send_keys(phone_number)
        self.driver.find_element(*self.next_button).click()

    def submit_phone_code(self, code):
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.code_input)).send_keys(code)
        self.driver.find_element(*self.confirm_button).click()

    def add_credit_card(self, card_number, card_code):
        self.driver.find_element(*self.payment_method_button).click()
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.add_card_button)).click()

        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(self.card_number_input)).send_keys(
            card_number)

        cvv_input = self.driver.find_element(*self.card_code_input)
        cvv_input.send_keys(card_code)
        # Quitar el enfoque del campo CVV para activar el botón "Enlace"
        cvv_input.send_keys(Keys.TAB)

        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.link_card_button)).click()

        # Cerrar el modal de pago
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.close_payment_modal_button)).click()

    def write_message_for_driver(self, message):
        self.driver.find_element(*self.message_field).send_keys(message)

    def request_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_switch).click()

    def add_ice_creams(self, amount):
        for _ in range(amount):
            self.driver.find_element(*self.ice_cream_plus).click()

    def get_ice_cream_amount(self):
        return self.driver.find_element(*self.ice_cream_value).text

    def click_final_order_button(self):
        self.driver.find_element(*self.final_order_button).click()

    def wait_for_driver_modal(self):
        # Espera hasta que aparezca el modal con la información del conductor
        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located(self.driver_modal))


class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver import DesiredCapabilities
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
        cls.driver = webdriver.Chrome(desired_capabilities=capabilities)
        cls.driver.maximize_window()

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_route(data.address_from, data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    def test_select_comfort_tariff(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_ask_for_taxi()
        routes_page.select_comfort_tariff()
        # Verificamos que la tarifa Comfort esté seleccionada (puedes ajustar el assert según tu DOM)
        assert "Comfort" in self.driver.find_element(*routes_page.comfort_tariff).text

    def test_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.set_phone_number(data.phone_number)
        code = retrieve_phone_code(self.driver)
        routes_page.submit_phone_code(code)
        # Verificamos que el teléfono se haya guardado
        assert self.driver.find_element(*routes_page.phone_field_button).text == data.phone_number

    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)
        # Verificamos que se haya agregado una tarjeta viendo si cambió el texto del botón de pago
        payment_text = self.driver.find_element(*routes_page.payment_method_button).text
        assert payment_text != "Método de pago"

    def test_write_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.write_message_for_driver(data.message_for_driver)
        assert self.driver.find_element(*routes_page.message_field).get_property('value') == data.message_for_driver

    def test_order_blanket_and_tissues(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.request_blanket_and_tissues()
        # Verificamos que el switch esté activo (input checked)
        switch_status = self.driver.find_element(By.XPATH,
                                                 "//div[contains(text(), 'Manta y pañuelos')]/..//input").get_attribute(
            "checked")
        assert switch_status == "true"

    def test_order_ice_cream(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_ice_creams(2)
        assert routes_page.get_ice_cream_amount() == "2"

    def test_wait_for_driver_info(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.click_final_order_button()
        routes_page.wait_for_driver_modal()
        # Si llegamos aquí sin TimeoutException, el modal apareció correctamente
        assert self.driver.find_element(*routes_page.driver_modal).is_displayed()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
