"""Génère data/code_du_travail_extraits.pdf — corpus pédagogique pour le RAG."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ARTICLES = {
    "Partie 1 — Le contrat de travail": [
        ("L.1121-1", "Nul ne peut apporter aux droits des personnes et aux libertés individuelles et collectives de restrictions qui ne seraient pas justifiées par la nature de la tâche à accomplir ni proportionnées au but recherché."),
        ("L.1221-1", "Le contrat de travail est soumis aux règles du droit commun. Il peut être établi selon les formes que les parties contractantes décident d'adopter."),
        ("L.1221-19", "Le contrat de travail à durée indéterminée peut comporter une période d'essai dont la durée maximale est de deux mois pour les ouvriers et employés, trois mois pour les agents de maîtrise et techniciens, et quatre mois pour les cadres."),
        ("L.1221-25", "Lorsqu'il est mis fin à la période d'essai par l'employeur, le salarié est prévenu dans un délai qui ne peut être inférieur à vingt-quatre heures en deçà de huit jours de présence, quarante-huit heures entre huit jours et un mois de présence, deux semaines après un mois de présence et un mois après trois mois de présence."),
        ("L.1222-9", "Le télétravail désigne toute forme d'organisation du travail dans laquelle un travail qui aurait pu être exécuté dans les locaux de l'employeur est effectué par un salarié hors de ces locaux de façon volontaire en utilisant les technologies de l'information et de la communication. Il est mis en place dans le cadre d'un accord collectif ou d'une charte élaborée par l'employeur."),
        ("L.1222-10", "L'employeur qui refuse d'accorder le bénéfice du télétravail à un salarié qui occupe un poste éligible dans les conditions prévues par accord collectif ou par la charte doit motiver sa réponse."),
        ("L.1222-11", "En cas de circonstances exceptionnelles, notamment de menace d'épidémie, ou en cas de force majeure, la mise en oeuvre du télétravail peut être considérée comme un aménagement du poste de travail rendu nécessaire pour permettre la continuité de l'activité de l'entreprise et garantir la protection des salariés."),
    ],
    "Partie 2 — Le contrat à durée déterminée (CDD)": [
        ("L.1242-1", "Un contrat de travail à durée déterminée, quel que soit son motif, ne peut avoir ni pour objet ni pour effet de pourvoir durablement un emploi lié à l'activité normale et permanente de l'entreprise."),
        ("L.1242-2", "Un contrat de travail à durée déterminée ne peut être conclu que pour l'exécution d'une tâche précise et temporaire, notamment le remplacement d'un salarié absent, l'accroissement temporaire de l'activité de l'entreprise, ou les emplois à caractère saisonnier."),
        ("L.1242-8", "La durée totale du contrat de travail à durée déterminée ne peut excéder dix-huit mois, renouvellement compris, sauf exceptions prévues par la loi ou par convention de branche."),
        ("L.1242-12", "Le contrat de travail à durée déterminée est établi par écrit et comporte la définition précise de son motif. À défaut, il est réputé conclu pour une durée indéterminée."),
        ("L.1243-8", "Lorsque, à l'issue d'un contrat de travail à durée déterminée, les relations contractuelles de travail ne se poursuivent pas par un contrat à durée indéterminée, le salarié a droit, à titre de complément de salaire, à une indemnité de fin de contrat égale à 10 % de la rémunération totale brute versée au salarié. Cette indemnité est dite prime de précarité."),
        ("L.1243-11", "Lorsque la relation contractuelle de travail se poursuit après l'échéance du terme du contrat à durée déterminée, celui-ci devient un contrat à durée indéterminée."),
    ],
    "Partie 3 — La rupture du contrat de travail": [
        ("L.1231-1", "Le contrat de travail à durée indéterminée peut être rompu à l'initiative de l'employeur ou du salarié, ou d'un commun accord, dans les conditions prévues par la loi."),
        ("L.1232-1", "Tout licenciement pour motif personnel est motivé et justifié par une cause réelle et sérieuse."),
        ("L.1232-2", "L'employeur qui envisage de licencier un salarié le convoque, avant toute décision, à un entretien préalable. La convocation est effectuée par lettre recommandée ou par lettre remise en main propre contre décharge."),
        ("L.1234-1", "Lorsque le licenciement n'est pas motivé par une faute grave, le salarié a droit à un préavis dont la durée est d'un mois s'il justifie chez le même employeur d'une ancienneté de services continus comprise entre six mois et moins de deux ans, et de deux mois pour une ancienneté d'au moins deux ans."),
        ("L.1234-9", "Le salarié titulaire d'un contrat de travail à durée indéterminée, licencié alors qu'il compte au moins huit mois d'ancienneté ininterrompus au service du même employeur, a droit, sauf en cas de faute grave, à une indemnité de licenciement."),
        ("L.1235-3", "Si le licenciement d'un salarié survient pour une cause qui n'est pas réelle et sérieuse, le juge peut proposer la réintégration du salarié dans l'entreprise. Si l'une ou l'autre des parties refuse, le juge octroie au salarié une indemnité à la charge de l'employeur, dont le montant est compris entre des montants minimaux et maximaux fixés par un barème en fonction de l'ancienneté du salarié."),
        ("L.1237-11", "L'employeur et le salarié peuvent convenir en commun des conditions de la rupture du contrat de travail qui les lie. Cette rupture conventionnelle, exclusive du licenciement ou de la démission, ne peut être imposée par l'une ou l'autre des parties."),
        ("L.1237-13", "La convention de rupture définit les conditions de celle-ci, notamment le montant de l'indemnité spécifique de rupture conventionnelle qui ne peut pas être inférieur à celui de l'indemnité de licenciement prévue à l'article L.1234-9. À compter de la date de sa signature, chacune des parties dispose d'un délai de quinze jours calendaires pour exercer son droit de rétractation."),
        ("L.1471-1", "Toute action portant sur l'exécution du contrat de travail se prescrit par deux ans à compter du jour où celui qui l'exerce a connu ou aurait dû connaître les faits lui permettant d'exercer son droit. Toute action portant sur la rupture du contrat de travail se prescrit par douze mois à compter de la notification de la rupture."),
    ],
    "Partie 4 — Durée du travail et repos": [
        ("L.3121-16", "Dès que le temps de travail quotidien atteint six heures, le salarié bénéficie d'un temps de pause d'une durée minimale de vingt minutes consécutives."),
        ("L.3121-18", "La durée quotidienne de travail effectif par salarié ne peut excéder dix heures, sauf dérogations prévues par la loi."),
        ("L.3121-20", "Au cours d'une même semaine, la durée maximale hebdomadaire de travail est de quarante-huit heures."),
        ("L.3121-22", "La durée hebdomadaire de travail calculée sur une période quelconque de douze semaines consécutives ne peut dépasser quarante-quatre heures, sauf dérogations."),
        ("L.3121-27", "La durée légale de travail effectif des salariés à temps complet est fixée à trente-cinq heures par semaine."),
        ("L.3121-28", "Toute heure accomplie au delà de la durée légale hebdomadaire est une heure supplémentaire qui ouvre droit à une majoration salariale ou, le cas échéant, à un repos compensateur équivalent."),
        ("L.3121-36", "À défaut d'accord, les heures supplémentaires donnent lieu à une majoration de salaire de 25 % pour chacune des huit premières heures supplémentaires, et de 50 % pour les heures suivantes."),
        ("L.3131-1", "Tout salarié bénéficie d'un repos quotidien d'une durée minimale de onze heures consécutives, sauf dérogations."),
        ("L.3132-1", "Il est interdit de faire travailler un même salarié plus de six jours par semaine."),
        ("L.3132-2", "Le repos hebdomadaire a une durée minimale de vingt-quatre heures consécutives auxquelles s'ajoutent les heures consécutives de repos quotidien, soit trente-cinq heures au total."),
    ],
    "Partie 5 — Congés et salaire": [
        ("L.3141-3", "Le salarié a droit à un congé de deux jours et demi ouvrables par mois de travail effectif chez le même employeur. La durée totale du congé exigible ne peut excéder trente jours ouvrables."),
        ("L.3142-1", "Le salarié a droit, sur justification, à un congé pour certains événements familiaux, notamment pour son mariage, la naissance d'un enfant ou le décès d'un proche."),
        ("L.1225-17", "La salariée a le droit de bénéficier d'un congé de maternité pendant une période qui commence six semaines avant la date présumée de l'accouchement et se termine dix semaines après la date de celui-ci, soit seize semaines au total pour une naissance simple."),
        ("L.1225-35", "Après la naissance de l'enfant, le père salarié bénéficie d'un congé de paternité et d'accueil de l'enfant de vingt-cinq jours calendaires, ou de trente-deux jours calendaires en cas de naissances multiples."),
        ("L.3221-2", "Tout employeur assure, pour un même travail ou pour un travail de valeur égale, l'égalité de rémunération entre les femmes et les hommes."),
        ("L.3231-2", "Le salaire minimum interprofessionnel de croissance (SMIC) assure aux salariés dont les rémunérations sont les plus faibles la garantie de leur pouvoir d'achat et une participation au développement économique de la nation."),
        ("L.3242-1", "La rémunération des salariés est mensuelle et indépendante, pour un horaire de travail effectif déterminé, du nombre de jours travaillés dans le mois."),
    ],
    "Partie 6 — Santé, sécurité, harcèlement et discrimination": [
        ("L.4121-1", "L'employeur prend les mesures nécessaires pour assurer la sécurité et protéger la santé physique et mentale des travailleurs. Ces mesures comprennent des actions de prévention des risques professionnels, des actions d'information et de formation, et la mise en place d'une organisation et de moyens adaptés."),
        ("L.4131-1", "Le travailleur alerte immédiatement l'employeur de toute situation de travail dont il a un motif raisonnable de penser qu'elle présente un danger grave et imminent pour sa vie ou sa santé. Il peut se retirer d'une telle situation : c'est le droit de retrait."),
        ("L.1152-1", "Aucun salarié ne doit subir les agissements répétés de harcèlement moral qui ont pour objet ou pour effet une dégradation de ses conditions de travail susceptible de porter atteinte à ses droits et à sa dignité, d'altérer sa santé physique ou mentale ou de compromettre son avenir professionnel."),
        ("L.1153-1", "Aucun salarié ne doit subir des faits de harcèlement sexuel, constitué par des propos ou comportements à connotation sexuelle ou sexiste répétés qui portent atteinte à sa dignité ou créent à son encontre une situation intimidante, hostile ou offensante."),
        ("L.1132-1", "Aucune personne ne peut être écartée d'une procédure de recrutement, ni sanctionnée, ni licenciée en raison notamment de son origine, de son sexe, de son âge, de son état de santé, de son handicap, de ses opinions politiques, de ses activités syndicales ou de ses convictions religieuses. C'est le principe de non-discrimination."),
    ],
    "Partie 7 — Représentation du personnel et contentieux": [
        ("L.2311-2", "Un comité social et économique (CSE) est mis en place dans les entreprises d'au moins onze salariés. Sa mise en place n'est obligatoire que si l'effectif d'au moins onze salariés est atteint pendant douze mois consécutifs."),
        ("L.2312-8", "Le comité social et économique a pour mission d'assurer une expression collective des salariés permettant la prise en compte permanente de leurs intérêts dans les décisions relatives à la gestion et à l'évolution économique et financière de l'entreprise, à l'organisation du travail et à la formation professionnelle."),
        ("L.2143-3", "Chaque organisation syndicale représentative dans l'entreprise ou l'établissement d'au moins cinquante salariés peut désigner un délégué syndical pour la représenter auprès de l'employeur."),
        ("L.1411-1", "Le conseil de prud'hommes règle par voie de conciliation les différends qui peuvent s'élever à l'occasion de tout contrat de travail entre les employeurs et les salariés. Il juge les litiges lorsque la conciliation n'a pas abouti."),
        ("L.6323-1", "Un compte personnel de formation (CPF) est ouvert pour toute personne dès son entrée sur le marché du travail. Il permet d'acquérir des droits à la formation mobilisables tout au long de la vie professionnelle."),
    ],
}

styles = getSampleStyleSheet()
title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=20, spaceAfter=6)
note_style = ParagraphStyle("N", parent=styles["Normal"], fontSize=9,
                            textColor="#555555", spaceAfter=18)
part_style = ParagraphStyle("P", parent=styles["Heading1"], fontSize=14,
                            spaceBefore=18, spaceAfter=8, textColor="#1a3a5c")
art_style = ParagraphStyle("A", parent=styles["Heading3"], fontSize=11,
                           spaceBefore=10, spaceAfter=2, textColor="#333333")
body_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=10,
                            leading=14, alignment=4)  # justify

story = [
    Paragraph("Code du travail — Extraits", title_style),
    Paragraph("Corpus pédagogique pour projet RAG (M2 MD5). Articles reformulés de manière "
              "simplifiée à des fins d'enseignement : le texte officiel consolidé fait foi "
              "et doit être vérifié sur legifrance.gouv.fr.", note_style),
]
for part, articles in ARTICLES.items():
    story.append(Paragraph(part, part_style))
    for ref, text in articles:
        story.append(Paragraph(f"Article {ref}", art_style))
        story.append(Paragraph(text, body_style))

doc = SimpleDocTemplate("data/code_du_travail_extraits.pdf", pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Code du travail — Extraits pédagogiques")
doc.build(story)

n = sum(len(a) for a in ARTICLES.values())
print(f"PDF généré : data/code_du_travail_extraits.pdf ({n} articles)")
