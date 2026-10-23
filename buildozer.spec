[app]
# Titolo dell'applicazione
title = Password Manager

# Nome del pacchetto (senza spazi)
package.name = passwordmanager

# Dominio del pacchetto
package.domain = org.gestore

# File sorgenti inclusi (assicurati che il tuo script si chiami main.py)
source.include_exts = py,png,jpg,kv,atlas,json

# Punto di ingresso dell'app
source.dir = .

# Requisiti dell'app (Python e librerie necessarie)
requirements = python3,kivy

# Versione dell'app
version = 1.0

# Orientamento dello schermo (portrait = verticale)
orientation = portrait

# Permessi Android (es. scrittura su file per il database JSON)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
# Livello di log
log_level = 2
