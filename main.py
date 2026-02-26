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
        self.root.title("Vedic Astrology Suite - V1.8 (Strict Range Validation)")
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
        
        # State & Constants
        self.lat, self.lon, self.tz = tk.DoubleVar(value=28.6139), tk.DoubleVar(value=77.2090), tk.DoubleVar(value=5.5)
        self.geolocator = Nominatim(user_agent="vedic_astro_v1_8")
        self._updating = False
        
        self.nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
                          "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                          "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        self.lord_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        self.signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        self.d_charts = {"D2 (Hora)": 2, "D3 (Drekkana)": 3, "D9 (Navamsha)": 9, "D10 (Dashamsha)": 10, "D60 (Shastiamsha)": 60}
        self.selected_d_label = tk.StringVar(value="D9 (Navamsha)")

        # --- UI Construction ---
        self.setup_ui()
        self.update_chart()

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
            tk.Button(sub, text="<", width=2, command=lambda x=l: self.step_time(x, -1)).pack(side=tk.LEFT)
            v = tk.StringVar(value=str(d)); v.trace_add("write", lambda *a, x=l: self.validate_and_sync(x))
            tk.Entry(sub, textvariable=v, width=5, justify='center').pack(side=tk.LEFT, padx=2)
            self.time_vars[l] = v
            tk.Button(sub, text=">", width=2, command=lambda x=l: self.step_time(x, 1)).pack(side=tk.LEFT)
        ttk.Combobox(time_frame, textvariable=self.selected_d_label, values=list(self.d_charts.keys()), state="readonly").grid(row=0, column=7, padx=20)

        chart_container = tk.Frame(parent); chart_container.pack(pady=5)
        self.canvas_d1 = tk.Canvas(chart_container, width=380, height=380, bg="white", highlightthickness=1); self.canvas_d1.pack(side=tk.LEFT, padx=10)
        self.canvas_div = tk.Canvas(chart_container, width=380, height=380, bg="white", highlightthickness=1); self.canvas_div.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(parent); table_frame.pack(fill="x", padx=20, pady=5)
        self.tree = ttk.Treeview(table_frame, columns=("Planet", "DMS", "Rashi", "Nakshatra", "Pada", "Nak Lord"), show="headings", height=10)
        for c in self.tree["columns"]: self.tree.heading(c, text=c); self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="x")

        self.setup_dasha_ui(parent)

    def setup_dasha_ui(self, parent):
        m_frame = tk.LabelFrame(parent, text=" Mahadasha (Click to see Antardasha) "); m_frame.pack(fill="x", padx=20, pady=5)
        self.dasha_tree = ttk.Treeview(m_frame, columns=("Planet", "Start Date", "End Date", "Age"), show="headings", height=5)
        for c in self.dasha_tree["columns"]: self.dasha_tree.heading(c, text=c); self.dasha_tree.column(c, width=150, anchor="center")
        self.dasha_tree.pack(fill="x")
        self.dasha_tree.bind("<<TreeviewSelect>>", self.on_mahadasha_select)

        a_frame = tk.LabelFrame(parent, text=" Antardasha (Click to see Pratyantar) "); a_frame.pack(fill="x", padx=20, pady=5)
        self.antardasha_tree = ttk.Treeview(a_frame, columns=("Planet", "Start Date", "End Date"), show="headings", height=5)
        for c in self.antardasha_tree["columns"]: self.antardasha_tree.heading(c, text=c); self.antardasha_tree.column(c, width=150, anchor="center")
        self.antardasha_tree.pack(fill="x")
        self.antardasha_tree.bind("<<TreeviewSelect>>", self.on_antardasha_select)

        p_frame = tk.LabelFrame(parent, text=" Pratyantardasha "); p_frame.pack(fill="x", padx=20, pady=5)
        self.pratyantar_tree = ttk.Treeview(p_frame, columns=("Planet", "Start Date", "End Date"), show="headings", height=5)
        for c in self.pratyantar_tree["columns"]: self.pratyantar_tree.heading(c, text=c); self.pratyantar_tree.column(c, width=150, anchor="center")
        self.pratyantar_tree.pack(fill="x")

    def validate_and_sync(self, label):
        if self._updating: return
        try:
            val = int(self.time_vars[label].get())
            # Restrict ranges
            if label == "Month":
                if val < 1: self.time_vars[label].set("1")
                elif val > 12: self.time_vars[label].set("12")
            elif label == "Day":
                y = int(self.time_vars["Year"].get())
                m = int(self.time_vars["Month"].get())
                max_days = calendar.monthrange(y, m)[1]
                if val < 1: self.time_vars[label].set("1")
                elif val > max_days: self.time_vars[label].set(str(max_days))
            elif label == "Hour":
                if val < 0: self.time_vars[label].set("0")
                elif val > 23: self.time_vars[label].set("23")
            elif label == "Minute":
                if val < 0: self.time_vars[label].set("0")
                elif val > 59: self.time_vars[label].set("59")
            
            self.sync_vars_to_cal(label)
        except: pass

    def step_time(self, u, v):
        try:
            curr = int(self.time_vars[u].get())
            new_val = curr + v
            if u == "Hour": new_val %= 24
            elif u == "Minute": new_val %= 60
            elif u == "Month": new_val = 1 if new_val > 12 else (12 if new_val < 1 else new_val)
            elif u == "Day":
                y, m = int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get())
                max_d = calendar.monthrange(y, m)[1]
                new_val = 1 if new_val > max_d else (max_d if new_val < 1 else new_val)
            
            self.time_vars[u].set(str(new_val))
        except: pass

    def format_dms(self, deg_float):
        d = int(deg_float % 30)
        m = int((deg_float * 60) % 60)
        s = int((deg_float * 3600) % 60)
        return f"{d:02d}°{m:02d}'{s:02d}\""

    def update_chart(self):
        try:
            y, m, d, hr, mn = [int(self.time_vars[k].get()) for k in ["Year", "Month", "Day", "Hour", "Minute"]]
            self.birth_dt = datetime(y, m, d, hr, mn)
            utc_dt = self.birth_dt - timedelta(hours=self.tz.get())
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0); flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            
            for tree in [self.tree, self.dasha_tree, self.antardasha_tree, self.pratyantar_tree]:
                for row in tree.get_children(): tree.delete(row)
            
            moon_long = swe.calc_ut(jd, swe.MOON, flags)[0][0]
            ascmc = swe.houses_ex(jd, self.lat.get(), self.lon.get(), b'A', flags)[1]
            p_d1, p_div = [[] for _ in range(12)], [[] for _ in range(12)]
            d_val = self.d_charts[self.selected_d_label.get()]
            
            objs = [("ASC", -1), ("Sun", 0), ("Moo", 1), ("Mar", 4), ("Mer", 2), ("Jup", 5), ("Ven", 3), ("Sat", 6), ("Rah", 11)]
            for name, p_id in objs:
                lon = ascmc[0] if name == "ASC" else swe.calc_ut(jd, p_id, flags)[0][0]
                dms_str = self.format_dms(lon)
                idx_d1, idx_div = int(lon/30), int((lon*d_val)/30)%12
                p_d1[idx_d1].append((name, dms_str)); p_div[idx_div].append((name, ""))
                
                abs_nak = lon / (360/27); nak_idx = int(abs_nak)
                self.tree.insert("", "end", values=(name, dms_str, self.signs[idx_d1], self.nakshatras[nak_idx], int((abs_nak - nak_idx)*4)+1, self.lord_order[nak_idx%9]))
                if name == "Rah":
                    k_lon = (lon + 180)%360
                    p_d1[int(k_lon/30)].append(("Ket", self.format_dms(k_lon)))
                    p_div[int((k_lon*d_val)/30)%12].append(("Ket", ""))

            self.calculate_mahadasha(moon_long)
            self.draw_square(self.canvas_d1, p_d1, int(ascmc[0]/30), "RASHI (D1)")
            self.draw_square(self.canvas_div, p_div, int((ascmc[0]*d_val)/30)%12, self.selected_d_label.get())
        except Exception as e: print(f"Update Error: {e}")

    def calculate_mahadasha(self, moon_long):
        nak_width = 360/27
        nak_index = int(moon_long / nak_width)
        elapsed = (moon_long % nak_width) / nak_width
        start_lord_idx = nak_index % 9
        first_lord = self.lord_order[start_lord_idx]
        rem_yrs = self.dasha_years[first_lord] * (1 - elapsed)
        current_start = self.birth_dt - timedelta(days=(self.dasha_years[first_lord] - rem_yrs) * 365.25)
        for i in range(9):
            lord = self.lord_order[(start_lord_idx + i) % 9]
            duration = self.dasha_years[lord]
            end_date = current_start + timedelta(days=duration * 365.25)
            age = (end_date - self.birth_dt).days // 365
            self.dasha_tree.insert("", "end", values=(lord, current_start.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), max(0, age)))
            current_start = end_date

    def on_mahadasha_select(self, event):
        selected = self.dasha_tree.selection()
        if not selected: return
        lord, start_str, end_str, _ = self.dasha_tree.item(selected[0], "values")
        m_start = datetime.strptime(start_str, '%Y-%m-%d')
        m_total_yrs = self.dasha_years[lord]
        for row in self.antardasha_tree.get_children(): self.antardasha_tree.delete(row)
        for row in self.pratyantar_tree.get_children(): self.pratyantar_tree.delete(row)
        curr_a_start = m_start
        lord_idx = self.lord_order.index(lord)
        for i in range(9):
            a_lord = self.lord_order[(lord_idx + i) % 9]
            a_duration_yrs = (m_total_yrs * self.dasha_years[a_lord]) / 120.0
            a_end = curr_a_start + timedelta(days=a_duration_yrs * 365.25)
            self.antardasha_tree.insert("", "end", values=(f"{lord}-{a_lord}", curr_a_start.strftime('%Y-%m-%d'), a_end.strftime('%Y-%m-%d')))
            curr_a_start = a_end

    def on_antardasha_select(self, event):
        selected = self.antardasha_tree.selection()
        if not selected: return
        dashas, start_str, end_str = self.antardasha_tree.item(selected[0], "values")
        m_lord, a_lord = dashas.split("-")
        a_start = datetime.strptime(start_str, '%Y-%m-%d')
        for row in self.pratyantar_tree.get_children(): self.pratyantar_tree.delete(row)
        curr_p_start = a_start
        a_idx = self.lord_order.index(a_lord)
        for i in range(9):
            p_lord = self.lord_order[(a_idx + i) % 9]
            p_dur_yrs = (self.dasha_years[m_lord] * self.dasha_years[a_lord] * self.dasha_years[p_lord]) / 14400.0
            p_end = curr_p_start + timedelta(days=p_dur_yrs * 365.25)
            self.pratyantar_tree.insert("", "end", values=(f"{a_lord}-{p_lord}", curr_p_start.strftime('%Y-%m-%d'), p_end.strftime('%Y-%m-%d')))
            curr_p_start = p_end

    def sync_cal_to_vars(self, e=None):
        if self._updating: return
        self._updating = True
        d = self.cal.get_date()
        self.time_vars["Year"].set(str(d.year)); self.time_vars["Month"].set(str(d.month)); self.time_vars["Day"].set(str(d.day))
        self._updating = False; self.update_chart()

    def sync_vars_to_cal(self, label):
        if self._updating: return
        try:
            if label in ["Year", "Month", "Day"]:
                y, m, d = int(self.time_vars["Year"].get()), int(self.time_vars["Month"].get()), int(self.time_vars["Day"].get())
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
            fill = "#e8f5e9" if i == asc_idx else "white"
            can.create_rectangle(c*b, r*b, (c+1)*b, (r+1)*b, fill=fill, outline="#dddddd")
            for j, (n, d) in enumerate(placements[i]):
                can.create_text(c*b+b/2, r*b+20+(j*15), text=f"{n}", font=("Arial", 8, "bold"))
                if d: can.create_text(c*b+b/2, r*b+32+(j*15), text=f"{d}", font=("Arial", 6))
        can.create_text(190, 190, text=title, font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk(); app = ProfessionalVedicAppV1(root); root.mainloop()
