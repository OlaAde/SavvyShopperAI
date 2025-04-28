import asyncio
import logging
import sahibinden_scraper.database as database
import nodriver as uc
from bs4 import BeautifulSoup

# Basit bir şekilde anlık logları takip etmeyi sağlar.
logging.basicConfig(level=30)

async def main(arama, yıl_min=None, yıl_max=None, motor_hacmi=None, vites=None, table_name=None):
    """
    Tüm değerler string olarak kabul edilir, örnek kullanım sayfanın en altında mevcuttur herhangi bir hata ile karşılaşırsanız issue oluşturabilirsiniz.

    Args:
        arama: Aramak istediğiniz araç. (Renault Clio?)
        yıl_min: Minimum araç yılı (2016)
        yıl_max: Maksimum araç yılı (2016)
        motor_hacmi: Motor hacmi filtresi (1.5)
        vites: Vites tipi filtresi (Manuel)
    """

    driver = await uc.start()
    # sahibinden.com'u açar.
    tab = await driver.get('https://www.sahibinden.com')
    await driver.sleep(5)
    # Cookileri kabul etme.
    accept_cookies = await tab.find('Tüm Çerezleri Kabul Et', best_match=True)
    if accept_cookies:
        await accept_cookies.click()

    ## Arama kısmına arama verisini gönderir.
    search_box = await tab.select('#searchText')
    await search_box.send_keys(arama)
    await driver.sleep(1)
    print('reacthed here 1')
    ## Arama kısmında ilk çıkan öneriye tıklanır.
    first_suggestion = await tab.select('li.first-child.ui-menu-item a')
    await first_suggestion.click()
    await driver.sleep(2)
    print('reacthed here 2')
    ## Sonuçları 50'ye çıkarır.
    results_dropdown = await tab.select('a.paging-size.Limit50Passive[title="50"]')
    await results_dropdown.click()
    await driver.sleep(2)
    print('reacthed here 3')
    # Filtre mevcutsa uygulanır.
    if any([yıl_min, yıl_max, motor_hacmi, vites]):

        try:
            filter_button = await tab.select('#searchCategoryContainer div div ul li:first-child a')
            print("Clicking filter button...")
            await filter_button.click()
            await driver.sleep(2)

            # Minimum yıl filtresi
            if yıl_min:
                print("Selecting minimum year filter...")
                year_min_input = await tab.select('input[name="a5_min"]')
                await year_min_input.send_keys(yıl_min)
                await driver.sleep(2)

            # Maximum yıl filtresi
            if yıl_max:
                print("Selecting maximum year filter...")
                year_max_input = await tab.select('input[name="a5_max"]')
                await year_max_input.send_keys(yıl_max)
                await driver.sleep(2)

            # Vites filtresi
            if vites:
                print("Selecting transmission filter...")
                vites = vites.lower()
                await tab.scroll_down(200)

                if vites == "manual":
                    manuel_checkbox = await tab.select('a[data-value="32467"].js-attribute.facetedCheckbox')
                    await manuel_checkbox.click()
                    await driver.sleep(2)

                elif vites == "automatic":
                    otomatik_checkbox = await tab.select('a[data-value="32466"].js-attribute.facetedCheckbox')
                    await otomatik_checkbox.click()
                    await driver.sleep(2)

            # Filtre uygulanır.
            filter_apply = await tab.select('#searchResultLeft-a5 dl dd div button')
            await filter_apply.click()
            await driver.sleep(2)
        except Exception as e:
            print("Issues while clicking filters: " + str(e))

    # Loop to pull vehicle data for each page.
    while True:
        try:
            # Sayfanın html içeriğini alır.
            html_content = await tab.get_content()
            # Alınan html'i bs4'e yapıştırır
            soup = BeautifulSoup(html_content, 'html.parser')

            # Sayfada eşleşen veriler çekilir.
            resim_urls = [img.get('src') for img in soup.select('.searchResultsLargeThumbnail img')]
            marka = soup.select_one('#search_cats ul li:nth-child(3) div a').text.strip()
            model_motor = [elem.text.strip() for elem in soup.select('.searchResultsTagAttributeValue')]
            basliklar = [elem.text.strip() for elem in soup.select('.searchResultsTitleValue')]
            renk_km_yil = [elem.text.strip() for elem in soup.select('.searchResultsAttributeValue')]
            fiyatlar = [elem.text.strip()[:-3].replace('.', '') for elem in soup.select('.searchResultsPriceValue')]
            tarihler = [elem.text.strip().replace('\n', ' ') for elem in soup.select('.searchResultsDateValue')]
            sehirler = [elem.text.strip().replace('\n', ' ') for elem in soup.select('.searchResultsLocationValue')]
            ilan_links = [a.get("href") for a in soup.select('.searchResultsTitleValue a.classifiedTitle')]

            ## Data is cleaned and Saved
            for i in range(len(basliklar)):
                # Organizes and cleans the data.
                resim_url = resim_urls[i] if i < len(resim_urls) else "N/A"
                model = model_motor[i * 2] if len(model_motor) > i * 2 else "N/A"
                motor = model_motor[i * 2 + 1] if len(model_motor) > i * 2 + 1 else "N/A"
                yil = renk_km_yil[i * 3] if len(renk_km_yil) > i * 3 else "N/A"
                km = renk_km_yil[i * 3 + 1].replace('.', '') if len(renk_km_yil) > i * 3 + 1 else "N/A"
                renk = renk_km_yil[i * 3 + 2] if len(renk_km_yil) > i * 3 + 2 else "N/A"
                ilan_url = f"https://www.sahibinden.com{ilan_links[i]}" if i < len(ilan_links) else "N/A"

                ## Spesifik bir motor hacmi isteniyorsa ona göre veriler kaydedilir.
                if not motor_hacmi or motor_hacmi in motor:
                    try:
                        yil_int = int(yil) if yil != "N/A" else 0
                        km_int = int(km) if km != "N/A" else 0
                        fiyat_int = int(fiyatlar[i]) if fiyatlar[i] != "N/A" else 0
                        database.veri_ekle(table_name, marka, motor, renk, model, yil_int, basliklar[i], km_int, fiyat_int, tarihler[i], sehirler[i], resim_url, ilan_url)
                    # Hata yakalama.
                    except ValueError as e:
                        print(f"Veri dönüşüm hatası: {e}")
                        continue

            # Sayfanın verileri alınıp işlendikten sonra sonraki sayfaya geçer
            next_button = await tab.select('.prevNextBut[title="Sonraki"]')
            if not next_button:
                print('Reached the last page.')
                break
            await next_button.click()
            await tab.sleep(2)

        except Exception as e:
            print("Son sayfaya ulaşıldı veya bir hata oluştu:", str(e))
            break

    # Driver kapatılır.
    print("Bitti")
    driver.stop()