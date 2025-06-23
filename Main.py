from tkinter import *
import tkintermapview
import requests
from urllib.parse import quote

# === DANE UCZELNI ===
uczelnie = []
uczelnia_pracownicy = {}
uczelnia_klienci = {}

class Uczelnia:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = map_widget.set_marker(self.latitude, self.longitude, text=self.nazwa)

    def get_coordinates(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search.php?q={quote(self.nazwa)}&format=jsonv2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return float(data[0]["lat"]), float(data[0]["lon"])
        except:
            return 52.23, 21.0

class Osoba:
    def __init__(self, imie_nazwisko, miasto, nazwa_uczelni):
        self.imie_nazwisko = imie_nazwisko
        self.miasto = miasto
        self.nazwa_uczelni = nazwa_uczelni
        self.latitude, self.longitude = self.get_coordinates()
        self.marker = None

    def get_coordinates(self):
        try:
            url = f"https://nominatim.openstreetmap.org/search.php?q={quote(self.miasto)}&format=jsonv2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return float(data[0]["lat"]), float(data[0]["lon"])
        except:
            return 52.23, 21.0

class Pracownik(Osoba): pass
class Klient(Osoba): pass

def otworz_panel_osob(nazwa_typu, typ_klasy, baza_danych):
    idx = listbox_uczelnie.curselection()
    if not idx:
        return
    uczelnia = uczelnie[idx[0]]
    nazwa_uczelni = uczelnia.nazwa
    if nazwa_uczelni not in baza_danych:
        baza_danych[nazwa_uczelni] = []

    okno = Toplevel(root)
    okno.title(f"{nazwa_typu} – {nazwa_uczelni}")
    okno.geometry("400x550")

    listbox = Listbox(okno, width=50, height=15)
    listbox.pack()

    def odswiez():
        listbox.delete(0, END)
        for i, o in enumerate(baza_danych[nazwa_uczelni]):
            listbox.insert(i, f"{i+1}. {o.imie_nazwisko} – {o.miasto}")

    def dodaj():
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        osoba = typ_klasy(imie, miasto, nazwa_uczelni)
        baza_danych[nazwa_uczelni].append(osoba)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)

    def usun():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        if baza_danych[nazwa_uczelni][i].marker:
            baza_danych[nazwa_uczelni][i].marker.delete()
        baza_danych[nazwa_uczelni].pop(i)
        odswiez()

    def edytuj():
        sel = listbox.curselection()
        if not sel:
            return
        i = sel[0]
        osoba = baza_danych[nazwa_uczelni][i]
        entry_imie.delete(0, END)
        entry_imie.insert(0, osoba.imie_nazwisko)
        entry_miasto.delete(0, END)
        entry_miasto.insert(0, osoba.miasto)
        button_dodaj.config(text="Zapisz", command=lambda: zapisz(i))

    def zapisz(i):
        imie = entry_imie.get().strip()
        miasto = entry_miasto.get().strip()
        if not imie or not miasto:
            return
        if baza_danych[nazwa_uczelni][i].marker:
            baza_danych[nazwa_uczelni][i].marker.delete()
        baza_danych[nazwa_uczelni][i] = typ_klasy(imie, miasto, nazwa_uczelni)
        odswiez()
        entry_imie.delete(0, END)
        entry_miasto.delete(0, END)
        button_dodaj.config(text=f"Dodaj {nazwa_typu.lower()}", command=dodaj)

    def pokaz_na_mapie_wszystkich():
        osoby = baza_danych[nazwa_uczelni]
        if not osoby:
            return
        for o in osoby:
            if o.marker:
                o.marker.delete()
            o.marker = map_widget.set_marker(o.latitude, o.longitude, text=f"{o.imie_nazwisko}\n({o.miasto})")
        lat = sum(o.latitude for o in osoby) / len(osoby)
        lon = sum(o.longitude for o in osoby) / len(osoby)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(8)

    entry_imie = Entry(okno, width=40)
    entry_imie.pack()
    entry_imie.insert(0, "Imię i nazwisko")

    entry_miasto = Entry(okno, width=40)
    entry_miasto.pack()
    entry_miasto.insert(0, "Miasto")

    button_dodaj = Button(okno, text=f"Dodaj {nazwa_typu.lower()}", command=dodaj)
    button_dodaj.pack(pady=2)

    Button(okno, text=f"Usuń {nazwa_typu.lower()}", command=usun).pack(pady=2)
    Button(okno, text=f"Edytuj {nazwa_typu.lower()}", command=edytuj).pack(pady=2)
    Button(okno, text="Pokaż wszystkich na mapie", command=pokaz_na_mapie_wszystkich).pack(pady=4)

    odswiez()

