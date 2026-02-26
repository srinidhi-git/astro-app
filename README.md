## README.md

This project is a professional-grade **Vedic Astrology (Jyotish) Suite** built with Python. It provides high-precision planetary calculations, divisional charts, and a drill-down Vimsottari Dasha system.

---

### ### Features

* **High-Precision Calculations:** Uses the Swiss Ephemeris (`pyswisseph`) for astronomical accuracy.
* **Ayanamsha:** Defaulted to **Lahiri (Chitra Paksha)**, the standard for Vedic Astrology.
* **Dynamic Charts:** * **Rashi Chart (D1):** Shows planetary positions in the South Indian style.
* **Divisional Charts:** Supports D2, D3, D9 (Navamsha), D10, and D60 via a dropdown selector.


* **Vimsottari Dasha System:** * 3-level nested calculation: **Mahadasha → Antardasha → Pratyantardasha**.
* Calculates based on the Moon's longitudinal position at birth.


* **Interactive UI:** * Scrollable interface to view all tables simultaneously.
* Geographic search (City to Lat/Lon conversion) via Nominatim.
* Strict input validation (Day/Month/Time range limits).
* Planetary details include **DMS (Degree, Minute, Second)**, Nakshatra, Pada, and Nakshatra Lord.



---

### ### Installation

To run this application, you need Python installed on your system. You must install the following dependencies:

#### 1. Core Libraries

Open your terminal or command prompt and run:

```bash
pip install pyswisseph geopy tkcalendar

```

#### 2. System Dependencies

* **Tkinter:** Usually comes pre-installed with Python. If you receive a `ModuleNotFoundError: No module named 'tkinter'`, install it via:
* **Linux (Ubuntu/Debian):** `sudo apt-get install python3-tk`
* **macOS:** Install via Homebrew: `brew install python-tk`
* **Windows:** Re-run the Python installer and ensure "tcl/tk and IDLE" is checked.



---

### ### Technical Details

The app calculates positions based on the **Sidereal Zodiac**.

| Component | Logic Applied |
| --- | --- |
| **Ephemeris** | Swiss Ephemeris (FLG_SIDEREAL) |
| **House System** | Equal House (Whole Sign) |
| **Dasha Year** | 365.25 Days (Solar Year Approximation) |
| **DMS Format** | $DD^\circ MM' SS''$ |

---

### ### How to Use

1. **Run the script:** `python main.py` (replace with your filename).
2. **Set Location:** Type a city name and click **Search** to fetch coordinates, or enter Lat/Lon manually.
3. **Enter Birth Details:** Use the calendar or the increment buttons (`<` / `>`) to set date and time. The chart updates automatically.
4. **View Dashas:** * Click on a row in the **Mahadasha** table to load its **Antardashas**.
* Click on an **Antardasha** row to load the **Pratyantardashas**.
