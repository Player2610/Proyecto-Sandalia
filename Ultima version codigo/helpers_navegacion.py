import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def esperar_productos(driver, timeout=15):
    """Espera a que los productos se carguen en la página (Algolia JS)."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.ais-Hits-item, li.product"))
        )
        time.sleep(1)  # Espera extra para que Algolia termine de renderizar
        return True
    except Exception:
        return False

def hay_pagina_siguiente(driver):
    """Verifica si hay un botón 'Siguiente' en la paginación y hace click."""
    try:
        # Selector para Algolia pagination
        next_btn = driver.find_element(
            By.CSS_SELECTOR, "a.ais-Pagination-link[aria-label='Next']"
        )
        if next_btn.is_displayed() and next_btn.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            time.sleep(0.5)
            next_btn.click()
            time.sleep(2)  # Esperar que cargue la nueva página
            return True
    except Exception:
        pass

    # Fallback: WooCommerce standard pagination
    try:
        next_link = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
        next_link.click()
        time.sleep(2)
        return True
    except Exception:
        pass

    return False
