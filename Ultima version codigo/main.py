from config import URLS, NOMBRE_EXCEL, URL_SITEMAP, USA_SITEMAP
from browser import crear_driver
from fases import fase1_recorrer_urls, fase2_obtener_descripciones, fase_sitemap
from excel_exporter import guardar_excel

def main():
    print("=" * 60)
    print("  SCRAPER ELECTRONILAB.CO")
    print("  Usando Selenium (contenido renderizado por JavaScript)")
    print("=" * 60)

    driver = crear_driver()

    try:
        if USA_SITEMAP:
            print(f"\n  Modo Activo: Extracción por SITEMAP")
            productos, resumen_urls = fase_sitemap(driver, URL_SITEMAP)
        else:
            print(f"\n  Modo Activo: Extracción por MÚLTIPLES URLs")
            print(f"  URLs configuradas: {len(URLS)}")
            for i, u in enumerate(URLS, 1):
                print(f"    {i}. {u}")

            # FASE 1: Recorrer todas las URLs y sus páginas
            productos, resumen_urls = fase1_recorrer_urls(driver, URLS)

        total = len(productos)
        print(f"\n{'=' * 60}")
        print(f"  TOTAL ALCANZADO: {total} productos")
        print(f"{'=' * 60}")

        if total == 0:
            print("\n[!] No se encontraron productos.")
            return

        if not USA_SITEMAP:
            # Si usamos URLs múltiples, las descripciones no se sacan en fase 1
            productos = fase2_obtener_descripciones(driver, productos)

        # FASE 3: Guardar en Excel formateado
        guardar_excel(productos, resumen_urls, NOMBRE_EXCEL)

    finally:
        driver.quit()
        print("\n  Navegador cerrado.")


if __name__ == "__main__":
    main()
