# LuthierPro
LuthierPro est un logiciel de gestion conçu spécifiquement pour les luthiers et artisans de la musique. Il permet de gérer l'intégralité de l'activité commerciale : devis, factures, clients, parc de guitares et articles/services.
# 🎸 LuthierPro

**Logiciel de gestion pour luthiers et artisans de la musique**

> Devis · Factures · Clients · Parc guitares · Bilan trimestriel

[![Licence: GPL v3](https://img.shields.io/badge/Licence-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/Interface-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

---

## Fonctionnalités

- **Tableau de bord** — CA du mois, devis en attente, factures impayées
- **Devis** — création, suivi, conversion en facture, envoi email
- **Factures** — facturation avec bilan technique guitare, coordonnées bancaires
- **Clients** — carnet d'adresses avec historique complet
- **Articles & Services** — catalogue réutilisable (services / produits / frais)
- **Parc guitares** — fiche par instrument + historique des interventions
- **Bilan trimestriel** — ventilation par type, aide à la déclaration URSSAF
- **PDF professionnels** — Playfair Display · DM Sans · DM Mono (incluses)

## Installation rapide

```bash
# 1. Extraire l'archive
unzip lutherpro.zip -d lutherpro/
cd lutherpro/

# 2. Installer les dépendances
pip install PySide6 reportlab

# 3. Lancer
python main.py
```

> **Windows** : lors de l'installation de Python, cochez "Add Python to PATH".

## Dépendances

| Package   | Version | Licence  |
|-----------|---------|----------|
| PySide6   | >= 6.5  | LGPL v3  |
| ReportLab | >= 4.0  | BSD      |
| Python    | >= 3.10 | PSF      |

## Données utilisateur

Stockées localement dans `~/LuthierPro/lutherpro.db` (SQLite).
Aucun serveur, aucun compte, aucune connexion internet requise.

**Sauvegarde** : copiez régulièrement `~/LuthierPro/lutherpro.db` sur un support externe.

## Licence

LuthierPro est un logiciel libre distribué sous la licence **GNU GPL v3**.
Voir le fichier [LICENSE](LICENSE) pour le texte complet.

---
*Fait avec ❤️ pour les luthiers*
