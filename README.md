# Money Map

Osobiste narzędzie do analizy wydatków: import wyciągów (Millennium, Revolut),
kategoryzacja (reguły + lokalna Ollama dla długiego ogona), wizualizacja
(Sankey i inne wykresy), docelowo insighty/optymalizacja per okres.

Architektura i decyzje projektowe (co zostaje z `ai-weekend-builds/vol-3/02-money-map`,
konkretne problemy w danych Millennium/Revolut, zero-cost AI layer) są opisane
w historii rozmowy, tu tylko stan aktualny kodu.

## Stack

- Backend: FastAPI + Celery (broker: Redis), zarządzane przez `uv`
- Baza danych: PostgreSQL, lokalny kontener, bez chmury
- Frontend: React + Vite + Tailwind v4 + shadcn/ui (ręcznie dopisane komponenty,
  `ui.shadcn.com` nie było dostępne z tego środowiska, więc `Button`/`Card`/`Select`
  są napisane ręcznie wg standardowego wzorca shadcn, warto je podmienić
  przez `npx shadcn@latest add ...` gdy masz pełny dostęp do sieci)
- AI: Ollama lokalnie (kategoryzacja długiego ogona), OpenRouter darmowy tier
  (miesięczne insighty), Gemini AI Studio jako zapasowa opcja

## Wymagania

- Docker Desktop (Windows, z backendem WSL2)
- [Ollama](https://ollama.com) zainstalowany natywnie na hoście, nie w Dockerze
- Node 22+ i uv, jeśli chcesz odpalać coś poza kontenerami lokalnie

## Pierwsze uruchomienie

```bash
# 1. Model do kategoryzacji (raz, ~4-5GB)
ollama pull qwen2.5:7b-instruct

# 2. Konfiguracja
cp .env.example .env
# uzupelnij OPENROUTER_API_KEY jesli chcesz miec insighty w chmurze

# 3. Cały stack
docker compose up --build
```

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173

## Struktura

```
money-map/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── pyproject.toml, uv.lock      # zależności przez uv
│   ├── Dockerfile
│   └── app/
│       ├── main.py                  # FastAPI, endpointy importu
│       ├── config.py                # ustawienia z .env
│       ├── db.py, models.py         # SQLAlchemy, tabela transactions
│       ├── celery_app.py, tasks.py  # import w tle + kategoryzacja
│       ├── categorize.py            # wywołanie Ollamy, wymuszony JSON schema
│       └── parsers/
│           ├── millennium.py        # coalesce Obciążenia/Uznania, cp1250
│           └── revolut.py           # filtr State=ZAKOŃCZONO
└── frontend/
    ├── src/App.tsx                  # placeholder dashboardu
    └── src/components/ui/           # button, card, select
```

## Stan obecny / czego brakuje

- [x] Scaffolding backendu i frontendu, docker-compose, parsery obu banków
- [ ] Alembic (na razie tabele przez `Base.metadata.create_all`, dodać przy
      pierwszej realnej zmianie schematu)
- [ ] Endpoint agregacji po okresie (miesiąc/kwartał/półrocze/rok)
- [ ] Sankey i pozostałe wykresy we froncie (`echarts-for-react`)
- [ ] Zadanie Celery do generowania insightów przez OpenRouter
- [ ] Testy na `sample-statement.csv` i na Twoich prawdziwych plikach
