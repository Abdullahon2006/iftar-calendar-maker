import streamlit as st
import requests
import datetime
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Ramadan Calendar Generator", page_icon="🌙")

def get_prayer_times(city, country, method_id, year):
    """Fetches prayer times from Aladhan API for the whole year."""
    # Method 13 is Diyanet (Turkey), suitable for your region.
    # See https://aladhan.com/prayer-times-api#GetCalendarByCity for other methods.
    url = "http://api.aladhan.com/v1/calendarByCity"
    params = {
        "city": city,
        "country": country,
        "method": method_id,
        "annual": "true",
        "year": year
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    return None

def create_ics(prayer_data, suhur_offset_minutes, iftar_duration_minutes):
    """Generates the ICS file content string."""
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ramadan Calendar Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ramadan Schedule",
    ]

    # Process each month and day
    for month_str, days in prayer_data.items():
        for day in days:
            date_str = day['date']['gregorian']['date']  # DD-MM-YYYY
            try:
                date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            except ValueError:
                continue

            # Check if it's Ramadan (Hijri month 9)
            hijri_month = day['date']['hijri']['month']['number']
            if hijri_month != 9:
                continue

            # Parse Times (Clean up format like "05:43 (TRT)")
            fajr_raw = day['timings']['Fajr'].split()[0]
            maghrib_raw = day['timings']['Maghrib'].split()[0]

            fajr_time = datetime.datetime.strptime(fajr_raw, "%H:%M").time()
            maghrib_time = datetime.datetime.strptime(maghrib_raw, "%H:%M").time()

            fajr_dt = datetime.datetime.combine(date_obj, fajr_time)
            maghrib_dt = datetime.datetime.combine(date_obj, maghrib_time)

            # --- SUHUR LOGIC ---
            # Suhur ends 10 mins before Fajr (User Rule)
            # Suhur starts earlier based on user offset
            suhur_end = fajr_dt - datetime.timedelta(minutes=10)
            suhur_start = suhur_end - datetime.timedelta(minutes=suhur_offset_minutes)
            
            # --- IFTAR LOGIC ---
            # Starts at Maghrib, lasts for user-defined duration
            iftar_start = maghrib_dt
            iftar_end = maghrib_dt + datetime.timedelta(minutes=iftar_duration_minutes)

            # Generate VEVENT blocks
            # Suhur Event
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"SUMMARY:Suhur (Stop Eating @ {suhur_end.strftime('%H:%M')})")
            ics_content.append(f"DTSTART;TZID=Europe/Istanbul:{suhur_start.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append(f"DTEND;TZID=Europe/Istanbul:{suhur_end.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append("DESCRIPTION:Suhur time based on Fajr.")
            ics_content.append("END:VEVENT")

            # Iftar Event
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"SUMMARY:Iftar")
            ics_content.append(f"DTSTART;TZID=Europe/Istanbul:{iftar_start.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append(f"DTEND;TZID=Europe/Istanbul:{iftar_end.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append("DESCRIPTION:Time to break fast.")
            ics_content.append("END:VEVENT")

    ics_content.append("END:VCALENDAR")
    return "\n".join(ics_content)

# --- APP UI ---
st.title("🌙 Ramadan Calendar Generator")
st.write("Generate a custom calendar for Google Calendar, Outlook, or Apple Calendar.")

# Inputs
col1, col2 = st.columns(2)
with col1:
    city = st.text_input("City", "Istanbul")
with col2:
    country = st.text_input("Country", "Turkey")

st.info("Default settings are for Diyanet (Turkey) calculation methods.")

# Advanced Settings Expander
with st.expander("Customize Timings"):
    # Default: 1.5 hours (90 mins) before Fajr - 10 mins buffer = 80 mins duration roughly
    suhur_duration = st.slider("Suhur Duration (Minutes)", 30, 120, 90, help="How long before 'Stop Time' does Suhur start?")
    iftar_duration = st.slider("Iftar Duration (Minutes)", 15, 120, 60, help="How long is the Iftar event?")

if st.button("Generate Calendar"):
    with st.spinner(f"Fetching prayer times for {city}..."):
        # 13 is the Method ID for Diyanet (Turkey)
        data = get_prayer_times(city, country, 13, 2026)
        
        if data:
            ics_string = create_ics(data, suhur_duration, iftar_duration)
            
            # Create download button
            st.success(f"Calendar ready for {city}, {country}!")
            st.download_button(
                label="📥 Download .ics File",
                data=ics_string,
                file_name=f"ramadan_{city}_2026.ics",
                mime="text/calendar"
            )
        else:
            st.error("Could not find that city. Please check the spelling.")
