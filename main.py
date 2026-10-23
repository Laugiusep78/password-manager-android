import random
import string
import json
import os
import hashlib
import tkinter as tk
from tkinter import messagebox

DB_FILE = "passwords.json"

def hash_codice(codice):
    return hashlib.sha256(codice.encode()).hexdigest()

def carica_database():
    if not os.path.exists(DB_FILE):
        return {"master_hash": None, "dati": []}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"master_hash": None, "dati": []}

def salva_database(contenuto):
    with open(DB_FILE, 'w') as f:
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
    return ''.join(password_chars)

class PasswordManagerMobile:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("360x600")
        
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.db = carica_database()
        
        if not self.db.get("master_hash"):
            self.imposta_master_iniziale()
        else:
            self.schermata_login()

    def pulisci_finestra(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def imposta_master_iniziale(self):
        self.pulisci_finestra()
        
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(expand=True, fill="both")
        
        tk.Label(container, text="Benvenuto!", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        tk.Label(container, text="Crea un codice di accesso:", font=("Arial", 11)).pack(pady=10)
        
        self.entry_master = tk.Entry(container, show="*", font=("Arial", 14), justify="center")
        self.entry_master.pack(fill="x", pady=15)
        
        btn = tk.Button(container, text="Imposta Codice", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", height=2, command=self.salva_master_iniziale)
        btn.pack(fill="x", pady=15)

    def salva_master_iniziale(self):
        codice = self.entry_master.get().strip()
        if not codice:
            messagebox.showerror("Errore", "Il codice non può essere vuoto!")
            return
        
        self.db["master_hash"] = hash_codice(codice)
        salva_database(self.db)
        messagebox.showinfo("Successo", "Codice impostato con successo!")
        self.schermata_login()

    def schermata_login(self):
        self.pulisci_finestra()
        
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(expand=True, fill="both")
        
        tk.Label(container, text="Sblocca App", font=("Arial", 18, "bold")).pack(pady=(30, 10))
        tk.Label(container, text="Inserisci il codice:", font=("Arial", 11)).pack(pady=10)
        
        self.entry_login = tk.Entry(container, show="*", font=("Arial", 14), justify="center")
        self.entry_login.pack(fill="x", pady=15)
        self.entry_login.bind("<Return>", lambda event: self.verifica_login())
        
        btn = tk.Button(container, text="Sblocca", font=("Arial", 12, "bold"), bg="#2196F3", fg="white", height=2, command=self.verifica_login)
        btn.pack(fill="x", pady=15)

    def verifica_login(self):
        inserito = self.entry_login.get().strip()
        if hash_codice(inserito) == self.db.get("master_hash"):
            self.schermata_principale()
        else:
            messagebox.showerror("Errore", "Codice errato!")
            self.entry_login.delete(0, tk.END)

    def schermata_principale(self):
        self.pulisci_finestra()
        
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(expand=True, fill="both")
        
        tk.Label(container, text="Gestore Password", font=("Arial", 16, "bold")).pack(pady=(10, 15))

        tk.Button(container, text="Nuova Password", font=("Arial", 11, "bold"), height=2, bg="#e0e0e0", command=self.schermata_aggiungi).pack(fill="x", pady=6)
        tk.Button(container, text="Visualizza Salvate", font=("Arial", 11, "bold"), height=2, bg="#e0e0e0", command=self.schermata_visualizza).pack(fill="x", pady=6)
        tk.Button(container, text="Modifica Password", font=("Arial", 11, "bold"), height=2, bg="#fff9c4", command=self.schermata_seleziona_modifica).pack(fill="x", pady=6)
        tk.Button(container, text="Elimina Password", font=("Arial", 11, "bold"), height=2, bg="#ffcdd2", command=self.schermata_elimina).pack(fill="x", pady=6)
        
        tk.Button(container, text="Blocca App", font=("Arial", 10, "bold"), height=1, bg="#f44336", fg="white", command=self.schermata_login).pack(fill="x", pady=(15, 0))

    def schermata_aggiungi(self):
        self.pulisci_finestra()

        container = tk.Frame(self.root, padx=20, pady=10)
        container.pack(expand=True, fill="both")

        tk.Label(container, text="Nuova Password", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        tk.Label(container, text="Nome Sito o Servizio:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_sito = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_sito.pack(fill="x", pady=(0, 8), ipady=4)

        tk.Label(container, text="Nome utente / Email:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_utente = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_utente.pack(fill="x", pady=(0, 8), ipady=4)

        tk.Label(container, text="Lunghezza (default 12):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_len = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_len.insert(0, "12")
        entry_len.pack(fill="x", pady=(0, 8), ipady=4)

        var_spec = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Includi caratteri speciali", variable=var_spec, font=("Arial", 10)).pack(anchor="w", pady=2)

        var_num = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Includi numeri", variable=var_num, font=("Arial", 10)).pack(anchor="w", pady=2)

        def salva_nuova():
            sito = entry_sito.get().strip() or "Sito Generico"
            utente = entry_utente.get().strip() or "Non specificato"
            try:
                lunghezza = int(entry_len.get().strip())
                password = genera_password(lunghezza, var_spec.get(), var_num.get())
                
                self.db = carica_database()
                self.db["dati"].append({"sito": sito, "utente": utente, "password": password})
                salva_database(self.db)
                
                messagebox.showinfo("Successo", f"Salvata per '{sito}'!\nPassword: {password}")
                self.schermata_principale()
            except ValueError as e:
                messagebox.showerror("Errore", str(e))

        # Bottoni grandi e ben visibili
        tk.Button(container, text="Genera e Salva", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", height=2, command=salva_nuova).pack(fill="x", pady=10)
        tk.Button(container, text="Indietro", font=("Arial", 10, "bold"), height=1, bg="#e0e0e0", command=self.schermata_principale).pack(fill="x", pady=2)

    def schermata_visualizza(self):
        self.pulisci_finestra()

        container = tk.Frame(self.root, padx=15, pady=15)
        container.pack(expand=True, fill="both")

        tk.Label(container, text="Password Salvate", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        self.db = carica_database()
        lista = self.db["dati"]

        text_area = tk.Text(container, font=("Courier", 10), wrap="word")
        text_area.pack(expand=True, fill="both", pady=5)

        if not lista:
            text_area.insert(tk.END, "Nessuna password salvata.")
        else:
            for i, item in enumerate(lista, 1):
                riga = f"[{i}] {item['sito']}\nUtente: {item['utente']}\nPass: {item['password']}\n" + "-"*30 + "\n"
                text_area.insert(tk.END, riga)
        
        text_area.config(state="disabled")

        tk.Button(container, text="Indietro", font=("Arial", 10, "bold"), height=2, bg="#e0e0e0", command=self.schermata_principale).pack(fill="x", pady=10)

    def schermata_seleziona_modifica(self):
        self.pulisci_finestra()

        container = tk.Frame(self.root, padx=15, pady=15)
        container.pack(expand=True, fill="both")

        tk.Label(container, text="Seleziona da Modificare", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        self.db = carica_database()
        lista = self.db["dati"]

        if not lista:
            messagebox.showinfo("Info", "Nessuna password da modificare.")
            self.schermata_principale()
            return

        listbox = tk.Listbox(container, font=("Arial", 11))
        for i, item in enumerate(lista, 1):
            listbox.insert(tk.END, f"{i}. {item['sito']} ({item['utente']})")
        listbox.pack(fill="both", expand=True, pady=5)

        def vai_a_modifica():
            selezione = listbox.curselection()
            if not selezione:
                messagebox.showerror("Errore", "Seleziona un elemento.")
                return
            self.schermata_form_modifica(selezione[0])

        tk.Button(container, text="Modifica Selezionato", font=("Arial", 11, "bold"), bg="#FF9800", fg="white", height=2, command=vai_a_modifica).pack(fill="x", pady=10)
        tk.Button(container, text="Indietro", font=("Arial", 10, "bold"), height=1, bg="#e0e0e0", command=self.schermata_principale).pack(fill="x", pady=2)

    def schermata_form_modifica(self, indice):
        self.pulisci_finestra()

        container = tk.Frame(self.root, padx=20, pady=10)
        container.pack(expand=True, fill="both")

        item = self.db["dati"][indice]

        tk.Label(container, text="Modifica Credenziali", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        tk.Label(container, text="Nuovo Sito o Servizio:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_sito = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_sito.insert(0, item['sito'])
        entry_sito.pack(fill="x", pady=(0, 8), ipady=4)

        tk.Label(container, text="Nuovo utente / Email:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_utente = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_utente.insert(0, item['utente'])
        entry_utente.pack(fill="x", pady=(0, 8), ipady=4)

        tk.Label(container, text="Nuova Password (lascia vuota per non cambiare):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(2, 2))
        entry_pass = tk.Entry(container, font=("Arial", 12), relief="solid", bd=1)
        entry_pass.insert(0, item['password'])
        entry_pass.pack(fill="x", pady=(0, 15), ipady=4)

        def salva_modifiche():
            item['sito'] = entry_sito.get().strip() or item['sito']
            item['utente'] = entry_utente.get().strip() or item['utente']
            nuova_p = entry_pass.get().strip()
            if nuova_p:
                item['password'] = nuova_p

            salva_database(self.db)
            messagebox.showinfo("Successo", "Modifiche salvate correttamente!")
            self.schermata_principale()

        tk.Button(container, text="Salva Modifiche", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", height=2, command=salva_modifiche).pack(fill="x", pady=10)
        tk.Button(container, text="Annulla", font=("Arial", 10, "bold"), height=1, bg="#e0e0e0", command=self.schermata_seleziona_modifica).pack(fill="x", pady=2)

    def schermata_elimina(self):
        self.pulisci_finestra()

        container = tk.Frame(self.root, padx=15, pady=15)
        container.pack(expand=True, fill="both")

        tk.Label(container, text="Elimina Password", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        self.db = carica_database()
        lista = self.db["dati"]

        if not lista:
            messagebox.showinfo("Info", "Nessuna password da eliminare.")
            self.schermata_principale()
            return

        tk.Label(container, text="Seleziona la voce da eliminare:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

        listbox = tk.Listbox(container, font=("Arial", 11))
        for i, item in enumerate(lista, 1):
            listbox.insert(tk.END, f"{i}. {item['sito']} ({item['utente']})")
        listbox.pack(fill="both", expand=True, pady=5)

        def conferma_eliminazione():
            selezione = listbox.curselection()
            if not selezione:
                messagebox.showerror("Errore", "Seleziona un elemento.")
                return
            
            indice = selezione[0]
            sito_rimosso = lista[indice]['sito']
            
            if messagebox.askyesno("Conferma", f"Eliminare '{sito_rimosso}'?"):
                lista.pop(indice)
                salva_database(self.db)
                messagebox.showinfo("Eliminato", "Rimosso con successo.")
                self.schermata_principale()

        tk.Button(container, text="Elimina Selezionato", font=("Arial", 11, "bold"), bg="#f44336", fg="white", height=2, command=conferma_eliminazione).pack(fill="x", pady=10)
        tk.Button(container, text="Indietro", font=("Arial", 10, "bold"), height=1, bg="#e0e0e0", command=self.schermata_principale).pack(fill="x", pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerMobile(root)
    root.mainloop()
