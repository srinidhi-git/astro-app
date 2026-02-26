import tkinter as tk
from tkinter import ttk, messagebox
import swisseph as swe
from datetime import datetime, timedelta
import calendar
from geopy.geocoders import Nominatim
from tkcalendar import DateEntry

class ProfessionalVedicAppV1:
    def __init__(self, root):
        self.root = root
        self.root.title("Vedic Astrology Suite - V1.9.3 (Cascading Time & Improved Alignment)")
        self.root.geometry("1000x900")
        
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

        # Mouse Wheel Binding
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # State & Constants
        self.lat, self.lon, self.tz = tk.DoubleVar(value=28.6139), tk.DoubleVar(value=77.2090), tk.DoubleVar(value=5.5)
        self.geolocator = Nominatim(user_agent="vedic_astro_v1_9")
        self._updating = False
        
        self.nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
                          "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                          "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        self.lord_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        self.signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        self.d_charts = {"D2 (Hora)": 2, "D3 (Drekkana)": 3, "D9 (Navamsha)": 9, "D10 (Dashamsha)": 10, "D60 (Shastiamsha)": 60}
        self.selected_d_label = tk.StringVar(value="D9 (Navamsha)")

        self.dignities = {
            "Sun": (0, 10), "Moo": (3, 3), "Mar": (9, 28), "Mer": (5, 15),
            "Jup": (3, 5), "Ven": (11, 27), "Sat": (6, 20)
        }
        
        self.combust_limits = {"Moo": 12, "Mar": 17, "Mer": 14, "Jup": 11, "Ven": 10, "Sat": 15}

        self.setup_ui()
        self.update_chart()

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def setup_ui(self):
        parent = self.scrollable_frame
        loc_frame = tk.LabelFrame(parent, text=" Location Settings "); loc_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(loc_frame, text="City:").pack(side=tk.LEFT, padx=5)
        self.ent_loc = tk.Entry(loc_frame, width=20); self.ent_loc.insert(0, "New Delhi"); self.ent_loc.pack(side=tk.LEFT, padx=5)
        tk.Button(loc_frame, text="Search", command=self.search_location).pack(side=tk.LEFT, padx=5)
        tk.Label(loc_frame, text="Lat:").pack(side=tk.LEFT, padx=(15,0)); tk.Entry(loc_frame, textvariable=self.lat, width=8).pack(side=tk.LEFT)
        tk.Label(loc_frame, text="Lon:").pack(side=tk.LEFT, padx=(10,0)); tk.Entry(loc_frame, textvariable=self.lon, width=8).pack(side=tk.LEFT)

        time_frame = tk.LabelFrame(parent, text=" Birth Date, Time & Chart Selection "); time_frame.pack(fill="x", padx=20, pady=5)
        self.cal = DateEntry(time_frame, width=12, background='darkblue', year=1990, month=5, day=15)
        self.cal.grid(row=0, column=0, padx=20, rowspan=2); self.cal.bind("<<DateEntrySelected>>", self.sync_cal_to_vars)
        self.time_vars = {}
          
        for i, (l, d) in enumerate([("Year", 1990), ("Month", 5), ("Day", 15), ("Hour", 10), ("Minute", 30)]):
            sub = tk.Frame(time_frame); sub.grid(row=0, column=i+1, padx=5)
            tk.Label(sub, text=l, font=("Arial", 7)).pack()
            btn_frame = tk.Frame(sub); btn_frame.pack()
            tk.Button(btn_frame, text="<", width=2, command=lambda x=l: self.step_time(x, -1)).pack(side=tk.LEFT)
            v = tk.StringVar(value=str(d)); v.trace_add("write", lambda *a, x=l: self.validate_and_sync(x))
            tk.Entry(btn_frame, textvariable=v, width=5, justify='center').pack(side=tk.LEFT, padx=2)
            self.time_vars[l] = v
            tk.Button(btn_frame, text=">", width=2, command=lambda x=l: self.step_time(x, 1)).pack(side=tk.LEFT)
        ttk.Combobox(time_frame, textvariable=self.selected_d_label, values=list(self.d_charts.keys()), state="readonly").grid(row=0, column=7, padx=20)

        chart_container = tk.Frame(parent); chart_container.pack(pady=5)
        self.canvas_d1 = tk.Canvas(chart_container, width=380, height=380, bg="white", highlightthickness=1); self.canvas_d1.pack(side=tk.LEFT, padx=10)
        self.canvas_div = tk.Canvas(chart_container, width=380, height=380, bg="white", highlightthickness=1); self.canvas_div.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(parent); table_frame.pack(fill="x", padx=20, pady=5)
        self.tree = ttk.Treeview(table_frame, columns=("Planet", "DMS", "Rashi", "Nakshatra", "Pada", "Nak Lord", "Status"), show="headings", height=10)
        for c in self.tree["columns"]: self.tree.heading(c, text=c); self.tree.column(c, width=110, anchor="center")
        self.tree.pack(fill="x")

        self.setup_dasha_ui(parent)

    def validate_and_sync(self, label):
        if self._updating: return
        try:
            val = int(self.time_vars[label].get())
            # Basic range clamping for manual entry
            if label == "Month": self.time_vars[label].set(str(max(1, min(12, val))))
            elif label == "Hour": self.time_vars[label].set(str(max(0, min(23, val))))
            elif label == "Minute": self.time_vars[label].set(str(max(0, min(59, val))))
            elif label == "Year": self.time_vars[label].set(str(max(1, val)))
            self.sync_vars_to_cal(label)
        except: pass

    def step_time(self, unit, value):
        try:
            y, m, d = int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get())
            hr, mn = int(self.time_vars["Hour"].get()), int(self.time_vars["Minute"].get())
            
            curr_dt = datetime(y, m, d, hr, mn)
            
            if unit == "Minute": new_dt = curr_dt + timedelta(minutes=value)
            elif unit == "Hour": new_dt = curr_dt + timedelta(hours=value)
            elif unit == "Day": new_dt = curr_dt + timedelta(days=value)
            elif unit == "Month":
                # Handle month logic manually to avoid timedelta issues with varying days
                nm = m + value
                ny = y + (nm - 1) // 12
                nm = (nm - 1) % 12 + 1
                max_d = calendar.monthrange(ny, nm)[1]
                new_dt = datetime(ny, nm, min(d, max_d), hr, mn)
            elif unit == "Year":
                ny = y + value
                max_d = calendar.monthrange(ny, m)[1]
                new_dt = datetime(ny, m, min(d, max_d), hr, mn)
            
            self._updating = True
            self.time_vars["Year"].set(str(new_dt.year))
            self.time_vars["Month"].set(str(new_dt.month))
            self.time_vars["Day"].set(str(new_dt.day))
            self.time_vars["Hour"].set(str(new_dt.hour))
            self.time_vars["Minute"].set(str(new_dt.minute))
            self.cal.set_date(new_dt.date())
            self._updating = False
            self.update_chart()
        except Exception as e:
            self._updating = False
            print(f"Step Error: {e}")

    def format_dms(self, deg_float):
        d = int(deg_float % 30)
        m = int((deg_float * 60) % 60)
        s = int((deg_float * 3600) % 60)
        return f"{d:02d}°{m:02d}'{s:02d}\""

    def get_planet_status(self, name, lon, speed, sun_lon):
        if name in ["ASC", "Rah", "Ket", "Sun"]: return ""
        status = []
        if speed < 0: status.append("↓")
        diff = abs(lon - sun_lon); diff = 360 - diff if diff > 180 else diff
        if diff < self.combust_limits.get(name, 8.0): status.append("*")
        return "".join(status)

    def get_dignity_color(self, name, lon):
        if name not in self.dignities: return "black"
        sign_idx = int(lon/30)
        exalt_sign, _ = self.dignities[name]
        if sign_idx == exalt_sign: return "green"
        if sign_idx == (exalt_sign + 6) % 12: return "red"
        return "black"

    def update_chart(self):
        try:
            y, m, d, hr, mn = [int(self.time_vars[k].get()) for k in ["Year", "Month", "Day", "Hour", "Minute"]]
            self.birth_dt = datetime(y, m, d, hr, mn)
            utc_dt = self.birth_dt - timedelta(hours=self.tz.get())
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0); flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            
            for tree in [self.tree, self.dasha_tree, self.antardasha_tree, self.pratyantar_tree]:
                for row in tree.get_children(): tree.delete(row)
            
            sun_lon = swe.calc_ut(jd, 0, flags)[0][0]
            moon_long = swe.calc_ut(jd, swe.MOON, flags)[0][0]
            ascmc = swe.houses_ex(jd, self.lat.get(), self.lon.get(), b'A', flags)[1]
            p_d1, p_div = [[] for _ in range(12)], [[] for _ in range(12)]
            d_val = self.d_charts[self.selected_d_label.get()]
            
            objs = [("ASC", -1), ("Sun", 0), ("Moo", 1), ("Mar", 4), ("Mer", 2), ("Jup", 5), ("Ven", 3), ("Sat", 6), ("Rah", 11)]
            for name, p_id in objs:
                res = [ascmc[0], 0] if name == "ASC" else swe.calc_ut(jd, p_id, flags)[0]
                lon, speed = res[0], res[1]
                idx_d1, idx_div = int(lon/30), int((lon*d_val)/30)%12
                status = self.get_planet_status(name, lon, speed, sun_lon)
                color = self.get_dignity_color(name, lon)
                
                p_d1[idx_d1].append((f"{name}{status}", self.format_dms(lon), color))
                p_div[idx_div].append((f"{name}{status}", "", color))
                
                abs_nak = lon / (360/27); n_idx = int(abs_nak)
                self.tree.insert("", "end", values=(f"{name}{status}", self.format_dms(lon), self.signs[idx_d1], self.nakshatras[n_idx], int((abs_nak - n_idx)*4)+1, self.lord_order[n_idx%9], status))
                
                if name == "Rah":
                    k_lon = (lon + 180)%360
                    p_d1[int(k_lon/30)].append(("Ket", self.format_dms(k_lon), "black"))
                    p_div[int((k_lon*d_val)/30)%12].append(("Ket", "", "black"))

            self.calculate_mahadasha(moon_long)
            self.draw_square(self.canvas_d1, p_d1, int(ascmc[0]/30), "RASHI (D1)")
            self.draw_square(self.canvas_div, p_div, int((ascmc[0]*d_val)/30)%12, self.selected_d_label.get())
        except Exception as e: print(f"Update Error: {e}")

    def setup_dasha_ui(self, parent):
        for name, tree_attr in [("Mahadasha", "dasha_tree"), ("Antardasha", "antardasha_tree"), ("Pratyantar", "pratyantar_tree")]:
            frame = tk.LabelFrame(parent, text=f" {name} "); frame.pack(fill="x", padx=20, pady=5)
            cols = ("Planet", "Start Date", "End Date", "Age") if name == "Mahadasha" else ("Planet", "Start Date", "End Date")
            tree = ttk.Treeview(frame, columns=cols, show="headings", height=5)
            for c in cols: tree.heading(c, text=c); tree.column(c, width=150, anchor="center")
            tree.pack(fill="x")
            setattr(self, tree_attr, tree)
        self.dasha_tree.bind("<<TreeviewSelect>>", self.on_mahadasha_select)
        self.antardasha_tree.bind("<<TreeviewSelect>>", self.on_antardasha_select)

    def calculate_mahadasha(self, moon_long):
        nak_w = 360/27
        nak_idx = int(moon_long / nak_w)
        rem_yrs = self.dasha_years[self.lord_order[nak_idx % 9]] * (1 - (moon_long % nak_w) / nak_w)
        curr_start = self.birth_dt - timedelta(days=(self.dasha_years[self.lord_order[nak_idx % 9]] - rem_yrs) * 365.25)
        for i in range(9):
            lord = self.lord_order[(nak_idx + i) % 9]
            end_date = curr_start + timedelta(days=self.dasha_years[lord] * 365.25)
            self.dasha_tree.insert("", "end", values=(lord, curr_start.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), max(0, (end_date - self.birth_dt).days // 365)))
            curr_start = end_date

    def on_mahadasha_select(self, e):
        sel = self.dasha_tree.selection()
        if not sel: return
        lord, start_str, _, _ = self.dasha_tree.item(sel[0], "values")
        m_start = datetime.strptime(start_str, '%Y-%m-%d')
        for t in [self.antardasha_tree, self.pratyantar_tree]:
            for row in t.get_children(): t.delete(row)
        curr_a = m_start
        l_idx = self.lord_order.index(lord)
        for i in range(9):
            al = self.lord_order[(l_idx + i) % 9]
            a_end = curr_a + timedelta(days=((self.dasha_years[lord] * self.dasha_years[al]) / 120.0) * 365.25)
            self.antardasha_tree.insert("", "end", values=(f"{lord}-{al}", curr_a.strftime('%Y-%m-%d'), a_end.strftime('%Y-%m-%d')))
            curr_a = a_end

    def on_antardasha_select(self, e):
        sel = self.antardasha_tree.selection()
        if not sel: return
        dashas, start_str, _ = self.antardasha_tree.item(sel[0], "values")
        ml, al = dashas.split("-")
        curr_p = datetime.strptime(start_str, '%Y-%m-%d')
        for row in self.pratyantar_tree.get_children(): self.pratyantar_tree.delete(row)
        a_idx = self.lord_order.index(al)
        for i in range(9):
            pl = self.lord_order[(a_idx + i) % 9]
            p_end = curr_p + timedelta(days=((self.dasha_years[ml] * self.dasha_years[al] * self.dasha_years[pl]) / 14400.0) * 365.25)
            self.pratyantar_tree.insert("", "end", values=(f"{al}-{pl}", curr_p.strftime('%Y-%m-%d'), p_end.strftime('%Y-%m-%d')))
            curr_p = p_end

    def sync_cal_to_vars(self, e=None):
        if self._updating: return
        d = self.cal.get_date()
        self._updating = True
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

    def search_location(self):
        try:
            loc = self.geolocator.geocode(self.ent_loc.get())
            if loc: self.lat.set(round(loc.latitude, 4)); self.lon.set(round(loc.longitude, 4)); self.update_chart()
        except: pass

    def draw_square(self, can, placements, asc_idx, title):
        can.delete("all"); b = 95
        grid = {11:(0,0), 0:(1,0), 1:(2,0), 2:(3,0), 10:(0,1), 3:(3,1), 9:(0,2), 4:(3,2), 8:(0,3), 7:(1,3), 6:(2,3), 5:(3,3)}
        
        for i in range(12):
            c, r = grid[i]
            fill = "#f1f8e9" if i == asc_idx else "white"
            can.create_rectangle(c*b, r*b, (c+1)*b, (r+1)*b, fill=fill, outline="#cccccc")
            # Alignment: Planet text at top, DMS below it, with more padding (j*25)
            for j, (n, d, col) in enumerate(placements[i]):
                y_off = r*b + 18 + (j * 25)
                can.create_text(c*b+b/2, y_off, text=n, font=("Arial", 9, "bold"), fill=col)
                if d:
                    can.create_text(c*b+b/2, y_off + 12, text=d, font=("Arial", 7), fill="#666666")
        
        can.create_text(190, 190, text=title, font=("Arial", 11, "bold"), fill="darkblue")

if __name__ == "__main__":
    root = tk.Tk(); app = ProfessionalVedicAppV1(root); root.mainloop()
