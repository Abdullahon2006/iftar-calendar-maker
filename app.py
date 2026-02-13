import streamlit as st
import requests
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Iftar Calendar Maker", page_icon="🌙")

def get_prayer_times(city, country, method_id, year):
    """Fetches prayer times and timezone from Aladhan API."""
    url = "http://api.aladhan.com/v1/calendarByCity"
    params = {
        "city": city,
        "country": country,
        "method": method_id,
        "annual": "true",
        "year": year
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            # Extract the timezone from the first available day
            first_day = list(data['data'].values())[0][0]
            timezone = first_day['meta']['timezone']
            return data['data'], timezone
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    return None, None

def create_ics(prayer_data, timezone, suhur_offset, iftar_duration, fajr_correction, maghrib_correction):
    """Generates the ICS file with dynamic timezone and corrections."""
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ramadan Calendar Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ramadan Schedule",
        f"X-WR-TIMEZONE:{timezone}"  # Critical Fix: Dynamic Timezone
    ]

    # Process each month and day
    for month_str, days in prayer_data.items():
        for day in days:
            date_str = day['date']['gregorian']['date']
            try:
                date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            except ValueError:
                continue

            # Check if it's Ramadan (Hijri month 9)
            hijri_month = day['date']['hijri']['month']['number']
            if hijri_month != 9:
                continue

            # Parse Times
            fajr_raw = day['timings']['Fajr'].split()[0]
            maghrib_raw = day['timings']['Maghrib'].split()[0]

            fajr_time = datetime.datetime.strptime(fajr_raw, "%H:%M").time()
            maghrib_time = datetime.datetime.strptime(maghrib_raw, "%H:%M").time()

            fajr_dt = datetime.datetime.combine(date_obj, fajr_time)
            maghrib_dt = datetime.datetime.combine(date_obj, maghrib_time)

            # --- APPLY MANUAL CORRECTIONS ---
            # Use this to match the website exactly (e.g. -2 mins)
            fajr_dt += datetime.timedelta(minutes=fajr_correction)
            maghrib_dt += datetime.timedelta(minutes=maghrib_correction)

            # --- SUHUR LOGIC ---
            # Suhur End: User defined buffer before Fajr (e.g. 10 mins or 0 mins)
            suhur_end = fajr_dt - datetime.timedelta(minutes=suhur_offset)
            # Suhur Start: 1.5 hours (90 mins) before the end time
            suhur_start = suhur_end - datetime.timedelta(minutes=90)
            
            # --- IFTAR LOGIC ---
            iftar_start = maghrib_dt
            iftar_end = maghrib_dt + datetime.timedelta(minutes=iftar_duration)

            # Generate VEVENT blocks
            # Suhur
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"SUMMARY:Suhur (Stop: {suhur_end.strftime('%H:%M')})")
            ics_content.append(f"DTSTART;TZID={timezone}:{suhur_start.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append(f"DTEND;TZID={timezone}:{suhur_end.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append(f"DESCRIPTION:Stop eating at {suhur_end.strftime('%H:%M')}")
            ics_content.append("END:VEVENT")

            # Iftar
            ics_content.append("BEGIN:VEVENT")
            ics_content.append(f"SUMMARY:Iftar ({iftar_start.strftime('%H:%M')})")
            ics_content.append(f"DTSTART;TZID={timezone}:{iftar_start.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append(f"DTEND;TZID={timezone}:{iftar_end.strftime('%Y%m%dT%H%M%S')}")
            ics_content.append("DESCRIPTION:Maghrib prayer time.")
            ics_content.append("END:VEVENT")

    ics_content.append("END:VCALENDAR")
    return "\n".join(ics_content)

# --- APP UI ---
st.title("🌙 Iftar Calendar Maker")
st.write("Generate a calendar that actually matches your local mosque.")

# 1. Location
col1, col2 = st.columns(2)
with col1:
    city = st.text_input("City", "Tashkent")
with col2:
    country = st.text_input("Country", "Uzbekistan")

# 2. Calculation Method (Crucial for Tashkent)
st.write("### ⚙️ Calculation Settings")
method_options = {
    3: "Muslim World League (Standard for Uzbekistan)",
    1: "University of Islamic Sciences, Karachi",
    13: "Diyanet (Turkey)",
    2: "ISNA (North America)",
    4: "Umm Al-Qura (Makkah)"
}
method_id = st.selectbox(
    "Calculation Method", 
    options=list(method_options.keys()), 
    format_func=lambda x: method_options[x],
    index=0 # Default to MWL for Tashkent
)

# 3. Fine Tuning (The Fix for namozvaqti.uz)
with st.expander("🛠️ Fine Tuning (Fix inconsistencies)"):
    st.write("If the API times differ from `namozvaqti.uz`, adjust them here.")
    
    col_tune1, col_tune2 = st.columns(2)
    with col_tune1:
        fajr_correction = st.number_input("Fajr Offset (Minutes)", min_value=-60, max_value=60, value=0, help="e.g., -2 to make it earlier")
    with col_tune2:
        maghrib_correction = st.number_input("Maghrib Offset (Minutes)", min_value=-60, max_value=60, value=0)

    st.write("---")
    suhur_buffer = st.slider("Stop Eating X mins before Fajr", 0, 60, 10, help="Set to 0 if the printed time is already the stop time.")
    iftar_duration = st.slider("Iftar Event Duration (Minutes)", 15, 120, 60)

# ... previous code ...

# 4. Year Selection (New Feature)
current_year = datetime.date.today().year
year = st.number_input("Year", min_value=2024, max_value=2030, value=current_year)

# 5. Generate
if st.button("Generate Calendar"):
    with st.spinner(f"Fetching data for {city} in {year}..."):
        # Pass the 'year' variable instead of 2026
        data, timezone = get_prayer_times(city, country, method_id, year)
        
        if data and timezone:
            ics_string = create_ics(
                data, timezone, 
                suhur_buffer, iftar_duration, 
                fajr_correction, maghrib_correction
            )
            
            st.success(f"✅ Success! Calendar for Ramadan {year} generated.")
            st.download_button(
                label=f"📥 Download {year} Calendar",
                data=ics_string,
                file_name=f"ramadan_{city}_{year}.ics",
                mime="text/calendar"
            )
        else:
            st.error("Could not find data. Please check your inputs.")
