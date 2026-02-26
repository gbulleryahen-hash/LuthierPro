"""
core/i18n.py — Internationalisation de LuthierPro (FR / EN / ES)

Usage :
    from core.i18n import t, set_language, current_language
    label = t("nav.dashboard")     # → "Tableau de bord" / "Dashboard" / "Panel principal"

La langue est persistée dans la base de données (clé "language").
"""

_LANG = "fr"   # langue active

# ══════════════════════════════════════════════════════════════════════════════
# DICTIONNAIRE DE TRADUCTIONS
# ══════════════════════════════════════════════════════════════════════════════
_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── Navigation sidebar ────────────────────────────────────────────────────
    "nav.principal":      {"fr": "PRINCIPAL",           "en": "MAIN",             "es": "PRINCIPAL"},
    "nav.documents":      {"fr": "DOCUMENTS",           "en": "DOCUMENTS",        "es": "DOCUMENTOS"},
    "nav.database":       {"fr": "BASE DE DONNÉES",     "en": "DATABASE",         "es": "BASE DE DATOS"},
    "nav.analysis":       {"fr": "ANALYSE",             "en": "ANALYSIS",         "es": "ANÁLISIS"},
    "nav.dashboard":      {"fr": "Tableau de bord",     "en": "Dashboard",        "es": "Panel principal"},
    "nav.devis":          {"fr": "Devis",               "en": "Quotes",           "es": "Presupuestos"},
    "nav.factures":       {"fr": "Factures",            "en": "Invoices",         "es": "Facturas"},
    "nav.clients":        {"fr": "Clients",             "en": "Clients",          "es": "Clientes"},
    "nav.articles":       {"fr": "Articles / Services", "en": "Items / Services", "es": "Artículos / Servicios"},
    "nav.guitares":       {"fr": "Guitares",            "en": "Guitars",          "es": "Guitarras"},
    "nav.bilan":          {"fr": "Bilan périodique",    "en": "Periodic report",  "es": "Balance periódico"},
    "nav.settings":       {"fr": "Mon entreprise",      "en": "My business",      "es": "Mi empresa"},
    "nav.about":          {"fr": "À propos",            "en": "About",            "es": "Acerca de"},

    # ── Titres de pages ───────────────────────────────────────────────────────
    "page.dashboard.h1":  {"fr": "Tableau de",          "en": "My",               "es": "Panel"},
    "page.dashboard.h2":  {"fr": "bord",                "en": "Dashboard",        "es": "principal"},
    "page.devis.h1":      {"fr": "Mes",                 "en": "My",               "es": "Mis"},
    "page.devis.h2":      {"fr": "Devis",               "en": "Quotes",           "es": "Presupuestos"},
    "page.factures.h1":   {"fr": "Mes",                 "en": "My",               "es": "Mis"},
    "page.factures.h2":   {"fr": "Factures",            "en": "Invoices",         "es": "Facturas"},
    "page.clients.h1":    {"fr": "Mes",                 "en": "My",               "es": "Mis"},
    "page.clients.h2":    {"fr": "Clients",             "en": "Clients",          "es": "Clientes"},
    "page.articles.h1":   {"fr": "Articles &",          "en": "Items &",          "es": "Artículos &"},
    "page.articles.h2":   {"fr": "Services",            "en": "Services",         "es": "Servicios"},
    "page.guitares.h1":   {"fr": "Parc",                "en": "Guitar",           "es": "Parque"},
    "page.guitares.h2":   {"fr": "Guitares",            "en": "Fleet",            "es": "Guitarras"},
    "page.bilan.h1":      {"fr": "Bilan",               "en": "Quarterly",        "es": "Balance"},
    "page.bilan.h2":      {"fr": "Trimestriel",         "en": "Report",           "es": "Trimestral"},
    "page.settings.h1":   {"fr": "Mon",                 "en": "My",               "es": "Mi"},
    "page.settings.h2":   {"fr": "Entreprise",          "en": "Business",         "es": "Empresa"},

    # ── Boutons communs ───────────────────────────────────────────────────────
    "btn.new_devis":      {"fr": "+ Nouveau devis",     "en": "+ New quote",      "es": "+ Nuevo presupuesto"},
    "btn.new_facture":    {"fr": "+ Nouvelle facture",  "en": "+ New invoice",    "es": "+ Nueva factura"},
    "btn.new_client":     {"fr": "+ Nouveau client",    "en": "+ New client",     "es": "+ Nuevo cliente"},
    "btn.new_article":    {"fr": "+ Nouvel article",    "en": "+ New item",       "es": "+ Nuevo artículo"},
    "btn.new_guitare":    {"fr": "+ Nouvelle guitare",  "en": "+ New guitar",     "es": "+ Nueva guitarra"},
    "btn.save":           {"fr": "💾  Sauvegarder",     "en": "💾  Save",         "es": "💾  Guardar"},
    "btn.cancel":         {"fr": "Annuler",             "en": "Cancel",           "es": "Cancelar"},
    "btn.delete":         {"fr": "Supprimer",           "en": "Delete",           "es": "Eliminar"},
    "btn.edit":           {"fr": "Modifier",            "en": "Edit",             "es": "Editar"},
    "btn.preview":        {"fr": "👁  Aperçu PDF",      "en": "👁  PDF Preview",  "es": "👁  Vista previa"},
    "btn.email":          {"fr": "📧  Email",           "en": "📧  Email",        "es": "📧  Email"},
    "btn.convert":        {"fr": "📋  → Facture",       "en": "📋  → Invoice",    "es": "📋  → Factura"},
    "btn.calculate":      {"fr": "📊  Calculer",        "en": "📊  Calculate",    "es": "📊  Calcular"},
    "btn.add_line":       {"fr": "+ Ajouter une ligne", "en": "+ Add line",       "es": "+ Añadir línea"},
    "btn.catalog":        {"fr": "📦 Catalogue",        "en": "📦 Catalog",       "es": "📦 Catálogo"},
    "btn.close":          {"fr": "Fermer",              "en": "Close",            "es": "Cerrar"},
    "btn.confirm":        {"fr": "Confirmer",           "en": "Confirm",          "es": "Confirmar"},
    "btn.about":          {"fr": "ℹ️  À propos",        "en": "ℹ️  About",        "es": "ℹ️  Acerca de"},

    # ── Tableau de bord ───────────────────────────────────────────────────────
    "dash.ca_month":      {"fr": "CA du mois TTC",      "en": "Monthly revenue",  "es": "Ingresos del mes"},
    "dash.quotes_pending":{"fr": "Devis en attente",    "en": "Pending quotes",   "es": "Presupuestos pendientes"},
    "dash.invoices_unpaid":{"fr":"Factures impayées",   "en": "Unpaid invoices",  "es": "Facturas impagadas"},
    "dash.active_clients":{"fr": "Clients actifs",      "en": "Active clients",   "es": "Clientes activos"},
    "dash.recent":        {"fr": "ACTIVITÉ RÉCENTE",    "en": "RECENT ACTIVITY",  "es": "ACTIVIDAD RECIENTE"},

    # ── Documents (devis/factures) ────────────────────────────────────────────
    "doc.numero":         {"fr": "Numéro",              "en": "Number",           "es": "Número"},
    "doc.date":           {"fr": "Date",                "en": "Date",             "es": "Fecha"},
    "doc.client":         {"fr": "Client",              "en": "Client",           "es": "Cliente"},
    "doc.object":         {"fr": "Objet",               "en": "Subject",          "es": "Asunto"},
    "doc.amount":         {"fr": "Montant TTC",         "en": "Total incl. tax",  "es": "Total IVA incl."},
    "doc.status":         {"fr": "Statut",              "en": "Status",           "es": "Estado"},
    "doc.total_ht":       {"fr": "Total HT",            "en": "Total excl. tax",  "es": "Total sin IVA"},
    "doc.total_tva":      {"fr": "TVA",                 "en": "VAT",              "es": "IVA"},
    "doc.total_ttc":      {"fr": "Total TTC",           "en": "Total incl. tax",  "es": "Total IVA incl."},
    "doc.notes":          {"fr": "Notes / Conditions",  "en": "Notes / Terms",    "es": "Notas / Condiciones"},
    "doc.due_date":       {"fr": "Échéance",            "en": "Due date",         "es": "Vencimiento"},
    "doc.devis_ref":      {"fr": "Réf. devis",          "en": "Quote ref.",       "es": "Ref. presupuesto"},
    "doc.designation":    {"fr": "Désignation",         "en": "Description",      "es": "Descripción"},
    "doc.qty":            {"fr": "Qté",                 "en": "Qty",              "es": "Cant."},
    "doc.unit_price":     {"fr": "PU HT (€)",           "en": "Unit price (€)",   "es": "P.U. sin IVA (€)"},
    "doc.type":           {"fr": "Type",                "en": "Type",             "es": "Tipo"},
    "doc.tva_rate":       {"fr": "TVA",                 "en": "VAT",              "es": "IVA"},
    "doc.search":         {"fr": "Rechercher...",       "en": "Search...",        "es": "Buscar..."},

    # ── Statuts ───────────────────────────────────────────────────────────────
    "status.draft":       {"fr": "brouillon",           "en": "draft",            "es": "borrador"},
    "status.sent":        {"fr": "envoyé",              "en": "sent",             "es": "enviado"},
    "status.accepted":    {"fr": "accepté",             "en": "accepted",         "es": "aceptado"},
    "status.refused":     {"fr": "refusé",              "en": "refused",          "es": "rechazado"},
    "status.paid":        {"fr": "payé",                "en": "paid",             "es": "pagado"},
    "status.late":        {"fr": "en retard",           "en": "overdue",          "es": "vencido"},
    "status.cancelled":   {"fr": "annulé",              "en": "cancelled",        "es": "anulado"},

    # ── Types d'articles ──────────────────────────────────────────────────────
    "type.service":       {"fr": "service",             "en": "service",          "es": "servicio"},
    "type.product":       {"fr": "produit",             "en": "product",          "es": "producto"},
    "type.fee":           {"fr": "frais",               "en": "fee",              "es": "gasto"},

    # ── Clients ───────────────────────────────────────────────────────────────
    "client.lastname":    {"fr": "Nom",                 "en": "Last name",        "es": "Apellido"},
    "client.firstname":   {"fr": "Prénom",              "en": "First name",       "es": "Nombre"},
    "client.company":     {"fr": "Société",             "en": "Company",          "es": "Empresa"},
    "client.address":     {"fr": "Adresse",             "en": "Address",          "es": "Dirección"},
    "client.zip":         {"fr": "Code postal",         "en": "Zip code",         "es": "Código postal"},
    "client.city":        {"fr": "Ville",               "en": "City",             "es": "Ciudad"},
    "client.phone":       {"fr": "Téléphone",           "en": "Phone",            "es": "Teléfono"},
    "client.email":       {"fr": "Email",               "en": "Email",            "es": "Email"},
    "client.notes":       {"fr": "Notes",               "en": "Notes",            "es": "Notas"},

    # ── Articles ──────────────────────────────────────────────────────────────
    "article.name":       {"fr": "Nom",                 "en": "Name",             "es": "Nombre"},
    "article.desc":       {"fr": "Description",         "en": "Description",      "es": "Descripción"},
    "article.price":      {"fr": "Prix HT",             "en": "Price excl. tax",  "es": "Precio sin IVA"},
    "article.unit":       {"fr": "Unité",               "en": "Unit",             "es": "Unidad"},

    # ── Guitares ──────────────────────────────────────────────────────────────
    "guitar.brand":       {"fr": "Marque",              "en": "Brand",            "es": "Marca"},
    "guitar.model":       {"fr": "Modèle",              "en": "Model",            "es": "Modelo"},
    "guitar.type":        {"fr": "Type",                "en": "Type",             "es": "Tipo"},
    "guitar.serial":      {"fr": "N° de série",         "en": "Serial no.",       "es": "N° de serie"},
    "guitar.year":        {"fr": "Année",               "en": "Year",             "es": "Año"},
    "guitar.color":       {"fr": "Couleur",             "en": "Color",            "es": "Color"},
    "guitar.owner":       {"fr": "Propriétaire",        "en": "Owner",            "es": "Propietario"},
    "guitar.history":     {"fr": "Historique",          "en": "History",          "es": "Historial"},

    # ── Bilan technique ───────────────────────────────────────────────────────
    "bilan.title":        {"fr": "🎸  Bilan technique de la guitare",
                           "en": "🎸  Guitar technical report",
                           "es": "🎸  Informe técnico de guitarra"},
    "bilan.toggle_on":    {"fr": "🎸  Remplir le bilan technique",
                           "en": "🎸  Fill technical report",
                           "es": "🎸  Rellenar informe técnico"},
    "bilan.toggle_off":   {"fr": "✕  Masquer le bilan technique",
                           "en": "✕  Hide technical report",
                           "es": "✕  Ocultar informe técnico"},
    "bilan.before":       {"fr": "AVANT intervention",  "en": "BEFORE service",   "es": "ANTES del servicio"},
    "bilan.after":        {"fr": "APRÈS intervention",  "en": "AFTER service",    "es": "DESPUÉS del servicio"},
    "bilan.observations": {"fr": "Observations",        "en": "Observations",     "es": "Observaciones"},
    "bilan.obs_ph":       {"fr": "Observations, recommandations...",
                           "en": "Observations, recommendations...",
                           "es": "Observaciones, recomendaciones..."},

    # ── Bilan champs ─────────────────────────────────────────────────────────
    "bilan.courbure":     {"fr": "Courbure du manche",  "en": "Neck relief",      "es": "Curvatura del mástil"},
    "bilan.hauteur":      {"fr": "Hauteur des cordes",  "en": "String action",    "es": "Altura de las cuerdas"},
    "bilan.tirant":       {"fr": "Tirant des cordes",   "en": "String gauge",     "es": "Calibre de cuerdas"},
    "bilan.tete":         {"fr": "Tête",                "en": "Headstock",        "es": "Cabezal"},
    "bilan.mecaniques":   {"fr": "Mécaniques",          "en": "Tuning machines",  "es": "Clavijeros"},
    "bilan.sillet":       {"fr": "Sillet",              "en": "Nut",              "es": "Cejilla"},
    "bilan.touche":       {"fr": "Touche",              "en": "Fretboard",        "es": "Diapasón"},
    "bilan.frettes":      {"fr": "Frettes",             "en": "Frets",            "es": "Trastes"},
    "bilan.manche":       {"fr": "Manche",              "en": "Neck",             "es": "Mástil"},
    "bilan.corps":        {"fr": "Corps",               "en": "Body",             "es": "Cuerpo"},
    "bilan.chevalet":     {"fr": "Chevalet",            "en": "Bridge",           "es": "Puente"},
    "bilan.cordes":       {"fr": "Cordes",              "en": "Strings",          "es": "Cuerdas"},
    "bilan.electronique": {"fr": "Électronique",        "en": "Electronics",      "es": "Electrónica"},

    # ── Bilan périodique ──────────────────────────────────────────────────────
    "report.period":      {"fr": "Période :",           "en": "Period:",          "es": "Período:"},
    "report.from":        {"fr": "Du :",                "en": "From:",            "es": "Desde:"},
    "report.to":          {"fr": "Au :",                "en": "To:",              "es": "Hasta:"},
    "report.statuses":    {"fr": "Statuts :",           "en": "Statuses:",        "es": "Estados:"},
    "report.paid":        {"fr": "Payé",                "en": "Paid",             "es": "Pagado"},
    "report.sent":        {"fr": "Envoyé",              "en": "Sent",             "es": "Enviado"},
    "report.late":        {"fr": "En retard",           "en": "Overdue",          "es": "Vencido"},
    "report.nb_invoices": {"fr": "Nb factures",         "en": "# invoices",       "es": "Nº facturas"},
    "report.total_ht":    {"fr": "Total HT",            "en": "Total excl. tax",  "es": "Total sin IVA"},
    "report.vat":         {"fr": "TVA collectée",       "en": "VAT collected",    "es": "IVA cobrado"},
    "report.total_ttc":   {"fr": "Total TTC",           "en": "Total incl. tax",  "es": "Total IVA incl."},
    "report.breakdown":   {"fr": "VENTILATION PAR TYPE","en": "BREAKDOWN BY TYPE","es": "DESGLOSE POR TIPO"},
    "report.services":    {"fr": "🔧  Services",        "en": "🔧  Services",     "es": "🔧  Servicios"},
    "report.products":    {"fr": "📦  Produits",        "en": "📦  Products",     "es": "📦  Productos"},
    "report.fees":        {"fr": "💸  Frais",           "en": "💸  Fees",         "es": "💸  Gastos"},
    "report.total_ht_l":  {"fr": "TOTAL HT",           "en": "TOTAL EXCL. TAX",  "es": "TOTAL SIN IVA"},
    "report.declaration": {"fr": "📋  RÉCAPITULATIF DÉCLARATION",
                           "en": "📋  TAX SUMMARY",
                           "es": "📋  RESUMEN DECLARACIÓN"},
    "report.top_clients": {"fr": "TOP CLIENTS",        "en": "TOP CLIENTS",      "es": "TOP CLIENTES"},
    "report.detail":      {"fr": "DÉTAIL DES FACTURES","en": "INVOICE DETAIL",   "es": "DETALLE FACTURAS"},
    "report.free":        {"fr": "— Période libre —",  "en": "— Custom period —","es": "— Período libre —"},
    "report.current_q":   {"fr": "(en cours)",         "en": "(current)",        "es": "(actual)"},
    "report.year":        {"fr": "Année",              "en": "Year",             "es": "Año"},

    # ── Paramètres ────────────────────────────────────────────────────────────
    "settings.identity":  {"fr": "Identité de l'entreprise",
                           "en": "Business identity",
                           "es": "Identidad de la empresa"},
    "settings.logo":      {"fr": "Logo de l'entreprise","en": "Business logo",   "es": "Logo de la empresa"},
    "settings.bank":      {"fr": "Coordonnées bancaires","en": "Bank details",   "es": "Datos bancarios"},
    "settings.numbering": {"fr": "Numérotation & TVA par défaut",
                           "en": "Numbering & default VAT",
                           "es": "Numeración e IVA por defecto"},
    "settings.smtp":      {"fr": "Configuration email (SMTP)",
                           "en": "Email configuration (SMTP)",
                           "es": "Configuración de email (SMTP)"},
    "settings.templates": {"fr": "Modèles d'email",    "en": "Email templates",  "es": "Plantillas de email"},
    "settings.legal":     {"fr": "Mentions légales (pied de page)",
                           "en": "Legal notices (footer)",
                           "es": "Menciones legales (pie de página)"},
    "settings.db":        {"fr": "Emplacement de la base de données",
                           "en": "Database location",
                           "es": "Ubicación de la base de datos"},
    "settings.backup":    {"fr": "Sauvegarde & Restauration",
                           "en": "Backup & Restore",
                           "es": "Copia de seguridad y restauración"},
    "settings.language":  {"fr": "Langue de l'interface",
                           "en": "Interface language",
                           "es": "Idioma de la interfaz"},
    "settings.lang_note": {"fr": "Le changement de langue sera effectif au prochain lancement.",
                           "en": "Language change takes effect on next launch.",
                           "es": "El cambio de idioma se aplicará en el próximo inicio."},
    "settings.name":      {"fr": "Nom / Raison sociale","en": "Name / Company",  "es": "Nombre / Razón social"},
    "settings.address":   {"fr": "Adresse",             "en": "Address",          "es": "Dirección"},
    "settings.city":      {"fr": "Ville / CP",          "en": "City / Zip",       "es": "Ciudad / CP"},
    "settings.phone":     {"fr": "Téléphone",           "en": "Phone",            "es": "Teléfono"},
    "settings.siret":     {"fr": "SIRET",               "en": "Company ID",       "es": "NIF/CIF"},
    "settings.tva_id":    {"fr": "N° TVA intracommunautaire",
                           "en": "EU VAT number",
                           "es": "N° IVA intracomunitario"},
    "settings.prefix_devis":   {"fr": "Préfixe devis",  "en": "Quote prefix",    "es": "Prefijo presupuesto"},
    "settings.prefix_facture": {"fr": "Préfixe facture","en": "Invoice prefix",  "es": "Prefijo factura"},
    "settings.tva_default":    {"fr": "TVA par défaut", "en": "Default VAT",     "es": "IVA por defecto"},
    "settings.saved":     {"fr": "Paramètres enregistrés ✓",
                           "en": "Settings saved ✓",
                           "es": "Configuración guardada ✓"},
    "settings.choose_logo":{"fr": "📁  Choisir une image...",
                            "en": "📁  Choose image...",
                            "es": "📁  Elegir imagen..."},
    "settings.remove_logo":{"fr": "🗑  Supprimer le logo",
                            "en": "🗑  Remove logo",
                            "es": "🗑  Eliminar logo"},
    "settings.no_logo":   {"fr": "Aucun logo",          "en": "No logo",          "es": "Sin logo"},
    "settings.backup_all":{"fr": "💾  Sauvegarder tout (JSON)",
                           "en": "💾  Backup all (JSON)",
                           "es": "💾  Guardar todo (JSON)"},
    "settings.restore":   {"fr": "📂  Restaurer depuis une sauvegarde",
                           "en": "📂  Restore from backup",
                           "es": "📂  Restaurar desde copia"},
    "settings.export_devis":  {"fr": "📤  Exporter devis CSV",
                               "en": "📤  Export quotes CSV",
                               "es": "📤  Exportar presupuestos CSV"},
    "settings.export_fac":    {"fr": "📤  Exporter factures CSV",
                               "en": "📤  Export invoices CSV",
                               "es": "📤  Exportar facturas CSV"},
    "settings.change_db": {"fr": "📁  Changer l'emplacement…",
                           "en": "📁  Change location…",
                           "es": "📁  Cambiar ubicación…"},
    "settings.open_dir":  {"fr": "📂  Ouvrir le dossier",
                           "en": "📂  Open folder",
                           "es": "📂  Abrir carpeta"},

    # ── Dialogues document ────────────────────────────────────────────────────
    "dlg.general":        {"fr": "Informations générales","en": "General info",   "es": "Información general"},
    "dlg.lines":          {"fr": "Lignes du document",  "en": "Document lines",   "es": "Líneas del documento"},
    "dlg.notes_grp":      {"fr": "Notes / Conditions",  "en": "Notes / Terms",    "es": "Notas / Condiciones"},
    "dlg.client_lbl":     {"fr": "Client",              "en": "Client",           "es": "Cliente"},
    "dlg.guitar_lbl":     {"fr": "Guitare",             "en": "Guitar",           "es": "Guitarra"},
    "dlg.object_lbl":     {"fr": "Objet",               "en": "Subject",          "es": "Asunto"},
    "dlg.new_client":     {"fr": "+ Nouveau client",    "en": "+ New client",     "es": "+ Nuevo cliente"},
    "dlg.new_guitar":     {"fr": "+ Nouvelle guitare",  "en": "+ New guitar",     "es": "+ Nueva guitarra"},
    "dlg.subtotal_ht":    {"fr": "Sous-total HT",       "en": "Subtotal excl.",   "es": "Subtotal sin IVA"},
    "dlg.tva_line":       {"fr": "TVA",                 "en": "VAT",              "es": "IVA"},
    "dlg.total_ttc":      {"fr": "TOTAL TTC",           "en": "TOTAL INCL. TAX",  "es": "TOTAL IVA INCL."},
    "dlg.new_devis":      {"fr": "Nouveau devis",       "en": "New quote",        "es": "Nuevo presupuesto"},
    "dlg.edit_devis":     {"fr": "Modifier le devis",   "en": "Edit quote",       "es": "Editar presupuesto"},
    "dlg.new_facture":    {"fr": "Nouvelle facture",    "en": "New invoice",      "es": "Nueva factura"},
    "dlg.edit_facture":   {"fr": "Modifier la facture", "en": "Edit invoice",     "es": "Editar factura"},

    # ── Confirmations / messages ──────────────────────────────────────────────
    "msg.confirm_delete": {"fr": "Confirmer la suppression",
                           "en": "Confirm deletion",
                           "es": "Confirmar eliminación"},
    "msg.delete_doc":     {"fr": "Supprimer ce document définitivement ?",
                           "en": "Permanently delete this document?",
                           "es": "¿Eliminar este documento definitivamente?"},
    "msg.delete_client":  {"fr": "Supprimer ce client définitivement ?",
                           "en": "Permanently delete this client?",
                           "es": "¿Eliminar este cliente definitivamente?"},
    "msg.delete_article": {"fr": "Supprimer cet article définitivement ?",
                           "en": "Permanently delete this item?",
                           "es": "¿Eliminar este artículo definitivamente?"},
    "msg.delete_guitar":  {"fr": "Supprimer cette guitare définitivement ?",
                           "en": "Permanently delete this guitar?",
                           "es": "¿Eliminar esta guitarra definitivamente?"},
    "msg.saved":          {"fr": "Sauvegardé",          "en": "Saved",            "es": "Guardado"},
    "msg.error":          {"fr": "Erreur",              "en": "Error",            "es": "Error"},
    "msg.warning":        {"fr": "Attention",           "en": "Warning",          "es": "Atención"},
    "msg.no_result":      {"fr": "Aucun résultat",      "en": "No results",       "es": "Sin resultados"},

    # ── Email dialog ──────────────────────────────────────────────────────────
    "email.to":           {"fr": "Destinataire :",      "en": "To:",              "es": "Para:"},
    "email.subject":      {"fr": "Objet :",             "en": "Subject:",         "es": "Asunto:"},
    "email.body":         {"fr": "Message :",           "en": "Message:",         "es": "Mensaje:"},
    "email.gen_pdf":      {"fr": "⬇️  Générer et télécharger le PDF",
                           "en": "⬇️  Generate and download PDF",
                           "es": "⬇️  Generar y descargar PDF"},
    "email.open_gmail":   {"fr": "📧  Ouvrir dans Gmail",
                           "en": "📧  Open in Gmail",
                           "es": "📧  Abrir en Gmail"},
    "email.send_smtp":    {"fr": "📤  Envoyer (SMTP)",  "en": "📤  Send (SMTP)",  "es": "📤  Enviar (SMTP)"},

    # ── À propos ──────────────────────────────────────────────────────────────
    "about.title":        {"fr": "À propos de LuthierPro",
                           "en": "About LuthierPro",
                           "es": "Acerca de LuthierPro"},
    "about.tagline":      {"fr": "Gestion de devis, factures & atelier\npour luthiers et artisans",
                           "en": "Quotes, invoices & workshop management\nfor luthiers and craftspeople",
                           "es": "Gestión de presupuestos, facturas y taller\npara luthiers y artesanos"},
    "about.version":      {"fr": "Version",             "en": "Version",          "es": "Versión"},
    "about.license":      {"fr": "Licence",             "en": "License",          "es": "Licencia"},
    "about.license_val":  {"fr": "GNU GPL v3 — Logiciel libre",
                           "en": "GNU GPL v3 — Free software",
                           "es": "GNU GPL v3 — Software libre"},
    "about.built_with":   {"fr": "Réalisé avec",        "en": "Built with",       "es": "Creado con"},
    "about.copyright":    {"fr": "© 2026 — Distribué sous licence GNU GPL v3\nVous êtes libre de l'utiliser, le modifier et le redistribuer.",
                           "en": "© 2026 — Distributed under GNU GPL v3\nFree to use, modify and redistribute.",
                           "es": "© 2026 — Distribuido bajo GNU GPL v3\nLibre para usar, modificar y redistribuir."},
}

