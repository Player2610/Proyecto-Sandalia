import time
import requests
import xml.etree.ElementTree as ET
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def extraer_productos_pagina(driver):
    """Extrae nombre, precio y link de cada producto en la página actual."""
    productos = []

    # Intentar selectores de Algolia primero, luego WooCommerce estándar
    items = driver.find_elements(By.CSS_SELECTOR, "li.ais-Hits-item")
    if not items:
        items = driver.find_elements(By.CSS_SELECTOR, "li.product")

    for item in items:
        # --- NOMBRE ---
        try:
            titulo = item.find_element(By.CSS_SELECTOR, "h2")
            nombre = titulo.text.strip()
        except Exception:
            nombre = "Sin nombre"

        # --- PRECIO ---
        try:
            # Precio con descuento (dentro de <ins>)
            try:
                precio_el = item.find_element(By.CSS_SELECTOR, "ins .woocommerce-Price-amount")
            except Exception:
                precio_el = item.find_element(By.CSS_SELECTOR, ".woocommerce-Price-amount")
            precio = precio_el.text.strip()
        except Exception:
            try:
                precio_el = item.find_element(By.CSS_SELECTOR, "span.price")
                precio = precio_el.text.strip()
            except Exception:
                precio = "Sin precio"

        # --- LINK ---
        try:
            link_el = item.find_element(By.CSS_SELECTOR, "a[href]")
            link = link_el.get_attribute("href")
        except Exception:
            link = None

        if nombre and nombre != "Sin nombre":
            productos.append({"nombre": nombre, "precio": precio, "link": link})

    return productos


def obtener_descripcion(driver, url):
    """Visita la página individual de un producto y extrae la descripción."""
    try:
        try:
            driver.get(url)
        except TimeoutException:
            pass  # Continuar aunque haya timeout
            
        # Espera breve inicial para que la página renderice estructura básica
        time.sleep(1.5)

        # Descripción corta (intentar primero)
        try:
            desc_corta = driver.find_element(
                By.CSS_SELECTOR, ".woocommerce-product-details__short-description"
            )
            # get_attribute("textContent") obtiene texto, incluso si el elemento no es visible
            texto_corto = desc_corta.get_attribute("textContent").strip()
            if texto_corto and len(texto_corto) > 10:
                return texto_corto
        except Exception:
            pass

        # Descripción larga (pestaña) - Usamos WebDriverWait por si demora en cargar el DOM
        try:
            desc_larga = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-description, .woocommerce-Tabs-panel--description"))
            )
            texto_largo = desc_larga.get_attribute("textContent").strip()
            # Limpiar posible basura de espacios múltiples
            texto_largo = " ".join(texto_largo.split())
            if texto_largo:
                return texto_largo[:600]  # A veces son muy largas, limitamos su tamaño en Excel
        except Exception:
            pass

        # Último intento: meta description del head
        try:
            meta = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
            texto_meta = meta.get_attribute("content").strip()
            if texto_meta:
                 return texto_meta
        except Exception:
            pass

        return "Sin descripción"
    except Exception:
        return "Sin descripción"


def extraer_categoria_de_url(url):
    """Extrae un nombre de categoría legible a partir de la URL."""
    partes = url.rstrip("/").split("/")
    segmentos = [p for p in partes[3:] if p and not p.isdigit() and p != "page"]
    if segmentos:
        return " > ".join(segmentos).replace("-", " ").title()
    return url

def extraer_urls_de_sitemap(sitemap_url):
    """Descarga el sitemap XML y extrae todas las URLs (<loc>)."""
    urls = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(sitemap_url, headers=headers, timeout=15)
        respuesta.raise_for_status()
        
        root = ET.fromstring(respuesta.content)
        for elem in root.iter():
            if 'loc' in elem.tag:
                url = elem.text.strip()
                # Filtrar: debe incluir '/tienda/', no ser la tienda principal, y no ser imagen
                if url and "/tienda/" in url and url != "https://electronilab.co/tienda/":
                    if not url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        urls.append(url)
                    
    except Exception as e:
        print(f"  [!] Error al obtener sitemap: {e}")
        
    return urls

def obtener_detalles_desde_url(driver, url):
    """Visita el link de un producto y extrae nombre, precio y descripción."""
    detalles = {"nombre": "Sin nombre", "precio": "Sin precio", "descripcion": "Sin descripción", "link": url, "categoria": "Sitemap"}
    try:
        try:
            driver.get(url)
        except TimeoutException:
            pass
            
        time.sleep(1.5)

        # Nombre
        try:
            titulo = driver.find_element(By.CSS_SELECTOR, "h1.product_title")
            detalles["nombre"] = titulo.text.strip()
        except Exception:
            pass

        # Precio
        try:
            try:
                precio_el = driver.find_element(By.CSS_SELECTOR, "p.price ins .woocommerce-Price-amount")
            except Exception:
                precio_el = driver.find_element(By.CSS_SELECTOR, "p.price .woocommerce-Price-amount")
            detalles["precio"] = precio_el.text.strip()
        except Exception:
            pass

        # Descripción
        try:
            desc_corta = driver.find_element(By.CSS_SELECTOR, ".woocommerce-product-details__short-description")
            texto_corto = desc_corta.get_attribute("textContent").strip()
            if texto_corto and len(texto_corto) > 10:
                detalles["descripcion"] = texto_corto
        except Exception:
            try:
                desc_larga = driver.find_element(By.CSS_SELECTOR, "#tab-description")
                texto_largo = desc_larga.get_attribute("textContent").strip()
                if texto_largo:
                    detalles["descripcion"] = " ".join(texto_largo.split())[:600]
            except Exception:
                pass

    except Exception:
        pass
        
    return detalles
