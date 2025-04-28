from pathlib import Path

from negotiation_assistant.negotiation_assistant import generate_initial_message


def generate_html_report(table_name, suggested_maximum_price,  cheapest_listings, listings_with_newest_production_year1,
                         least_used_listings):
    def generate_table_html(data, title, negotiation_messages=None):
        if not data:
            return f"<h2 class='text-xl font-semibold my-4'>{title}</h2><p>No data available.</p>"

        headers = list(data[0].keys())
        rows_html = ""

        for row in data:
            row_cells = ""
            for col in headers:
                cell = row[col]

                # Special case: render image
                if col == "resim_url" and isinstance(cell, str) and cell.startswith("http"):
                    cell_html = f"""
                    <img src="{cell}" alt="Listing Image" class="w-32 h-auto rounded shadow-sm" />
                    """

                # ilan_url as View Details button
                elif col == "ilan_url" and isinstance(cell, str) and cell.startswith("http"):
                    cell_html = f"""<a href="{cell}" target="_blank">
                        <button class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition">
                            View Details
                        </button>
                    </a>"""

                # Generic URL
                elif isinstance(cell, str) and (cell.startswith("http://") or cell.startswith("https://")):
                    cell_html = f"""<a href="{cell}" target="_blank">
                        <button class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition">
                            Open Link
                        </button>
                    </a>"""
                else:
                    cell_html = str(cell)

                row_cells += f"<td class='px-4 py-2 border align-top'>{cell_html}</td>"

            # Add copy message button (new column)
            message = generate_initial_message(table_name, row['id'])
            copy_button = f"""
            <button onclick="copyToClipboard(this)" data-message="{message.replace('"', '&quot;')}"
                class="bg-yellow-400 text-black px-3 py-1 rounded hover:bg-yellow-500 transition">
                📋 Copy Message
            </button>
            """
            row_cells += f"<td class='px-4 py-2 border align-top'>{copy_button}</td>"

            rows_html += f"<tr class='hover:bg-gray-100'>{row_cells}</tr>"

        # Add "Negotiation Message" to the header
        table_headers = ''.join(f"<th class='px-4 py-2 border'>{col}</th>" for col in headers)
        table_headers += "<th class='px-4 py-2 border'>Negotiation</th>"

        table_html = f"""
        <div class="my-10">
            <h2 class="text-2xl font-bold text-blue-600 mb-4">{title}</h2>
            <div class="overflow-x-auto shadow rounded-lg">
                <table class="min-w-full text-sm text-left border border-gray-300 bg-white">
                    <thead class="bg-blue-100">
                        <tr>{table_headers}</tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        <script>
            function copyToClipboard(button) {{
                const message = button.getAttribute("data-message");
                navigator.clipboard.writeText(message).then(function() {{
                    button.innerText = "✅ Copied!";
                    setTimeout(() => button.innerText = "📋 Copy Message", 2000);
                }});
            }}
        </script>
        """
        return table_html

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Car Listings Report</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 text-gray-800 font-sans leading-relaxed p-8">
        <div class="max-w-7xl mx-auto">
            <h1 class="text-4xl font-extrabold text-center text-blue-800 mb-8">🚗 Car Listings Report</h1>

            <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-12 shadow rounded-lg max-w-2xl mx-auto">
                <p class="text-lg">
                    💡 <strong>Expert Suggested Maximum Price:</strong>
                    <span class="text-green-800 font-semibold text-xl">{format_price(suggested_maximum_price)} TL</span>
                </p>
            </div>

            {generate_table_html(cheapest_listings, "Top 10 Cheapest Listings")}
            {generate_table_html(listings_with_newest_production_year1, "Alternative Top 10 Newest Year Listings")}
            {generate_table_html(least_used_listings, "Top 10 Least Used Listings")}
        </div>
    </body>
    </html>
    """

    output_file_name = f"{table_name}_report.html"
    with open(output_file_name, "w", encoding="utf-8") as file:
        file.write(html_content)

    output_file = Path(output_file_name).resolve()
    print(f"✅ HTML report generated: file://{output_file}")


def format_price(price):
    try:
        return f"{int(price):,} TL".replace(",", ".")  # optional: replace with dots for Turkish style
    except (ValueError, TypeError):
        return "N/A"