# ══════════════════════════════════════════════════════════════════════════════

def set_language(lang: str):
    """Change la langue active. lang = 'fr', 'en' ou 'es'."""
    global _LANG
    if lang in ("fr", "en", "es"):
        _LANG = lang


def current_language() -> str:
    return _LANG


def t(key: str, lang: str = None) -> str:
    """Retourne la traduction de key dans la langue active (ou lang si fourni)."""
    l = lang or _LANG
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        return key   # clé inconnue → retourne la clé brute
    return entry.get(l) or entry.get("fr") or key


def bilan_fields_translated() -> list[tuple[str, str]]:
    """Retourne la liste des champs bilan traduits dans la langue active."""
    keys = [
        "courbure", "hauteur", "tirant", "tete", "mecaniques", "sillet",
        "touche", "frettes", "manche", "corps", "chevalet", "cordes", "electronique"
    ]
    return [(k, t(f"bilan.{k}")) for k in keys]


def statuts_devis() -> list[str]:
    return [t(f"status.{s}") for s in ("draft", "sent", "accepted", "refused")]


def statuts_facture() -> list[str]:
    return [t(f"status.{s}") for s in ("draft", "sent", "paid", "late", "cancelled")]


def types_article() -> list[str]:
    return [t(f"type.{s}") for s in ("service", "product", "fee")]
