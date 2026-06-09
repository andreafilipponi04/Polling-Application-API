# POLLING APPLICATION API

**Studente:** Andrea Filipponi  
**Project type:** REST API  
**Framework:** Django + Django REST Framework  
**Repository:** https://github.com/andreafilipponi04/Polling-Application-API  
**Deployment:** [DEPLOYMENT_URL]

## Descrizione

Questo progetto è una REST API per una **Polling Application** sviluppata con Django REST Framework.  
L’applicazione permette di creare sondaggi, aggiungere scelte, votare, visualizzare i risultati e gestire i sondaggi in base ai permessi dell’utente autenticato.

L’obiettivo del progetto è realizzare un back-end API-first con autenticazione JWT, validazione JSON, permessi coerenti e workflow di test riproducibile tramite comandi HTTP.

## Funzionalità principali

- Visualizzazione pubblica della lista dei sondaggi.
- Visualizzazione pubblica del dettaglio di un sondaggio.
- Visualizzazione pubblica dei risultati di un sondaggio.
- Creazione di nuovi sondaggi da parte di utenti autenticati.
- Modifica ed eliminazione dei propri sondaggi.
- Voto autenticato su un sondaggio.
- Blocco del doppio voto sullo stesso sondaggio.
- Validazione che la scelta votata appartenga davvero al sondaggio selezionato.
- Creazione di nuove scelte per un sondaggio solo da parte del creatore del sondaggio.
- Supporto a filtri, ricerca, ordinamento e paginazione sulla lista dei sondaggi.

## Ruoli e permessi

### Anonymous user
- Può leggere la lista dei sondaggi.
- Può leggere il dettaglio di un sondaggio.
- Può vedere i risultati.
- Non può creare sondaggi.
- Non può votare.
- Non può creare scelte.
- Non può modificare o eliminare sondaggi.

### Authenticated user
- Può creare un sondaggio.
- Può votare una sola volta per ciascun sondaggio.
- Può aggiungere scelte solo ai sondaggi creati da lui.
- Può modificare o eliminare solo i propri sondaggi.

### Admin / superuser
- Può gestire tutti i sondaggi tramite i permessi amministrativi del progetto.
- Può accedere al pannello admin Django.

## Tecnologie usate

- Python
- Django
- Django REST Framework
- SimpleJWT
- django-filter
- SQLite

## Struttura del progetto

```text
[PROJECT_TITLE]/
├── config/
├── polls/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

## Database demo

Il repository include il database SQLite:

- `db.sqlite3`

Il database contiene dati demo e account già pronti per testare l’applicazione senza dover creare tutto da zero.

## Demo accounts

| Username | Password | Ruolo |
|---|---|---|
| admin | password | Admin / superuser |
| user1 | provaprova | Authenticated user |
| user2 | provaprova | Authenticated user |

## Installazione locale

### 1. Clonare la repository

```bash
git clone https://github.com/andreafilipponi04/Polling-Application-API
cd [PROJECT_TITLE]
```

### 2. Creare e attivare l’ambiente

#### Opzione consigliata: Anaconda

```bash
conda create --name django python=3.10
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

## Autenticazione JWT

L’API usa autenticazione JWT per gli endpoint protetti.

### Ottenere access e refresh token

**POST** `/api/token/`

Body JSON:

