try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    import streamlit as st
    st.error(f"WeasyPrint nie jest dostępny: {e}")
    st.info("Sprawdź czy wszystkie systemowe zależności są zainstalowane")
from jinja2 import Template
import base64
import os
from datetime import datetime
from data.prices import base_prices, furnace_prices, base_paint_prices, get_delivery_info

def get_image_base64(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None

def get_sauna_images(sauna_type, sauna_model):
    images = []
    base_path = "images/"
    
    folder_mapping = {
        "Ankel Mini 1,8m": "Ankel Mini/",
        "Ankel Medium Open 2,4m": "Ankel Medium/Ankel Medium OPEN 2,4M/",
        "Ankel Medium Close 2,4m": "Ankel Medium/Ankel Medium CLOSE 2,4M/",
        "Ankel Large 3,0m": "Ankel Large/",
        "Ankel XL 3,6m": "Ankel XL/Ankel XL close/",
        "Toone Mini 1,8m": "Tønne Mini/",
        "Toone 2,4 Open": "Tønne Medium/Open/",
        "Toone 2,4 Close": "Tønne Medium/Close/",
        "Toone 3,0 Close": "Tønne Large/Close/",
        "Toone 3,6 Close": "Tønne XL/",
        "Toone 3,6 Open": "Tønne XL/"
    }
    
    folder = folder_mapping.get(sauna_model, "")
    if folder:
        full_path = os.path.join(base_path, folder)
        if os.path.exists(full_path):
            files = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            for file in files[:4]:
                img_path = os.path.join(full_path, file)
                img_base64 = get_image_base64(img_path)
                if img_base64:
                    images.append(img_base64)
    
    return images

def get_furnace_image(furnace_name):
    """Pobiera zdjęcie pieca na podstawie nazwy"""
    base_path = "images/Piece/"
    
    # Mapowanie nazw pieców na pliki zdjęć
    furnace_mapping = {
        "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz": "Piec_Harvia_z_kominem_i_kamieniami_Spalinowy_ładowany_od_wewnątrz.png",
        "Piec do sauny opalany drewnem - STOVEMAN 13-LS z kominem i kamieniami – ładowany od zewnątrz": "Piec_opalany_drewnem.png", 
        "Piec elektryczny NARVI 9 kW": "Piec_elektryczny.png"
    }
    
    filename = furnace_mapping.get(furnace_name)
    if filename:
        img_path = os.path.join(base_path, filename)
        return get_image_base64(img_path)
    
    return None

def get_logo_image():
    """Pobiera logo firmy jako base64"""
    logo_path = "images/LOGO/Wooden_spa.png"
    return get_image_base64(logo_path)

TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Oferta – Wooden Spa</title>
<style>
body {
font-family: Arial, sans-serif;
background: #fafafa;
color: #333;
margin: 0;
padding: 0px;
}
.container {
max-width: 1200px;
margin: auto;
background: #fff;
padding: 30px;
border-radius: 12px;
box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.header {
text-align: center;
margin-bottom: 30px;
}

h2 {
margin-top: 30px;
border-bottom: 2px solid #ddd;
padding-bottom: 5px;
}
.row {
display: flex;
justify-content: space-between;
margin-bottom: 20px;
}
.specs, .pricing, .contact {
margin-top: 20px;
}
table {
width: 100%;
border-collapse: collapse;
margin-top: 10px;
}
table td {
padding: 8px;
border-bottom: 1px solid #eee;
}
table td:first-child {
font-weight: bold;
width: 30%;
}
.images {
display: grid;
grid-template-columns: repeat(2, 1fr);
gap: 15px;
margin-top: 20px;
}
.images img {
width: 100%;
height: 200px;
object-fit: cover;
border-radius: 8px;
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.pricing table td {
font-size: 16px;
}
.pricing table tr:last-child td {
font-weight: bold;
font-size: 18px;
}
</style>
</head>
<body>
<div class="container">
<div class="header">
{% if logo_image %}
<img src="data:image/png;base64,{{ logo_image }}" alt="Wooden Spa Logo" style="width: 200px; height: auto; margin-bottom: 15px;">
{% endif %}
</div>

<div class="row">
  <div><strong>Lokalizacja dostawy:</strong>{{ sauna.location or "Do uzgodnienia" }}</div>
  <div><strong>Data oferty:</strong>{{ data }} | Nr: <span class="badge">{{ numer }}</div>
</div>

<h2>SPECIFICATIONS</h2>
<table>
  <tr><td>Model:</td><td>{{ sauna.model }}</td></tr>
  <tr><td>Piec:</td><td>{{ sauna.furnace }}</td></tr>
  {% if sauna.paint %}
  <tr><td>Malowanie:</td><td>{{ sauna.paint }}x krotne</td></tr>
  {% endif %}
  <tr><td>Odległość:</td><td>{{ distance_km }} km</td></tr>
</table>

  {% if furnace_image %}
  <h2>WYBRANY PIEC</h2>
  <div style="text-align: center; margin: 20px 0;">
    <img src="data:image/png;base64,{{ furnace_image }}" alt="Zdjęcie pieca" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <p style="margin-top: 10px; font-style: italic; color: #666;">{{ sauna.furnace }}</p>
  </div>
  {% endif %}

  {% if images %}
  <div class="images">
    {% for image in images %}
      <img src="data:image/jpeg;base64,{{ image }}" alt="Zdjęcie sauny {{ loop.index }}">
    {% endfor %}
  </div>
  {% endif %}

  

<h2>Kontakt</h2>
<p>Email: <a href="mailto:info@woodenvilla.com">info@woodenvilla.com</a> lub info@woodenvilla.com</p>
<p>Telefon: +48 533 664 102</p>
<p>Telefon: +48 601 750 925</p>

<h2>Podsumowanie</h2>
<div class="pricing">
  <table>
    <tr><td>Cena modelu</td><td>{{ model_price }} zł</td></tr>
    <tr><td>Cena pieca</td><td>{{ furnace_price }} zł</td></tr>
    <tr><td>Koszt dostawy</td><td>{{ delivery_cost }} zł</td></tr>
    {% if sauna.paint %}
    <tr><td>Cena malowania</td><td>{{ base_paint_price }} zł</td></tr>
    {% endif %}
    {% if sauna.custom_delivery %}
    <tr><td>Niestandardowy rozładunek</td><td>{{ custom_delivery_cost }} zł</td></tr>
    {% endif %}
    <tr style="border-top: 2px solid #333;"><td><strong>Cena końcowa</strong></td><td><strong>{{ base_price }} zł</strong></td></tr>
  </table>
</div>

</div>
</body>
</html>
"""

def generate_sauna_offer(sauna_data):
    if not WEASYPRINT_AVAILABLE:
        raise ImportError("WeasyPrint nie jest dostępny. Sprawdź instalację bibliotek systemowych.")
    
    images = get_sauna_images(sauna_data["type"], sauna_data["model"])
    furnace_image = get_furnace_image(sauna_data.get("furnace", ""))
    logo_image = get_logo_image()

    model_price = base_prices.get(sauna_data["model"], 0)
    base_paint_price = base_paint_prices.get(sauna_data['model'], 0)
    paint_multiplier = int(sauna_data.get("paint", 0))
    furnace_price = furnace_prices.get(sauna_data["furnace"], 0)

    delivery_info = get_delivery_info(sauna_data.get("location", ""))
    delivery_cost = delivery_info["delivery_cost"]
    distance_km = delivery_info["distance_km"]

    custom_delivery_cost = 0
    if sauna_data.get("custom_delivery"):
        try:
            custom_delivery_cost = float(sauna_data["custom_delivery"].replace("zł", "").replace(",", ""))
        except:
            custom_delivery_cost = 0

    paint_cost = base_paint_price * paint_multiplier if sauna_data.get("paint") else 0

    total_price = model_price + furnace_price + delivery_cost + custom_delivery_cost + paint_cost

    data = {
        "sauna": sauna_data,
        "images": images,
        "furnace_image": furnace_image,
        "logo_image": logo_image,
        "numer": f"SAU/{datetime.now().strftime('%Y/%m')}/{datetime.now().strftime('%d')}",
        "data": datetime.now().strftime("%d.%m.%Y"),
        "delivery_info": delivery_info,
        "distance_km": distance_km,
        
        # Poszczególne składniki cenowe dla podsumowania
        "model_price": f"{model_price:,.0f}".replace(",", " "),
        "furnace_price": f"{furnace_price:,.0f}".replace(",", " "),
        "delivery_cost": f"{delivery_cost:,.0f}".replace(",", " "),
        "base_paint_price": f"{paint_cost:,.0f}".replace(",", " "),
        "custom_delivery_cost": f"{custom_delivery_cost:,.0f}".replace(",", " "),
        
        # Cena końcowa
        "base_price": f"{total_price:,.0f}".replace(",", " ")
    }
    
    html = Template(TEMPLATE).render(**data)
    
    pdf_from_memory_to_bytes = HTML(string=html).write_pdf()
    return pdf_from_memory_to_bytes

def get_pdf_filename(sauna_data):
    final_pdf = sauna_data['model'].replace(" ", "_").replace(",", "").replace("/", "_")
    return f"{datetime.now().strftime('%d.%m.%Y')}_oferta_sauny_{final_pdf}.pdf"

if __name__ == "__main__":
    sample_data = {
        "type": "Ankel",
        "model": "Ankel Medium Open 2,4m",
        "location": "Warszawa",
        "custom_delivery": "1000zł",
        "furnace": "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz",
        "paint": "1x krotne"
    }
    
    generate_sauna_offer(sample_data)
