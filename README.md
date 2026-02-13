# Iftar Calendar Maker 🌙

A web application that generates personalized **Ramadan Timetables** compatible with Google Calendar, Apple Calendar, and Outlook.

Built with **Python** and **Streamlit**, this tool allows users to input any city in the world and download a custom `.ics` file containing precisely calculated Suhur and Iftar events for the entire month of Ramadan.

## Features

* ** Global Coverage:** Fetches accurate prayer times for any city/country using the [Aladhan API](https://aladhan.com/prayer-times-api).
* ** Customizable Schedules:**
* **Suhur:** Intelligent calculation (default: starts 1.5 hours before Fajr, ends 10 mins before Fajr).
* **Iftar:** Schedule blocking (default: starts at Maghrib, lasts 1 hour).


* **📅 Universal Export:** Generates standard iCalendar (`.ics`) files supported by all major calendar apps.
* **Instant:** No installation required for end-users; runs entirely in the browser.

## 🛠️ How It Works

1. **Enter Location:** Type your City and Country (e.g., `Istanbul, Turkey` or `Tashkent, Uzbekistan`).
2. **Customize:** Adjust the duration sliders if you want a longer Suhur or shorter Iftar window.
3. **Download:** Click "Generate Calendar" to get your `.ics` file.
4. **Import:** Open the file to add it to your personal calendar.

## 💻 Running Locally

If you want to run this code on your own machine or contribute to it:

### 1. Clone the Repository

```bash
git clone https://github.com/Abdullahon2006/iftar-calendar-maker.git
cd iftar-calendar-maker

```

### 2. Install Requirements

Make sure you have Python installed, then run:

```bash
pip install -r requirements.txt

```

### 3. Run the App

```bash
streamlit run app.py

```

The app will open in your browser at `http://localhost:8501`.

## 📦 Project Structure

```text
iftar-calendar-maker/
├── app.py              # Main application logic (Frontend + Backend)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Git configuration

```

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features (e.g., different calculation methods for Hanafi/Shafi'i, notification integration, etc.), feel free to open an issue or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
