"""
core/database.py — Couche base de données SQLite
"""
import sqlite3
import os
import json
import shutil
from pathlib import Path
from datetime import date


# ── Config externe (stockée dans AppData ou ~/.config) ───────
# Permet de mémoriser le chemin DB même si on le change.

def _config_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    cfg_dir = base / "LuthierPro"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / "config.json"


def load_config() -> dict:
    p = _config_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(data: dict):
    _config_path().write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_db_path() -> Path:
    cfg = load_config()
    if cfg.get("db_path"):
        p = Path(cfg["db_path"])
        if p.parent.exists():
            return p
    default = Path.home() / "LuthierPro" / "lutherpro.db"
    default.parent.mkdir(exist_ok=True)
    return default


class Database:
    def __init__(self):
        self.db_path = get_db_path()
        self.conn = None

    def initialize(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._migrate()
        self._set_default_logo()

    def change_db_path(self, new_path: str, move_file: bool = True) -> tuple:
        """
        Change le chemin de la base de données.
        move_file=True : déplace le fichier existant vers le nouveau chemin.
        Retourne (success: bool, message: str)
        """
        new = Path(new_path)
        try:
            new.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Impossible de créer le dossier :\n{e}"

        if move_file and self.db_path.exists() and new != self.db_path:
            if new.exists():
                return False, f"Un fichier existe déjà à cet emplacement :\n{new}"
            try:
                shutil.move(str(self.db_path), str(new))
            except Exception as e:
                return False, f"Impossible de déplacer la base de données :\n{e}"

        # Mémoriser dans config.json
        cfg = load_config()
        cfg["db_path"] = str(new)
        save_config(cfg)

        # Reconnecter
        if self.conn:
            self.conn.close()
        self.db_path = new
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return True, str(new)

    # ──────────────────────────────────────────────────────────
    def _create_tables(self):
        c = self.conn
        c.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS clients (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nom       TEXT,
            prenom    TEXT,
            societe   TEXT,
            email     TEXT,
            telephone TEXT,
            adresse   TEXT,
            cp        TEXT,
            ville     TEXT,
            siret     TEXT,
            tva_intra TEXT,
            notes     TEXT,
            created_at TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nom         TEXT NOT NULL,
            reference   TEXT,
            type        TEXT DEFAULT 'service',
            prix_ht     REAL DEFAULT 0,
            tva         REAL DEFAULT 20,
            unite       TEXT DEFAULT 'unité',
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS guitares (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            marque     TEXT NOT NULL,
            modele     TEXT NOT NULL,
            type       TEXT DEFAULT 'électrique',
            serie      TEXT,
            annee      TEXT,
            couleur    TEXT,
            client_id  INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            valeur     REAL DEFAULT 0,
            notes      TEXT,
            created_at TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL CHECK(type IN ('devis','facture')),
            numero      TEXT NOT NULL,
            client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            guitare_id  INTEGER REFERENCES guitares(id) ON DELETE SET NULL,
            date_doc    TEXT NOT NULL,
            date_echeance TEXT,
            objet       TEXT,
            statut      TEXT DEFAULT 'brouillon',
            tva_rate    REAL DEFAULT 20,
            total_ht    REAL DEFAULT 0,
            total_tva   REAL DEFAULT 0,
            total_ttc   REAL DEFAULT 0,
            notes       TEXT,
            devis_ref   TEXT,
            created_at  TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS document_lignes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            designation TEXT,
            quantite    REAL DEFAULT 1,
            prix_ht     REAL DEFAULT 0,
            position    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS bilans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            champ       TEXT NOT NULL,
            val_avant   TEXT DEFAULT '',
            val_apres   TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS bilan_observations (
            document_id  INTEGER PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
            observations TEXT DEFAULT ''
        );
        """)
        c.commit()

    def _migrate(self):
        # Migration 1 : devis_ref sur documents
        try:
            self.conn.execute("ALTER TABLE documents ADD COLUMN devis_ref TEXT")
            self.conn.commit()
        except Exception:
            pass
        # Migration 2 : type_article sur document_lignes
        try:
            self.conn.execute("ALTER TABLE document_lignes ADD COLUMN type_article TEXT DEFAULT 'service'")
            self.conn.commit()
        except Exception:
            pass

    def _set_default_logo(self):
        if self.get_setting("logo_path"):
            return
        src = os.path.join(os.path.dirname(__file__), "..", "resources", "logo.png")
        src = os.path.normpath(src)
        if os.path.exists(src):
            import shutil as _sh
            dest = self.db_path.parent / "logo.png"
            if not dest.exists():
                _sh.copy(src, dest)
            self.set_setting("logo_path", str(dest))

    def close(self):
        if self.conn:
            self.conn.close()

    # ── SETTINGS ──────────────────────────────────────────────
    def get_setting(self, key, default=""):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, str(value)))
        self.conn.commit()

    def get_all_settings(self):
        rows = self.conn.execute("SELECT key, value FROM settings").fetchall()
        return {r[0]: r[1] for r in rows}

    # ── CLIENTS ───────────────────────────────────────────────
    def get_clients(self, search=""):
        q = f"%{search}%"
        return self.conn.execute("""
            SELECT * FROM clients
            WHERE nom LIKE ? OR prenom LIKE ? OR societe LIKE ? OR email LIKE ? OR ville LIKE ?
            ORDER BY COALESCE(NULLIF(societe,''), nom) COLLATE NOCASE
        """, (q,q,q,q,q)).fetchall()

    def get_client(self, client_id):
        return self.conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()

    def save_client(self, data, client_id=None):
        fields = ["nom","prenom","societe","email","telephone","adresse","cp","ville","siret","tva_intra","notes"]
        vals = [data.get(f,"") for f in fields]
        if client_id:
            sets = ", ".join(f"{f}=?" for f in fields)
            self.conn.execute(f"UPDATE clients SET {sets} WHERE id=?", vals + [client_id])
        else:
            placeholders = ",".join("?" * len(fields))
            cols = ",".join(fields)
            self.conn.execute(f"INSERT INTO clients ({cols}) VALUES ({placeholders})", vals)
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0] if not client_id else client_id

    def delete_client(self, client_id):
        self.conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
        self.conn.commit()

    def get_client_total(self, client_id):
        row = self.conn.execute("""
            SELECT COALESCE(SUM(total_ttc),0) FROM documents
            WHERE client_id=? AND type='facture' AND statut='payé'
        """, (client_id,)).fetchone()
        return row[0] if row else 0

    # ── ARTICLES ──────────────────────────────────────────────
    def get_articles(self, search=""):
        q = f"%{search}%"
        return self.conn.execute("""
            SELECT * FROM articles
            WHERE nom LIKE ? OR reference LIKE ? OR description LIKE ?
            ORDER BY nom COLLATE NOCASE
        """, (q,q,q)).fetchall()

    def get_article(self, article_id):
        return self.conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()

    def save_article(self, data, article_id=None):
        fields = ["nom","reference","type","prix_ht","tva","unite","description"]
        vals = [data.get(f,"") for f in fields]
        if article_id:
            sets = ", ".join(f"{f}=?" for f in fields)
            self.conn.execute(f"UPDATE articles SET {sets} WHERE id=?", vals + [article_id])
        else:
            placeholders = ",".join("?" * len(fields))
            cols = ",".join(fields)
            self.conn.execute(f"INSERT INTO articles ({cols}) VALUES ({placeholders})", vals)
        self.conn.commit()

    def delete_article(self, article_id):
        self.conn.execute("DELETE FROM articles WHERE id=?", (article_id,))
        self.conn.commit()

    # ── GUITARES ──────────────────────────────────────────────
    def get_guitares(self, search="", client_id=None):
        q = f"%{search}%"
        sql = """
            SELECT g.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM guitares g
            LEFT JOIN clients c ON g.client_id = c.id
            WHERE (g.marque LIKE ? OR g.modele LIKE ? OR g.serie LIKE ? OR g.couleur LIKE ?)
        """
        params = [q,q,q,q]
        if client_id:
            sql += " AND g.client_id=?"
            params.append(client_id)
        sql += " ORDER BY g.marque COLLATE NOCASE"
        return self.conn.execute(sql, params).fetchall()

    def get_guitare(self, guitare_id):
        return self.conn.execute("""
            SELECT g.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM guitares g LEFT JOIN clients c ON g.client_id=c.id
            WHERE g.id=?
        """, (guitare_id,)).fetchone()

    def save_guitare(self, data, guitare_id=None):
        fields = ["marque","modele","type","serie","annee","couleur","client_id","valeur","notes"]
        vals = [data.get(f) or None for f in fields]
        if guitare_id:
            sets = ", ".join(f"{f}=?" for f in fields)
            self.conn.execute(f"UPDATE guitares SET {sets} WHERE id=?", vals + [guitare_id])
            self.conn.commit()
            return guitare_id
        else:
            placeholders = ",".join("?" * len(fields))
            cols = ",".join(fields)
            cur = self.conn.execute(f"INSERT INTO guitares ({cols}) VALUES ({placeholders})", vals)
            self.conn.commit()
            return cur.lastrowid

    def delete_guitare(self, guitare_id):
        self.conn.execute("DELETE FROM guitares WHERE id=?", (guitare_id,))
        self.conn.commit()

    def get_guitare_interventions(self, guitare_id):
        return self.conn.execute("""
            SELECT d.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM documents d
            LEFT JOIN clients c ON d.client_id=c.id
            WHERE d.guitare_id=?
            ORDER BY d.date_doc DESC
        """, (guitare_id,)).fetchall()

    # ── DOCUMENTS ─────────────────────────────────────────────
    def get_documents(self, doc_type, search="", statut=""):
        q = f"%{search}%"
        sql = """
            SELECT d.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM documents d
            LEFT JOIN clients c ON d.client_id=c.id
            WHERE d.type=? AND (d.numero LIKE ? OR d.objet LIKE ? OR c.nom LIKE ? OR c.societe LIKE ?)
        """
        params = [doc_type, q, q, q, q]
        if statut:
            sql += " AND d.statut=?"
            params.append(statut)
        sql += " ORDER BY d.date_doc DESC"
        return self.conn.execute(sql, params).fetchall()

    def get_document(self, doc_id):
        return self.conn.execute("""
            SELECT d.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe,
                   c.adresse as client_adresse, c.cp as client_cp, c.ville as client_ville,
                   c.email as client_email, c.telephone as client_tel,
                   g.marque as guitare_marque, g.modele as guitare_modele, g.serie as guitare_serie
            FROM documents d
            LEFT JOIN clients c ON d.client_id=c.id
            LEFT JOIN guitares g ON d.guitare_id=g.id
            WHERE d.id=?
        """, (doc_id,)).fetchone()

    def get_document_lignes(self, doc_id):
        return self.conn.execute("""
            SELECT * FROM document_lignes WHERE document_id=? ORDER BY position
        """, (doc_id,)).fetchall()

    def get_bilan(self, doc_id):
        rows = self.conn.execute("SELECT * FROM bilans WHERE document_id=?", (doc_id,)).fetchall()
        obs = self.conn.execute("SELECT observations FROM bilan_observations WHERE document_id=?", (doc_id,)).fetchone()
        bilan = {r["champ"]: {"avant": r["val_avant"], "apres": r["val_apres"]} for r in rows}
        bilan["_observations"] = obs[0] if obs else ""
        return bilan

    def next_numero(self, doc_type):
        prefix = self.get_setting("devisPrefix", "DEV-") if doc_type == "devis" else self.get_setting("facturePrefix", "FAC-")
        if not prefix:
            prefix = "DEV-" if doc_type == "devis" else "FAC-"
        row = self.conn.execute("SELECT COUNT(*) FROM documents WHERE type=?", (doc_type,)).fetchone()
        n = (row[0] or 0) + 1
        return f"{prefix}{n:04d}"

    def save_document(self, data, lignes, bilan, doc_id=None):
        fields = ["type","numero","client_id","guitare_id","date_doc","date_echeance",
                  "objet","statut","tva_rate","total_ht","total_tva","total_ttc","notes","devis_ref"]
        vals = [data.get(f) for f in fields]

        if doc_id:
            sets = ", ".join(f"{f}=?" for f in fields)
            self.conn.execute(f"UPDATE documents SET {sets} WHERE id=?", vals + [doc_id])
        else:
            placeholders = ",".join("?" * len(fields))
            cols = ",".join(fields)
            cur = self.conn.execute(f"INSERT INTO documents ({cols}) VALUES ({placeholders})", vals)
            doc_id = cur.lastrowid

        self.conn.execute("DELETE FROM document_lignes WHERE document_id=?", (doc_id,))
        for i, l in enumerate(lignes):
            self.conn.execute("""
                INSERT INTO document_lignes(document_id,designation,type_article,quantite,prix_ht,position)
                VALUES(?,?,?,?,?,?)
            """, (doc_id, l.get("designation",""), l.get("type_article","service"),
                  l.get("quantite",1), l.get("prix_ht",0), i))

        self.conn.execute("DELETE FROM bilans WHERE document_id=?", (doc_id,))
        self.conn.execute("DELETE FROM bilan_observations WHERE document_id=?", (doc_id,))
        for champ, vals_bilan in bilan.items():
            if champ == "_observations":
                self.conn.execute("INSERT OR REPLACE INTO bilan_observations(document_id,observations) VALUES(?,?)",
                                  (doc_id, vals_bilan))
            else:
                self.conn.execute("INSERT INTO bilans(document_id,champ,val_avant,val_apres) VALUES(?,?,?,?)",
                                  (doc_id, champ, vals_bilan.get("avant",""), vals_bilan.get("apres","")))

        self.conn.commit()
        return doc_id

    def delete_document(self, doc_id):
        self.conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
        self.conn.commit()

    def convert_devis_to_facture(self, devis_id):
        devis = self.get_document(devis_id)
        if not devis: return None
        lignes = self.get_document_lignes(devis_id)
        bilan  = self.get_bilan(devis_id)
        self.conn.execute("UPDATE documents SET statut='accepté' WHERE id=?", (devis_id,))
        numero = self.next_numero("facture")
        data = {
            "type": "facture", "numero": numero,
            "client_id": devis["client_id"], "guitare_id": devis["guitare_id"],
            "date_doc": date.today().isoformat(), "date_echeance": "",
            "objet": devis["objet"], "statut": "envoyé",
            "tva_rate": devis["tva_rate"],
            "total_ht": devis["total_ht"], "total_tva": devis["total_tva"], "total_ttc": devis["total_ttc"],
            "notes": devis["notes"], "devis_ref": devis["numero"],
        }
        lignes_data = [{"designation": l["designation"], "quantite": l["quantite"], "prix_ht": l["prix_ht"]} for l in lignes]
        new_id = self.save_document(data, lignes_data, bilan)
        self.conn.commit()
        return new_id

    # ── DASHBOARD ─────────────────────────────────────────────
    def get_dashboard_stats(self):
        from datetime import date
        month = date.today().strftime("%Y-%m")
        stats = {}
        stats["ca_mois"] = self.conn.execute("""
            SELECT COALESCE(SUM(total_ttc),0) FROM documents
            WHERE type='facture' AND statut='payé' AND date_doc LIKE ?
        """, (f"{month}%",)).fetchone()[0]
        stats["a_encaisser"] = self.conn.execute("""
            SELECT COALESCE(SUM(total_ttc),0) FROM documents
            WHERE type='facture' AND statut='envoyé'
        """).fetchone()[0]
        stats["en_retard"] = self.conn.execute("""
            SELECT COALESCE(SUM(total_ttc),0) FROM documents
            WHERE type='facture' AND statut='en retard'
        """).fetchone()[0]
        stats["devis_en_cours"] = self.conn.execute("""
            SELECT COUNT(*) FROM documents WHERE type='devis' AND statut IN ('envoyé','brouillon')
        """).fetchone()[0]
        stats["derniers_docs"] = self.conn.execute("""
            SELECT d.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM documents d LEFT JOIN clients c ON d.client_id=c.id
            ORDER BY d.created_at DESC LIMIT 8
        """).fetchall()
        return stats

    # ── BILAN PÉRIODIQUE ──────────────────────────────────────
    def get_bilan_periode(self, date_debut, date_fin, statuts=None):
        """
        Bilan des factures entre deux dates (format YYYY-MM-DD).
        Retourne un dict avec :
          - total_ht, total_tva, total_ttc
          - total_produits_ht, total_services_ht, total_frais_ht
          - nb_factures
          - factures : liste des factures
          - detail_par_client : list of (client, total_ttc)
        """
        if statuts is None:
            statuts = ["payé", "envoyé", "en retard"]

        placeholders = ",".join("?" * len(statuts))
        params = [date_debut, date_fin] + statuts

        rows = self.conn.execute(f"""
            SELECT d.*, c.nom as client_nom, c.prenom as client_prenom, c.societe as client_societe
            FROM documents d
            LEFT JOIN clients c ON d.client_id = c.id
            WHERE d.type='facture'
              AND d.date_doc >= ?
              AND d.date_doc <= ?
              AND d.statut IN ({placeholders})
            ORDER BY d.date_doc
        """, params).fetchall()

        doc_ids = [r["id"] for r in rows]

        # Totaux globaux
        total_ht  = sum(float(r["total_ht"]  or 0) for r in rows)
        total_tva = sum(float(r["total_tva"] or 0) for r in rows)
        total_ttc = sum(float(r["total_ttc"] or 0) for r in rows)

        # Détail produits / services / frais depuis les lignes
        total_services = 0.0
        total_produits = 0.0
        total_frais    = 0.0

        if doc_ids:
            ph2 = ",".join("?" * len(doc_ids))
            lignes = self.conn.execute(f"""
                SELECT type_article, quantite, prix_ht
                FROM document_lignes
                WHERE document_id IN ({ph2})
            """, doc_ids).fetchall()
            for l in lignes:
                montant = float(l["quantite"] or 1) * float(l["prix_ht"] or 0)
                t = (l["type_article"] or "service").lower()
                if t == "produit":
                    total_produits += montant
                elif t == "frais":
                    total_frais += montant
                else:
                    total_services += montant

        # Par client
        from collections import defaultdict
        by_client = defaultdict(float)
        for r in rows:
            parts = []
            if r["client_societe"]: parts.append(r["client_societe"])
            name = f'{r["client_prenom"] or ""} {r["client_nom"] or ""}'.strip()
            if name: parts.append(name)
            cname = " — ".join(parts) if parts else "Client inconnu"
            by_client[cname] += float(r["total_ttc"] or 0)

        return {
            "factures":           [dict(r) for r in rows],
            "nb_factures":        len(rows),
            "total_ht":           total_ht,
            "total_tva":          total_tva,
            "total_ttc":          total_ttc,
            "total_services_ht":  total_services,
            "total_produits_ht":  total_produits,
            "total_frais_ht":     total_frais,
            "par_client":         sorted(by_client.items(), key=lambda x: -x[1]),
        }