def dodaj_uczelnie():
    nazwa = entry_nazwa.get().strip()
    if not nazwa:
        return
    uczelnia = Uczelnia(nazwa)
    uczelnie.append(uczelnia)
    uczelnia_pracownicy[nazwa] = []
    uczelnia_klienci[nazwa] = []
    pokaz_uczelnie()
    entry_nazwa.delete(0, END)
    entry_nazwa.focus()

def pokaz_uczelnie():
    listbox_uczelnie.delete(0, END)
    for i, uczelnia in enumerate(uczelnie):
        listbox_uczelnie.insert(i, f"{i+1}. {uczelnia.nazwa}")

def pokaz_na_mapie_uczelni():
    idx = listbox_uczelnie.curselection()
    if not idx:
        return
    uczelnia = uczelnie[idx[0]]
    map_widget.set_position(uczelnia.latitude, uczelnia.longitude)
    map_widget.set_zoom(13)

def pokaz_wszystkie_uczelnie_na_mapie():
    for u in uczelnie:
        if u.marker:
            u.marker.delete()
        u.marker = map_widget.set_marker(u.latitude, u.longitude, text=u.nazwa)
    if uczelnie:
        lat = sum(u.latitude for u in uczelnie) / len(uczelnie)
        lon = sum(u.longitude for u in uczelnie) / len(uczelnie)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(6)

def pokaz_osoby_uczelni(typ):
    idx = listbox_uczelnie.curselection()
    if not idx:
        return
    uczelnia = uczelnie[idx[0]]
    nazwa = uczelnia.nazwa
    dane = uczelnia_pracownicy if typ == "pracownik" else uczelnia_klienci
    osoby = dane.get(nazwa, [])
    for o in osoby:
        if o.marker:
            o.marker.delete()
        o.marker = map_widget.set_marker(o.latitude, o.longitude, text=f"{o.imie_nazwisko}\n({o.miasto})")
    if osoby:
        lat = sum(o.latitude for o in osoby) / len(osoby)
        lon = sum(o.longitude for o in osoby) / len(osoby)
        map_widget.set_position(lat, lon)
        map_widget.set_zoom(7)

def usun_uczelnie():
    idx = listbox_uczelnie.curselection()
    if not idx:
        return
    i = idx[0]
    uczelnia = uczelnie[i]
    for p in uczelnia_pracownicy.get(uczelnia.nazwa, []):
        if p.marker:
            p.marker.delete()
    for k in uczelnia_klienci.get(uczelnia.nazwa, []):
        if k.marker:
            k.marker.delete()
    if uczelnia.marker:
        uczelnia.marker.delete()
    uczelnie.pop(i)
    uczelnia_pracownicy.pop(uczelnia.nazwa, None)
    uczelnia_klienci.pop(uczelnia.nazwa, None)
    pokaz_uczelnie()

def edytuj_uczelnie():
    idx = listbox_uczelnie.curselection()
    if not idx:
        return
    i = idx[0]
    entry_nazwa.delete(0, END)
    entry_nazwa.insert(0, uczelnie[i].nazwa)
    button_dodaj.config(text="Zapisz", command=lambda: zapisz_edycje(i))

def zapisz_edycje(i):
    nowa_nazwa = entry_nazwa.get().strip()
    if not nowa_nazwa:
        return
    stara_nazwa = uczelnie[i].nazwa
    if uczelnie[i].marker:
        uczelnie[i].marker.delete()
    uczelnie[i] = Uczelnia(nowa_nazwa)
    uczelnia_pracownicy[nowa_nazwa] = uczelnia_pracownicy.pop(stara_nazwa, [])
    uczelnia_klienci[nowa_nazwa] = uczelnia_klienci.pop(stara_nazwa, [])
    pokaz_uczelnie()
    entry_nazwa.delete(0, END)
    button_dodaj.config(text="Dodaj uczelnię", command=dodaj_uczelnie)


# === GUI ===
root = Tk()
root.title("Uczelnie – Mapa i Zarządzanie")
root.geometry("1200x700")

ramka_lista = Frame(root)
ramka_formularz = Frame(root)
ramka_mapa = Frame(root)

ramka_lista.pack(side=LEFT, padx=10, pady=10)
ramka_formularz.pack(side=TOP, padx=10, pady=10)
ramka_mapa.pack(side=BOTTOM, padx=10, pady=10, fill=BOTH, expand=True)