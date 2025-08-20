import streamlit as st 
from pdf_template import generate_sauna_offer, get_pdf_filename
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def sauny_config_text():
    st.subheader("Konfiguracja")
    sauna_configuration = st.text_area("Konfiguracja sauny", value="", height=300, placeholder="Opisz saunę słowami, np: 'Chcę saunę Ankel Medium Open 2,4m z piecem elektrycznym NARVI, dostawa do Warszawy, malowanie 2x krotne'")
    
    if st.button("Generuj ofertę PDF", key="text_pdf_button"):
        if not sauna_configuration.strip():
            st.error("Proszę wpisać opis konfiguracji sauny")
            return
            
        try:
            response = client.chat.completions.create(
                model="gpt-5-nano-2025-08-07",
                messages=[
                    {"role": "system", "content": """Od teraz twoim zadaniem jest poukladanie calego tekstu i zwrocenie go w odpowiednim formacie JSON: 

                    Przyklad:
                    {
                        "type": "Ankel",
                        "model": "Ankel Mini 1,8m",
                        "location": "Warszawa",
                        "custom_delivery": "1000",
                        "furnace": "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz",
                        "paint": "1"
                    }
                    
                    Do indentyfikacji modelu typu rodzaju pieca skorzystaj z tych danych:
                    type:
                    "Ankel"
                    "Toone"

                    model:
                    "Ankel Mini 1,8m"
                    "Ankel Medium Open 2,4m"
                    "Ankel Medium Close 2,4m"
                    "Ankel Large 3,0m"
                    "Ankel XL 3,6m"
                    "Toone Mini 1,8m"
                    "Toone 2,4 Open"
                    "Toone 2,4 Close"
                    "Toone 3,0 Close"
                    "Toone 3,6 Close"
                    "Toone 3,6 Open"


                    furnace:
                    "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz"
                    "Piec do sauny opalany drewnem - STOVEMAN 13-LS z kominem i kamieniami – ładowany od zewnątrz"
                    "Piec elektryczny NARVI 9 kW"
                    """},
                    {"role": "user", "content": sauna_configuration}
                ]
            )
            
            # Parsuj odpowiedź z OpenAI
            sauna_data = json.loads(response.choices[0].message.content)
            
            # Wyświetl sparsowane dane
            st.success("✅ Konfiguracja została rozpoznana!")
            
            # Generuj PDF z sparsowanymi danymi
            pdf_bytes = generate_sauna_offer(sauna_data)
            filename = get_pdf_filename(sauna_data)
            
            st.success("✅ Oferta PDF została wygenerowana!")
            st.balloons()
            
            # Wyświetl podsumowanie oferty
            st.subheader("📋 Podsumowanie oferty:")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Typ:** {sauna_data.get('type', 'Nieznany')}")
                st.write(f"**Model:** {sauna_data.get('model', 'Nieznany')}")
                st.write(f"**Lokalizacja:** {sauna_data.get('location', 'Do uzgodnienia')}")
            
            with col2:
                st.write(f"**Piec:** {sauna_data.get('furnace', 'Nieznany')}")
                if sauna_data.get('paint'):
                    st.write(f"**Malowanie:** {sauna_data.get('paint')}x krotne")
                if sauna_data.get('custom_delivery'):
                    st.write(f"**Dodatkowy rozładunek:** {sauna_data.get('custom_delivery')}")
            
            # Przycisk pobierania PDF
            st.download_button(
                label="📥 Pobierz PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary"
            )
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Błąd parsowania odpowiedzi AI: {str(e)}")
            st.write("AI nie zwróciło poprawnego formatu JSON. Spróbuj ponownie z bardziej precyzyjnym opisem.")
        except Exception as e:
            st.error(f"❌ Błąd podczas generowania oferty: {str(e)}")
            st.write(f"Szczegóły błędu: {str(e)}")


def sauny_config():
    st.subheader("Konfiguracja")
    type = st.selectbox("Typ sauny", ["Ankel", "Toone"], index=0)

    if type == "Ankel":
        model = st.radio("Wybierz model Ankel:", [
            "Ankel Mini 1,8m",
            "Ankel Medium Open 2,4m", 
            "Ankel Medium Close 2,4m",
            "Ankel Large 3,0m",
            "Ankel XL 3,6m"
        ])
    elif type == "Toone":
        model = st.radio("Wybierz model Toone:", [
            "Toone Mini 1,8m",
            "Toone 2,4 Open",
            "Toone 2,4 Close", 
            "Toone 3,0 Close",
            "Toone 3,6 Close",
            "Toone 3,6 Open"
        ])
    
    location = st.text_input("Lokalizacja dostawy", value="", placeholder="Warszawa")
    
    if location:
        try:
            from data.prices import get_delivery_info
            delivery_info = get_delivery_info(location)
            
            if delivery_info["distance_km"] > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📏 Odległość: **{delivery_info['distance_km']} km**")
                with col2:
                    st.warning(f"🚚 Koszt dostawy: **{delivery_info['delivery_cost']} zł**")
        except Exception as e:
            st.error(f"Nie można obliczyć odległości: {e}")

    custom_delivery = st.text_input("Niestandardowy rozładunek", value="", placeholder="1000zł")

    furnace = st.radio("Wybierz piec", [
        "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz", 
        "Piec do sauny opalany drewnem - STOVEMAN 13-LS z kominem i kamieniami – ładowany od zewnątrz", 
        "Piec elektryczny NARVI 9 kW"
        ])
    
    paint = st.text_input("Malowanie", value="", placeholder="1x krotne")

    if st.button("Generuj ofertę PDF"):
        sauna_data = {
            "type": type,
            "model": model,
            "location": location,
            "custom_delivery": custom_delivery,
            "furnace": furnace,
            "paint": paint
        }
        
        try:
            pdf_bytes = generate_sauna_offer(sauna_data)
            filename = get_pdf_filename(sauna_data)
            
            st.success("✅ Oferta PDF została wygenerowana!")
            st.balloons()
            
            st.subheader("📋 Podsumowanie oferty:")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Typ:** {type}")
                st.write(f"**Model:** {model}")
                st.write(f"**Lokalizacja:** {location or 'Do uzgodnienia'}")
            
            with col2:
                st.write(f"**Piec:** {furnace}")
                if paint:
                    st.write(f"**Malowanie:** {paint}")
                if custom_delivery:
                    st.write(f"**Dodatkowy rozładunek:** {custom_delivery}")
            
            st.download_button(
                label="📥 Pobierz PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"❌ Błąd podczas generowania PDF: {str(e)}")
            st.write("Sprawdź czy wszystkie wymagane biblioteki są zainstalowane.")
            st.write(f"Szczegóły błędu: {str(e)}")
    
    return {
        "type": type,
        "model": model,
        "location": location,
        "custom_delivery": custom_delivery,
        "furnace": furnace,
        "paint": paint
    }

def sauny_interface():
    st.set_page_config(page_title="Ofertownik Sauny")
    st.image("images/LOGO/Wooden_spa.png", width=300)
    st.title("Generator ofert AI - Wooden Spa")
    
    config = st.radio("Wybierz tryb konfiguracji", ["Głosowa/Tekstowa", "Lista do zaznaczania"])
    if config == "Głosowa/Tekstowa":
        sauny_config_text()
    elif config == "Lista do zaznaczania":
        sauny_config()

if __name__ == "__main__":
    sauny_interface()

