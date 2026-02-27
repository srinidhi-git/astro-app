This `README.md` is designed to provide a professional overview of your **Vedic Astrology Suite**, highlighting its advanced astronomical calculations and UI features.

---

# 🌌 Vedic Astrology Suite (V1.9.5)

A professional-grade Vedic Astrology application built with Python. This suite leverages the **Swiss Ephemeris** for high-precision planetary calculations and features a dynamic GUI for natal chart analysis, divisional charts, and predictive timing systems.

## 🚀 Key Features

* **Dual Chart Styles**: Toggle between **South Indian** (fixed sign) and **North Indian** (fixed house/diamond) layouts.
* **Accurate Divisional Charts**: Includes logic for:
* **D1**: Rashi (Main Chart)
* **D2**: Hora (Wealth/Character)
* **D3**: Drekkana (Siblings/Action)
* **D9**: Navamsha (Marriage/Fruit of Chart)
* **D10**: Dashamsha (Career/Success)
* **D60**: Shastiamsha (Subtle Karma)


* **Real-time Transit Overlay**: Visualize current planetary positions (in orange) layered over natal placements.
* **Planetary Drishti (Aspects)**: Color-coded aspect lines identifying the influence of planets (e.g., Mars' 4th/7th/8th aspects in red, Jupiter's 5th/7th/9th in gold).
* **Vimshottari Dasha System**: Comprehensive 3-level time-period calculation (Mahadasha, Antardasha, and Pratyantar Dasha) with age tracking.
* **Automated Timezone Engine**: Search for any city globally; the app automatically calculates the correct UTC offset, accounting for historical Daylight Saving Time (DST).
* **Planetary Status Markers**: Icons for Retrograde (↓) and Combustion (*).

---

## 🛠 Prerequisites & Installation

To run this application, you must have Python 3.8+ installed. You will need to install the following dependencies:

### 1. Install System Dependencies

The core engine uses the Swiss Ephemeris. Install the required Python wrappers and utility libraries:

```bash
pip install pyswisseph geopy tkcalendar timezonefinder pytz

```

### 2. Package Breakdown

| Package | Purpose |
| --- | --- |
| `pyswisseph` | Precision astronomical calculations (Ephemeris). |
| `geopy` | Geocoding city names into Latitude/Longitude. |
| `tkcalendar` | Calendar widget for date selection. |
| `timezonefinder` | Determines Timezone names from coordinates. |
| `pytz` | Handles UTC offset and Daylight Saving Time logic. |

---

## 🖥 How to Run

1. Save the provided Python code into a file named `vedic_astro.py`.
2. Open your terminal or command prompt.
3. Navigate to the directory containing the file.
4. Execute the script:

```bash
python vedic_astro.py

```

---

## 📖 Usage Guide

### 1. Setting Location & Time

* **City Search**: Enter a city (e.g., "London" or "Tokyo") and click **Search & Get TZ**. The app will fetch coordinates and the correct timezone offset for that location.
* **Cascading Time**: Use the `<` and `>` buttons to step through minutes, hours, or days. The chart updates instantly, allowing you to see how planetary positions shift in real-time.

### 2. Analyzing Charts

* **Divisional Selection**: Use the dropdown menu to switch the secondary chart between D9, D10, etc.
* **Dignity Colors**:
* <span style="color:green">**Green**</span>: Exalted Planet.
* <span style="color:red">**Red**</span>: Debilitated Planet.
* **Black**: Neutral/Friend/Enemy status.



### 3. Predictive Analysis

* **Dasha Tables**: Select a row in the **Mahadasha** table to populate its **Antardashas**. Selecting an Antardasha will reveal the **Pratyantar** (sub-sub) periods.

---

## ⚠️ Notes

* **Ayanamsha**: The system defaults to **Lahiri (Chitra Paksha)**, the standard for Vedic Astrology.
* **Ephemeris Files**: The `swisseph` library calculates positions mathematically, but for extreme date ranges (thousands of years), it may seek external `.se1` files.

## How the app looks like
<img width="1284" height="1128" alt="image" src="https://github.com/user-attachments/assets/ee302586-6fa5-477b-aacf-895911261865" />

## Why this Jyotish Suite?

Most astrology software is either closed-source or lacks astronomical precision. This **Vedic Astrology Suite** bridges the gap by providing:

* **NASA-Grade Accuracy:** Powered by the Swiss Ephemeris for Lahiri Ayanamsha.
* **Dynamic UX:** Instant chart updates as you step through time—perfect for birth-time rectification.
* **Global Readiness:** Integrated `timezonefinder` and `geopy` for automatic UTC offset detection anywhere in the world.
* **Visual Intelligence:** Toggleable North/South Indian styles with color-coded planetary dignities and custom Drishti (aspect) line mapping.
