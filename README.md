# FraudWatch — Dashboard de Prevenção a Fraudes em Assistência Veicular

Sistema de monitoramento de casos suspeitos com score de risco automático, block list, exportação e dashboard visual.

---

> **Aviso — Projeto de portfólio**
>
> As regras de negócio implementadas neste projeto (critérios de suspeita, score de risco, block list, meios de transporte e fatores de valor) são **fictícias** e foram criadas especificamente para fins de demonstração técnica, inspiradas em conceitos genéricos e públicos do setor de assistência veicular.
>
> Todos os nomes, datas de nascimento e dados pessoais exibidos no dashboard são **inteiramente fictícios**, gerados artificialmente para popular o ambiente de demonstração. Nenhuma informação real de clientes, apólices ou sinistros foi utilizada.

---

## Pré-requisitos

- Docker e Docker Compose

---

## Subindo a aplicação

A aplicação é orquestrada via `docker-compose.yml`, que sobe três serviços:

| Serviço | Descrição |
|---------|-----------|
| `db` | PostgreSQL 16, com dados persistidos no volume `pgdata` |
| `app` | API FastAPI (build a partir de `backend/Dockerfile`), exposta em `localhost:8000` |
| `seed` | Job que popula o banco (15 clientes na block list e 80 casos suspeitos) e encerra |

```bash
# 1. Clone e entre na pasta
cd fraudwatch

# 2. Suba os serviços (db, app e seed)
docker compose up -d --build
```

A API ficará disponível em `http://localhost:8000`.  
Documentação Swagger: `http://localhost:8000/docs`

> As datas dos casos do seed são geradas **relativas à data de execução**.
> O caso mais antigo sempre cai 45 dias antes de hoje, garantindo que os filtros
> "Últimos 7 dias" e "Últimos 30 dias" sempre retornem dados independentemente de quando o seed for rodado.

### Repovoando o banco

O serviço `seed` roda uma única vez na subida (`restart: "no"`). Para rodá-lo novamente
(por exemplo, para renovar as datas dos casos para a data atual):

```bash
docker compose run --rm seed
```

### Encerrando

```bash
docker compose down        # mantém os dados (volume pgdata)
docker compose down -v     # remove também o volume — apaga todos os dados
```

---

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

## Funcionalidades do dashboard

### Filtros de período

| Filtro | Comportamento |
|--------|---------------|
| Todos os casos | Exibe todos os casos cadastrados |
| Últimos 7 dias | Janela móvel: casos dos últimos 7 dias corridos (hoje incluído) |
| Últimos 30 dias | Janela móvel: casos dos últimos 30 dias corridos (hoje incluído) |

Os KPIs, a tabela de casos e todos os 4 gráficos respeitam o filtro selecionado.

### Casos suspeitos

- **Criar caso:** preencha nome, horas de viagem, data e status; transporte, valor e motivo da suspeita são gerados automaticamente.
- **Editar caso:** todos os campos são editáveis após a criação, exceto os calculados automaticamente (Transporte, Valor envolvido e Motivo da suspeita — que recalculam ao alterar horas, data ou fatores de risco).
- **Alterar status:** botões de atalho "Liberar" e "Negar" na sidebar de detalhe do caso.
- **Excluir caso:** botão "Excluir caso permanentemente" na sidebar, com confirmação obrigatória. Remove o caso, seus fatores de risco e histórico de acionamentos.

### Block List

- **Adicionar suspeito:** nome, data de nascimento e motivos do bloqueio.
- **Editar suspeito:** todos os campos editáveis após o cadastro.
- **Remover suspeito:** confirmação obrigatória antes da exclusão.
- Remoção ou edição de um cliente na block list **não afeta casos históricos já registrados** — score, fatores e motivo da suspeita são gravados no momento da criação do caso e não são recalculados retroativamente.

### Exportação

- Casos: CSV e JSON
- Block list: CSV e JSON

---

## Seed — dados iniciais

A cada execução do `seed.py`, o banco é repopulado com:

**Block list:** 15 clientes bloqueados com motivos realistas e variados.

**Casos suspeitos:** 80 casos gerados dinamicamente com as seguintes regras:

| Regra | Detalhe |
|-------|---------|
| Janela temporal | 45 dias (hoje − 44 até hoje) |
| Frequência | 1 a 3 casos por dia; todos os dias têm pelo menos 1 |
| Distribuição | 80% dos casos nos últimos 30 dias · 20% nos dias 31–45 |
| Status | 95% negados ou liberados · 5% em andamento (sempre as datas mais recentes) |
| Proporção liberados/negados | Sorteada a cada execução entre 52–60% liberados · 40–48% negados, com distribuição embaralhada para que a proporção varie entre os filtros de período |

---

## Exemplos de requisições (curl)

### Listar todos os casos
```bash
curl http://localhost:8000/api/cases
```

### Listar casos dos últimos 7 dias
```bash
curl "http://localhost:8000/api/cases?filter=week"
```

### Listar casos dos últimos 30 dias
```bash
curl "http://localhost:8000/api/cases?filter=month"
```

