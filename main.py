from datetime import datetime

import nodriver as uc


from negotiation_assistant.negotiation_assistant import suggest_maximum_price
from query_extractor import structured_query_extractor
from report_generator.report_generator import generate_html_report
from sahibinden_scraper.database import get_cheapest_10_listings, get_top_10_listings_with_the_newest_years, \
    get_least_used_10_listings
from sahibinden_scraper.scraper import main


def generate_table_name(structured_query):
    # Get the car name and model
    car_name_model = structured_query['car_name_model']

    # Replace spaces with underscores
    car_name_clean = car_name_model.replace(' ', '_').replace(':','_').lower()

    # Get current timestamp in format YYYY_MM_DD_HH:MMpm/am
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y_%m_%d_%I:%M%p").lower()

    # Combine to create the table name
    table_name = f"{car_name_clean}_{timestamp}"

    return table_name
    # return "toyota_camry_2025_04_14_03_13pm"


def scrape_marketplace_for_cars_meeting_criteria(structured_query, table_name):
    try:
        arama = structured_query['car_name_model'] = None if structured_query['car_name_model'] == 'None' else \
            structured_query['car_name_model']
        transmission = structured_query['transmission'] = None if structured_query['transmission'] == 'None' else \
            structured_query['transmission']
        min_year = structured_query['min_year'] = None if structured_query['min_year'] == 'None' else structured_query[
            'min_year']
        max_year = structured_query['max_year'] = None if structured_query['max_year'] == 'None' else structured_query[
            'max_year']

        uc.loop().run_until_complete(main(
            arama=arama,
            vites=transmission,
            yıl_min=min_year,
            yıl_max=max_year,
            table_name=table_name
        ))

    except Exception as e:
        print(e)


def select_ideal_matches(table_name):
    cheapest_listings = get_cheapest_10_listings(table_name)
    print("cheapest_listings: " + str(cheapest_listings))

    listings_with_newest_production_year = get_top_10_listings_with_the_newest_years(table_name)
    print("listings_with_newest_production_year: " + str(listings_with_newest_production_year))

    least_used_listings = get_least_used_10_listings(table_name)
    print("least_used_listings: " + str(least_used_listings))

    return cheapest_listings, listings_with_newest_production_year, least_used_listings



if __name__ == '__main__':
    query = "I want to buy a Fiat Egea, Manual not older than 2019"
    structured_query = structured_query_extractor.extract_structured_query(query)
    print("structured_query: " + str(structured_query))

    table_name = generate_table_name(structured_query)
    print("table_name: " + str(table_name))
    scrape_marketplace_for_cars_meeting_criteria(structured_query, table_name)

    cheapest_listings, listings_with_newest_production_year, least_used_listings = select_ideal_matches(
        table_name)
    suggested_maximum_price = suggest_maximum_price(table_name)
    generate_html_report(table_name, suggested_maximum_price, cheapest_listings, listings_with_newest_production_year,
                         least_used_listings)