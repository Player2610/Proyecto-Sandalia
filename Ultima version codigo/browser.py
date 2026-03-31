from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def crear_driver():
    """Crea un navegador Chrome controlado por Selenium."""
    opciones = Options()
    opciones.page_load_strategy = 'eager'  # No esperar a que carguen todas las imágenes/scripts
    opciones.add_argument("--headless=new")  # Sin ventana visible
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memoria con renderer
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--log-level=3")  # Menos logs
    opciones.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio, options=opciones)
    driver.set_page_load_timeout(30)
    return driver
