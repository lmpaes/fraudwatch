"""Run: python seed.py  (from backend/ folder with venv active)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from database import SessionLocal, engine
import models
from services.score import generate_initials, generate_color, calculate_score

models.Base.metadata.create_all(bind=engine)

# ── Blocklist seed ────────────────────────────────────────────
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
            "5 acionamentos em 12 meses — todos acima de 400km",
            "Passagens aéreas para destinos distintos da residência",
        ],
    },
]

# ── Cases seed ────────────────────────────────────────────────
CASES_SEED = [
    # Original 15 cases
    {
        "name": "Roberto Alves Mendes", "suspicion": "Reincidência + Block List",
        "hours": 17, "transport": "air", "value": 2840,
        "status": "denied", "date": date(2026, 5, 19),
        "justification": "Cliente consta na block list com fraude confirmada por perícia. Terceiro acionamento no ano com sinistro reportado em véspera de feriado nacional. Passagem aérea solicitada para destino diferente da residência cadastrada.",
        "factors": {"blocklist": 45, "reincidencia": 25, "transporte": 20, "data": 10},
        "history": [
            {"d": date(2026, 3, 10), "t": "Passagem aérea · R$ 2.100"},
            {"d": date(2025, 11, 22), "t": "Rodoviário · R$ 680"},
            {"d": date(2025, 8, 15), "t": "Passagem aérea · R$ 1.950"},
        ],
    },
    {
        "name": "Ana Paula Gomes", "suspicion": "Transporte aéreo + data suspeita",
        "hours": 16, "transport": "air", "value": 2100,
        "status": "open", "date": date(2026, 5, 18),
        "justification": "Sinistro registrado na sexta antes de feriado prolongado. Distância justifica passagem aérea. Histórico limpo — apenas um acionamento anterior no ano passado. Caso em análise preventiva.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 10},
        "history": [{"d": date(2025, 6, 3), "t": "Táxi · R$ 310"}],
    },
    {
        "name": "Carlos Eduardo Pinto", "suspicion": "Reincidência (3x no ano)",
        "hours": 11, "transport": "road", "value": 720,
        "status": "open", "date": date(2026, 5, 17),
        "justification": "Três acionamentos no ano corrente. Padrão de sinistros em rodovias próximas a destinos turísticos frequentes. Necessita revisão detalhada.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 10, "data": 0},
        "history": [
            {"d": date(2026, 4, 2), "t": "Rodoviário · R$ 650"},
            {"d": date(2026, 1, 28), "t": "Táxi · R$ 290"},
        ],
    },
    {
        "name": "Camila Torres Souza", "suspicion": "Block List · aéreo · reincidência",
        "hours": 18, "transport": "air", "value": 3100,
        "status": "denied", "date": date(2026, 5, 16),
        "justification": "Reincidente em block list. Dois acionamentos anteriores com passagem aérea em anos consecutivos. Caso negado automaticamente pela presença em block list.",
        "factors": {"blocklist": 45, "reincidencia": 15, "transporte": 20, "data": 0},
        "history": [
            {"d": date(2025, 12, 27), "t": "Passagem aérea · R$ 2.800"},
            {"d": date(2025, 3, 14), "t": "Aéreo · R$ 2.400"},
        ],
    },
    {
        "name": "Luís Henrique Ramos", "suspicion": "Data suspeita · véspera de feriado",
        "hours": 8, "transport": "taxi", "value": 390,
        "status": "released", "date": date(2026, 5, 15),
        "justification": "Único fator de risco: data próxima a feriado. Sem histórico de reincidência. Primeiro acionamento. Sinistro validado com documentação completa. Caso liberado.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 0, "data": 10},
        "history": [],
    },
    {
        "name": "Fernanda Melo Castro", "suspicion": "Reincidência (2x) + rodoviário",
        "hours": 13, "transport": "road", "value": 680,
        "status": "released", "date": date(2026, 5, 14),
        "justification": "Dois acionamentos no ano com transporte rodoviário. Score na faixa de risco baixo. Documentação do sinistro válida. Liberado após análise.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 10, "data": 0},
        "history": [{"d": date(2026, 2, 10), "t": "Rodoviário · R$ 630"}],
    },
    {
        "name": "Ricardo Souza Barros", "suspicion": "Reincidência + aéreo + data",
        "hours": 16, "transport": "air", "value": 2650,
        "status": "open", "date": date(2026, 5, 13),
        "justification": "Segunda passagem aérea no ano. Sinistro ocorrido na quinta antes de feriado. Padrão de acionamentos em períodos estratégicos de viagem. Em análise prioritária.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 20, "data": 10},
        "history": [
            {"d": date(2026, 3, 19), "t": "Aéreo · R$ 2.200"},
            {"d": date(2025, 11, 5), "t": "Táxi · R$ 350"},
        ],
    },
    {
        "name": "Mariana Lopes Vieira", "suspicion": "Transporte aéreo · 1º acionamento",
        "hours": 15.5, "transport": "air", "value": 1980,
        "status": "open", "date": date(2026, 5, 12),
        "justification": "Primeiro acionamento no histórico. Passagem aérea como único fator de risco. Monitoramento preventivo ativado.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 0},
        "history": [],
    },
    {
        "name": "Fernando Lima Costa", "suspicion": "Block List · guincho suspeito",
        "hours": 10.5, "transport": "road", "value": 740,
        "status": "denied", "date": date(2026, 5, 11),
        "justification": "Cliente em block list por conluio com oficina parceira. Guincho registrado com carga incomum pelo operador. Negado preventivamente.",
        "factors": {"blocklist": 45, "reincidencia": 15, "transporte": 10, "data": 0},
        "history": [
            {"d": date(2026, 1, 5), "t": "Aéreo · R$ 2.600"},
            {"d": date(2025, 9, 22), "t": "Rodoviário · R$ 710"},
        ],
    },
    {
        "name": "Juliana Ferreira Dias", "suspicion": "Reincidência (3x) + data suspeita",
        "hours": 9, "transport": "taxi", "value": 420,
        "status": "open", "date": date(2026, 5, 10),
        "justification": "Três acionamentos no ano, todos registrados próximos a feriados nacionais. Padrão consistente de uso oportunista do benefício.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 0, "data": 10},
        "history": [
            {"d": date(2026, 4, 18), "t": "Táxi · R$ 380"},
            {"d": date(2026, 2, 1), "t": "Táxi · R$ 400"},
        ],
    },
    {
        "name": "Thiago Nascimento Reis", "suspicion": "Primeiro acionamento · aéreo",
        "hours": 16, "transport": "air", "value": 2200,
        "status": "released", "date": date(2026, 5, 8),
        "justification": "Sem histórico anterior. Sinistro validado com boletim de ocorrência e fotos. Passagem aérea autorizada.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 0},
        "history": [],
    },
    {
        "name": "Beatriz Almeida Cruz", "suspicion": "Rodoviário + véspera de feriado",
        "hours": 12, "transport": "road", "value": 610,
        "status": "open", "date": date(2026, 5, 7),
        "justification": "Acionamento em véspera de feriado com transporte rodoviário. Aguardando documentação complementar para análise.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 10, "data": 10},
        "history": [],
    },
    {
        "name": "Márcio Vieira Braga", "suspicion": "Block List · aéreo · reincidência máx.",
        "hours": 17.5, "transport": "air", "value": 3200,
        "status": "denied", "date": date(2026, 5, 6),
        "justification": "Score máximo (100). Block list + maior faixa de reincidência + passagem aérea + data suspeita. Negado automaticamente pelo sistema.",
        "factors": {"blocklist": 45, "reincidencia": 25, "transporte": 20, "data": 10},
        "history": [
            {"d": date(2026, 2, 14), "t": "Aéreo · R$ 3.100"},
            {"d": date(2025, 12, 20), "t": "Aéreo · R$ 2.900"},
            {"d": date(2025, 8, 10), "t": "Aéreo · R$ 2.750"},
        ],
    },
    {
        "name": "Patrícia Rocha Nunes", "suspicion": "Block List · objetos suspeitos no guincho",
        "hours": 14, "transport": "road", "value": 890,
        "status": "denied", "date": date(2026, 5, 4),
        "justification": "Block list ativa. Objetos pesados encontrados no veículo pelo operador do guincho, sugerindo uso do serviço para transporte de pertences.",
        "factors": {"blocklist": 45, "reincidencia": 15, "transporte": 10, "data": 0},
        "history": [{"d": date(2025, 7, 30), "t": "Rodoviário · R$ 760"}],
    },
    {
        "name": "Alexandre Cunha Torres", "suspicion": "Reincidência (2x) + aéreo",
        "hours": 15.5, "transport": "air", "value": 2050,
        "status": "open", "date": date(2026, 5, 2),
        "justification": "Dois acionamentos no ano. Segundo com passagem aérea. Padrão crescente de custo. Monitoramento ativo.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 20, "data": 0},
        "history": [{"d": date(2026, 1, 11), "t": "Táxi · R$ 320"}],
    },
    # Additional 15 realistic cases
    {
        "name": "Diego Rocha Ferreira", "suspicion": "Aéreo + data suspeita + reincidência",
        "hours": 14.5, "transport": "air", "value": 2380,
        "status": "open", "date": date(2026, 4, 20),
        "justification": "Acionamento registrado na véspera do feriado de Tiradentes. Segunda passagem aérea no semestre. Padrão de uso em períodos de feriados nacionais.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 20, "data": 10},
        "history": [{"d": date(2026, 1, 30), "t": "Aéreo · R$ 2.100"}],
    },
    {
        "name": "Isabela Fontes Martins", "suspicion": "Rodoviário recorrente",
        "hours": 9.5, "transport": "road", "value": 590,
        "status": "released", "date": date(2026, 4, 15),
        "justification": "Dois acionamentos rodoviários em três meses. Documentação completa em ambos. Score baixo, caso liberado após revisão.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 10, "data": 0},
        "history": [{"d": date(2026, 1, 20), "t": "Rodoviário · R$ 540"}],
    },
    {
        "name": "Gustavo Mendes Araújo", "suspicion": "Transporte aéreo isolado",
        "hours": 17, "transport": "air", "value": 1950,
        "status": "open", "date": date(2026, 4, 10),
        "justification": "Primeiro acionamento com passagem aérea. Sem histórico anterior. Monitoramento padrão ativado para perfil de novo cliente.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 0},
        "history": [],
    },
    {
        "name": "Larissa Campos Duarte", "suspicion": "Reincidência táxi + data feriado",
        "hours": 6, "transport": "taxi", "value": 350,
        "status": "open", "date": date(2026, 4, 19),
        "justification": "Terceiro acionamento de táxi em quatro meses. Data coincide com feriado de Tiradentes. Valor baixo mas padrão suspeito.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 0, "data": 10},
        "history": [
            {"d": date(2026, 3, 5), "t": "Táxi · R$ 290"},
            {"d": date(2026, 1, 15), "t": "Táxi · R$ 310"},
        ],
    },
    {
        "name": "Eduardo Pires Nogueira", "suspicion": "Rodoviário · véspera carnaval",
        "hours": 12, "transport": "road", "value": 870,
        "status": "denied", "date": date(2026, 3, 4),
        "justification": "Sinistro registrado na quarta de carnaval com veículo carregado de pertences. Operador relatou irregularidade. Caso negado.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 10, "data": 10},
        "history": [],
    },
    {
        "name": "Vanessa Lima Teixeira", "suspicion": "Aéreo + reincidência alta",
        "hours": 18, "transport": "air", "value": 2750,
        "status": "open", "date": date(2026, 3, 20),
        "justification": "Quarta passagem aérea nos últimos 18 meses. Destinos variados sem relação com endereço de residência. Em análise de reincidência.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 20, "data": 0},
        "history": [
            {"d": date(2025, 12, 10), "t": "Aéreo · R$ 2.600"},
            {"d": date(2025, 8, 22), "t": "Aéreo · R$ 2.400"},
            {"d": date(2025, 4, 5), "t": "Aéreo · R$ 2.300"},
        ],
    },
    {
        "name": "Bruno Cavalcante Mota", "suspicion": "Táxi + data suspeita",
        "hours": 7, "transport": "taxi", "value": 410,
        "status": "released", "date": date(2026, 3, 15),
        "justification": "Acionamento próximo a feriado, porém com documentação válida e histórico limpo. Liberado após análise documental.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 0, "data": 10},
        "history": [],
    },
    {
        "name": "Renata Souza Monteiro", "suspicion": "Rodoviário + reincidência moderada",
        "hours": 11, "transport": "road", "value": 660,
        "status": "open", "date": date(2026, 3, 8),
        "justification": "Dois acionamentos rodoviários no trimestre. Rotas diferentes mas com padrão de distância superior a 400km. Em monitoramento.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 10, "data": 0},
        "history": [{"d": date(2026, 1, 12), "t": "Rodoviário · R$ 600"}],
    },
    {
        "name": "Fábio Andrade Rocha", "suspicion": "Aéreo isolado · alto valor",
        "hours": 19, "transport": "air", "value": 3050,
        "status": "open", "date": date(2026, 2, 25),
        "justification": "Primeiro acionamento com valor acima da média para passagem aérea. Sem histórico anterior. Análise preventiva em andamento.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 0},
        "history": [],
    },
    {
        "name": "Tatiane Borges Oliveira", "suspicion": "Táxi + reincidência moderada",
        "hours": 5.5, "transport": "taxi", "value": 320,
        "status": "released", "date": date(2026, 2, 18),
        "justification": "Dois acionamentos de táxi no bimestre. Valores compatíveis com distâncias declaradas. Documentação aprovada. Liberado.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 0, "data": 0},
        "history": [{"d": date(2026, 1, 3), "t": "Táxi · R$ 280"}],
    },
    {
        "name": "Henrique Vasconcelos Cruz", "suspicion": "Rodoviário · alto valor + data",
        "hours": 13.5, "transport": "road", "value": 920,
        "status": "open", "date": date(2026, 2, 12),
        "justification": "Acionamento próximo ao Carnaval com valor acima do padrão para transporte rodoviário. Primeiro acionamento mas com valor atípico.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 10, "data": 10},
        "history": [],
    },
    {
        "name": "Simone Cardoso Baptista", "suspicion": "Aéreo + data Carnaval",
        "hours": 15, "transport": "air", "value": 2480,
        "status": "denied", "date": date(2026, 3, 5),
        "justification": "Passagem aérea durante o Carnaval sem comprovação de sinistro válido. Destino não corresponde à residência. Negado após investigação.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 20, "data": 10},
        "history": [],
    },
    {
        "name": "Leandro Figueiredo Santos", "suspicion": "Reincidência máxima sem blocklist",
        "hours": 10, "transport": "road", "value": 780,
        "status": "open", "date": date(2026, 1, 28),
        "justification": "Quarto acionamento rodoviário no período. Padrão altamente suspeito mesmo sem constar na block list. Encaminhado para análise especial.",
        "factors": {"blocklist": 0, "reincidencia": 25, "transporte": 10, "data": 0},
        "history": [
            {"d": date(2025, 11, 10), "t": "Rodoviário · R$ 700"},
            {"d": date(2025, 8, 5), "t": "Rodoviário · R$ 650"},
            {"d": date(2025, 5, 18), "t": "Táxi · R$ 350"},
        ],
    },
    {
        "name": "Priscila Menezes Costa", "suspicion": "Táxi · primeiro acionamento",
        "hours": 4.5, "transport": "taxi", "value": 280,
        "status": "released", "date": date(2026, 1, 20),
        "justification": "Primeiro acionamento com táxi. Valor e distância coerentes. Documentação completa. Aprovado sem ressalvas.",
        "factors": {"blocklist": 0, "reincidencia": 0, "transporte": 0, "data": 0},
        "history": [],
    },
    {
        "name": "Rodrigo Albuquerque Lima", "suspicion": "Aéreo + reincidência + data suspeita",
        "hours": 16.5, "transport": "air", "value": 2920,
        "status": "open", "date": date(2026, 1, 2),
        "justification": "Acionamento logo após o Ano Novo com passagem aérea e histórico de duas ocorrências anteriores. Perfil de alto risco em análise.",
        "factors": {"blocklist": 0, "reincidencia": 15, "transporte": 20, "data": 10},
        "history": [
            {"d": date(2025, 9, 15), "t": "Aéreo · R$ 2.700"},
            {"d": date(2025, 4, 22), "t": "Rodoviário · R$ 580"},
        ],
    },
]


def seed():
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(models.CaseHistory).delete()
        db.query(models.CaseFactor).delete()
        db.query(models.Case).delete()
        db.query(models.BlocklistReason).delete()
        db.query(models.Blocklist).delete()
        db.commit()

        # Seed blocklist
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
        print(f"✓ Blocklist: {len(BLOCKLIST_SEED)} entries inserted")

        # Seed cases
        blocklist_names = {b["name"].lower() for b in BLOCKLIST_SEED}

        class FactorsObj:
            def __init__(self, d):
                self.blocklist = d["blocklist"]
                self.reincidencia = d["reincidencia"]
                self.transporte = d["transporte"]
                self.data = d["data"]

        for c in CASES_SEED:
            in_bl = c["name"].lower() in blocklist_names
            f_obj = FactorsObj(c["factors"])
            score, computed = calculate_score(db, c["name"], c["transport"], c["date"], f_obj, in_bl)

            case = models.Case(
                name=c["name"],
                initials=generate_initials(c["name"]),
                col=generate_color(),
                suspicion=c["suspicion"],
                hours=c["hours"],
                transport=c["transport"],
                value=c["value"],
                score=score,
                status=c["status"],
                date=c["date"],
                justification=c.get("justification"),
            )
            db.add(case)
            db.flush()

            db.add(models.CaseFactor(case_id=case.id, **computed))

            for h in c.get("history", []):
                db.add(models.CaseHistory(case_id=case.id, d=h["d"], t=h["t"]))

        db.commit()
        print(f"✓ Cases: {len(CASES_SEED)} cases inserted")
        print("Seed complete.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
