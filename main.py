import tkinter as tk
from tkinter import ttk, messagebox
import swisseph as swe
from datetime import datetime, timedelta
import calendar
import math
import json
import os
from geopy.geocoders import Nominatim
from tkcalendar import DateEntry
from timezonefinder import TimezoneFinder
import pytz

class ProfessionalVedicAppV1:
    def __init__(self, root):
        self.root = root
        self.root.title("Vedic Astrology Suite - V1.9.14 (Precision Seconds & Searchable Profiles)")
        self.root.geometry("1400x1000")
        
        # --- Scrollable Main Container ---
        self.main_canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # State & Constants
        self.profile_file = "astro_profiles.json"
        self.lat, self.lon, self.tz = tk.DoubleVar(value=12.9716), tk.DoubleVar(value=77.5946), tk.DoubleVar(value=5.5)
        self.geolocator = Nominatim(user_agent="vedic_astro_v1_9_14")
        self.tz_finder = TimezoneFinder()
        self._updating = False
        self.all_profiles = []
        
        # Display Toggles
        self.north_style = tk.BooleanVar(value=False)
        self.show_transits = tk.BooleanVar(value=False)
        self.show_drishti = tk.BooleanVar(value=False)
        self.show_outer = tk.BooleanVar(value=False)

        self.nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
                          "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                          "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        self.lord_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        self.signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        self.tithis = ["Pratipada (S)", "Dwitiya (S)", "Tritiya (S)", "Chaturthi (S)", "Panchami (S)", "Shashthi (S)", "Saptami (S)", "Ashtami (S)", "Navami (S)", "Dashami (S)", "Ekadashi (S)", "Dwadashi (S)", "Trayodashi (S)", "Chaturdashi (S)", "Purnima", 
                       "Pratipada (K)", "Dwitiya (K)", "Tritiya (K)", "Chaturthi (K)", "Panchami (K)", "Shashthi (K)", "Saptami (K)", "Ashtami (K)", "Navami (K)", "Dashami (K)", "Ekadashi (K)", "Dwadashi (K)", "Trayodashi (K)", "Chaturdashi (K)", "Amavasya"]
        self.yogas = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
        self.varjyam_starts = [50, 24, 30, 40, 14, 21, 30, 20, 32, 30, 20, 18, 21, 20, 14, 14, 10, 14, 20, 24, 20, 10, 10, 18, 16, 24, 30]

        self.d_charts = {"D2 (Hora)": 2, "D3 (Drekkana)": 3, "D4 (Chaturthamsha)": 4, "D7 (Saptamsha)": 7, "D9 (Navamsha)": 9, "D10 (Dashamsha)": 10, "D12 (Dwadashamsha)": 12, "D16 (Shodashamsha)": 16, "D20 (Vimshamsha)": 20, "D24 (Chaturvimshamsha)": 24, "D27 (Saptavimshamsha)": 27, "D30 (Trimshamsha)": 30, "D40 (Khavedamsha)": 40, "D45 (Akshavedamsha)": 45, "D60 (Shastiamsha)": 60}
        self.selected_d_label = tk.StringVar(value="D9 (Navamsha)")

        self.dignities = {"Sun": (0, 10), "Moo": (1, 3), "Mar": (9, 28), "Mer": (5, 15), "Jup": (3, 5), "Ven": (11, 27), "Sat": (6, 20)}
        self.combust_limits = {"Moo": 12, "Mar": 17, "Mer": 14, "Jup": 11, "Ven": 10, "Sat": 15}

        self.setup_ui()
        self.update_chart()

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _create_scrollable_tree(self, parent, columns, height, widths, anchors=None):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=2)
        scroll = ttk.Scrollbar(frame, orient="vertical")
        scroll.pack(side="right", fill="y")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height, yscrollcommand=scroll.set)
        scroll.config(command=tree.yview)
        for i, c in enumerate(columns):
            anchor = anchors[i] if anchors else "center"
            tree.heading(c, text=c)
            tree.column(c, width=widths[i], anchor=anchor)
        tree.pack(side="left", fill="x", expand=True)
        return tree

    def setup_ui(self):
        parent = self.scrollable_frame
        now = datetime.now()

        # --- Profile Management (Searchable) ---
        prof_frame = tk.LabelFrame(parent, text=" Profile Management ")
        prof_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(prof_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        self.ent_name = tk.Entry(prof_frame, width=15); self.ent_name.insert(0, "Default")
        self.ent_name.pack(side=tk.LEFT, padx=5)
        tk.Button(prof_frame, text="Save Profile", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        
        tk.Label(prof_frame, text="Search Profile:").pack(side=tk.LEFT, padx=(15, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_profiles)
        self.profile_cb = ttk.Combobox(prof_frame, textvariable=self.search_var, width=20)
        self.profile_cb.pack(side=tk.LEFT, padx=5)
        self.load_profile_list()
        tk.Button(prof_frame, text="Load Selected", command=self.load_profile).pack(side=tk.LEFT, padx=5)
        
        # --- Location Settings ---
        loc_frame = tk.LabelFrame(parent, text=" Location Settings ")
        loc_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(loc_frame, text="City:").pack(side=tk.LEFT, padx=5)
        self.ent_loc = tk.Entry(loc_frame, width=20); self.ent_loc.insert(0, "Bangalore")
        self.ent_loc.pack(side=tk.LEFT, padx=5)
        tk.Button(loc_frame, text="Search & Get TZ", command=self.search_location).pack(side=tk.LEFT, padx=5)
        tk.Label(loc_frame, text="Lat:").pack(side=tk.LEFT, padx=(15,0)); tk.Entry(loc_frame, textvariable=self.lat, width=7).pack(side=tk.LEFT)
        tk.Label(loc_frame, text="Lon:").pack(side=tk.LEFT, padx=(10,0)); tk.Entry(loc_frame, textvariable=self.lon, width=7).pack(side=tk.LEFT)
        tk.Label(loc_frame, text="TZ Offset:").pack(side=tk.LEFT, padx=(10,0)); tk.Entry(loc_frame, textvariable=self.tz, width=5).pack(side=tk.LEFT)

        # --- Time & Chart Selection (Included Seconds) ---
        time_frame = tk.LabelFrame(parent, text=" Birth Date, Time & Chart Selection ")
        time_frame.pack(fill="x", padx=20, pady=5)
        self.cal = DateEntry(time_frame, width=12, background='darkblue', year=now.year, month=now.month, day=now.day)
        self.cal.grid(row=0, column=0, padx=20, rowspan=2); self.cal.bind("<<DateEntrySelected>>", self.sync_cal_to_vars)
        self.time_vars = {}
          
        units = [("Year", now.year), ("Month", now.month), ("Day", now.day), ("Hour", now.hour), ("Minute", now.minute), ("Second", now.second)]
        for i, (l, d) in enumerate(units):
            sub = tk.Frame(time_frame); sub.grid(row=0, column=i+1, padx=5)
            tk.Label(sub, text=l, font=("Arial", 7)).pack()
            btn_frame = tk.Frame(sub); btn_frame.pack()
            tk.Button(btn_frame, text="<", width=2, command=lambda x=l: self.step_time(x, -1)).pack(side=tk.LEFT)
            v = tk.StringVar(value=str(d)); v.trace_add("write", lambda *a, x=l: self.validate_and_sync(x))
            tk.Entry(btn_frame, textvariable=v, width=5, justify='center').pack(side=tk.LEFT, padx=2)
            self.time_vars[l] = v
            tk.Button(btn_frame, text=">", width=2, command=lambda x=l: self.step_time(x, 1)).pack(side=tk.LEFT)
        
        div_cb = ttk.Combobox(time_frame, textvariable=self.selected_d_label, values=list(self.d_charts.keys()), state="readonly", width=20)
        div_cb.grid(row=0, column=8, padx=20)
        div_cb.bind("<<ComboboxSelected>>", lambda e: self.update_chart())

        view_frame = tk.LabelFrame(parent, text=" Display Options ")
        view_frame.pack(fill="x", padx=20, pady=5)
        tk.Checkbutton(view_frame, text="North Indian Style", variable=self.north_style, command=self.update_chart).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(view_frame, text="Transits", variable=self.show_transits, command=self.update_chart).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(view_frame, text="Drishti", variable=self.show_drishti, command=self.update_chart).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(view_frame, text="Outer Planets", variable=self.show_outer, command=self.update_chart).pack(side=tk.LEFT, padx=10)

        chart_container = tk.Frame(parent); chart_container.pack(pady=5)
        self.canvas_d1 = tk.Canvas(chart_container, width=500, height=500, bg="white", highlightthickness=1); self.canvas_d1.pack(side=tk.LEFT, padx=20)
        self.canvas_div = tk.Canvas(chart_container, width=500, height=500, bg="white", highlightthickness=1); self.canvas_div.pack(side=tk.LEFT, padx=20)

        table_frame = tk.LabelFrame(parent, text=" Planetary Positions ")
        table_frame.pack(fill="x", padx=20, pady=5)
        self.tree = self._create_scrollable_tree(
            table_frame, 
            ("Planet", "DMS", "Rashi", "Nakshatra", "Pada", "Nak Lord", "Status"), 
            8, [130]*7
        )

        panchang_frame = tk.LabelFrame(parent, text=" Panchang & Daily Muhurta ")
        panchang_frame.pack(fill="x", padx=20, pady=5)
        self.panchang_tree = self._create_scrollable_tree(
            panchang_frame, 
            ("Attribute", "Value", "Attribute2", "Value2"), 
            7, [250]*4, ["w", "center", "w", "center"]
        )

        self.setup_dasha_ui(parent)

    # --- Profile Logic (Searchable & Sorted) ---
    def filter_profiles(self, *args):
        search_term = self.search_var.get().lower()
        filtered = [p for p in self.all_profiles if search_term in p.lower()]
        self.profile_cb['values'] = filtered

    def save_profile(self):
        name = self.ent_name.get()
        if not name: return
        data = {
            "name": name, "city": self.ent_loc.get(), "lat": self.lat.get(), "lon": self.lon.get(), "tz": self.tz.get(),
            "year": self.time_vars["Year"].get(), "month": self.time_vars["Month"].get(), "day": self.time_vars["Day"].get(),
            "hour": self.time_vars["Hour"].get(), "minute": self.time_vars["Minute"].get(), "second": self.time_vars["Second"].get()
        }
        profiles = {}
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f: profiles = json.load(f)
        profiles[name] = data
        with open(self.profile_file, 'w') as f: json.dump(profiles, f)
        self.load_profile_list()
        messagebox.showinfo("Success", f"Profile '{name}' saved.")

    def load_profile_list(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                self.all_profiles = sorted(list(json.load(f).keys()))
                self.profile_cb['values'] = self.all_profiles

    def load_profile(self):
        name = self.profile_cb.get()
        if not name: return
        with open(self.profile_file, 'r') as f:
            profiles = json.load(f)
            if name not in profiles: return
            d = profiles[name]
            self.ent_name.delete(0, tk.END); self.ent_name.insert(0, d['name'])
            self.ent_loc.delete(0, tk.END); self.ent_loc.insert(0, d['city'])
            self.lat.set(d['lat']); self.lon.set(d['lon']); self.tz.set(d['tz'])
            self._updating = True
            for k in ["Year", "Month", "Day", "Hour", "Minute", "Second"]: 
                val = d.get(k.lower(), "0")
                self.time_vars[k].set(str(val))
            self.cal.set_date(datetime(int(d['year']), int(d['month']), int(d['day'])))
            self._updating = False
            self.update_chart()

    def format_time(self, hrs_float):
        h = int(hrs_float) % 24
        m = int(round((hrs_float - int(hrs_float)) * 60))
        if m == 60: h = (h + 1) % 24; m = 0
        return f"{h:02d}:{m:02d}"

    def get_panchang_data(self, sun_lon, moon_lon, moon_speed, jd, curr_dt):
        tithi_idx = int((moon_lon - sun_lon) % 360 / 12)
        yoga_idx = int((moon_lon + sun_lon) % 360 / 13.333333)
        karana_idx = int((moon_lon - sun_lon) % 360 / 6)
        k_name = "Kintughna" if karana_idx == 0 else "Shakuni" if karana_idx == 57 else "Chatushpada" if karana_idx == 58 else "Naga" if karana_idx == 59 else ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"][(karana_idx - 1) % 7]

        sun_equ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
        decl = sun_equ[1]
        rad = math.pi / 180.0
        lat_rad = self.lat.get() * rad
        decl_rad = decl * rad
        alt_rad = -0.833 * rad 
        try:
            cos_h = (math.sin(alt_rad) - math.sin(lat_rad) * math.sin(decl_rad)) / (math.cos(lat_rad) * math.cos(decl_rad))
            cos_h = max(-1.0, min(1.0, cos_h))
            h_hours = math.acos(cos_h) / rad / 15.0
        except: h_hours = 6.0
            
        day_dur = 2.0 * h_hours
        night_dur = 24.0 - day_dur
        lon_diff = self.lon.get() - (self.tz.get() * 15.0)
        B = 360.0/365.24 * (curr_dt.timetuple().tm_yday - 81) * rad
        eot_hours = (9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)) / 60.0
        local_noon = 12.0 - (lon_diff / 15.0) - eot_hours
        sunrise_hrs = local_noon - h_hours
        sunset_hrs = local_noon + h_hours

        def format_pan_time(t):
            if t < 0: t += 24.0
            elif t >= 24.0: t -= 24.0
            return self.format_time(t)

        wd = curr_dt.weekday()
        day_part = day_dur / 8.0
        rk_parts = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        yk_parts = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
        gk_parts = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
        
        def get_kala(part_dict):
            p = part_dict[wd]
            s = sunrise_hrs + (p - 1) * day_part
            return f"{format_pan_time(s)} - {format_pan_time(s + day_part)}"

        muh_dur_day = day_dur / 15.0
        muh_dur_night = night_dur / 15.0
        abhijit_start = sunrise_hrs + 7 * muh_dur_day
        abhijit = f"{format_pan_time(abhijit_start)} - {format_pan_time(abhijit_start + muh_dur_day)}"
        
        dm_parts = {6: [(14, 'D')], 0: [(9, 'D'), (12, 'D')], 1: [(4, 'D'), (11, 'N')], 2: [(8, 'D')], 3: [(10, 'D'), (13, 'D')], 4: [(4, 'D'), (9, 'D')], 5: [(2, 'D')]}
        dms = []
        for p, dn in dm_parts[wd]:
            ds = (sunrise_hrs + (p - 1) * muh_dur_day) if dn == 'D' else (sunset_hrs + (p - 1) * muh_dur_night)
            dur = muh_dur_day if dn == 'D' else muh_dur_night
            dms.append(f"{format_pan_time(ds)}-{format_pan_time(ds+dur)}")

        nak_dur_hrs = 13.333333 / moon_speed * 24.0
        v_start_ghati = self.varjyam_starts[int(moon_lon / 13.333333)]
        entry_time = (curr_dt.hour + curr_dt.minute/60.0 + curr_dt.second/3600.0) - ((moon_lon % 13.333333) / moon_speed * 24.0)
        v_time = entry_time + (v_start_ghati / 60.0) * nak_dur_hrs
        v_dur = (4.0 / 60.0) * nak_dur_hrs
        a_time = v_time + (24.0/60.0 * nak_dur_hrs)

        return [
            ("Sunrise", self.format_time(sunrise_hrs), "Sunset", self.format_time(sunset_hrs)),
            ("Tithi", self.tithis[tithi_idx], "Rahu Kala", get_kala(rk_parts)),
            ("Yoga", self.yogas[yoga_idx], "Yamaganda Kala", get_kala(yk_parts)),
            ("Karana", k_name, "Gulika Kala", get_kala(gk_parts)),
            ("Day Duration", f"{int(day_dur)}h {int((day_dur%1)*60)}m", "Abhijit Muhurta", abhijit),
            ("Night Duration", f"{int(night_dur)}h {int((night_dur%1)*60)}m", "Dur Muhurta", ", ".join(dms)),
            ("Vishagatika (Varjyam)", f"{format_pan_time(v_time)} - {format_pan_time(v_time+v_dur)}", "Amrita Kala", f"{format_pan_time(a_time)} - {format_pan_time(a_time+v_dur)}")
        ]

    def validate_and_sync(self, label):
        if self._updating: return
        try:
            val = int(self.time_vars[label].get())
            if label == "Month": self.time_vars[label].set(str(max(1, min(12, val))))
            elif label == "Hour": self.time_vars[label].set(str(max(0, min(23, val))))
            elif label == "Minute" or label == "Second": self.time_vars[label].set(str(max(0, min(59, val))))
            elif label == "Year": self.time_vars[label].set(str(max(1, val)))
            self.sync_vars_to_cal(label)
        except: pass

    def step_time(self, unit, value):
        try:
            y, m, d = int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get())
            hr, mn, sc = int(self.time_vars["Hour"].get()), int(self.time_vars["Minute"].get()), int(self.time_vars["Second"].get())
            curr_dt = datetime(y, m, d, hr, mn, sc)
            if unit == "Second": new_dt = curr_dt + timedelta(seconds=value)
            elif unit == "Minute": new_dt = curr_dt + timedelta(minutes=value)
            elif unit == "Hour": new_dt = curr_dt + timedelta(hours=value)
            elif unit == "Day": new_dt = curr_dt + timedelta(days=value)
            elif unit == "Month":
                nm = m + value; ny = y + (nm - 1) // 12; nm = (nm - 1) % 12 + 1
                new_dt = datetime(ny, nm, min(d, calendar.monthrange(ny, nm)[1]), hr, mn, sc)
            elif unit == "Year":
                ny = y + value
                new_dt = datetime(ny, m, min(d, calendar.monthrange(ny, m)[1]), hr, mn, sc)
            self._updating = True
            for k, val in zip(["Year", "Month", "Day", "Hour", "Minute", "Second"], [new_dt.year, new_dt.month, new_dt.day, new_dt.hour, new_dt.minute, new_dt.second]): 
                self.time_vars[k].set(str(val))
            self.cal.set_date(new_dt.date()); self._updating = False; self.update_chart()
        except: pass

    def format_dms(self, deg_float):
        d = int(deg_float % 30); m = int((deg_float * 60) % 60); s = int((deg_float * 3600) % 60)
        return f"{d:02d}°{m:02d}'{s:02d}\""

    def get_planet_status(self, name, lon, speed, sun_lon):
        if name == "ASC": return ""
        status = []
        is_retro = (name in ["Rah", "Ket"]) or (name not in ["Sun", "Moo"] and speed < 0)
        if is_retro: status.append("↓")
        if name not in ["Sun", "Rah", "Ket", "Ura", "Nep", "Plu"]:
            diff = abs(lon - sun_lon); diff = 360 - diff if diff > 180 else diff
            limit = self.combust_limits.get(name, 15.0)
            if is_retro: limit = 12.0 if name == "Mer" else 8.0 if name == "Ven" else limit
            if diff <= limit: status.append("*")
        return "".join(status)

    def get_dignity_color(self, name, lon):
        if name not in self.dignities: return "black"
        sign_idx = int(lon/30); exalt_sign, _ = self.dignities[name]
        if sign_idx == exalt_sign: return "green"
        if sign_idx == (exalt_sign + 6) % 12: return "red"
        return "black"

    def search_location(self):
        try:
            loc = self.geolocator.geocode(self.ent_loc.get())
            if loc: 
                self.lat.set(round(loc.latitude, 4)); self.lon.set(round(loc.longitude, 4))
                tz_name = self.tz_finder.timezone_at(lng=loc.longitude, lat=loc.latitude)
                if tz_name:
                    local_tz = pytz.timezone(tz_name)
                    b_dt = datetime(int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get()), int(self.time_vars["Hour"].get()), int(self.time_vars["Minute"].get()))
                    self.tz.set(round(local_tz.utcoffset(b_dt).total_seconds() / 3600.0, 2))
                self.update_chart()
        except Exception as e: messagebox.showerror("Error", str(e))

    def get_divisional_sign(self, lon, d_chart_val):
        sign, rem = int(lon / 30), lon % 30
        if d_chart_val == 2: return (4 if int(rem/15)==0 else 3) if sign%2==0 else (3 if int(rem/15)==0 else 4)
        elif d_chart_val == 3: return (sign + int(rem/10)*4) % 12
        elif d_chart_val == 4: return (sign + int(rem/7.5)*3) % 12
        elif d_chart_val == 7: return (sign if sign%2==0 else (sign+6)%12 + int(rem/(30/7))) % 12
        elif d_chart_val == 9: return int((lon*9)/30) % 12
        elif d_chart_val == 10: return (sign if sign%2==0 else (sign+8)%12 + int(rem/3)) % 12
        elif d_chart_val == 12: return (sign + int(rem/2.5)) % 12
        elif d_chart_val == 16: return ((sign%3)*4 + int(rem/(30/16))) % 12
        elif d_chart_val == 20: return ({0:0, 1:8, 2:4}[sign%3] + int(rem/1.5)) % 12
        elif d_chart_val == 24: return ((4 if sign%2==0 else 3) + int(rem/1.25)) % 12
        elif d_chart_val == 27: return ((sign%4)*3 + int(rem/(30/27))) % 12
        elif d_chart_val == 30:
            if sign%2==0: return 0 if rem<5 else 10 if rem<10 else 8 if rem<18 else 2 if rem<25 else 6
            else: return 1 if rem<5 else 5 if rem<12 else 11 if rem<20 else 9 if rem<25 else 7
        elif d_chart_val == 40: return ((0 if sign%2==0 else 6) + int(rem/0.75)) % 12
        elif d_chart_val == 45: return ((sign%3)*4 + int(rem/(30/45))) % 12
        elif d_chart_val == 60: return (sign + int(rem*2)) % 12
        return sign

    def update_chart(self):
        try:
            y, m, d, hr, mn, sc = [int(self.time_vars[k].get()) for k in ["Year", "Month", "Day", "Hour", "Minute", "Second"]]
            curr_dt = datetime(y, m, d, hr, mn, sc)
            utc_dt = curr_dt - timedelta(hours=self.tz.get())
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0); flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            for tree in [self.tree, self.panchang_tree, self.dasha_tree, self.antardasha_tree, self.pratyantar_tree]:
                for row in tree.get_children(): tree.delete(row)
            sun_lon = swe.calc_ut(jd, 0, flags)[0][0]
            m_res = swe.calc_ut(jd, swe.MOON, flags)[0]; moon_long, moon_speed = m_res[0], m_res[3]
            ascmc = swe.houses_ex(jd, self.lat.get(), self.lon.get(), b'A', flags)[1]
            p_d1, p_div, t_d1, t_div = [[] for _ in range(12)], [[] for _ in range(12)], [[] for _ in range(12)], [[] for _ in range(12)]
            d_val = self.d_charts[self.selected_d_label.get()]
            for row_data in self.get_panchang_data(sun_lon, moon_long, moon_speed, jd, curr_dt): self.panchang_tree.insert("", "end", values=row_data)
            objs = [("ASC", -1), ("Sun", 0), ("Moo", 1), ("Mar", 4), ("Mer", 2), ("Jup", 5), ("Ven", 3), ("Sat", 6), ("Rah", 11)]
            if self.show_outer.get(): objs += [("Ura", swe.URANUS), ("Nep", swe.NEPTUNE), ("Plu", swe.PLUTO)]
            for name, p_id in objs:
                res = [ascmc[0], 0, 0, 0] if name == "ASC" else swe.calc_ut(jd, p_id, flags)[0]
                lon, speed = res[0], res[3]; idx_d1, idx_div = int(lon/30), self.get_divisional_sign(lon, d_val)
                st = self.get_planet_status(name, lon, speed, sun_lon); col = self.get_dignity_color(name, lon)
                p_d1[idx_d1].append((f"{name}{st}", self.format_dms(lon), col))
                p_div[idx_div].append((f"{name}{st}", self.format_dms(lon) if name == "ASC" else "", col))
                n_idx = int(lon / (360/27))
                self.tree.insert("", "end", values=(f"{name}{st}", self.format_dms(lon), self.signs[idx_d1], self.nakshatras[n_idx], int(((lon/(360/27))-n_idx)*4)+1, self.lord_order[n_idx%9], st))
                if name == "Rah":
                    k_lon = (lon + 180)%360; ks = self.get_planet_status("Ket", k_lon, speed, sun_lon)
                    p_d1[int(k_lon/30)].append((f"Ket{ks}", self.format_dms(k_lon), "black"))
                    p_div[self.get_divisional_sign(k_lon, d_val)].append((f"Ket{ks}", "", "black"))
                    kn_idx = int(k_lon / (360/27))
                    self.tree.insert("", "end", values=(f"Ket{ks}", self.format_dms(k_lon), self.signs[int(k_lon/30)], self.nakshatras[kn_idx], int(((k_lon/(360/27))-kn_idx)*4)+1, self.lord_order[kn_idx%9], ks))
            
            if self.show_transits.get():
                jd_n = swe.julday(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day, datetime.utcnow().hour + datetime.utcnow().minute/60.0)
                for n, pid in objs:
                    if n == "ASC": continue
                    r = swe.calc_ut(jd_n, pid, flags)[0][0]
                    t_d1[int(r/30)].append((f"T-{n}", "", "darkorange"))
                    t_div[self.get_divisional_sign(r, d_val)].append((f"T-{n}", "", "darkorange"))
                    if n == "Rah":
                        kr = (r + 180)%360
                        t_d1[int(kr/30)].append(("T-Ket", "", "darkorange"))
                        t_div[self.get_divisional_sign(kr, d_val)].append(("T-Ket", "", "darkorange"))

            self.calculate_mahadasha(moon_long)
            self.draw_chart(self.canvas_d1, p_d1, t_d1, int(ascmc[0]/30), "RASHI (D1)", show_dms=True)
            self.draw_chart(self.canvas_div, p_div, t_div, self.get_divisional_sign(ascmc[0], d_val), self.selected_d_label.get(), show_dms=False)
        except Exception as e: print(f"Update Error: {e}")

    def get_sign_center(self, is_n, s_idx, a_idx):
        if not is_n:
            c, r = {11:(0,0), 0:(1,0), 1:(2,0), 2:(3,0), 10:(0,1), 3:(3,1), 9:(0,2), 4:(3,2), 8:(0,3), 7:(1,3), 6:(2,3), 5:(3,3)}[s_idx]
            return (c*125 + 62.5, r*125 + 62.5)
        h_idx = (s_idx - a_idx) % 12
        return [(250,125), (125,62.5), (62.5,125), (125,250), (62.5,375), (125,437.5), (250,375), (375,437.5), (437.5,375), (375,250), (437.5,125), (375,62.5)][h_idx]

    def draw_chart(self, can, placements, transits, asc_idx, title, show_dms=False):
        can.delete("all"); is_n = self.north_style.get()
        if not is_n:
            grid = {11:(0,0), 0:(1,0), 1:(2,0), 2:(3,0), 10:(0,1), 3:(3,1), 9:(0,2), 4:(3,2), 8:(0,3), 7:(1,3), 6:(2,3), 5:(3,3)}
            for i in range(12):
                c, r = grid[i]; can.create_rectangle(c*125, r*125, (c+1)*125, (r+1)*125, fill="#f1f8e9" if i == asc_idx else "white", outline="#cccccc")
        else:
            can.create_rectangle(0, 0, 500, 500, fill="white", outline="black")
            can.create_line(0, 0, 500, 500); can.create_line(500, 0, 0, 500); can.create_line(250, 0, 500, 250); can.create_line(500, 250, 250, 500); can.create_line(250, 500, 0, 250); can.create_line(0, 250, 250, 0)
        can.create_text(250, 250, text=title, font=("Arial", 12, "bold"), fill="darkblue")
        if self.show_drishti.get():
            am = {"Mar":[3,6,7], "Jup":[4,6,8], "Sat":[2,6,9], "Rah":[4,6,8], "Ket":[4,6,8], "Sun":[6], "Moo":[6], "Ven":[6], "Mer":[6]}
            dc = {"Mar":"red", "Jup":"#DAA520", "Sat":"blue", "Rah":"brown", "Ket":"brown", "Sun":"orange", "Moo":"gray", "Ven":"magenta", "Mer":"green"}
            for si in range(12):
                for n, _, _ in placements[si]:
                    bn = n[:3]
                    if bn in am:
                        for off in am[bn]:
                            ts = (si+off)%12; x1, y1 = self.get_sign_center(is_n, si, asc_idx); x2, y2 = self.get_sign_center(is_n, ts, asc_idx)
                            can.create_line(x1, y1, x2, y2, fill=dc.get(bn, "#eee"), dash=(2, 2))
        for si in range(12):
            cx, cy = self.get_sign_center(is_n, si, asc_idx)
            if is_n: can.create_text(cx, cy-30, text=str(si+1), font=("Arial", 8), fill="gray")
            items = placements[si] + transits[si]
            for j, (n, d, col) in enumerate(items):
                y_off = (cy - 45 + (j*14)) if is_n else ({11:0,0:0,1:0,2:0,10:1,3:1,9:2,4:2,8:3,7:3,6:3,5:3}[si]*125 + 15 + (j*(22 if show_dms else 16)))
                can.create_text(cx, y_off, text=n, font=("Arial", 8, "bold"), fill=col)
                if d and show_dms: can.create_text(cx, y_off + 10, text=d, font=("Arial", 7), fill="#555555")

    def setup_dasha_ui(self, parent):
        for name, tree_attr in [("Mahadasha", "dasha_tree"), ("Antardasha", "antardasha_tree"), ("Pratyantar", "pratyantar_tree")]:
            frame = tk.LabelFrame(parent, text=f" {name} "); frame.pack(fill="x", padx=20, pady=5)
            cols = ("Planet", "Start Date", "End Date", "Age (Y-M-D)")
            tree = self._create_scrollable_tree(frame, cols, 5, [150]*len(cols))
            setattr(self, tree_attr, tree)
        self.dasha_tree.bind("<<TreeviewSelect>>", self.on_mahadasha_select)
        self.antardasha_tree.bind("<<TreeviewSelect>>", self.on_antardasha_select)

    def get_precise_age(self, event_date):
        try:
            birth = datetime(int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get()))
            if event_date <= birth: return "0y 0m 0d"
            
            years = event_date.year - birth.year
            months = event_date.month - birth.month
            days = event_date.day - birth.day

            if days < 0:
                months -= 1
                prev_month = event_date.month - 1 if event_date.month > 1 else 12
                prev_year = event_date.year if event_date.month > 1 else event_date.year - 1
                days += calendar.monthrange(prev_year, prev_month)[1]
            if months < 0:
                years -= 1
                months += 12
            
            return f"{years}y {months}m {days}d"
        except: return "0y 0m 0d"

    def calculate_mahadasha(self, moon_long):
        nak_w = 360/27; nak_idx = int(moon_long / nak_w)
        rem_frac = 1 - (moon_long % nak_w) / nak_w
        lord = self.lord_order[nak_idx % 9]
        total_yrs = self.dasha_years[lord]
        birth = datetime(int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get()), int(self.time_vars["Hour"].get()), int(self.time_vars["Minute"].get()), int(self.time_vars["Second"].get()))
        
        used_days = total_yrs * (1 - rem_frac) * 365.25
        curr_start = birth - timedelta(days=used_days)

        for i in range(9):
            l = self.lord_order[(nak_idx + i) % 9]
            end_date = curr_start + timedelta(days=self.dasha_years[l] * 365.25)
            self.dasha_tree.insert("", "end", values=(l, curr_start.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), self.get_precise_age(curr_start)))
            curr_start = end_date

    def on_mahadasha_select(self, e):
        sel = self.dasha_tree.selection()
        if not sel: return
        lord, start_str, _, _ = self.dasha_tree.item(sel[0], "values")
        curr_a = datetime.strptime(start_str, '%Y-%m-%d')
        for t in [self.antardasha_tree, self.pratyantar_tree]:
            for row in t.get_children(): t.delete(row)
        for i in range(9):
            al = self.lord_order[(self.lord_order.index(lord) + i) % 9]
            a_dur = (self.dasha_years[lord] * self.dasha_years[al]) / 120.0
            a_end = curr_a + timedelta(days=a_dur * 365.25)
            self.antardasha_tree.insert("", "end", values=(f"{lord}-{al}", curr_a.strftime('%Y-%m-%d'), a_end.strftime('%Y-%m-%d'), self.get_precise_age(curr_a)))
            curr_a = a_end

    def on_antardasha_select(self, e):
        sel = self.antardasha_tree.selection()
        if not sel: return
        dashas, start_str, _, _ = self.antardasha_tree.item(sel[0], "values")
        ml, al = dashas.split("-"); curr_p = datetime.strptime(start_str, '%Y-%m-%d')
        for row in self.pratyantar_tree.get_children(): self.pratyantar_tree.delete(row)
        for i in range(9):
            pl = self.lord_order[(self.lord_order.index(al) + i) % 9]
            p_dur = (self.dasha_years[ml] * self.dasha_years[al] * self.dasha_years[pl]) / 14400.0
            p_end = curr_p + timedelta(days=p_dur * 365.25)
            self.pratyantar_tree.insert("", "end", values=(f"{al}-{pl}", curr_p.strftime('%Y-%m-%d'), p_end.strftime('%Y-%m-%d'), self.get_precise_age(curr_p)))
            curr_p = p_end

    def sync_cal_to_vars(self, e=None):
        if self._updating: return
        d = self.cal.get_date(); self._updating = True
        for k, v in zip(["Year", "Month", "Day"], [d.year, d.month, d.day]): self.time_vars[k].set(str(v))
        self._updating = False; self.update_chart()

    def sync_vars_to_cal(self, label):
        if self._updating: return
        try:
            if label in ["Year", "Month", "Day"]:
                y, m, d = [int(self.time_vars[k].get()) for k in ["Year", "Month", "Day"]]
                self._updating = True; self.cal.set_date(datetime(y, m, d)); self._updating = False
            self.update_chart()
        except: pass

if __name__ == "__main__":
    root = tk.Tk(); app = ProfessionalVedicAppV1(root); root.mainloop()
