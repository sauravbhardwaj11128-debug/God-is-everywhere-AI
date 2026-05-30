import streamlit as st
import requests
import google.generativeai as genai
from geopy.distance import geodesic
st.set_page_config(
    page_title="AI Temple Finder",
    page_icon="🛕",
    layout="wide"
)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🛕 AI Temple Finder")
st.write("Find nearby temples using OpenStreetMap + Gemini AI")
col1, col2 = st.columns(2)

with col1:
    lat = st.text_input("Latitude", "28.4595")

with col2:
    lon = st.text_input("Longitude", "77.0266")

radius = st.slider(
    "Search Radius (meters)",
    1000,
    10000,
    5000
)

if st.button("🔍 Find Nearby Temples"):

    with st.spinner("Finding temples..."):

        query = f"""
        [out:json];

        (
          node["amenity"="place_of_worship"]
          ["religion"="hindu"]
          (around:{radius},{lat},{lon});
        );

        out;
        """

        url = "https://overpass-api.de/api/interpreter"

        response = requests.get(
            url,
            params={'data': query}
        )

        data = response.json()

        temples = []

        for element in data['elements']:

            tags = element.get('tags', {})

            name = tags.get('name')

            if name:

                temple = {
                    "name": name,
                    "lat": element['lat'],
                    "lon": element['lon']
                }

                temples.append(temple)

        if temples:

            st.success(f"{len(temples)} temples found!")

            for temple in temples[:5]:

                st.divider()

                st.subheader(f"🛕 {temple['name']}")

                user_location = (float(lat), float(lon))

                temple_location = (
                    temple['lat'],
                    temple['lon']
                )

                distance = geodesic(
                    user_location,
                    temple_location
                ).km

                st.write(f"📍 Distance: {distance:.2f} km")

                maps_link = (
                    f"https://www.openstreetmap.org/"
                    f"?mlat={temple['lat']}"
                    f"&mlon={temple['lon']}"
                )

                st.write("🗺 Map:", maps_link)

                prompt = f"""
                Give detailed information about
                {temple['name']} temple.

                Include:

                - History
                - Timings
                - Importance
                - Famous things
                - Visitor tips

                Keep response clean and readable.
                """

                ai_response = model.generate_content(prompt)

                st.write(ai_response.text)

        else:
            st.error("No temples found nearby.")
