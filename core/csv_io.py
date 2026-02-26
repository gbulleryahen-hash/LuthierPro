"""core/csv_io.py — Import / Export CSV pour clients, articles, documents"""
import csv
import io
import os
from datetime import datetime


# ──────────────────────────────────────────────────────────────
# ARTICLES
# ──────────────────────────────────────────────────────────────

ARTICLES_HEADERS = ["nom", "reference", "type", "prix_ht", "tva", "unite", "description"]
ARTICLES_HEADERS_FR = ["Désignation", "Référence", "Type", "Prix HT", "TVA %", "Unité", "Description"]

def export_articles_csv(articles) -> str:
    """Retourne le contenu CSV des articles en string."""
    out = io.StringIO()
    w = csv.writer(out, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    w.writerow(ARTICLES_HEADERS_FR)
    for a in articles:
        w.writerow([
            a["nom"] or "", a["reference"] or "", a["type"] or "service",
            f'{float(a["prix_ht"] or 0):.2f}', f'{float(a["tva"] or 20):g}',
            a["unite"] or "unité", a["description"] or ""
        ])
    return out.getvalue()

def import_articles_csv(content: str, db) -> tuple:
    """
    Importe des articles depuis un contenu CSV.
    Retourne (nb_importés, nb_doublons, erreurs)
    """
    imported = 0
    skipped  = 0
    errors   = []

    # Détecter séparateur
    sep = ";" if content.count(";") >= content.count(",") else ","
    reader = csv.DictReader(io.StringIO(content), delimiter=sep)

    # Normalisation des colonnes
    ALIASES = {
        "nom": ["nom","désignation","designation","libelle","libellé","article"],
        "reference": ["reference","référence","ref","code","sku"],
        "type": ["type"],
        "prix_ht": ["prix_ht","prix ht","prix","pu","tarif","montant"],
        "tva": ["tva","tva %","taux tva","tva_rate"],
        "unite": ["unite","unité","unit","unité de vente"],
        "description": ["description","desc","détail","detail"],
    }

    existing = {(a["nom"].lower(), (a["reference"] or "").lower()) for a in db.get_articles()}

    for row_num, row in enumerate(reader, start=2):
        # Mapper les colonnes
        mapped = {}
        for field, aliases in ALIASES.items():
            for alias in aliases:
                for col in row.keys():
                    if col.strip().lower() == alias:
                        mapped[field] = row[col].strip()
                        break
                if field in mapped:
                    break

        if not mapped.get("nom"):
            errors.append(f"Ligne {row_num} : nom manquant, ignorée")
            continue

        # Normaliser
        nom = mapped.get("nom","").strip()
        ref = mapped.get("reference","").strip()

        # Doublon ?
        if (nom.lower(), ref.lower()) in existing:
            skipped += 1
            continue

        try:
            prix = float(mapped.get("prix_ht","0").replace(",",".") or 0)
            tva  = float(mapped.get("tva","20").replace(",",".").replace("%","") or 20)
        except ValueError:
            errors.append(f"Ligne {row_num} : prix ou TVA invalide")
            continue

        # Normaliser type
        raw_type = (mapped.get("type","") or "service").lower()
        type_map = {"service":"service","prestation":"service","produit":"produit",
                    "product":"produit","frais":"frais","expense":"frais"}
        article_type = type_map.get(raw_type, "service")

        data = {
            "nom": nom, "reference": ref, "type": article_type,
            "prix_ht": prix, "tva": tva,
            "unite": mapped.get("unite","unité") or "unité",
            "description": mapped.get("description","") or "",
        }
        db.save_article(data)
        existing.add((nom.lower(), ref.lower()))
        imported += 1

    return imported, skipped, errors


# ──────────────────────────────────────────────────────────────
# CLIENTS
# ──────────────────────────────────────────────────────────────

CLIENTS_HEADERS_FR = ["Nom","Prénom","Société","Email","Téléphone","Adresse","Code postal","Ville","SIRET","N° TVA","Notes"]
CLIENTS_FIELDS     = ["nom","prenom","societe","email","telephone","adresse","cp","ville","siret","tva_intra","notes"]

def export_clients_csv(clients) -> str:
    out = io.StringIO()
    w = csv.writer(out, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    w.writerow(CLIENTS_HEADERS_FR)
    for c in clients:
        w.writerow([c[f] or "" for f in CLIENTS_FIELDS])
    return out.getvalue()

def import_clients_csv(content: str, db) -> tuple:
    imported = 0
    skipped  = 0
    errors   = []

    sep = ";" if content.count(";") >= content.count(",") else ","
    reader = csv.DictReader(io.StringIO(content), delimiter=sep)

    ALIASES = {
        "nom":       ["nom","name","last name","lastname","nom de famille"],
        "prenom":    ["prenom","prénom","first name","firstname"],
        "societe":   ["societe","société","company","entreprise","raison sociale"],
        "email":     ["email","e-mail","mail","courriel"],
        "telephone": ["telephone","téléphone","tel","tél","phone","mobile"],
        "adresse":   ["adresse","address","rue","street"],
        "cp":        ["cp","code postal","zip","postal code","code_postal"],
        "ville":     ["ville","city","localité"],
        "siret":     ["siret"],
        "tva_intra": ["tva_intra","tva intra","n° tva","numero tva","vat"],
        "notes":     ["notes","note","commentaire","remarque"],
    }

    existing_emails = {c["email"].lower() for c in db.get_clients() if c["email"]}

    for row_num, row in enumerate(reader, start=2):
        mapped = {}
        for field, aliases in ALIASES.items():
            for alias in aliases:
                for col in row.keys():
                    if col.strip().lower() == alias:
                        mapped[field] = row[col].strip()
                        break
                if field in mapped:
                    break

        nom     = mapped.get("nom","").strip()
        societe = mapped.get("societe","").strip()
        if not nom and not societe:
            errors.append(f"Ligne {row_num} : nom ou société requis, ignorée")
            continue

        email = mapped.get("email","").lower().strip()
        if email and email in existing_emails:
            skipped += 1
            continue

        data = {f: mapped.get(f,"") for f in CLIENTS_FIELDS}
        db.save_client(data)
        if email:
            existing_emails.add(email)
        imported += 1

    return imported, skipped, errors


# ──────────────────────────────────────────────────────────────
# SAUVEGARDE GÉNÉRALE (JSON)
# ──────────────────────────────────────────────────────────────

def export_backup_json(db) -> str:
    """Exporte toute la base en JSON."""
    import json

    clients  = [dict(c) for c in db.get_clients()]
    articles = [dict(a) for a in db.get_articles()]
    guitares = [dict(g) for g in db.get_guitares()]

    devis    = []
    factures = []
    for doc in db.get_documents("devis"):
        d = dict(doc)
        d["lignes"] = [dict(l) for l in db.get_document_lignes(doc["id"])]
        d["bilan"]  = db.get_bilan(doc["id"])
        devis.append(d)
    for doc in db.get_documents("facture"):
        d = dict(doc)
        d["lignes"] = [dict(l) for l in db.get_document_lignes(doc["id"])]
        d["bilan"]  = db.get_bilan(doc["id"])
        factures.append(d)

    settings = db.get_all_settings()

    backup = {
        "lutherpro_version": "1.0",
        "export_date": datetime.now().isoformat(),
        "settings": settings,
        "clients":  clients,
        "articles": articles,
        "guitares": guitares,
        "devis":    devis,
        "factures": factures,
    }
    return json.dumps(backup, ensure_ascii=False, indent=2, default=str)


def import_backup_json(content: str, db) -> dict:
    """
    Importe une sauvegarde JSON complète.
    Retourne un dict de stats {clients, articles, guitares, devis, factures}
    """
    import json
    data = json.loads(content)
    stats = {"clients":0,"articles":0,"guitares":0,"devis":0,"factures":0}

    # Settings (ne pas écraser le logo existant)
    if "settings" in data:
        for k, v in data["settings"].items():
            if k not in ("logo_path",):  # on ne réimporte pas le chemin du logo
                db.set_setting(k, v)

    # Clients
    client_id_map = {}
    for c in data.get("clients", []):
        old_id = c.get("id")
        c_data = {f: c.get(f,"") for f in ["nom","prenom","societe","email","telephone","adresse","cp","ville","siret","tva_intra","notes"]}
        new_id = db.save_client(c_data)
        if old_id:
            client_id_map[old_id] = new_id
        stats["clients"] += 1

    # Articles
    for a in data.get("articles", []):
        a_data = {f: a.get(f,"") for f in ["nom","reference","type","prix_ht","tva","unite","description"]}
        db.save_article(a_data)
        stats["articles"] += 1

    # Guitares
    guitare_id_map = {}
    for g in data.get("guitares", []):
        old_id = g.get("id")
        old_client = g.get("client_id")
        g_data = {
            "marque": g.get("marque",""), "modele": g.get("modele",""),
            "type": g.get("type","électrique"), "serie": g.get("serie",""),
            "annee": g.get("annee",""), "couleur": g.get("couleur",""),
            "client_id": client_id_map.get(old_client),
            "valeur": g.get("valeur",0), "notes": g.get("notes",""),
        }
        new_id = db.save_guitare(g_data)
        if old_id:
            guitare_id_map[old_id] = new_id
        stats["guitares"] += 1

    # Documents
    for doc_list, key in [(data.get("devis",[]),"devis"), (data.get("factures",[]),"factures")]:
        for d in doc_list:
            old_client  = d.get("client_id")
            old_guitare = d.get("guitare_id")
            doc_data = {
                "type":         "devis" if key == "devis" else "facture",
                "numero":       d.get("numero",""),
                "client_id":    client_id_map.get(old_client),
                "guitare_id":   guitare_id_map.get(old_guitare),
                "date_doc":     d.get("date_doc",""),
                "date_echeance":d.get("date_echeance",""),
                "objet":        d.get("objet",""),
                "statut":       d.get("statut","brouillon"),
                "tva_rate":     d.get("tva_rate",20),
                "total_ht":     d.get("total_ht",0),
                "total_tva":    d.get("total_tva",0),
                "total_ttc":    d.get("total_ttc",0),
                "notes":        d.get("notes",""),
                "devis_ref":    d.get("devis_ref",""),
            }
            lignes = [{"designation":l.get("designation",""),"quantite":l.get("quantite",1),"prix_ht":l.get("prix_ht",0)}
                      for l in d.get("lignes",[])]
            bilan  = d.get("bilan",{})
            db.save_document(doc_data, lignes, bilan)
            stats[key] += 1

    return stats


# ──────────────────────────────────────────────────────────────
# EXPORT DOCUMENTS CSV (liste devis ou factures)
# ──────────────────────────────────────────────────────────────

def export_documents_csv(docs, db) -> str:
    out = io.StringIO()
    w = csv.writer(out, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    w.writerow(["Numéro","Type","Date","Échéance","Client","Objet","Total HT","TVA","Total TTC","Statut","Réf. devis"])
    for d in docs:
        client = " — ".join(filter(None,[d["client_societe"] or "",
                                          " ".join(filter(None,[d["client_prenom"] or "", d["client_nom"] or ""]))]))
        w.writerow([
            d["numero"], d["type"], d["date_doc"] or "", d["date_echeance"] or "",
            client, d["objet"] or "",
            f'{float(d["total_ht"] or 0):.2f}',
            f'{float(d["total_tva"] or 0):.2f}',
            f'{float(d["total_ttc"] or 0):.2f}',
            d["statut"] or "", d["devis_ref"] or ""
        ])
    return out.getvalue()
