from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
import random

class Szoba(ABC): # Absztrakt Szoba osztály
    def __init__(self, szobaszam, ar):
        self.szobaszam = szobaszam
        self.ar = ar

    @abstractmethod
    def info(self):
        pass

class EgyagyasSzoba(Szoba): # EgyagyasSzoba osztály
    def __init__(self, szobaszam, ar):
        super().__init__(szobaszam, ar)

    def info(self):
        return f"Egyágyas szoba, szobaszám: {self.szobaszam}, ár: {self.ar} Ft/éj"

class KetagyasSzoba(Szoba): # KetagyasSzoba osztály
    def __init__(self, szobaszam, ar):
        super().__init__(szobaszam, ar)

    def info(self):
        return f"Kétágyas szoba, szobaszám: {self.szobaszam}, ár: {self.ar} Ft/éj"

class Szalloda:  # Szalloda osztály
    def __init__(self, nev):
        self.nev = nev
        self.szobak = []
        self.foglalasok = []

    def szoba_hozzaadas(self, szoba):
        self.szobak.append(szoba)

    def foglalas(self, szobaszam, datum, show_messagebox=True):
        if any(f.szobaszam == szobaszam and f.datum == datum for f in self.foglalasok):
            if show_messagebox:
                messagebox.showerror("Foglalási hiba", "Ez a szoba ezen a napon már foglalt.")
            return False
        for szoba in self.szobak:
            if szoba.szobaszam == szobaszam:
                self.foglalasok.append(Foglalas(szobaszam, datum))
                if show_messagebox:
                    messagebox.showinfo("Foglalás", f"Foglalás sikeres: {szoba.info()}, dátum: {datum}")
                return True
        return False # Ha valamilyen okból kifolyólag mégsem sikerült a foglalás, hamissal térünk vissza

    def foglalas_lemondas(self, kijelolt_elemek):
        sikeres_torlesek = []
        sikertelen_torlesek = []

        for szobaszam, datum in kijelolt_elemek:
            torles_sikeres = False
            for foglalas in list(self.foglalasok):  # Másolatot készítünk a listáról iterálás előtt
                if foglalas.szobaszam == szobaszam and foglalas.datum == datum:
                    self.foglalasok.remove(foglalas)
                    torles_sikeres = True
                    break  # Kilépünk a belső ciklusból, mivel megtaláltuk a törlendő foglalást
            if torles_sikeres:
                sikeres_torlesek.append((szobaszam, datum))
            else:
                sikertelen_torlesek.append((szobaszam, datum))

        # Összeállítjuk az üzenetet a törlések eredményéről
        uzenet = ""
        if sikeres_torlesek:
            uzenet += "Sikeres törlések:\n" + "\n".join([f"Szobaszám: {sz}, Dátum: {dt}" for sz, dt in sikeres_torlesek]) + "\n\n"
        if sikertelen_torlesek:
            uzenet += "Sikertelen törlések:\n" + "\n".join([f"Szobaszám: {sz}, Dátum: {dt}" for sz, dt in sikertelen_torlesek])

        # Ha volt sikeres törlés, megjelenítjük az összefoglaló üzenetet
        if uzenet:
            messagebox.showinfo("Törlés eredménye", uzenet)

    def foglalas_listazasa(self):
        if not self.foglalasok:
            messagebox.showinfo("Foglalások", "Jelenleg nincsenek foglalások.")
            return        

class Foglalas: # Foglalas osztály
    def __init__(self, szobaszam, datum):
        self.szobaszam = szobaszam
        self.datum = datum