### Criar um novo caso
```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva Santos",
    "suspicion": "Transporte Aéreo (fator de risco) · Indícios de reincidência identificados",
    "hours": 16.5,
    "transport": "air",
    "value": 2640.00,
    "status": "open",
    "date": "2026-06-01",
    "justification": "Segunda passagem aérea no semestre.",
    "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 0, "data": 0},
    "history": [{"d": "2026-02-10", "t": "Aéreo · R$ 2.100"}]
  }'
```

### Editar um caso completo
```bash
curl -X PUT http://localhost:8000/api/cases/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva Santos",
    "hours": 18.0,
    "transport": "air",
    "value": 2880.00,
    "status": "denied",
    "date": "2026-06-01",
    "justification": "Terceira passagem aérea no semestre. Caso negado.",
    "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 0, "data": 0}
  }'
```

### Atualizar apenas o status de um caso
```bash
curl -X PATCH http://localhost:8000/api/cases/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "denied"}'
```

### Excluir um caso
```bash
curl -X DELETE http://localhost:8000/api/cases/1
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

### Editar suspeito na block list
```bash
curl -X PUT http://localhost:8000/api/blocklist/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Aparecida Lima",
    "dob": "1982-05-14",
    "reasons": ["Fraude confirmada por perícia", "Reincidência em 3 anos consecutivos", "Novo motivo identificado"]
  }'
```

### Remover suspeito da block list
```bash
curl -X DELETE http://localhost:8000/api/blocklist/1
```

### Exportar casos em CSV
```bash
curl http://localhost:8000/api/export/cases/csv -o casos.csv
```

### KPIs do dashboard
```bash
curl "http://localhost:8000/api/dashboard/kpis?filter=all"
```

### Dados dos gráficos (respeitam o filtro de período)
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
| PUT | `/api/cases/{id}` | Atualiza um caso completo |
| PATCH | `/api/cases/{id}/status` | Atualiza apenas o status |
| DELETE | `/api/cases/{id}` | Remove um caso e todo seu histórico |
| GET | `/api/blocklist` | Lista block list |
| GET | `/api/blocklist/{id}` | Detalhe de um suspeito |
| POST | `/api/blocklist` | Adiciona suspeito à block list |
| PUT | `/api/blocklist/{id}` | Atualiza dados de um suspeito |
| DELETE | `/api/blocklist/{id}` | Remove suspeito da block list |
| GET | `/api/export/cases/csv` | Exporta casos em CSV |
| GET | `/api/export/cases/json` | Exporta casos em JSON |
| GET | `/api/export/blocklist/csv` | Exporta block list em CSV |
| GET | `/api/export/blocklist/json` | Exporta block list em JSON |
| GET | `/api/dashboard/kpis` | KPIs agregados (`?filter=all\|week\|month`) |
| GET | `/api/dashboard/charts` | Dados para os 4 gráficos (`?filter=all\|week\|month`) |

---

## Cálculo do Score

O score de risco é calculado automaticamente pelo backend no momento da criação ou edição de um caso e armazenado junto ao registro.

| Fator | Peso máximo | Como é determinado |
|-------|-------------|--------------------|
| Block list | 45 pts | Automático — nome do cliente encontrado na block list |
| Reincidência | 25 pts | Manual — soma dos motivos comportamentais marcados pelo operador (teto: 25 pts) |
| Transporte | 20 pts | Automático — derivado do tempo de viagem (Aéreo=20, Marítimo=10, Rodoviário=0) |
| Data suspeita | 10 pts | Automático — data do acionamento próxima a feriado nacional (±3 dias) |

**Score máximo:** 100 pontos

| Faixa | Classificação |
|-------|---------------|
| 0–25 | Risco **BAIXO** |
| 26–55 | Risco **MÉDIO** |
| 56–100 | Risco **ALTO** |

### Fatores manuais no formulário

O operador seleciona os comportamentos observados; cada seleção incrementa o fator de reincidência (respeitando o teto de 25 pts):

| Comportamento observado | Pontos |
|-------------------------|--------|
| Sinistros pouco críveis (pane proposital para acionar o benefício) | +15 |
| Uso indevido do benefício (guincho utilizado para transportar objetos/bagagens) | +10 |
| Solicitação fora do padrão (aciona o serviço para conseguir passagem aérea) | +10 |

### Definição automática do transporte e valor

Com base no tempo de viagem informado, o sistema define automaticamente o meio de transporte e calcula o valor envolvido:

| Horas de viagem | Transporte | Fórmula do valor |
|-----------------|------------|------------------|
| Até 8h | Rodoviário | horas × 80 km/h × 0,8 |
| 8h a 15h | Marítimo | horas × 80 km/h × 1,5 |
| Acima de 15h | Aéreo | horas × 80 km/h × 2,0 |

Exemplo: viagem de 16h → Aéreo → 16 × 80 × 2,0 = **R$ 2.560,00**

Esses campos são exibidos em modo somente-leitura no formulário e recalculam automaticamente ao alterar as horas ou a data.