```json
{
  "username": "user1",
  "password": "provaprova"
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

### Uso del token nelle richieste protette

Header:

```text
Authorization: Bearer ACCESS_TOKEN
```

## Endpoint principali

| Metodo | Endpoint | Auth | Ruolo | Descrizione |
|---|---|---|---|---|
| GET | `/api/polls/` | No | Anonymous / Authenticated | Lista dei sondaggi con paginazione, filtri, ricerca e ordinamento |
| POST | `/api/polls/` | Sì | Authenticated | Crea un nuovo sondaggio |
| GET | `/api/polls/<id>/` | No | Anonymous / Authenticated | Dettaglio di un sondaggio |
| PUT | `/api/polls/<id>/` | Sì | Owner / Admin | Aggiorna completamente un sondaggio |
| PATCH | `/api/polls/<id>/` | Sì | Owner / Admin | Aggiorna parzialmente un sondaggio |
| DELETE | `/api/polls/<id>/` | Sì | Owner / Admin | Elimina un sondaggio |
| GET | `/api/polls/<id>/results/` | No | Anonymous / Authenticated | Mostra risultati e percentuali |
| POST | `/api/votes/` | Sì | Authenticated | Registra un voto |
| POST | `/api/choices/` | Sì | Authenticated | Aggiunge una scelta a un proprio sondaggio |
| POST | `/api/token/` | No | Anonymous / Authenticated | Ottiene access e refresh token |
| POST | `/api/token/refresh/` | No | Anonymous / Authenticated | Rinnova l’access token |

## Endpoint dettagliati

### 1. List polls

**GET** `/api/polls/`

Accesso pubblico.

Possibili query params:

- `is_active=true` o `is_active=false`
- `question=testo`
- `created_by=username`
- `search=testo`
- `ordering=created_at`
- `ordering=-created_at`
- `ordering=updated_at`
- `ordering=-updated_at`
- `page=1`
- `page_size=10`

Esempio:

```bash
http GET http://127.0.0.1:8000/api/polls/
```

### 2. Create poll

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
http POST http://127.0.0.1:8000/api/polls/ \
Authorization:"Bearer ACCESS_TOKEN" \
question="Qual è il tuo linguaggio preferito?" \
is_active:=true
```

Risposta attesa:
- `201 Created`

### 3. Poll detail

**GET** `/api/polls/<id>/`

Accesso pubblico.

Esempio:

```bash
http GET http://127.0.0.1:8000/api/polls/1/
```

### 4. Update poll

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
http PATCH http://127.0.0.1:8000/api/polls/1/ \
Authorization:"Bearer ACCESS_TOKEN" \
question="Domanda aggiornata"
```

Risposte attese:
- `200 OK` se l’utente è autorizzato
- `403 Forbidden` se l’utente autenticato non è proprietario
- `401 Unauthorized` se manca autenticazione

### 5. Delete poll

**DELETE** `/api/polls/<id>/`

Richiede autenticazione JWT.  
Consentito solo al creatore del sondaggio o all’admin.

Esempio:

```bash
http DELETE http://127.0.0.1:8000/api/polls/1/ \
Authorization:"Bearer ACCESS_TOKEN"
```

Risposte attese:
- `204 No Content`
- `403 Forbidden`
- `401 Unauthorized`

### 6. Poll results

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
http GET http://127.0.0.1:8000/api/polls/1/results/
```

### 7. Create vote

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
http POST http://127.0.0.1:8000/api/votes/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
choice:=2
```

Validazioni:
- un utente non può votare due volte nello stesso sondaggio
- la choice deve appartenere al poll selezionato

Possibili risposte:
- `201 Created`
- `400 Bad Request` se il voto è duplicato
- `400 Bad Request` se la choice non appartiene al poll
- `401 Unauthorized` se non autenticato

Esempio errore doppio voto:

```json
{
  "non_field_errors": [
    "Hai già votato in questo sondaggio."
  ]
}
```

Esempio errore choice non valida:

```json
{
  "choice": [
    "La scelta selezionata non appartiene a questo sondaggio."
  ]
}
```

### 8. Create choice

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
http POST http://127.0.0.1:8000/api/choices/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
text="Nuova scelta"
```

Possibili risposte:
- `201 Created`
- `403 Forbidden` se il sondaggio non appartiene all’utente
- `401 Unauthorized` se non autenticato

Messaggio previsto in caso di permesso negato:

```json
{
  "detail": "Puoi aggiungere scelte solo ai sondaggi che hai creato tu."
}
```

## Serializer e rappresentazione JSON