class ScrollableFrame(tk.Frame):
    def __init__(self, master, items, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.items = items
        self.labels = []  # Label widgetek és azok állapotát tároló lista
        self.selected_items = []  # Kijelölt elemek tárolása
        self.init_ui()

    def init_ui(self):
        self.canvas = tk.Canvas(self, width=200)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="canvas_window")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

         # A scrollable_frame szélességének beállítása a canvas szélességére, de csak ha a canvas szélessége nagyobb, mint 0
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("canvas_window", width=e.width) if e.width > 0 else None)

        # A görgetési régió frissítése a scrollable_frame tartalmának változásakor
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Lista elemeinek megjelenítése Label widgetekként
        self.set_items(self.items)

    def set_items(self, items):
        for label in self.labels:
            label.destroy() # Előző elemek eltávolítása
        self.labels = []
        
        for item in items: # Új elemek hozzáadása
            lbl = tk.Label(self.scrollable_frame, text=item, bg="white", anchor="w")
            lbl.pack(fill="x", padx=5, pady=2)
            lbl.bind("<Button-1>", self.toggle_selection)
            self.labels.append(lbl)

    def toggle_selection(self, event):
        if not self.selection_enabled:  # Ha a kijelölhetőség nincs engedélyezve, ne tegyen semmit
            return
        lbl = event.widget # Az esemény forrása, ami a kattintott Label widget
        if lbl in self.selected_items:
            lbl.config(bg="white")  # Ha már kijelölt, akkor visszaállítjuk a háttérszínt és eltávolítjuk a listából
            self.selected_items.remove(lbl)
        else:
            lbl.config(bg="lightblue") # Ha nincs kijelölve, akkor beállítjuk kijelölt színre és hozzáadjuk a listához
            self.selected_items.append(lbl)

    def enable_selection(self, enable=True):
        self.selection_enabled = enable  # Kijelölhetőség állapotának beállítása

    def delete_selected(self):
        response = messagebox.askyesno("Megerősítés", "Biztosan törölni szeretné a kiválasztott elemeket?")
        if response:
            for lbl in self.selected_items:
                lbl.destroy() # Minden kijelölt elemet eltávolítunk
            self.selected_items.clear() # Ürítjük a kijelölt elemek listáját
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))  # Frissítjük a görgethető területet a maradék elemek alapján

class ButtonFrame(tk.Frame):
    def __init__(self, master, text, command=None):
        super().__init__(master)
        self.button_text = tk.StringVar()  # StringVar létrehozása
        self.button = ttk.Button(self, textvariable=self.button_text, command=command, width=20)
        self.button_text.set(text)  # Kezdeti felirat beállítása
        self.button.pack(padx=10, pady=10)

    def set_button_text(self, new_text):
        self.button_text.set(new_text)  # Felirat frissítése

    def disable(self):
        self.button.state(['disabled'])  # A gomb inaktívvá tétele

    def enable(self):
        self.button.state(['!disabled'])  # A gomb aktívvá tétele

class LabelFrame(tk.Frame):
    def __init__(self, master, text):
        super().__init__(master)
        self.label = ttk.Label(self, text=text)
        self.label.pack(side=tk.RIGHT, padx=10, pady=10)

class ComboBoxFrame(tk.Frame):
    def __init__(self, master, values):
        super().__init__(master)
        self.values = values
        self.combobox = ttk.Combobox(self, values=values, width=18, state="readonly")
        self.combobox.pack(padx=10, pady=10)
        self.combobox.bind("<Key>", lambda event: "break")  # Megakadályozza a felhasználót, hogy írjon a Combobox-ba
        self.combobox.set(values[0])  # Beállítjuk az alapértelmezett értéket az első elemre

    def disable(self):
        self.combobox.config(state='disabled')  # A combobox inaktívvá tétele

    def enable(self):
        self.combobox.config(state='normal')  # A combobox aktívvá tétele

