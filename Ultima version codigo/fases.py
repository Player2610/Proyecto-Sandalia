import time
from selenium.common.exceptions import TimeoutException
from helpers_navegacion import esperar_productos, hay_pagina_siguiente
from extractores import extraer_productos_pagina, extraer_categoria_de_url, obtener_descripcion, extraer_urls_de_sitemap, obtener_detalles_desde_url

def scrape_url_completa(driver, url):
    """Scrapea TODAS las páginas de una URL (paginación incluida)."""
    productos = []
    try:
        driver.get(url)
    except TimeoutException:
        print("  [!] Warning: Timeout al cargar la página. Intentando continuar...")
        
    pagina = 1

    while True:
        print(f"\n    Página {pagina}...", end=" ")

        if not esperar_productos(driver):
            print("(sin productos, fin)")
            break

        prods = extraer_productos_pagina(driver)
        print(f"{len(prods)} productos extraídos")

        if len(prods) == 0:
            break

        for p in prods:
            print(f"      >> {p['nombre'][:55]}  |  {p['precio']}")

        productos.extend(prods)

        if not hay_pagina_siguiente(driver):
            break

        pagina += 1

    return productos, pagina


def fase1_recorrer_urls(driver, urls):
    """
    Fase 1: Recorrer todas las URLs configuradas y extraer productos sin descripción detallada.
    """
    todos = []
    resumen_urls = []

    for idx, url in enumerate(urls, 1):
        categoria = extraer_categoria_de_url(url)
        print(f"\n{'-' * 60}")
        print(f"  [{idx}/{len(urls)}] Procesando link: {categoria}")
        print(f"  URL: {url}")
        print(f"{'-' * 60}")

        prods, paginas = scrape_url_completa(driver, url)

        # Agregar la categoría a cada producto encontrado
        for p in prods:
            p["categoria"] = categoria

        todos.extend(prods)
        resumen_urls.append((categoria, len(prods), paginas))
        print(f"  Subtotal URL: {len(prods)} productos en {paginas} página(s)")

    return todos, resumen_urls


def fase2_obtener_descripciones(driver, productos):
    """
    Fase 2: Visitar el link de cada producto para obtener su descripción detallada (larga).
    """
    print(f"\n[FASE 2] Obteniendo descripción de cada producto...\n")
    total = len(productos)
    for i, prod in enumerate(productos, 1):
        if prod["link"]:
            nombre_corto = prod["nombre"][:45]
            print(f"  [{i}/{total}] {nombre_corto}...", end=" ")
            prod["descripcion"] = obtener_descripcion(driver, prod["link"])
            estado = "OK" if prod["descripcion"] != "Sin descripción" else "sin desc."
            print(estado)
            time.sleep(0.5)
        else:
            prod["descripcion"] = "Sin descripción"
            
    return productos

def fase_sitemap(driver, sitemap_url):
    """
    Alternativa: Usar un Sitemap XML para obtener todos los productos y visitarlos uno por uno.
    """
    print(f"\n[FASE SITEMAP] Descargando Sitemap desde: {sitemap_url}")
    urls = extraer_urls_de_sitemap(sitemap_url)
    
    if not urls:
        print("  [!] No se encontraron URLs en el sitemap.")
        return [], []
        
    print(f"  Se encontraron {len(urls)} URLs. Extrayendo datos...")
    
    productos = []
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{total}] Procesando {url}...", end=" ")
        detalles = obtener_detalles_desde_url(driver, url)
        productos.append(detalles)
        
        estado = "OK" if detalles["nombre"] != "Sin nombre" else "Falló/Sin datos"
        print(estado)
        time.sleep(0.5)
        
    resumen_urls = [("Sitemap Completo", len(productos), 1)]
    return productos, resumen_urls
