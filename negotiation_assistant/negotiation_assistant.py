from sahibinden_scraper.database import get_all_listings, get_listing
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")


def llama_generate_fn(prompt):
    response = llm(prompt)
    return response.strip()


def suggest_maximum_price(table_name, ):
    listings = get_all_listings(table_name)

    def format_listing(l):
        return (
            f"Year: {l.get('yil')}, "
            f"Kilometre: {l.get('kilometre')}, "
            f"Transmission: {l.get('vites', 'N/A')}, "
            f"Fuel: {l.get('yakit', 'N/A')}, "
            f"Price: {l.get('fiyat')} TL"
        )

    formatted_listings = [format_listing(l) for l in listings if l.get("fiyat")]

    prompt = f"""
You are a professional car market expert in Turkey.

Below are real listings for a specific Fiat Egea model. Each line contains the year, kilometres, transmission, fuel type, and listed price in Turkish Lira.

Listings:
{chr(10).join(f"{i + 1}. {line}" for i, line in enumerate(formatted_listings))}

Based on these listings, what is the **maximum fair price** an expert would recommend paying today?

Exclude extreme outliers. Think like a cautious buyer looking for a good deal.

Please respond with **only the number**, no currency symbol or explanation.
"""

    response = llama_generate_fn(prompt)

    try:
        # Extract the number
        price = int(''.join(c for c in response if c.isdigit()))
        print(f"✅ Suggested Maximum Price: {price:,} TL")
        return price
    except:
        print("❌ Could not parse a number from the model's response:")
        print(response)
        return None


def generate_initial_message(table_name, listing_id):
    listing = get_listing(table_name, listing_id)

    # Extract details
    brand = listing.get("marka", "Belirtilmemiş")
    model = listing.get("model", "Model Bilinmiyor")
    year = listing.get("yil", "N/A")
    km = listing.get("kilometre", "N/A")
    gear = listing.get("vites", "Otomatik")
    fuel = listing.get("yakit", "Benzin")
    engine = listing.get("motor", "")
    location = listing.get("adres", "Türkiye")
    raw_price = listing.get("fiyat", "0")
    price = int(str(raw_price).replace(".", "").replace(",", "").strip() or 0)
    formatted_price = format_price(price)
    title = listing.get("baslik", "")

    # Suggest 5–10% lower offer
    offer_price = int(price * 0.92)
    formatted_offer = format_price(offer_price)

    # Prompt for LLaMA
    prompt = f"""
You are a polite but confident car buyer messaging a seller on Sahibinden. You saw their listing and you're interested, but you'd like to offer a slightly lower price.

You are respectful, sound informed, and explain that you're a serious buyer ready to complete the transaction quickly — if the seller accepts your offer.

Write the message in Turkish. Mention their listed price ({formatted_price}), then make your offer ({formatted_offer}). Be persuasive but not pushy.

Car Listing:
- Title: {title}
- Brand: {brand}
- Model: {model}
- Year: {year}
- Kilometre: {km}
- Gear: {gear}
- Fuel: {fuel}
- Engine: {engine}
- Location: {location}

Keep the message between 3–6 sentences. The tone should be confident, kind, and to the point.
"""

    message = llama_generate_fn(prompt)
    print("message", message)
    return message.strip()

def format_price(price):
    try:
        return f"{int(price):,} TL".replace(",", ".")  # optional: replace with dots for Turkish style
    except (ValueError, TypeError):
        return "N/A"