def main():   
    global root, button1, button2, button3, button4, button5, button6, label1, label2, label3, label4, combobox1, combobox2, combobox3, combobox4, scrollable_frame, items, hotel
    root = tk.Tk()
    root.title("Szoba foglalás program")

    # Szobák hozzáadása
    hotel = Szalloda("Példa Hotel")
    hotel.szoba_hozzaadas(EgyagyasSzoba(101, 15000))
    hotel.szoba_hozzaadas(KetagyasSzoba(102, 20000))
    hotel.szoba_hozzaadas(EgyagyasSzoba(103, 15000))

    # A szobaszámok listájának létrehozása
    szobaszamok = [str(szoba.szobaszam) for szoba in hotel.szobak]

    # Véletlenszerű foglalások generálása
    ma = date.today()
    for _ in range(5):  # Például generálj 5 véletlenszerű foglalást
        szobaszam = random.choice([101, 102, 103])  # Válassz véletlenszerűen egy szobaszámot
        napok_hozzaadasa = random.randint(1, 30)  # Válassz véletlenszerűen egy számot 1 és 30 között
        veletlen_datum = ma + timedelta(days=napok_hozzaadasa)  # Adj hozzá véletlenszerű számú napot a mai dátumhoz
        hotel.foglalas(szobaszam, veletlen_datum.isoformat(), show_messagebox=False) # Hozzáad egy foglalást a véletlenszerűen választott dátumra, messagebox megjelenítés nélkül

     # A 'items' lista feltöltése a frissen generált foglalásokkal
    items = [f"Szobaszám: {foglalas.szobaszam}, Dátum: {foglalas.datum}" for foglalas in hotel.foglalasok]

    # A ScrollableFrame inicializálása az 'items' listával
    scrollable_frame = ScrollableFrame(root, items)
    scrollable_frame.grid(row=0, column=0, rowspan=5, columnspan=2, sticky="nsew")

    # A többi GUI elem inicializálása
    button1 = ButtonFrame(root, "Szoba foglalása", command=szoba_foglalasa)
    button1.grid(row=5, column=0)
    button2 = ButtonFrame(root, "Foglalás lemondása", command=foglalasok_lemondasa)
    button2.grid(row=5, column=1)
    button3 = ButtonFrame(root, "Foglalások listázása", command=foglalasok_listazasa)
    button3.grid(row=5, column=2)
    button4 = ButtonFrame(root, "Kilépés", command=on_exit)
    button4.grid(row=5, column=3)
    button5 = ButtonFrame(root, "Mentés vagy Törlés", command=mentes_vagy_torles)
    button5.grid(row=0, column=2)
    button6 = ButtonFrame(root, "Vissza", command=beginning)
    button6.grid(row=0, column=3)

    label1 = LabelFrame(root, "Szoba")
    label1.grid(row=1, column=2, sticky="e")
    label2 = LabelFrame(root, "Év")
    label2.grid(row=2, column=2, sticky="e")
    label3 = LabelFrame(root, "Hónap")
    label3.grid(row=3, column=2, sticky="e")
    label4 = LabelFrame(root, "Nap")
    label4.grid(row=4, column=2, sticky="e")

    combobox1 = ComboBoxFrame(root, szobaszamok)
    combobox1.grid(row=1, column=3)

    # Évek ComboBox inicializálása
    current_year = datetime.now().year
    years = [str(year) for year in range(current_year - 10, current_year + 11)]
    combobox2 = ComboBoxFrame(root, years)
    current_year_index = years.index(str(current_year))  # Az aktuális év indexének meghatározása a listában
    combobox2.combobox.current(current_year_index)  # Az aktuális év beállítása alapértelmezettként
    combobox2.grid(row=2, column=3)

    # Hónapok ComboBox inicializálása
    months = ['Január', 'Február', 'Március', 'Április', 'Május', 'Június', 'Július', 'Augusztus', 'Szeptember', 'Október', 'November', 'December']
    combobox3 = ComboBoxFrame(root, months)
    combobox3.combobox.current(datetime.now().month - 1)  # Jelenlegi hónap beállítása
    combobox3.grid(row=3, column=3)

    # Napok ComboBox inicializálása
    days = [str(day) for day in range(1, 32)]
    combobox4 = ComboBoxFrame(root, days)
    combobox4.combobox.current(datetime.now().day - 1)  # Jelenlegi nap beállítása
    combobox4.grid(row=4, column=3)

    beginning()  # Kezdeti állapot beállítása

    root.mainloop()

def beginning():
    # A többi widget inaktívvá tétele és elhalványítása
    for widget in [button5, button6, combobox1, combobox2, combobox3, combobox4]:
        widget.disable()  # Minden releváns widget inaktívvá tétele
    # Az 1, 2, 3, és 4-es gombok engedélyezése
    for widget in [button1, button2, button3, button4]:
        widget.enable()  # Minden releváns widget újra aktívvá tétele
    
    # A button5 feliratának megváltoztatása
    button5.set_button_text("Mentés vagy Törlés")

    # ttk stílus definiálása az inaktív címkékhez
    style = ttk.Style()
    style.configure("Inactive.TLabel", foreground="#D3D3D3")
    # A LabelFrame példányok címkéit inaktívvá tesszük az új stílus alkalmazásával      
    label1.label.configure(style="Inactive.TLabel")
    label2.label.configure(style="Inactive.TLabel")
    label3.label.configure(style="Inactive.TLabel")
    label4.label.configure(style="Inactive.TLabel")

    # A ScrollableFrame tartalmának ürítése
    clear_scrollable_frame(scrollable_frame)
    scrollable_frame.enable_selection(False)  # Kijelölhetőség kikapcsolása
    
