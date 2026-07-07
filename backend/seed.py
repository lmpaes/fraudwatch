"""Run: python seed.py  (from backend/ folder with venv active)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import random
from datetime import date, timedelta
from database import SessionLocal, engine
import models
from services.score import generate_initials, generate_color, calculate_score

models.Base.metadata.create_all(bind=engine)

# ── Blocklist seed (15 entradas) ──────────────────────────────
BLOCKLIST_SEED = [
    {
        "name": "Roberto Alves Mendes", "dob": date(1978, 3, 12),
        "reasons": [
            "Sinistro proposital confirmado por perícia",
            "Guincho utilizado para mudança residencial",
            "3 acionamentos em 45 dias consecutivos",
        ],
    },
    {
        "name": "Camila Torres Souza", "dob": date(1985, 7, 28),
        "reasons": [
            "Passagem aérea sem comprovação de sinistro real",
            "Reincidência em 4 anos consecutivos",
        ],
    },
    {
        "name": "Fernando Lima Costa", "dob": date(1971, 11, 5),
        "reasons": [
            "Falsificação de documentos do sinistro confirmada",
            "Conluio comprovado com oficina parceira",
        ],
    },
    {
        "name": "Patrícia Rocha Nunes", "dob": date(1990, 9, 19),
        "reasons": [
            "Pane fabricada em véspera de feriado nacional",
            "Objetos pessoais encontrados no interior do guincho",
        ],
    },
    {
        "name": "Márcio Vieira Braga", "dob": date(1968, 4, 30),
        "reasons": [
            "5 acionamentos em 12 meses — todos de longa distância da residência",
            "Passagens aéreas para destinos distintos da residência",
        ],
    },
    # ── 10 novos ──────────────────────────────────────────────
    {
        "name": "Andréia Sampaio Correia", "dob": date(1983, 6, 14),
        "reasons": [
            "Solicitou mudança de endereço durante o acionamento",
            "Motorista relatou bagagens volumosas incompatíveis com pane",
        ],
    },
    {
        "name": "Sérgio Pinheiro Moraes", "dob": date(1976, 2, 22),
        "reasons": [
            "Dois sinistros em 30 dias com diferentes veículos",
            "Documentação do segundo sinistro identificada como fraudulenta",
        ],
    },
    {
        "name": "Alessandra Viana Roque", "dob": date(1992, 10, 8),
        "reasons": [
            "Reincidência confirmada em 3 apólices distintas",
            "Acionamento em área sem cobertura de rede — localização inconsistente",
        ],
    },
    {
        "name": "Celso Drummond Netto", "dob": date(1965, 5, 3),
        "reasons": [
            "Conluio com borracheiro para fabricação de pane",
            "Testemunhas contradizem versão apresentada pelo cliente",
        ],
    },
    {
        "name": "Mirela Assis Furtado", "dob": date(1988, 12, 17),
        "reasons": [
            "Passagem aérea solicitada para rota turística sem justificativa de sinistro",
            "4 acionamentos em 24 meses com destinos incoerentes",
        ],
    },
    {
        "name": "Jonas Tavares Brito", "dob": date(1973, 8, 30),
        "reasons": [
            "Sinistro encenado confirmado por câmeras de segurança",
            "Utilizou serviço de reboque para transporte de mercadorias",
        ],
    },
    {
        "name": "Débora Mendonça Leal", "dob": date(1995, 3, 25),
        "reasons": [
            "Acionamentos sempre em vésperas de feriados prolongados",
            "Destinos dos acionamentos coincidem com roteiros turísticos frequentes",
        ],
    },
    {
        "name": "Paulo Rogerio Farias", "dob": date(1969, 7, 11),
        "reasons": [
            "Declaração falsa sobre local do sinistro comprovada por GPS",
            "Três apólices ativas em nome de familiares acionadas sequencialmente",
        ],
    },
    {
        "name": "Cristiane Dornelas Paz", "dob": date(1980, 1, 9),
        "reasons": [
            "Guincho desviado do trajeto acordado pelo motorista",
            "Histórico de fraudes em outras seguradoras identificado",
        ],
    },
    {
        "name": "Wendell Carvalho Dias", "dob": date(1987, 4, 16),
        "reasons": [
            "Veículo encontrado em perfeito estado após acionamento de pane",
            "Reincidência com 6 acionamentos em 18 meses — padrão atípico",
        ],
    },
]

# ── Pool de nomes (clientes sem blocklist) ────────────────────
CLIENT_NAME_POOL = [
    "Ana Paula Gomes", "Carlos Eduardo Pinto", "Luís Henrique Ramos",
    "Fernanda Melo Castro", "Ricardo Souza Barros", "Mariana Lopes Vieira",
    "Juliana Ferreira Dias", "Thiago Nascimento Reis", "Beatriz Almeida Cruz",
    "Alexandre Cunha Torres", "Diego Rocha Ferreira", "Isabela Fontes Martins",
    "Gustavo Mendes Araújo", "Larissa Campos Duarte", "Eduardo Pires Nogueira",
    "Vanessa Lima Teixeira", "Bruno Cavalcante Mota", "Renata Souza Monteiro",
    "Fábio Andrade Rocha", "Tatiane Borges Oliveira", "Henrique Vasconcelos Cruz",
    "Simone Cardoso Baptista", "Leandro Figueiredo Santos", "Priscila Menezes Costa",
    "Rodrigo Albuquerque Lima", "Juliane Barros Martins", "Andressa Pimentel Cardoso",
    "Vinicius Teixeira Araujo", "Marcos Aurélio Batista", "Silvana Ramos Ferraz",
    "Diogo Pereira Brandão", "Carolina Assunção Lima", "Fabiana Nogueira Gomes",
    "Rafael Carvalho Siqueira", "Luciana Prado Mendes",
]

# ── Helpers de transporte e valor ─────────────────────────────
TRANSPORT_VALUE_FACTOR = {"road": 0.8, "maritime": 1.5, "air": 2.0}
TRANSPORT_LABELS      = {"road": "Rodoviário", "maritime": "Marítimo", "air": "Aéreo"}

def _suggest_transport(hours: float) -> str:
    if hours <= 8:
        return "road"
    if hours >= 15:
        return "air"
    return "maritime"

def _calc_value(hours: float, transport: str) -> float:
    return round(hours * 80 * TRANSPORT_VALUE_FACTOR[transport], 2)

# ── Templates de justificativa ────────────────────────────────
_JUSTIFS = {
    "blocklist": [
        "Cliente consta na block list com histórico de fraude confirmada. "
        "Acionamento negado preventivamente pelo sistema de monitoramento.",
        "Reincidente na block list. Documentação apresentada contém inconsistências "
        "com registros anteriores. Caso encaminhado para auditoria.",
        "Cliente em block list por conluio comprovado. Sinistro segue padrão idêntico "
        "a ocorrências anteriores já negadas.",
    ],
    "air_reinc": [
        "Passagem aérea com valor elevado e reincidência identificada. Destino não "
        "corresponde à residência cadastrada. Aguardando comprovação documental.",
        "Terceiro acionamento aéreo no período. Valor acima da média histórica do "
        "perfil. Encaminhado para análise prioritária.",
        "Acionamento aéreo em período de alta temporada com histórico de reincidência. "
        "Padrão de uso suspeito identificado pelo sistema.",
    ],
    "maritime_reinc": [
        "Múltiplos acionamentos marítimos em rotas distintas. Padrão consistente "
        "com uso indevido do benefício. Em análise.",
        "Segundo acionamento marítimo no trimestre com origem distante da residência. "
        "Score elevado por reincidência identificada.",
        "Acionamento marítimo com destino incompatível com o sinistro declarado. "
        "Documentação em revisão para validação.",
    ],
    "road_reinc": [
        "Terceiro acionamento rodoviário no bimestre. Frequência suspeita detectada "
        "pelo sistema de monitoramento. Análise em andamento.",
        "Acionamento rodoviário com histórico de reincidência. Valor dentro do esperado, "
        "porém padrão de uso monitorado.",
    ],
    "holiday": [
        "Sinistro registrado em véspera de feriado nacional — fator de risco "
        "automático ativado. Documentação solicitada ao cliente.",
        "Acionamento durante período de feriado prolongado. Padrão coincidente com "
        "histórico de usos suspeitos na base.",
        "Data suspeita: feriado nacional. Sinistro sem boletim de ocorrência imediato. "
        "Em análise documental.",
    ],
    "air_only": [
        "Passagem aérea como fator de risco principal. Sem histórico anterior. "
        "Monitoramento preventivo ativado para este perfil.",
        "Primeiro acionamento com passagem aérea. Documentação em análise pelo time "
        "de prevenção a fraudes.",
    ],
    "generic": [
        "Acionamento com características de risco moderado. Documentação em análise "
        "pelo time de investigação.",
        "Perfil com fatores de risco pontuais identificados. Monitoramento preventivo "
        "ativado conforme protocolo.",
        "Score acima do limiar de monitoramento. Caso em análise padrão pelo time "
        "de prevenção a fraudes.",
        "Fatores de risco identificados automaticamente. Análise manual em andamento "
        "para validação.",
        "Acionamento com combinação de fatores que ativa monitoramento especial. "
        "Aguardando documentação complementar.",
    ],
}

def _pick_justification(is_bl: bool, transport: str, near_hol: bool, reinc_pts: int) -> str:
    if is_bl:
        return random.choice(_JUSTIFS["blocklist"])
    if transport == "air" and reinc_pts >= 10:
        return random.choice(_JUSTIFS["air_reinc"])
    if transport == "maritime" and reinc_pts >= 10:
        return random.choice(_JUSTIFS["maritime_reinc"])
    if transport == "road" and reinc_pts >= 10:
        return random.choice(_JUSTIFS["road_reinc"])
    if near_hol:
        return random.choice(_JUSTIFS["holiday"])
    if transport == "air":
        return random.choice(_JUSTIFS["air_only"])
    return random.choice(_JUSTIFS["generic"])

def _build_suspicion(is_bl: bool, reinc_pts: int, transport: str, near_hol: bool) -> str:
    parts = []
    if is_bl:
        parts.append(("Cliente consta na block list", 45))
    if reinc_pts > 0:
        parts.append(("Indícios de reincidência identificados", reinc_pts))
    tr_pts = {"air": 20, "maritime": 10, "road": 0}.get(transport, 0)
    if tr_pts > 0:
        parts.append((f"Transporte {TRANSPORT_LABELS[transport]} (fator de risco)", tr_pts))
    if near_hol:
        parts.append(("Acionamento próximo a data de feriado nacional", 10))
    parts.sort(key=lambda x: x[1], reverse=True)
    return " · ".join(p[0] for p in parts) if parts else "Monitoramento preventivo"

# ── Feriados nacionais (mesmo conjunto do score.py) ───────────
_NATIONAL_HOLIDAYS = {
    (1, 1), (4, 21), (5, 1), (9, 7), (10, 12),
    (11, 2), (11, 15), (12, 25),
    (4, 18), (4, 19), (3, 4), (3, 5),
    (4, 3), (4, 5),
}

def _is_near_holiday(d: date) -> bool:
    for delta in range(-3, 4):
        check = d + timedelta(days=delta)
        if (check.month, check.day) in _NATIONAL_HOLIDAYS:
            return True
    return False

# ── Geração das 80 datas ──────────────────────────────────────
def _build_date_slots() -> list[date]:
    """
    80 casos ao longo de 45 dias (hoje-44 até hoje).

    Regras:
      - Todos os 45 dias têm pelo menos 1 caso (1-3 por dia).
      - 80% dos casos ficam nos últimos 30 dias  → 64 casos.
      - 20% ficam nos dias 31-45 atrás           → 16 casos.
      - Os 35 casos extras são distribuídos para respeitar essa proporção.
    """
    today = date.today()
    all_days = [today - timedelta(days=44 - i) for i in range(45)]   # 45 dias ordenados

    older_days  = all_days[:15]   # dias 44 a 30 atrás  (zona 20%)
    recent_days = all_days[15:]   # dias 29 a 0  atrás  (zona 80%)

    # Base: 1 por dia = 45 slots
    slots: list[date] = all_days[:]

    # Extras necessários: older 16-15=1 / recent 64-30=34
    extra_older  = 16 - len(older_days)   # = 1
    extra_recent = 64 - len(recent_days)  # = 34

    slots += [random.choice(older_days)  for _ in range(extra_older)]
    slots += [random.choice(recent_days) for _ in range(extra_recent)]

    # Validação: nunca mais de 3 por dia
    from collections import Counter
    counts = Counter(slots)
    for d, cnt in counts.items():
        while counts[d] > 3:
            # Mover excesso para outro dia da mesma zona
            pool = recent_days if d >= (today - timedelta(days=29)) else older_days
            new_day = random.choice([x for x in pool if counts[x] < 3] or pool)
            slots[slots.index(d)] = new_day
            counts[d] -= 1
            counts[new_day] += 1

    slots.sort()
    return slots  # 80 datas ordenadas do mais antigo ao mais recente

# ── Distribuição de status ────────────────────────────────────
def _assign_statuses(n: int) -> list[str]:
    """
    - 5% em andamento (open) — sempre os mais recentes.
    - Do restante: 52-60% liberados, 40-48% negados.
    - O embaralhamento garante variação de proporção entre os filtros.
    """
    n_open    = max(1, round(n * 0.05))   # 4
    n_closed  = n - n_open                # 76

    # Sorteio da quantidade de liberados (varia a cada execução)
    n_released = random.randint(round(n * 0.52), round(n * 0.60))
    n_denied   = n_closed - n_released

    closed = ["released"] * n_released + ["denied"] * n_denied
    random.shuffle(closed)   # embaralha para variar ratio por janela de filtro

    # Os n_open mais recentes (índices finais) ficam como open
    result = closed[:n_closed] + ["open"] * n_open
    return result   # alinhado com slots já ordenados (antigo → recente)

# ── Objeto auxiliar para calculate_score ─────────────────────
class _FactorInput:
    def __init__(self, blocklist: int, reincidencia: int):
        self.blocklist   = blocklist
        self.reincidencia = reincidencia
        self.transporte  = 0   # recalculado pelo score.py a partir do transport
        self.data        = 0   # recalculado pelo score.py a partir da data


# ── Seed principal ────────────────────────────────────────────
def seed():
    db = SessionLocal()
    try:
        # ── Limpeza ──────────────────────────────────────────
        db.query(models.CaseHistory).delete()
        db.query(models.CaseFactor).delete()
        db.query(models.Case).delete()
        db.query(models.BlocklistReason).delete()
        db.query(models.Blocklist).delete()
        db.commit()

        # ── Blocklist ─────────────────────────────────────────
        for b in BLOCKLIST_SEED:
            entry = models.Blocklist(
                name=b["name"],
                initials=generate_initials(b["name"]),
                dob=b["dob"],
            )
            db.add(entry)
            db.flush()
            for r in b["reasons"]:
                db.add(models.BlocklistReason(blocklist_id=entry.id, reason=r))
        db.commit()
        print(f"✓ Blocklist: {len(BLOCKLIST_SEED)} entradas inseridas")

        # ── Cases ─────────────────────────────────────────────
        blocklist_names     = {b["name"].lower() for b in BLOCKLIST_SEED}
        blocklist_name_list = [b["name"] for b in BLOCKLIST_SEED]

        date_slots = _build_date_slots()    # 80 datas
        statuses   = _assign_statuses(len(date_slots))  # 80 status

        # Valores de horas possíveis (0.5 em 0.5, de 4.5 a 20)
        hour_options = [x / 2 for x in range(9, 41)]

        for case_date, status in zip(date_slots, statuses):
            # ── Nome ──────────────────────────────────────────
            # ~15% de chance de ser um cliente da blocklist
            if random.random() < 0.15:
                name = random.choice(blocklist_name_list)
            else:
                name = random.choice(CLIENT_NAME_POOL)

            is_bl = name.lower() in blocklist_names

            # ── Perfil de viagem ──────────────────────────────
            hours     = random.choice(hour_options)
            transport = _suggest_transport(hours)
            value     = _calc_value(hours, transport)
            near_hol  = _is_near_holiday(case_date)

            # ── Fator de reincidência ──────────────────────────
            # Clientes da blocklist têm maior probabilidade de reincidência
            if is_bl:
                reinc_pts = random.choices([15, 25], weights=[0.45, 0.55])[0]
            else:
                reinc_pts = random.choices([0, 10, 15, 25], weights=[0.40, 0.25, 0.22, 0.13])[0]

            # Garantia: pelo menos um fator de risco deve existir
            tr_pts = {"air": 20, "maritime": 10, "road": 0}[transport]
            if not is_bl and reinc_pts == 0 and tr_pts == 0 and not near_hol:
                reinc_pts = 10

            # ── Suspicion e justificativa ─────────────────────
            suspicion     = _build_suspicion(is_bl, reinc_pts, transport, near_hol)
            justification = _pick_justification(is_bl, transport, near_hol, reinc_pts)

            # ── Score ─────────────────────────────────────────
            f_input = _FactorInput(45 if is_bl else 0, reinc_pts)
            score, computed = calculate_score(db, name, transport, case_date, f_input, is_bl)

            # ── Histórico de acionamentos anteriores ──────────
            hist_count = random.choices([0, 1, 2], weights=[0.50, 0.35, 0.15])[0]
            history_entries = []
            for _ in range(hist_count):
                days_back = random.randint(45, 400)
                h_date      = case_date - timedelta(days=days_back)
                h_transport = random.choice(["Rodoviário", "Marítimo", "Aéreo"])
                h_factor    = {"Rodoviário": 0.8, "Marítimo": 1.5, "Aéreo": 2.0}[h_transport]
                h_hours     = random.choice(hour_options)
                h_value     = int(round(h_hours * 80 * h_factor))
                h_value_str = f"R$ {h_value:,}".replace(",", ".")
                history_entries.append((h_date, f"{h_transport} · {h_value_str}"))

            # ── Persistência ──────────────────────────────────
            case = models.Case(
                name=name,
                initials=generate_initials(name),
                col=generate_color(),
                suspicion=suspicion,
                hours=hours,
                transport=transport,
                value=value,
                score=score,
                status=status,
                date=case_date,
                justification=justification,
            )
            db.add(case)
            db.flush()

            db.add(models.CaseFactor(case_id=case.id, **computed))
            for h_date, h_text in history_entries:
                db.add(models.CaseHistory(case_id=case.id, d=h_date, t=h_text))

        db.commit()

        # ── Resumo ────────────────────────────────────────────
        today  = date.today()
        last7  = today - timedelta(days=6)
        last30 = today - timedelta(days=29)
        n      = len(date_slots)
        n_last30  = sum(1 for d in date_slots if d >= last30)
        n_last7   = sum(1 for d in date_slots if d >= last7)
        n_open    = statuses.count("open")
        n_released = statuses.count("released")
        n_denied  = statuses.count("denied")

        print(f"✓ Cases: {n} casos inseridos")
        print(f"  → Todos os casos : {n}")
        print(f"  → Últimos 30 dias: {n_last30} ({round(n_last30 / n * 100)}%)")
        print(f"  → Últimos 7 dias : {n_last7}")
        print(f"  → Em andamento   : {n_open}  ({round(n_open / n * 100)}%)")
        print(f"  → Liberados      : {n_released} ({round(n_released / n * 100)}%)")
        print(f"  → Negados        : {n_denied} ({round(n_denied / n * 100)}%)")
        print(f"  → Caso mais antigo: {date_slots[0].strftime('%d/%m/%Y')}")
        print(f"  → Caso mais recente: {date_slots[-1].strftime('%d/%m/%Y')}")
        print("Seed concluído.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
