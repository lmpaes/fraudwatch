# FraudWatch — Dashboard de Prevenção a Fraudes em Assistência Veicular

Sistema de monitoramento de casos suspeitos com score de risco automático, block list, exportação e dashboard visual.

## Pré-requisitos

- Docker e Docker Compose

## Subindo a aplicação

A aplicação é orquestrada via `docker-compose.yml`, que sobe três serviços:

| Serviço | Descrição |
|---------|-----------|
| `db` | PostgreSQL 16, com dados persistidos no volume `pgdata` |
| `app` | API FastAPI (build a partir de `backend/Dockerfile`), exposta em `localhost:8000` |
| `seed` | Job que popula o banco (5 clientes na block list e 30 casos suspeitos com fatores e histórico) e encerra |

```bash
# 1. Clone e entre na pasta
cd fraudwatch

# 2. Suba os serviços (db, app e seed)
docker compose up -d --build
```

A API ficará disponível em `http://localhost:8000`.
Documentação Swagger: `http://localhost:8000/docs`

> As datas dos casos do seed são geradas **relativas à data de execução** (o caso mais
> recente sempre cai em "hoje", preservando o espaçamento entre os demais). Isso garante
> que os filtros "Semana atual" e "Mês atual" sempre retornem dados, não importa quando
> o seed for rodado.

### Repovoando o banco

O serviço `seed` roda uma única vez na subida (`restart: "no"`). Para rodá-lo novamente
(por exemplo, para "renovar" as datas dos casos para a data atual):

```bash
docker compose run --rm seed
```

### Encerrando

```bash
docker compose down        # mantém os dados (volume pgdata)
docker compose down -v     # remove também o volume — apaga todos os dados
```

## Abrindo o front-end

Abra o arquivo diretamente no navegador:
```
fraudwatch/frontend/fraud_dashboard.html
```

Ou sirva com qualquer servidor estático. O front-end consome a API em `http://localhost:8000`.

---

## Rodando sem Docker (modo manual)

Pré-requisitos: Python 3.11+ e PostgreSQL 14+ rodando localmente.

```bash
cd fraudwatch/backend

# Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
cp .env.example .env
# Edite .env com suas credenciais do PostgreSQL
```

Crie o banco antes de iniciar:
```sql
CREATE DATABASE fraudwatch;
```

Popule o banco:
```bash
python seed.py
```

Inicie o servidor:
```bash
uvicorn main:app --reload --port 8000
```

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
    "transport_override_reason": null,
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

### Gráficos do dashboard (também respeitam o filtro de período)
```bash
curl "http://localhost:8000/api/dashboard/charts?filter=week"
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
| GET | `/api/dashboard/charts` | Dados para os 4 gráficos (`?filter=all\|week\|month`) |

## Cálculo do Score

| Fator | Peso máximo | Condição |
|-------|-------------|----------|
| Block list | 45 pts | Cliente consta na block list |
| Reincidência | 25 pts | Soma dos motivos de suspeita comportamentais selecionados |
| Transporte | 20 pts | Aéreo=20, Rodoviário=10, Táxi=0 |
| Data | 10 pts | Data próxima a feriado nacional ou sinistro em data estratégica |

- 0–25 → Risco **BAIXO**
- 26–55 → Risco **MÉDIO**
- 56–100 → Risco **ALTO**

### Fatores de risco no formulário de novo caso

Em vez de informar pontuações numéricas diretamente, o operador seleciona os motivos de
suspeita observados; cada seleção soma pontos ao fator correspondente (respeitando os
tetos de 25 e 10 acima):

| Motivo de suspeita | Fator | Pontos |
|---|---|---|
| Pane proposital para acionar o benefício de retorno (longe de casa) | Reincidência | +15 |
| Guincho usado para transportar objetos pesados (mudança gratuita) | Reincidência | +10 |
| Aciona o serviço apenas para conseguir passagem aérea | Reincidência | +10 |
| Reincidência: várias vezes por ano sempre acima de 400 km | Reincidência | +25 |
| Sinistro em data estratégica (véspera de feriado / feriadão) | Data suspeita | +10 |

### Definição automática do meio de transporte

Com base no tempo de viagem informado, o sistema sugere automaticamente o transporte:

- até 8h → Táxi
- 8h a 15h → Rodoviário
- acima de 15h → Aéreo

Essa sugestão pode ser sobrescrita marcando "Alterar transporte manualmente", desde que
seja informado o motivo da alteração (registrado junto ao caso).

### Valor envolvido para casos de Táxi

Quando o transporte é Táxi, o valor envolvido é calculado automaticamente a partir do
tempo de viagem, considerando 80 km percorridos por hora a R$ 1,60/km:

```
valor = horas × 80 × 1,60
```

Exemplo: viagem de 8h → 8 × 80 = 640 km → 640 × 1,60 = R$ 1.024,00
