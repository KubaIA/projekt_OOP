from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import random
import sys

# Absztrakt Szoba osztály
class Szoba(ABC):
    def __init__(self, szobaszam, ar):
        self.szobaszam = szobaszam
        self.ar = ar

    @abstractmethod
    def info(self):
        pass

# EgyagyasSzoba osztály
class EgyagyasSzoba(Szoba):
    def __init__(self, szobaszam, ar):
        super().__init__(szobaszam, ar)

    def info(self):
        return f"Egyágyas szoba, szobaszám: {self.szobaszam}, ár: {self.ar} Ft/éj"

# KetagyasSzoba osztály
class KetagyasSzoba(Szoba):
    def __init__(self, szobaszam, ar):
        super().__init__(szobaszam, ar)

    def info(self):
        return f"Kétágyas szoba, szobaszám: {self.szobaszam}, ár: {self.ar} Ft/éj"

# Szalloda osztály
class Szalloda:
    def __init__(self, nev):
        self.nev = nev
        self.szobak = []
        self.foglalasok = []

    def szoba_hozzaadas(self, szoba):
        self.szobak.append(szoba)

    def foglalas(self, szobaszam, datum):
        if any(f.szobaszam == szobaszam and f.datum == datum for f in self.foglalasok):
            print("Ez a szoba ezen a napon már foglalt.")
            return
        for szoba in self.szobak:
            if szoba.szobaszam == szobaszam:
                self.foglalasok.append(Foglalas(szobaszam, datum))
                # Rendezzük a foglalásokat dátum szerint minden sikeres foglalás után
                self.foglalasok = sorted(self.foglalasok, key=lambda x: x.datum)
                print(f"Foglalás sikeres: {szoba.info()}, dátum: {datum}")
                return
        print("Nincs ilyen szobaszám.")

    def foglalas_lemondas(self, szobaszam, datum):
        for foglalas in self.foglalasok:
            if foglalas.szobaszam == szobaszam and foglalas.datum == datum:
                self.foglalasok.remove(foglalas)
                print(f"Foglalás lemondva: Szobaszám: {szobaszam}, Dátum: {datum}")
                return
        print("Nincs ilyen foglalás.")

    def foglalasok_listazasa(self):
        if not self.foglalasok:
            print("Nincsenek foglalások.")
            return
        for foglalas in self.foglalasok:
            print(f"Szobaszám: {foglalas.szobaszam}, Dátum: {foglalas.datum}")

# Foglalas osztály
class Foglalas:
    def __init__(self, szobaszam, datum):
        self.szobaszam = szobaszam
        self.datum = datum

# Felhasználói interfész
def felhasznaloi_interfesz():
    hotel = Szalloda("Példa Hotel")
    # Szobák hozzáadása (szobatípus osztály(szobanév, szoba ár))
    hotel.szoba_hozzaadas(EgyagyasSzoba(101, 15000))
    hotel.szoba_hozzaadas(KetagyasSzoba(102, 20000))
    hotel.szoba_hozzaadas(EgyagyasSzoba(103, 15000))
    # Kezdeti foglalások (5 darab) 
    ma = date.today()
    for _ in range(5):
        szobaszam = 101 + random.randint(0, 2)  # Válasszon egy véletlenszerű szobát a három közül
        foglalt = True
        while foglalt:  # Addig próbálkozzon, amíg nem talál szabad dátumot
            veletlen_nap = random.randint(0, 30)  # Véletlenszerű nap a következő 30 napból
            datum = ma + timedelta(days=veletlen_nap)
            if all(f.szobaszam != szobaszam or f.datum != datum.isoformat() for f in hotel.foglalasok):
                hotel.foglalas(szobaszam, datum.isoformat())
                foglalt = False

    while True:
        print("\n*** Szálloda Szobafoglalási Rendszer ***")
        print("1. Szoba foglalása")
        print("2. Foglalás lemondása")
        print("3. Foglalások listázása")
        print("4. Kilépés")
        valasztas = input("Válasszon egy opciót: ")

        if valasztas == '1':
            szobaszam = int(input("Adja meg a szobaszámot: "))
            datum = input("Adja meg a foglalás dátumát (YYYY-MM-DD formátumban): ")
            if datetime.strptime(datum, "%Y-%m-%d").date() <= date.today():
                print("A foglalás dátuma érvénytelen. Kérjük, adjon meg egy jövőbeli dátumot.")
                continue
            hotel.foglalas(szobaszam, datum)
        elif valasztas == '2':
            szobaszam = int(input("Adja meg a lemondandó foglalás szobaszámát: "))
            datum = input("Adja meg a foglalás dátumát (YYYY-MM-DD formátumban): ")
            hotel.foglalas_lemondas(szobaszam, datum)
        elif valasztas == '3':
            hotel.foglalasok_listazasa()
        elif valasztas == '4':
            print("Köszönjük, hogy használta a rendszert.")
            break
        else:
            print("Érvénytelen opció. Kérem, próbálja újra.")

felhasznaloi_interfesz()