def foglalasok_listazasa():	
    # Az inaktívá tett elemek újra aktívvá tétele
    for widget in [button6, button4]:
        widget.enable()  # Minden releváns widget újra aktívvá tétele
	# A többi widget inaktívvá tétele és elhalványítása
    for widget in [button5, button1, button2, button3, combobox1, combobox2, combobox3, combobox4]:
        widget.disable()  # Minden releváns widget inaktívvá tétele

    # ttk stílus definiálása az inaktív címkékhez
    style = ttk.Style()
    style.configure("Inactive.TLabel", foreground="#D3D3D3")
    # A LabelFrame példányok címkéit inaktívvá tesszük az új stílus alkalmazásával      
    label1.label.configure(style="Inactive.TLabel")
    label2.label.configure(style="Inactive.TLabel")
    label3.label.configure(style="Inactive.TLabel")
    label4.label.configure(style="Inactive.TLabel")

    # Frissítsük a foglalások listáját
    refresh_scrollable_frame()	

    # Meghívjuk a Szalloda osztály foglalas_listazasa metódusát
    hotel.foglalas_listazasa()

def szoba_foglalasa():
    # Az inaktívá tett elemek újra aktívvá tétele
    for widget in [button4, button5, button6, combobox1, combobox2, combobox3, combobox4]:
        widget.enable()  # Minden releváns widget újra aktívvá tétele	
    # A többi widget inaktívvá tétele és elhalványítása
    for widget in [button1, button2, button3]:
        widget.disable()  # Minden releváns widget inaktívvá tétele

    # A button5 feliratának megváltoztatása
    button5.set_button_text("Mentés")

    # ttk stílus definiálása az aktív címkékhez
    style = ttk.Style()
    style.configure("Active.TLabel", foreground="black")
    # A LabelFrame példányok címkéit inaktívvá tesszük az új stílus alkalmazásával      
    label1.label.configure(style="Active.TLabel")
    label2.label.configure(style="Active.TLabel")
    label3.label.configure(style="Active.TLabel")
    label4.label.configure(style="Active.TLabel")

    # Frissítsük a foglalások listáját
    refresh_scrollable_frame()	    

def foglalasok_lemondasa():	
    # Az inaktívá tett elemek újra aktívvá tétele
    for widget in [button4, button5, button6]:
        widget.enable()  # Minden releváns widget újra aktívvá tétele
	# A többi widget inaktívvá tétele és elhalványítása
    for widget in [button1, button2, button3, combobox1, combobox2, combobox3, combobox4]:
        widget.disable()  # Minden releváns widget inaktívvá tétele
		
	# A button5 feliratának megváltoztatása
    button5.set_button_text("Törlés")

    # ttk stílus definiálása az inaktív címkékhez
    style = ttk.Style()
    style.configure("Inactive.TLabel", foreground="#D3D3D3")
    # A LabelFrame példányok címkéit inaktívvá tesszük az új stílus alkalmazásával      
    label1.label.configure(style="Inactive.TLabel")
    label2.label.configure(style="Inactive.TLabel")
    label3.label.configure(style="Inactive.TLabel")
    label4.label.configure(style="Inactive.TLabel")

    # Frissítsük a foglalások listáját
    refresh_scrollable_frame()		
    scrollable_frame.enable_selection(True)  # Kijelölhetőség engedélyezése

