# 🌌 Vedic Astrology Suite (V1.9.7)

A high-precision Jyotish (Vedic Astrology) application built in Python. This suite utilizes the **NASA-grade Swiss Ephemeris** to provide professional-level accuracy for natal, divisional, and transit analysis.

## ✨ What's New in V1.9.7

* **Corrected Planetary Dignities:** Fixed Moon's exaltation (Taurus/1) and debilitation (Scorpio/7) logic.
* **Smart Combustion Engine:** Implemented variable combustion limits for Mercury and Venus based on their retrogression status.
* **True Node Handling:** Corrected Rahu/Ketu retrogression display and ensured Ketu is included in all data tables.
* **Full Shodashvarga:** Added all 16 prescribed Parashara divisional charts (D2 through D60) with accurate mathematical algorithms.

---

## 🚀 Core Features

* **Dual Chart Styles:** Toggle between **South Indian** (Fixed Sign) and **North Indian** (Fixed House) layouts.
* **Precision Astronomical Engine:** Powered by `pyswisseph` with Lahiri Ayanamsha (Chitra Paksha).
* **16 Divisional Charts (Vargas):**
* **D1 to D7:** Rashi, Hora, Drekkana, Chaturthamsha, Saptamsha.
* **D9 to D12:** Navamsha, Dashamsha, Dwadashamsha.
* **D16 to D60:** Shodashamsha, Vimshamsha, Chaturvimshamsha, Saptavimshamsha, Trimshamsha, Khavedamsha, Akshavedamsha, Shastiamsha.


* **Dynamic Transit Overlay:** View real-time planetary transits (Orange) layered directly over the natal chart.
* **Intelligent Aspect Lines (Drishti):** Planet-specific colored lines visualizing 4th, 5th, 7th, 8th, and 9th aspects.
* **Predictive Dasha System:** 3-level Vimshottari Dasha (Mahadasha, Antardasha, Pratyantar) with automatic age calculation.
* **Global Geocoding & Auto-TZ:** Search any city; the app fetches coordinates and calculates the exact historical UTC offset (DST-aware).

---

## 🛠 Installation & Setup

### 1. Requirements

* Python 3.8 or higher.
* Internet connection (for initial city/timezone search).

### 2. Install Dependencies

Run the following command to install the necessary libraries:

```bash
pip install pyswisseph geopy tkcalendar timezonefinder pytz

```
### 3. Package Breakdown

| Package | Purpose |
| --- | --- |
| `pyswisseph` | Precision astronomical calculations (Ephemeris). |
| `geopy` | Geocoding city names into Latitude/Longitude. |
| `tkcalendar` | Calendar widget for date selection. |
| `timezonefinder` | Determines Timezone names from coordinates. |
| `pytz` | Handles UTC offset and Daylight Saving Time logic. |

---

### 4. Running the App

```bash
python main.py

```

---

## 📖 User Guide

### Understanding Planetary Status

* **Green Text:** Planet is in its **Exaltation** sign.
* **Red Text:** Planet is in its **Debilitation** sign.
* **Symbol (↓):** Planet is in **Retrograde** motion.
* **Symbol (*):** Planet is **Combust** (too close to the Sun).

### Navigation

1. **Time Travel:** Use the `<` and `>` buttons to step through time. The chart recalculates instantly—useful for birth time rectification.
2. **Location:** Enter a city name and click **Search & Get TZ**. The longitude, latitude, and UTC offset will update automatically.
3. **Varga Selection:** Change the divisional chart using the dropdown menu next to the time settings.

---

## 🧮 Astronomical Specifications

* **Ayanamsha:** Lahiri (Chitra Paksha).
* **House System:** Sripati / Porphyry (Vedic standard).
* **Nodes:** Mean Nodes (Standard Vedic configuration).

---

## How the app looks like
<img width="1296" height="1126" alt="image" src="https://github.com/user-attachments/assets/2b9bcf6b-6885-4294-b97a-53c4570b6071" />


## Why this Jyotish Suite?

Most astrology software is either closed-source or lacks astronomical precision. This **Vedic Astrology Suite** bridges the gap by providing:

* **NASA-Grade Accuracy:** Powered by the Swiss Ephemeris for Lahiri Ayanamsha.
* **Dynamic UX:** Instant chart updates as you step through time—perfect for birth-time rectification.
* **Global Readiness:** Integrated `timezonefinder` and `geopy` for automatic UTC offset detection anywhere in the world.
* **Visual Intelligence:** Toggleable North/South Indian styles with color-coded planetary dignities and custom Drishti (aspect) line mapping.
