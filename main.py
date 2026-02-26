import tkinter as tk
from tkinter import ttk, messagebox
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from tkcalendar import DateEntry

class ProfessionalVedicAppV1:
    def __init__(self, root):
        self.root = root
        self.root.title("Vedic Astrology Suite - Version 1.2 (Bi-Directional Sync)")
        self.root.geometry("1000x950")
        
        # State Variables
        self.lat = tk.DoubleVar(value=28.6139)
        self.lon = tk.DoubleVar(value=77.2090)
        self.tz = tk.DoubleVar(value=5.5)
        self.geolocator = Nominatim(user_agent="vedic_astro_v1_2")
        self._updating = False  # Flag to prevent infinite recursion during sync

        # --- UI Section 1: Location ---
        loc_frame = tk.LabelFrame(root, text=" Location Settings ", padx=10, pady=10)
        loc_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(loc_frame, text="City:").pack(side=tk.LEFT)
        self.ent_loc = tk.Entry(loc_frame, width=20)
        self.ent_loc.insert(0, "New Delhi")
        self.ent_loc.pack(side=tk.LEFT, padx=5)
        tk.Button(loc_frame, text="Search", command=self.search_location).pack(side=tk.LEFT, padx=5)
        
        tk.Label(loc_frame, text="Lat:").pack(side=tk.LEFT, padx=(15,0))
        tk.Entry(loc_frame, textvariable=self.lat, width=10).pack(side=tk.LEFT)
        tk.Label(loc_frame, text="Lon:").pack(side=tk.LEFT, padx=(10,0))
        tk.Entry(loc_frame, textvariable=self.lon, width=10).pack(side=tk.LEFT)

        # --- UI Section 2: Date & Time Picker ---
        time_frame = tk.LabelFrame(root, text=" Birth Date & Time Selection ", padx=10, pady=10)
        time_frame.pack(fill="x", padx=20, pady=5)

        # 2a. Calendar Picker
        cal_sub = tk.Frame(time_frame)
        cal_sub.grid(row=0, column=0, padx=20, rowspan=2)
        tk.Label(cal_sub, text="Calendar Picker", font=("Arial", 8, "bold")).pack()
        self.cal = DateEntry(cal_sub, width=12, background='darkblue', foreground='white', borderwidth=2, 
                             year=1990, month=5, day=15)
        self.cal.pack(pady=5)
        self.cal.bind("<<DateEntrySelected>>", self.sync_cal_to_vars)

        # 2b. Manual Text & Arrow Inputs
        self.time_vars = {}
        units = [("Year", 1990), ("Month", 5), ("Day", 15), ("Hour", 10), ("Minute", 30)]
        
        for i, (label, default) in enumerate(units):
            sub = tk.Frame(time_frame)
            sub.grid(row=0, column=i+1, padx=10)
            
            tk.Label(sub, text=label, font=("Arial", 8, "bold")).pack()
            btn_frame = tk.Frame(sub)
            btn_frame.pack()
            
            tk.Button(btn_frame, text="<", width=2, command=lambda l=label: self.step_time(l, -1)).pack(side=tk.LEFT)
            v = tk.StringVar(value=str(default))
            # Trace triggers both the Chart update and the Calendar update
            v.trace_add("write", lambda *args, l=label: self.sync_vars_to_cal(l))
            tk.Entry(btn_frame, textvariable=v, width=6, justify='center', font=("Arial", 11)).pack(side=tk.LEFT, padx=2)
            self.time_vars[label] = v
            tk.Button(btn_frame, text=">", width=2, command=lambda l=label: self.step_time(l, 1)).pack(side=tk.LEFT)

        # --- UI Section 3: Visual Chart ---
        self.canvas = tk.Canvas(root, width=540, height=540, bg="white", highlightthickness=1)
        self.canvas.pack(pady=15)
        
        status_bar = tk.Frame(root)
        status_bar.pack(fill="x", side=tk.BOTTOM, pady=5)
        tk.Label(status_bar, text="🟢 Exalted | 🔴 Debilitated | (R) Retrograde | (C) Combust | Blue: ASC", font=("Arial", 9)).pack()

        self.update_chart()

    def sync_cal_to_vars(self, event=None):
        """Action: User picked date on Calendar -> Update Text Boxes"""
        if self._updating: return
        self._updating = True
        date = self.cal.get_date()
        self.time_vars["Year"].set(str(date.year))
        self.time_vars["Month"].set(str(date.month))
        self.time_vars["Day"].set(str(date.day))
        self._updating = False
        self.update_chart()

    def sync_vars_to_cal(self, label):
        """Action: User typed/clicked arrows in Text Boxes -> Update Calendar"""
        if self._updating: return
        try:
            # Only sync if the change is to Date fields
            if label in ["Year", "Month", "Day"]:
                y = int(self.time_vars["Year"].get())
                m = int(self.time_vars["Month"].get())
                d = int(self.time_vars["Day"].get())
                
                self._updating = True
                self.cal.set_date(datetime(y, m, d))
                self._updating = False
            
            self.update_chart()
        except (ValueError, tk.TclError):
            pass # Ignore partial inputs while typing

    def search_location(self):
        try:
            location = self.geolocator.geocode(self.ent_loc.get())
            if location:
                self.lat.set(round(location.latitude, 4))
                self.lon.set(round(location.longitude, 4))
                self.update_chart()
        except: messagebox.showerror("Error", "Geocoding failed.")

    def step_time(self, unit, val):
        try:
            current = int(self.time_vars[unit].get())
            self.time_vars[unit].set(str(current + val))
        except: pass

    def dms(self, decimal_deg):
        d = int(decimal_deg)
        m = int((decimal_deg - d) * 60)
        s = int((decimal_deg - d - m/60) * 3600)
        return f"{d:02d}°{m:02d}'{s:02d}\""

    def get_dignity_color(self, name, sign_idx):
        dignities = {"Sun":(0,6), "Moo":(1,7), "Mar":(9,3), "Mer":(5,11), "Jup":(3,9), "Ven":(11,5), "Sat":(6,0)}
        if name in dignities:
            if sign_idx == dignities[name][0]: return "green"
            if sign_idx == dignities[name][1]: return "red"
        return "black"

    def update_chart(self):
        try:
            y, m, d = int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get())
            hr, mn = int(self.time_vars["Hour"].get()), int(self.time_vars["Minute"].get())
            
            dt = datetime(y, m, d, hr, mn)
            utc_dt = dt - timedelta(hours=self.tz.get())
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

            sun_long = swe.calc_ut(jd, swe.SUN, flags)[0][0]
            ascmc = swe.houses_ex(jd, self.lat.get(), self.lon.get(), b'A', flags)[1]
            asc_long, asc_idx = ascmc[0], int(ascmc[0] / 30)
            
            placements = [[] for _ in range(12)]
            placements[asc_idx].append(("ASC", self.dms(asc_long % 30), "blue", ""))

            planets_map = {"Sun": swe.SUN, "Moo": swe.MOON, "Mar": swe.MARS, "Mer": swe.MERCURY, 
                           "Jup": swe.JUPITER, "Ven": swe.VENUS, "Sat": swe.SATURN, "Rah": swe.MEAN_NODE}
            combust_dist = {"Moo":12, "Mar":17, "Mer":13, "Jup":11, "Ven":9, "Sat":15}

            for name, p_id in planets_map.items():
                res, _ = swe.calc_ut(jd, p_id, flags)
                lon, speed = res[0], res[3]
                idx = int(lon / 30)
                suffix = ""
                if speed < 0 and name not in ["Sun", "Moo", "Rah"]: suffix += "(R)"
                if name in combust_dist:
                    diff = abs(lon - sun_long)
                    if diff > 180: diff = 360 - diff
                    if diff < combust_dist[name]: suffix += "(C)"

                color = self.get_dignity_color(name, idx)
                placements[idx].append((name, self.dms(lon % 30), color, suffix))
                if name == "Rah":
                    placements[(idx + 6) % 12].append(("Ket", self.dms(lon % 30), "black", ""))

            self.draw_chart(placements, asc_idx)
        except: pass

    def draw_chart(self, placements, asc_idx):
        self.canvas.delete("all")
        b = 135
        grid = {11:(0,0), 0:(1,0), 1:(2,0), 2:(3,0), 10:(0,1), 3:(3,1), 
                9:(0,2), 4:(3,2), 8:(0,3), 7:(1,3), 6:(2,3), 5:(3,3)}
        signs = ["Ar", "Ta", "Ge", "Ca", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

        for i in range(12):
            c, r = grid[i]
            fill = "#e8f5e9" if i == asc_idx else "white" 
            self.canvas.create_rectangle(c*b, r*b, (c+1)*b, (r+1)*b, fill=fill, outline="#dddddd")
            self.canvas.create_text(c*b+18, r*b+12, text=signs[i], fill="#aaaaaa", font=("Arial", 7, "bold"))
            for j, (name, dms, col, suf) in enumerate(placements[i]):
                self.canvas.create_text(c*b+b/2, r*b+35+(j*18), text=f"{name} {dms}{suf}", fill=col, font=("Consolas", 8, "bold"))
        self.canvas.create_text(270, 270, text="RASHI CHART V1.2", font=("Arial", 12, "bold"), justify="center")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalVedicAppV1(root)
    root.mainloop()