def mentes_vagy_torles():
    global hotel
     # Ellenőrizzük a button5 gomb feliratát
    if button5.button_text.get() == "Mentés":  # Mentési művelet végrehajtása
        selected_szobaszam = combobox1.combobox.get()  # A kiválasztott szobaszám lekérése
        selected_year = combobox2.combobox.get()
        selected_month = str(combobox3.combobox.current() + 1).zfill(2)  # Hozzáadunk egyet, mert a `.current()` 0-tól indexel
        selected_day = combobox4.combobox.get().zfill(2)
        selected_date_str = f"{selected_year}-{selected_month}-{selected_day}"  # A kiválasztott dátum sztring formátumba összeállítása

        try:
            # A kiválasztott dátum átalakítása datetime.date objektummá
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Érvénytelen dátum", "A megadott dátum érvénytelen vagy nem létezik.")
            return  # Kilépünk a függvényből, nem folytatjuk tovább

        # Mai dátum lekérése
        today = datetime.today().date()

        # Ellenőrizzük, hogy a kiválasztott dátum nem korábbi-e, mint a mai nap
        if selected_date < today:
            messagebox.showwarning("Foglalási hiba", "A foglalás dátuma nem lehet korábbi, mint a mai nap!")
            return  # Kilépünk a függvényből, nem folytatjuk a foglalást

        # Hozzáadjuk a foglalást a hotelhez, ha a dátum érvényes
        hotel.foglalas(int(selected_szobaszam), selected_date_str)

        # Frissítjük a felületet az új foglalással
        refresh_scrollable_frame()
    
    elif button5.button_text.get() == "Törlés":
        # Ellenőrizzük, hogy van-e kijelölt elem
        if not scrollable_frame.selected_items:
            messagebox.showwarning("Törlés", "Nincs kijelölt elem a törléshez.")
        elif messagebox.askyesno("Megerősítés", "Biztosan törölni szeretné a kiválasztott elemeket?"):
            kijelolt_elemek = [(int(lbl.cget("text").split(", Dátum: ")[0].split(": ")[1]), lbl.cget("text").split(", Dátum: ")[1]) for lbl in scrollable_frame.selected_items if lbl.winfo_exists()]
            hotel.foglalas_lemondas(kijelolt_elemek)
            refresh_scrollable_frame()  # Frissítjük a megjelenítést

    else:
        print("Egyéb művelet...") # Ez az ág felesleges, mert az algoritmus szerint nem lehet ilyen aktív állapota a gombnak

def delete_selected():
    # Ellenőrizzük, hogy vannak-e kijelölt elemek
    if not scrollable_frame.selected_items:
        messagebox.showinfo("Törlés", "Nincs kijelölt elem.")
        return

    # Összegyűjtjük a kijelölt elemek adatait
    kijelolt_elemek_adatok = []
    for lbl in scrollable_frame.selected_items:
        kijelolt_elemek_adatok.append(lbl.cget("text"))

    # Megjelenítjük a megerősítő üzenetet az összes kijelölt elemmel
    valasz = messagebox.askyesno("Megerősítés", "Biztosan törölni szeretnéd a következő elemeket?\n" + "\n".join(kijelolt_elemek_adatok))
    if valasz:
        for lbl in scrollable_frame.selected_items:
            lbl.destroy()
        scrollable_frame.selected_items.clear()  # Töröljük a kijelölt elemek listáját
        scrollable_frame.canvas.configure(scrollregion=scrollable_frame.canvas.bbox("all"))  # Frissítjük a görgethető területet

        # Frissítjük a foglalások listáját (szükség esetén)
        refresh_scrollable_frame()

def refresh_scrollable_frame():
    global hotel, scrollable_frame
    # A foglalások rendezése dátum szerint
    sorted_foglalasok = sorted(hotel.foglalasok, key=lambda x: datetime.strptime(x.datum, "%Y-%m-%d"))

    # A ScrollableFrame újratöltése az rendezett foglalásokkal
    items = [f"Szobaszám: {foglalas.szobaszam}, Dátum: {foglalas.datum}" for foglalas in sorted_foglalasok]
    scrollable_frame.set_items(items)

def clear_scrollable_frame(scrollable_frame):
    # Végigiterálunk a scrollable_frame scrollable_frame widgetjén belüli összes widgeten
    for widget in scrollable_frame.scrollable_frame.winfo_children():
        widget.destroy()  # Minden egyes widget eltávolítása
    # A scrollable_frame frissítése, hogy tükrözze a tartalom eltávolítását
    scrollable_frame.canvas.configure(scrollregion=scrollable_frame.canvas.bbox("all"))

def on_exit():
    result = messagebox.askquestion("Kilépés", "Biztosan ki szeretnél lépni?", icon='question')
    if result == 'yes':  
        root.destroy()      # főablak bezárása

if __name__ == "__main__":
    main()