import hashlib
import json
import os
import random
import string

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passwords.json")


def hash_codice(codice):
    return hashlib.sha256(codice.encode("utf-8")).hexdigest()


def carica_database():
    if not os.path.exists(DB_FILE):
        return {"master_hash": None, "dati": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"master_hash": None, "dati": []}


def salva_database(contenuto):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(contenuto, f, indent=4)


def genera_password(lunghezza=12, usa_speciali=True, usa_numeri=True):
    min_richiesto = 2 + (1 if usa_numeri else 0) + (1 if usa_speciali else 0)
    if lunghezza < min_richiesto:
        raise ValueError(f"Minimo richiesto: {min_richiesto}")

    minuscole = string.ascii_lowercase
    maiuscole = string.ascii_uppercase
    numeri = string.digits
    speciali = string.punctuation

    password_chars = [random.choice(maiuscole)]
    caratteri_disponibili = minuscole + maiuscole

    if usa_numeri:
        password_chars.append(random.choice(numeri))
        caratteri_disponibili += numeri
    if usa_speciali:
        password_chars.append(random.choice(speciali))
        caratteri_disponibili += speciali

    rimanenti = lunghezza - len(password_chars)
    password_chars.extend(random.choice(caratteri_disponibili) for _ in range(rimanenti))

    random.shuffle(password_chars)
    return "".join(password_chars)


class InfoPopup(Popup):
    def __init__(self, title, text, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size_hint = (0.8, 0.5)
        content = BoxLayout(orientation="vertical", spacing=10, padding=20)
        content.add_widget(Label(text=text, halign="center", valign="middle"))
        close = Button(text="Chiudi", size_hint_y=None, height=48)
        close.bind(on_press=self.dismiss)
        content.add_widget(close)
        self.content = content


class SetupMasterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        title = Label(text="Benvenuto!", font_size="24sp", bold=True)
        subtitle = Label(text="Crea un codice di accesso:")
        self.entry = TextInput(password=True, multiline=False, hint_text="Inserisci codice", font_size="18sp")
        button = Button(text="Imposta Codice", size_hint_y=None, height=52)
        button.bind(on_press=self.salva_master)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.entry)
        layout.add_widget(button)
        self.add_widget(layout)

    def salva_master(self, instance):
        app = App.get_running_app()
        codice = self.entry.text.strip()
        if not codice:
            popup = InfoPopup("Errore", "Il codice non può essere vuoto!")
            popup.open()
            return

        app.db = carica_database()
        app.db["master_hash"] = hash_codice(codice)
        salva_database(app.db)
        app.sm.current = "login"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        title = Label(text="Sblocca App", font_size="24sp", bold=True)
        subtitle = Label(text="Inserisci il codice:")
        self.entry = TextInput(password=True, multiline=False, hint_text="Codice", font_size="18sp")
        self.entry.bind(on_text_validate=self.verifica_login)
        button = Button(text="Sblocca", size_hint_y=None, height=52)
        button.bind(on_press=self.verifica_login)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.entry)
        layout.add_widget(button)
        self.add_widget(layout)

    def verifica_login(self, instance):
        app = App.get_running_app()
        inserito = self.entry.text.strip()
        if hash_codice(inserito) == app.db.get("master_hash"):
            self.entry.text = ""
            app.sm.current = "home"
            app.home_screen.refresh()
        else:
            popup = InfoPopup("Errore", "Codice errato!")
            popup.open()
            self.entry.text = ""


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def refresh(self):
        self.layout.clear_widgets()
        title = Label(text="Gestore Password", font_size="22sp", bold=True)
        self.layout.add_widget(title)

        buttons = [
            ("Nuova Password", "new_password"),
            ("Visualizza Salvate", "view_passwords"),
            ("Modifica Password", "edit_password"),
            ("Elimina Password", "delete_password"),
            ("Blocca App", "login"),
        ]

        for label, screen_name in buttons:
            btn = Button(text=label, size_hint_y=None, height=48)
            btn.bind(on_press=self.go_to_screen(screen_name))
            self.layout.add_widget(btn)

    def go_to_screen(self, screen_name):
        def _handler(instance):
            app = App.get_running_app()
            if screen_name == "login":
                app.sm.current = "login"
                return
            app.sm.current = screen_name
            if hasattr(app, screen_name + "_screen"):
                screen = getattr(app, screen_name + "_screen")
                if hasattr(screen, "refresh"):
                    screen.refresh()
        return _handler


class NewPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=8)
        self.add_widget(self.layout)

    def refresh(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Nuova Password", font_size="22sp", bold=True))

        self.entry_sito = TextInput(hint_text="Nome sito o servizio", multiline=False)
        self.entry_utente = TextInput(hint_text="Nome utente / Email", multiline=False)
        self.entry_lunghezza = TextInput(text="12", multiline=False)
        self.var_spec = CheckBox(active=True)
        self.var_num = CheckBox(active=True)

        self.layout.add_widget(Label(text="Nome sito o servizio:"))
        self.layout.add_widget(self.entry_sito)
        self.layout.add_widget(Label(text="Nome utente / Email:"))
        self.layout.add_widget(self.entry_utente)
        self.layout.add_widget(Label(text="Lunghezza:"))
        self.layout.add_widget(self.entry_lunghezza)

        spec_box = BoxLayout(orientation="horizontal")
        spec_box.add_widget(Label(text="Includi speciali"))
        spec_box.add_widget(self.var_spec)
        self.layout.add_widget(spec_box)

        num_box = BoxLayout(orientation="horizontal")
        num_box.add_widget(Label(text="Includi numeri"))
        num_box.add_widget(self.var_num)
        self.layout.add_widget(num_box)

        btn_save = Button(text="Genera e Salva", size_hint_y=None, height=48)
        btn_save.bind(on_press=self.salva_nuova)
        self.layout.add_widget(btn_save)

        btn_back = Button(text="Indietro", size_hint_y=None, height=42)
        btn_back.bind(on_press=self.go_back)
        self.layout.add_widget(btn_back)

    def salva_nuova(self, instance):
        app = App.get_running_app()
        sito = self.entry_sito.text.strip() or "Sito Generico"
        utente = self.entry_utente.text.strip() or "Non specificato"
        try:
            lunghezza = int(self.entry_lunghezza.text.strip() or 12)
            password = genera_password(lunghezza, self.var_spec.active, self.var_num.active)
            app.db = carica_database()
            app.db["dati"].append({"sito": sito, "utente": utente, "password": password})
            salva_database(app.db)
            popup = InfoPopup("Successo", f"Salvata per '{sito}'!\nPassword: {password}")
            popup.open()
            app.sm.current = "home"
            app.home_screen.refresh()
        except ValueError:
            popup = InfoPopup("Errore", "Inserisci un numero valido!")
            popup.open()

    def go_back(self, instance):
        App.get_running_app().sm.current = "home"


class ViewPasswordsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def refresh(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Password Salvate", font_size="22sp", bold=True))

        app = App.get_running_app()
        lista = app.db.get("dati", [])

        scroll = ScrollView(do_scroll_x=False)
        text = Label(size_hint_y=None, valign="top")
        text.bind(size=lambda instance, value: setattr(text, "text_size", (instance.width, None)))

        if not lista:
            text.text = "Nessuna password salvata."
        else:
            righe = []
            for i, item in enumerate(lista, 1):
                righe.append(f"[{i}] {item['sito']}\nUtente: {item['utente']}\nPass: {item['password']}\n{'-'*30}\n")
            text.text = "".join(righe)
        scroll.add_widget(text)
        self.layout.add_widget(scroll)

        back = Button(text="Indietro", size_hint_y=None, height=42)
        back.bind(on_press=self.go_back)
        self.layout.add_widget(back)

    def go_back(self, instance):
        App.get_running_app().sm.current = "home"


class EditPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def refresh(self):
        app = App.get_running_app()
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Seleziona da modificare", font_size="22sp", bold=True))
        lista = app.db.get("dati", [])
        if not lista:
            self.layout.add_widget(Label(text="Nessuna password da modificare."))
            btn = Button(text="Indietro", size_hint_y=None, height=42)
            btn.bind(on_press=self.go_back)
            self.layout.add_widget(btn)
            return

        self.entries = []
        for i, item in enumerate(lista, 1):
            btn = Button(text=f"{i}. {item['sito']} ({item['utente']})")
            btn.bind(on_press=self.open_edit_screen(i - 1))
            self.layout.add_widget(btn)

        back = Button(text="Indietro", size_hint_y=None, height=42)
        back.bind(on_press=self.go_back)
        self.layout.add_widget(back)

    def open_edit_screen(self, index):
        def _handler(instance):
            app = App.get_running_app()
            app.edit_item_screen.set_index(index)
            app.sm.current = "edit_single"
        return _handler

    def go_back(self, instance):
        App.get_running_app().sm.current = "home"


class EditSingleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = 0
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=8)
        self.add_widget(self.layout)

    def set_index(self, index):
        self.index = index
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        item = app.db["dati"][self.index]
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Modifica Credenziali", font_size="22sp", bold=True))

        self.entry_sito = TextInput(text=item["sito"], multiline=False)
        self.entry_utente = TextInput(text=item["utente"], multiline=False)
        self.entry_pass = TextInput(text=item["password"], multiline=False)

        self.layout.add_widget(Label(text="Nuovo sito o servizio:"))
        self.layout.add_widget(self.entry_sito)
        self.layout.add_widget(Label(text="Nuovo utente / Email:"))
        self.layout.add_widget(self.entry_utente)
        self.layout.add_widget(Label(text="Nuova password (lascia vuota per non cambiare):"))
        self.layout.add_widget(self.entry_pass)

        save = Button(text="Salva Modifiche", size_hint_y=None, height=48)
        save.bind(on_press=self.salva_modifiche)
        self.layout.add_widget(save)

        back = Button(text="Annulla", size_hint_y=None, height=42)
        back.bind(on_press=self.go_back)
        self.layout.add_widget(back)

    def salva_modifiche(self, instance):
        app = App.get_running_app()
        item = app.db["dati"][self.index]
        item["sito"] = self.entry_sito.text.strip() or item["sito"]
        item["utente"] = self.entry_utente.text.strip() or item["utente"]
        nuova_p = self.entry_pass.text.strip()
        if nuova_p:
            item["password"] = nuova_p
        salva_database(app.db)
        popup = InfoPopup("Successo", "Modifiche salvate correttamente!")
        popup.open()
        app.sm.current = "home"
        app.home_screen.refresh()

    def go_back(self, instance):
        App.get_running_app().sm.current = "edit_password"


class DeletePasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def refresh(self):
        app = App.get_running_app()
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Elimina Password", font_size="22sp", bold=True))
        lista = app.db.get("dati", [])

        if not lista:
            self.layout.add_widget(Label(text="Nessuna password da eliminare."))
            btn = Button(text="Indietro", size_hint_y=None, height=42)
            btn.bind(on_press=self.go_back)
            self.layout.add_widget(btn)
            return

        for i, item in enumerate(lista, 1):
            btn = Button(text=f"{i}. {item['sito']} ({item['utente']})")
            btn.bind(on_press=self.elimina(i - 1))
            self.layout.add_widget(btn)

        back = Button(text="Indietro", size_hint_y=None, height=42)
        back.bind(on_press=self.go_back)
        self.layout.add_widget(back)

    def elimina(self, index):
        def _handler(instance):
            app = App.get_running_app()
            sito_rimosso = app.db["dati"][index]["sito"]
            app.db["dati"].pop(index)
            salva_database(app.db)
            popup = InfoPopup("Eliminato", f"Rimosso: {sito_rimosso}")
            popup.open()
            app.sm.current = "home"
            app.home_screen.refresh()
        return _handler

    def go_back(self, instance):
        App.get_running_app().sm.current = "home"


class PasswordManagerApp(App):
    def build(self):
        self.db = carica_database()
        self.sm = ScreenManager()

        self.setup_master_screen = SetupMasterScreen(name="setup_master")
        self.login_screen = LoginScreen(name="login")
        self.home_screen = HomeScreen(name="home")
        self.new_password_screen = NewPasswordScreen(name="new_password")
        self.view_passwords_screen = ViewPasswordsScreen(name="view_passwords")
        self.edit_password_screen = EditPasswordScreen(name="edit_password")
        self.edit_item_screen = EditSingleScreen(name="edit_single")
        self.delete_password_screen = DeletePasswordScreen(name="delete_password")

        self.sm.add_widget(self.setup_master_screen)
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.new_password_screen)
        self.sm.add_widget(self.view_passwords_screen)
        self.sm.add_widget(self.edit_password_screen)
        self.sm.add_widget(self.edit_item_screen)
        self.sm.add_widget(self.delete_password_screen)

        if self.db.get("master_hash"):
            self.sm.current = "login"
        else:
            self.sm.current = "setup_master"

        return self.sm

    def on_start(self):
        self.home_screen.refresh()
        self.new_password_screen.refresh()
        self.view_passwords_screen.refresh()
        self.edit_password_screen.refresh()
        self.delete_password_screen.refresh()


if __name__ == "__main__":
    PasswordManagerApp().run()
