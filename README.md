# FraudWatch — Dashboard de Prevenção a Fraudes em Assistência Veicular

Sistema de monitoramento de casos suspeitos com score de risco automático, block list, exportação e dashboard visual.

## Pré-requisitos

- Python 3.11+
- PostgreSQL 14+ (rodando localmente)

## Instalação

```bash
# 1. Clone e entre na pasta
cd fraudwatch/backend

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o banco de dados
cp .env.example .env
# Edite .env com suas credenciais do PostgreSQL
```

## Configuração do `.env`

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/fraudwatch
```

Crie o banco antes de iniciar:
```sql
CREATE DATABASE fraudwatch;
```

## Populando o banco (seed)

```bash
python seed.py
```

Isso insere **5 clientes** na block list e **30 casos suspeitos** com fatores e histórico associados.

## Iniciando o servidor

```bash
uvicorn main:app --reload --port 8000
```

A API ficará disponível em `http://localhost:8000`.  
Documentação Swagger: `http://localhost:8000/docs`

## Abrindo o front-end

Abra o arquivo diretamente no navegador:
```
fraudwatch/frontend/fraud_dashboard.html
```

Ou sirva com qualquer servidor estático. O front-end consome a API em `http://localhost:8000`.

---

## Exemplos de requisições (curl)

### Listar todos os casos
```bash
curl http://localhost:8000/api/cases
```

### Listar casos do mês atual
```bash
curl "http://localhost:8000/api/cases?filter=month"
```

### Criar um novo caso
```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva Santos",
    "suspicion": "Transporte aéreo + reincidência",
    "hours": 16.5,
    "transport": "air",
    "value": 2400.00,
    "status": "open",
    "date": "2026-06-01",
    "justification": "Segunda passagem aérea no semestre.",
    "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 0, "data": 0},
    "history": [{"d": "2026-02-10", "t": "Aéreo · R$ 2.100"}]
  }'
```

### Atualizar status de um caso
```bash
curl -X PATCH http://localhost:8000/api/cases/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "denied"}'
```

### Adicionar suspeito à block list
```bash
curl -X POST http://localhost:8000/api/blocklist \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Aparecida Lima",
    "dob": "1982-05-14",
    "reasons": ["Fraude confirmada por perícia", "Reincidência em 3 anos consecutivos"]
  }'
```

### Exportar casos em CSV
```bash
curl http://localhost:8000/api/export/cases/csv -o casos.csv
```

### KPIs do dashboard
```bash
curl "http://localhost:8000/api/dashboard/kpis?filter=all"
```

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/cases` | Lista casos (`?filter=all\|week\|month`) |
| GET | `/api/cases/{id}` | Detalhes de um caso |
| POST | `/api/cases` | Cria novo caso (score calculado automaticamente) |
| PUT | `/api/cases/{id}` | Atualiza um caso |
| PATCH | `/api/cases/{id}/status` | Atualiza apenas o status |
| DELETE | `/api/cases/{id}` | Remove um caso |
| GET | `/api/blocklist` | Lista block list |
| GET | `/api/blocklist/{id}` | Detalhe de suspeito |
| POST | `/api/blocklist` | Adiciona suspeito |
| PUT | `/api/blocklist/{id}` | Atualiza suspeito |
| DELETE | `/api/blocklist/{id}` | Remove suspeito |
| GET | `/api/export/cases/csv` | Exporta casos em CSV |
| GET | `/api/export/cases/json` | Exporta casos em JSON |
| GET | `/api/export/blocklist/csv` | Exporta block list em CSV |
| GET | `/api/export/blocklist/json` | Exporta block list em JSON |
| GET | `/api/dashboard/kpis` | KPIs agregados (`?filter=all\|week\|month`) |
| GET | `/api/dashboard/charts` | Dados para os 4 gráficos |

## Cálculo do Score

| Fator | Peso máximo | Condição |
|-------|-------------|----------|
| Block list | 45 pts | Cliente consta na block list |
| Reincidência | 25 pts | Número de acionamentos anteriores |
| Transporte | 20 pts | Aéreo=20, Rodoviário=10, Táxi=0 |
| Data | 10 pts | Data próxima a feriado nacional |

- 0–25 → Risco **BAIXO**
- 26–55 → Risco **MÉDIO**
- 56–100 → Risco **ALTO**