### Poll
Campi principali restituiti dal serializer:
- `id`
- `question`
- `created_by`
- `created_at`
- `updated_at`
- `is_active`
- `choices` (nested, read-only)

### Choice
Campi:
- `id`
- `poll`
- `text`

### Vote
Campi:
- `id`
- `poll`
- `choice`
- `user`
- `voted_at`

## Workflow completo di test con HTTPie

> Installazione HTTPie: [https://httpie.io/](https://httpie.io/).

### 1. Ottenere i token

```bash
http POST http://127.0.0.1:8000/api/token/ username=user1 password=provaprova
```

Copiare il valore di `access` e salvarlo come `ACCESS_TOKEN`.

### 2. Leggere i sondaggi pubblici

```bash
http GET http://127.0.0.1:8000/api/polls/
```

### 3. Creare un nuovo sondaggio

```bash
http POST http://127.0.0.1:8000/api/polls/ \
Authorization:"Bearer ACCESS_TOKEN" \
question="Sondaggio demo" \
is_active:=true
```

### 4. Aggiungere una scelta al sondaggio

```bash
http POST http://127.0.0.1:8000/api/choices/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
text="Opzione A"
```

```bash
http POST http://127.0.0.1:8000/api/choices/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
text="Opzione B"
```

### 5. Votare

```bash
http POST http://127.0.0.1:8000/api/votes/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
choice:=1
```

### 6. Vedere i risultati

```bash
http GET http://127.0.0.1:8000/api/polls/1/results/
```

### 7. Aggiornare il proprio sondaggio

```bash
http PATCH http://127.0.0.1:8000/api/polls/1/ \
Authorization:"Bearer ACCESS_TOKEN" \
question="Sondaggio demo aggiornato"
```

### 8. Eliminare il proprio sondaggio

```bash
http DELETE http://127.0.0.1:8000/api/polls/1/ \
Authorization:"Bearer ACCESS_TOKEN"
```

## Scenario di test dei permessi

### Caso 1: utente anonimo non può votare

```bash
http POST http://127.0.0.1:8000/api/votes/ poll:=1 choice:=1
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
http PATCH http://127.0.0.1:8000/api/polls/1/ \
Authorization:"Bearer USER2_ACCESS_TOKEN" \
question="Tentativo non autorizzato"
```

Risposta attesa:
- `403 Forbidden`

### Caso 3: doppio voto vietato

Dopo aver già votato una volta:

```bash
http POST http://127.0.0.1:8000/api/votes/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
choice:=1
```

Risposta attesa:
- `400 Bad Request`

### Caso 4: scelta non appartenente al sondaggio

```bash
http POST http://127.0.0.1:8000/api/votes/ \
Authorization:"Bearer ACCESS_TOKEN" \
poll:=1 \
choice:=999
```

Risposta attesa:
- `400 Bad Request`

> Sostituire `999` con una `choice` reale appartenente a un altro sondaggio per testare correttamente questa validazione.

## Filtri, ordinamento e paginazione

La lista dei sondaggi supporta:
- paginazione personalizzata tramite `PollPagination`
- ordinamento per `created_at`
- ordinamento per `updated_at`
- filtri definiti in `PollFilter`
- ricerca testuale su `question` e sul testo delle `choices`

Esempi:

```bash
http GET "http://127.0.0.1:8000/api/polls/?ordering=-created_at"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?page=1"
```

```bash
http GET "http://127.0.0.1:8000/api/polls/?is_active=true&search=pizza"
```

## Status code principali

| Codice | Significato |
|---|---|
| 200 | Richiesta completata con successo |
| 201 | Risorsa creata correttamente |
| 204 | Risorsa eliminata correttamente |
| 400 | Dati non validi |
| 401 | Utente non autenticato |
| 403 | Utente autenticato ma non autorizzato |
| 404 | Risorsa non trovata |

## Placeholder da completare

Sostituire questi valori prima della consegna finale:

- `[PROJECT_TITLE]`
- `[DEPLOYMENT_URL]`
