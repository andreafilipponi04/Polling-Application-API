# 📊 Polling Application API

**Studente:** Andrea Filipponi  
**Project type:** REST API  
**Framework:** Django REST Framework  
**Repository:** [https://github.com/andreafilipponi04/Polling-Application-API](https://github.com/andreafilipponi04/Polling-Application-API)  
**Deployment:** [https://polling-application-api.onrender.com](https://polling-application-api.onrender.com)

## 📖 Descrizione

Questo progetto è una REST API per una **Polling Application** sviluppata con Django REST Framework.  
L’applicazione permette di creare sondaggi, aggiungere scelte, votare, visualizzare i risultati e gestire i sondaggi in base ai permessi dell’utente autenticato.

L’obiettivo del progetto è realizzare un back-end API-first con autenticazione JWT, validazione JSON, permessi coerenti e workflow di test riproducibile tramite comandi HTTP.

## 🖥️ Frontend Client

Per una gestione visiva dei sondaggi tramite interfaccia grafica, è disponibile un client frontend dedicato salvato in una repository separata.

👉 **[https://github.com/andreafilipponi04/Polling-Application-Frontend](https://github.com/andreafilipponi04/Polling-Application-Frontend)**

> ⚠️ **Nota:** Il frontend **non viene deployato online** ed è pensato esclusivamente per l'utilizzo in locale (aprendo il file `index.html` nel browser). Tutte le istruzioni specifiche per l'avvio e la configurazione del client sono disponibili nel `README.md` all'interno della sua repository.

## ✨ Funzionalità principali

- Visualizzazione pubblica della lista dei sondaggi.
- Visualizzazione pubblica del dettaglio di un sondaggio.
- Visualizzazione pubblica dei risultati di un sondaggio.
- Registrazione di nuovi utenti tramite endpoint API pubblico.
- Creazione di nuovi sondaggi da parte di utenti autenticati.
- Modifica ed eliminazione dei propri sondaggi.
- Voto autenticato su un sondaggio.
- Blocco del doppio voto sullo stesso sondaggio.
- Validazione che la scelta votata appartenga davvero al sondaggio selezionato.
- Creazione di nuove scelte per un sondaggio solo da parte del creatore del sondaggio.
- Endpoint per visualizzare i sondaggi già votati dall’utente autenticato.
- Supporto a filtri, ricerca, ordinamento e paginazione sulla lista dei sondaggi.

## 🔐 Ruoli e permessi

### Anonymous user
- Può leggere la lista dei sondaggi.
- Può leggere il dettaglio di un sondaggio.
- Può vedere i risultati.
- Può registrare un nuovo account.
- Può ottenere token JWT tramite credenziali valide.
- Non può creare sondaggi.
- Non può votare.
- Non può creare scelte.
- Non può modificare o eliminare sondaggi.

### Authenticated user
- Può creare un sondaggio.
- Può votare una sola volta per ciascun sondaggio.
- Può aggiungere scelte solo ai sondaggi creati da lui.
- Può modificare o eliminare solo i propri sondaggi.
- Può visualizzare i sondaggi che ha già votato.

### Admin / superuser
- Può gestire tutti i sondaggi tramite i permessi amministrativi del progetto.
- Può accedere al pannello admin Django.

## 🛠 Tecnologie usate

- Python 3.13
- Django
- Django REST Framework
- SimpleJWT
- django-filter
- SQLite

## 📁 Struttura del progetto

```text
Polling-Application-API/
├── config/
├── polls/
├── profiles/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

## 💾 Database demo

Il repository include il database SQLite:

- `db.sqlite3`

Il database contiene dati demo e account già pronti per testare l’applicazione senza dover creare tutto da zero.

Nel database demo sono presenti:
- 3 account demo principali
- 8 sondaggi classici pre-popolati
- 34 scelte associate ai sondaggi
- 21 voti già registrati
- 1 sondaggio chiuso, utile per testare la validazione sui voti

## 👥 Demo accounts

| Username | Password | Ruolo |
|---|---|---|
| admin | password | Admin / superuser |
| user1 | provaprova | Authenticated user |
| user2 | provaprova | Authenticated user |

## 🚀 Installazione locale

### 1. Clonare la repository

```bash
git clone https://github.com/andreafilipponi04/Polling-Application-API.git
cd Polling-Application-API
```

### 2. Creare e attivare l’ambiente

#### Opzione consigliata: Anaconda

Il progetto usa Django 6, quindi è consigliato usare Python 3.13.

```bash
conda create --name django python=3.13
conda activate django
```

#### Opzione alternativa: venv

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Installare le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Applicare le migrazioni

```bash
python manage.py migrate
```

### 5. Avviare il server

```bash
python manage.py runserver
```

### 6. Base URL locale

```text
http://127.0.0.1:8000/
```

## 📝 Registrazione utenti

L’API espone un endpoint pubblico per la registrazione di nuovi utenti.

### Creare un nuovo account

**POST** `/api/register/`

Body JSON:

```json
{
  "username": "newuser",
  "password": "Password123!",
  "password2": "Password123!"
}
```

Esempio HTTPie:

```bash
http POST http://127.0.0.1:8000/api/register/ username="newuser" password="Password123!" password2="Password123!"
```

Risposta attesa:
- `201 Created`

Dopo la registrazione, l’utente può ottenere i token JWT tramite `/api/token/`.

## 🔑 Autenticazione JWT

L’API usa autenticazione JWT per gli endpoint protetti.

### Ottenere access e refresh token

**POST** `/api/token/`

Body JSON:

```json
{
  "username": "newuser",
  "password": "Password123!"
}
```

Esempio risposta:

```json
{
  "refresh": "REFRESH_TOKEN",
  "access": "ACCESS_TOKEN"
}
```

### Ottenere un nuovo access token

**POST** `/api/token/refresh/`

Body JSON:

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

Esempio risposta:

```json
{
  "access": "NEW_ACCESS_TOKEN"
}
```

### Verificare un token

**POST** `/api/token/verify/`

Body JSON:

```json
{
  "token": "ACCESS_TOKEN"
}
```

### Uso del token nelle richieste protette

Header:

```text
Authorization: Bearer ACCESS_TOKEN
```

## 🛣️ Endpoint principali

| Metodo | Endpoint | Auth | Ruolo | Descrizione |
|---|---|---|---|---|
| POST | `/api/register/` | No | Anonymous / Authenticated | Registra un nuovo utente |
| GET | `/api/polls/` | No | Anonymous / Authenticated | Lista dei sondaggi con paginazione, filtri, ricerca e ordinamento |
| POST | `/api/polls/` | Sì | Authenticated | Crea un nuovo sondaggio |
| GET | `/api/polls/<id>/` | No | Anonymous / Authenticated | Dettaglio di un sondaggio |
| PUT | `/api/polls/<id>/` | Sì | Owner / Admin | Aggiorna completamente un sondaggio |
| PATCH | `/api/polls/<id>/` | Sì | Owner / Admin | Aggiorna parzialmente un sondaggio |
| DELETE | `/api/polls/<id>/` | Sì | Owner / Admin | Elimina un sondaggio |
| GET | `/api/polls/<id>/results/` | No | Anonymous / Authenticated | Mostra risultati e percentuali |
| GET | `/api/polls/voted/` | Sì | Authenticated | Mostra i sondaggi già votati dall’utente |
| GET | `/api/profiles/me/` | Sì | Authenticated | Mostra profilo e ruolo dell’utente autenticato |
| POST | `/api/votes/` | Sì | Authenticated | Registra un voto |
| POST | `/api/choices/` | Sì | Authenticated | Aggiunge una scelta a un proprio sondaggio |
| POST | `/api/token/` | No | Anonymous / Authenticated | Ottiene access e refresh token |
| POST | `/api/token/refresh/` | No | Anonymous / Authenticated | Rinnova l’access token |
| POST | `/api/token/verify/` | No | Anonymous / Authenticated | Verifica la validità di un token |

## 🔍 Endpoint dettagliati

Negli esempi seguenti, sostituire `POLL_ID`, `CHOICE_ID` e `OTHER_CHOICE_ID` con ID numerici reali restituiti dall’API.

### 1. Register user

**POST** `/api/register/`

Accesso pubblico.

Body JSON di esempio:

```json
{
  "username": "newuser",
  "password": "Password123!",
  "password2": "Password123!"
}
```

Esempio HTTPie:

```bash
http POST http://127.0.0.1:8000/api/register/ username="newuser" password="Password123!" password2="Password123!"
```

Risposte attese:
- `201 Created`
- `400 Bad Request` se username già esistente
- `400 Bad Request` se le password non coincidono
- `400 Bad Request` se la password non supera i validator Django

### 2. List polls

**GET** `/api/polls/`

Accesso pubblico.

Possibili query params:

- `question=testo`
- `is_active=true` o `is_active=false`
- `created_by=username`
- `search=testo`
- `ordering=created_at`
- `ordering=-created_at`
- `ordering=updated_at`
- `ordering=-updated_at`
- `page=1`
- `page_size=5`

Esempio:

```bash
http GET http://127.0.0.1:8000/api/polls/
```

### 3. Create poll

**POST** `/api/polls/`

Richiede autenticazione JWT.

Body JSON di esempio:

```json
{
  "question": "Qual è il tuo linguaggio preferito?",
  "is_active": true
}
```

Esempio HTTPie:

```bash
http POST http://127.0.0.1:8000/api/polls/ Authorization:"Bearer ACCESS_TOKEN" question="Qual è il tuo linguaggio preferito?" is_active:=true
```

Risposta attesa:
- `201 Created`

### 4. Poll detail

**GET** `/api/polls/<id>/`

Accesso pubblico.

Esempio:

```bash
http GET http://127.0.0.1:8000/api/polls/POLL_ID/
```

### 5. Update poll

**PATCH** `/api/polls/<id>/`

Richiede autenticazione JWT.  
Consentito solo al creatore del sondaggio o all’admin.

Body JSON di esempio:

```json
{
  "question": "Domanda aggiornata"
}
```

Esempio:

```bash
http PATCH http://127.0.0.1:8000/api/polls/POLL_ID/ Authorization:"Bearer ACCESS_TOKEN" question="Domanda aggiornata"
```

Risposte attese:
- `200 OK` se l’utente è autorizzato
- `403 Forbidden` se l’utente autenticato non è proprietario
- `401 Unauthorized` se manca autenticazione

### 6. Delete poll

**DELETE** `/api/polls/<id>/`

Richiede autenticazione JWT.  
Consentito solo al creatore del sondaggio o all’admin.

Esempio:

```bash
http DELETE http://127.0.0.1:8000/api/polls/POLL_ID/ Authorization:"Bearer ACCESS_TOKEN"
```

Risposte attese:
- `204 No Content`
- `403 Forbidden`
- `401 Unauthorized`

### 7. Poll results

**GET** `/api/polls/<id>/results/`

Accesso pubblico.

Esempio risposta:

```json
{
  "poll_id": 1,
  "question": "Qual è il tuo linguaggio preferito?",
  "total_votes": 3,
  "choices": [
    {
      "id": 1,
      "text": "Python",
      "votes_count": 2,
      "percentage": "66.67"
    },
    {
      "id": 2,
      "text": "JavaScript",
      "votes_count": 1,
      "percentage": "33.33"
    }
  ]
}
```

Esempio HTTPie:

```bash
http GET http://127.0.0.1:8000/api/polls/POLL_ID/results/
```

### 8. Voted polls

**GET** `/api/polls/voted/`

Richiede autenticazione JWT.

Mostra l’elenco dei sondaggi a cui l’utente autenticato ha già votato.

Esempio:

```bash
http GET http://127.0.0.1:8000/api/polls/voted/ Authorization:"Bearer ACCESS_TOKEN"
```

### 9. Create vote

**POST** `/api/votes/`

Richiede autenticazione JWT.

Body JSON di esempio:

```json
{
  "poll": 1,
  "choice": 2
}
```

Esempio HTTPie:

```bash
http POST http://127.0.0.1:8000/api/votes/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID choice:=CHOICE_ID
```

Validazioni:
- un utente non può votare due volte nello stesso sondaggio
- la choice deve appartenere al poll selezionato

Possibili risposte:
- `201 Created`
- `400 Bad Request` se il voto è duplicato
- `400 Bad Request` se la choice non appartiene al poll
- `401 Unauthorized` se non autenticato

### 10. Create choice

**POST** `/api/choices/`

Richiede autenticazione JWT.  
Consentito solo al creatore del sondaggio.

Body JSON di esempio:

```json
{
  "poll": 1,
  "text": "Nuova scelta"
}
```

Esempio HTTPie:

```bash
http POST http://127.0.0.1:8000/api/choices/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID text="Nuova scelta"
```

Possibili risposte:
- `201 Created`
- `403 Forbidden` se il sondaggio non appartiene all’utente
- `401 Unauthorized` se non autenticato

### 11. My profile

**GET** `/api/profiles/me/`

Richiede autenticazione JWT.

Mostra i dati essenziali del profilo dell’utente autenticato, incluso il ruolo.

Esempio risposta:

```json
{
  "id": 1,
  "username": "user1",
  "role": "user"
}
```

Esempio HTTPie:

```bash
http GET http://127.0.0.1:8000/api/profiles/me/ Authorization:"Bearer ACCESS_TOKEN"
```

Possibili risposte:
- `200 OK`
- `401 Unauthorized` se non autenticato

## 🧪 Workflow completo di test con HTTPie

> Installazione HTTPie: [https://httpie.io/](https://httpie.io/).

> **Nota:** tutti gli esempi HTTPie presenti in questo README sono scritti per il test in locale usando `http://127.0.0.1:8000/`.
> Per testare l’API online, è sufficiente sostituire l’URL locale con quello deployato: `https://polling-application-api.onrender.com/`.

Nei comandi che usano `POLL_ID` e `CHOICE_ID`, sostituire questi valori con gli ID numerici restituiti dalle risposte dell’API.

### 1. Registrare un nuovo utente

```bash
http POST http://127.0.0.1:8000/api/register/ username="newuser" password="Password123!" password2="Password123!"
```

### 2. Ottenere i token

```bash
http POST http://127.0.0.1:8000/api/token/ username=newuser password="Password123!"
```

Copiare il valore di `access` e salvarlo come `ACCESS_TOKEN`.

### 3. Verificare il profilo dell’utente autenticato

```bash
http GET http://127.0.0.1:8000/api/profiles/me/ Authorization:"Bearer ACCESS_TOKEN"
```

### 4. Leggere i sondaggi pubblici

```bash
http GET http://127.0.0.1:8000/api/polls/
```

### 5. Creare un nuovo sondaggio

```bash
http POST http://127.0.0.1:8000/api/polls/ Authorization:"Bearer ACCESS_TOKEN" question="Sondaggio demo" is_active:=true
```

Annotare il valore `id` restituito nella risposta e usarlo come `POLL_ID`.

### 6. Aggiungere una scelta al sondaggio

```bash
http POST http://127.0.0.1:8000/api/choices/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID text="Opzione A"
```

```bash
http POST http://127.0.0.1:8000/api/choices/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID text="Opzione B"
```

Annotare l’`id` di una delle scelte create e usarlo come `CHOICE_ID`.

### 7. Votare

```bash
http POST http://127.0.0.1:8000/api/votes/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID choice:=CHOICE_ID
```

### 8. Vedere i risultati

```bash
http GET http://127.0.0.1:8000/api/polls/POLL_ID/results/
```

### 9. Vedere i sondaggi già votati

```bash
http GET http://127.0.0.1:8000/api/polls/voted/ Authorization:"Bearer ACCESS_TOKEN"
```

### 10. Aggiornare il proprio sondaggio

```bash
http PATCH http://127.0.0.1:8000/api/polls/POLL_ID/ Authorization:"Bearer ACCESS_TOKEN" question="Sondaggio demo aggiornato"
```

### 11. Eliminare il proprio sondaggio

```bash
http DELETE http://127.0.0.1:8000/api/polls/POLL_ID/ Authorization:"Bearer ACCESS_TOKEN"
```

## 📋 Scenario di test della registrazione

### Caso 1: registrazione corretta

```bash
http POST http://127.0.0.1:8000/api/register/ username="utenteprova" password="Password123!" password2="Password123!"
```

Risposta attesa:
- `201 Created`

### Caso 2: password non coincidenti

```bash
http POST http://127.0.0.1:8000/api/register/ username="utenteerrore" password="Password123!" password2="Password456!"
```

Risposta attesa:
- `400 Bad Request`

### Caso 3: username già esistente

```bash
http POST http://127.0.0.1:8000/api/register/ username="user1" password="Password123!" password2="Password123!"
```

Risposta attesa:
- `400 Bad Request`

### Caso 4: ottenere JWT dopo registrazione

```bash
http POST http://127.0.0.1:8000/api/token/ username="utenteprova" password="Password123!"
```

Risposta attesa:
- `200 OK`
- risposta JSON con `refresh` e `access`

## 🛡️ Scenario di test dei permessi

### Caso 1: utente anonimo non può votare

```bash
http POST http://127.0.0.1:8000/api/votes/ poll:=POLL_ID choice:=CHOICE_ID
```

Risposta attesa:
- `401 Unauthorized`

### Caso 2: un utente non può modificare il sondaggio di un altro utente

Login come `user1` e creare un sondaggio.  
Poi login come `user2` e provare a modificarlo:

```bash
http POST http://127.0.0.1:8000/api/token/ username=user2 password=provaprova
```

```bash
http PATCH http://127.0.0.1:8000/api/polls/POLL_ID/ Authorization:"Bearer USER2_ACCESS_TOKEN" question="Tentativo non autorizzato"
```

Risposta attesa:
- `403 Forbidden`

### Caso 3: doppio voto vietato

Dopo aver già votato una volta:

```bash
http POST http://127.0.0.1:8000/api/votes/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID choice:=CHOICE_ID
```

Risposta attesa:
- `400 Bad Request`

### Caso 4: scelta non appartenente al sondaggio

```bash
http POST http://127.0.0.1:8000/api/votes/ Authorization:"Bearer ACCESS_TOKEN" poll:=POLL_ID choice:=OTHER_CHOICE_ID
```

Risposta attesa:
- `400 Bad Request`

> `OTHER_CHOICE_ID` deve essere l’id di una scelta reale appartenente a un altro sondaggio.

## 🎛️ Filtri, ricerca, ordinamento e paginazione

La lista dei sondaggi supporta:
- filtri definiti in `PollFilter`
- ricerca testuale su `question` e sul testo delle `choices`
- ordinamento per `created_at`
- ordinamento per `updated_at`
- paginazione personalizzata tramite `PollPagination`

Esempi:

```bash
http GET "http://127.0.0.1:8000/api/polls/?question=python"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?is_active=true"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?created_by=user1"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?search=python"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?ordering=-created_at"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?ordering=updated_at"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?page=1"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?page=2&page_size=10"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?is_active=true&search=pizza&ordering=-created_at"
```

## 🚦 Status code principali

| Codice | Significato |
|---|---|
| 200 | Richiesta completata con successo |
| 201 | Risorsa creata correttamente |
| 204 | Risorsa eliminata correttamente |
| 400 | Dati non validi |
| 401 | Utente non autenticato |
| 403 | Utente autenticato ma non autorizzato |
| 404 | Risorsa non trovata |
