#!/usr/bin/env python3
"""Construit la page de lecture de la veille TikTok à partir des rapports Markdown.

Lit veille-tiktok/rapports/AAAA-MM-JJ.md, intègre les 14 rapports les plus récents
dans veille-tiktok/page/veille.html (un sélecteur permet de passer de l'un à l'autre)
et liste les plus anciens avec un lien vers GitHub.

Usage : python3 veille-tiktok/outils/construire_page.py
Dépendance : pip install markdown
"""

from __future__ import annotations

import datetime as dt
import html
import re
import sys
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import slugify
except ImportError:  # pragma: no cover
    sys.exit("Module 'markdown' manquant : lance d'abord  pip install markdown")

BASE = Path(__file__).resolve().parent.parent
RAPPORTS = BASE / "rapports"
SORTIE = BASE / "page" / "veille.html"
GITHUB = ("https://github.com/dembadia965-source/expresstransport/blob/"
          "claude/cool-lamport-e46u76/veille-tiktok/rapports/")
NB_INTEGRES = 14

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

COURTS = {"A": "Infos du jour", "B": "Top 5", "C": "Idées vidéo", "D": "Outils",
          "E": "Aujourd'hui", "F": "Opportunité n°1", "G": "Bilan hebdo"}

ETIQUETTES = {
    "CONFIRMÉ": ("ok", "Confirmé"),
    "ÉMERGENT": ("warn", "Émergent"),
    "EXPÉRIMENTAL": ("exp", "Expérimental"),
    "CONFIANCE ÉLEVÉE": ("conf conf-high", "Confiance élevée"),
    "CONFIANCE MOYENNE": ("conf conf-mid", "Confiance moyenne"),
    "CONFIANCE FAIBLE": ("conf conf-low", "Confiance faible"),
}


def date_fr(d: dt.date, avec_jour: bool = True) -> str:
    texte = f"{d.day} {MOIS[d.month - 1]} {d.year}"
    return f"{JOURS[d.weekday()]} {texte}" if avec_jour else texte


def lister_rapports() -> list[tuple[dt.date, Path]]:
    rapports = []
    for chemin in RAPPORTS.glob("*.md"):
        try:
            jour = dt.date.fromisoformat(chemin.stem)
        except ValueError:
            continue
        rapports.append((jour, chemin))
    return sorted(rapports, reverse=True)


def rendre(jour: dt.date, chemin: Path) -> tuple[str, list[tuple[str, str]]]:
    prefixe = f"r-{jour.isoformat()}"
    md = markdown.Markdown(
        extensions=["tables", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": lambda v, s: f"{prefixe}-{slugify(v, s)}"}},
    )
    corps = md.convert(chemin.read_text(encoding="utf-8"))

    # Sommaire : titres de niveau 2 (sections A à G).
    sommaire = []
    def parcourir(jetons):
        for jeton in jetons:
            if jeton["level"] == 2:
                nom = html.unescape(jeton["name"])
                m = re.match(r"([A-G])\. ", nom)
                sommaire.append((jeton["id"], f"{m.group(1)} · {COURTS[m.group(1)]}" if m else nom))
            parcourir(jeton.get("children", []))
    parcourir(md.toc_tokens)

    # Étiquettes de statut et de confiance.
    def etiquette(m: re.Match) -> str:
        texte = m.group(1)
        if texte in ETIQUETTES:
            classe, libelle = ETIQUETTES[texte]
            return f'<span class="chip {classe}">{libelle}</span>'
        return m.group(0)
    corps = re.sub(r"<code>([^<]+)</code>", etiquette, corps)

    # Lettre de section mise en valeur : « A. Titre ».
    corps = re.sub(r'(<h2 id="[^"]+">)([A-G])\. ',
                   r'\1<span class="sec-letter" aria-hidden="true">\2</span>', corps)
    # Tableaux défilants sur mobile, liens externes dans un nouvel onglet.
    corps = corps.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    corps = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', corps)
    return corps, sommaire


CSS = """
:root {
  /* Mise en page : une colonne de lecture façon conducteur de tournage, barre de date collante, repères en chasse fixe. */
  --bg: #F2F4F7;
  --surface: #FFFFFF;
  --fg: #151920;
  --muted: #5A6373;
  --line: #D8DDE5;
  --tint: #E8EDF2;
  --rec: #D92D2D;
  --link: #0A6A7A;
  --ok-fg: #23753A; --ok-bg: #E3F3E7;
  --warn-fg: #9A4F00; --warn-bg: #FDEFD9;
  --exp-fg: #5B3CC4; --exp-bg: #EEE9FD;
  --conf-fg: #3D4757; --conf-bg: #E4E9EF;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --font-body: "IBM Plex Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0F1217; --surface: #161A21; --fg: #E5E8ED; --muted: #9AA3B2; --line: #2A303A; --tint: #1D232C;
    --rec: #FF6B6B; --link: #5CC8D6;
    --ok-fg: #8CE99A; --ok-bg: #12301B; --warn-fg: #FFC078; --warn-bg: #3A2810;
    --exp-fg: #B9A4FF; --exp-bg: #251B47; --conf-fg: #C3CAD5; --conf-bg: #232A34;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0F1217; --surface: #161A21; --fg: #E5E8ED; --muted: #9AA3B2; --line: #2A303A; --tint: #1D232C;
  --rec: #FF6B6B; --link: #5CC8D6;
  --ok-fg: #8CE99A; --ok-bg: #12301B; --warn-fg: #FFC078; --warn-bg: #3A2810;
  --exp-fg: #B9A4FF; --exp-bg: #251B47; --conf-fg: #C3CAD5; --conf-bg: #232A34;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body {
  background: var(--bg); color: var(--fg);
  font-family: var(--font-body); font-size: 16px; line-height: 1.62;
  -webkit-text-size-adjust: 100%;
}
body::before {
  content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px);
  z-index: 10; background: var(--surface);
}
a { color: var(--link); text-underline-offset: 2px; text-decoration-thickness: 1px; }
a:hover { text-decoration-thickness: 2px; }
a:focus-visible, select:focus-visible, summary:focus-visible { outline: 2px solid var(--link); outline-offset: 2px; border-radius: 3px; }

.bar {
  position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5;
  background: var(--surface); border-bottom: 1px solid var(--line);
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
.bar-inner {
  max-width: 46rem; margin: 0 auto; padding-block: 10px;
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 16px;
}
.brand { display: flex; align-items: center; gap: 10px; font-family: var(--font-display); font-weight: 700; font-size: 1.05rem; letter-spacing: -0.01em; }
.rec { width: 10px; height: 10px; border-radius: 50%; background: var(--rec); flex: none; }
.brand small { font-family: var(--font-mono); font-weight: 400; font-size: .72rem; color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }
.picker { display: flex; align-items: center; gap: 8px; font-size: .85rem; color: var(--muted); }
.picker select {
  font: inherit; font-family: var(--font-mono); font-size: .85rem; color: var(--fg);
  background: var(--bg); border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; max-width: 100%;
}

.col {
  max-width: 46rem; margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 28px 56px;
}
.report h1 {
  font-family: var(--font-display); font-weight: 800; letter-spacing: -0.025em; line-height: 1.08;
  font-size: clamp(1.9rem, 1.3rem + 2.6vw, 2.75rem); margin: 0 0 12px; text-wrap: balance;
}
.report h2 {
  font-family: var(--font-display); font-weight: 700; letter-spacing: -0.015em; line-height: 1.2;
  font-size: 1.55rem; margin: 56px 0 16px; padding-top: 18px; border-top: 2px solid var(--fg);
  display: flex; align-items: baseline; gap: 12px; text-wrap: balance; scroll-margin-top: 80px;
}
.sec-letter {
  font-family: var(--font-mono); font-weight: 500; font-size: .95rem; color: var(--surface); background: var(--fg);
  min-width: 1.9em; height: 1.9em; display: inline-grid; place-items: center; border-radius: 4px; flex: none;
  transform: translateY(-2px);
}
.report h3 {
  font-family: var(--font-display); font-weight: 650; font-size: 1.18rem; line-height: 1.3; letter-spacing: -0.01em;
  margin: 36px 0 10px; text-wrap: balance; scroll-margin-top: 80px;
}
.report p { margin: 0 0 14px; max-width: 68ch; }
.report ul, .report ol { margin: 0 0 16px; padding-left: 1.3em; max-width: 68ch; }
.report li { margin: 6px 0; }
.report li > ul, .report li > ol { margin: 6px 0 4px; }
.report li::marker { color: var(--muted); }
.report strong { font-weight: 600; }
.report em { font-style: italic; }
.report code {
  font-family: var(--font-mono); font-size: .86em; background: var(--tint); padding: 1px 5px; border-radius: 4px;
  overflow-wrap: anywhere;
}
.report pre { background: var(--tint); padding: 12px 14px; border-radius: 6px; overflow-x: auto; font-size: .85rem; }
.report pre code { background: none; padding: 0; }
.report blockquote {
  margin: 18px 0; padding: 14px 16px; background: var(--tint); border-radius: 6px; color: var(--fg);
  font-size: .95rem;
}
.report blockquote p:last-child { margin-bottom: 0; }

.report .toc { display: flex; flex-wrap: wrap; gap: 6px; margin: 18px 0 8px; padding: 0; list-style: none; }
.report .toc a {
  display: inline-block; font-size: .82rem; text-decoration: none; color: var(--fg);
  border: 1px solid var(--line); background: var(--surface); border-radius: 999px; padding: 4px 11px;
}
.report .toc a:hover { border-color: var(--fg); }

.chip {
  display: inline-block; font-family: var(--font-mono); font-size: .72rem; font-weight: 500; letter-spacing: .05em;
  text-transform: uppercase; padding: 2px 8px; border-radius: 4px; line-height: 1.5; white-space: nowrap; vertical-align: 1px;
}
.chip.ok { color: var(--ok-fg); background: var(--ok-bg); }
.chip.warn { color: var(--warn-fg); background: var(--warn-bg); }
.chip.exp { color: var(--exp-fg); background: var(--exp-bg); }
.chip.conf { color: var(--conf-fg); background: var(--conf-bg); }

.table-wrap { overflow-x: auto; margin: 12px 0 20px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
.report table { border-collapse: collapse; width: 100%; font-size: .88rem; font-variant-numeric: tabular-nums; }
.report th, .report td { text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid var(--line); }
.report th { font-weight: 600; background: var(--tint); white-space: nowrap; }
.report tr:last-child td { border-bottom: 0; }

.archive { margin-top: 64px; padding-top: 18px; border-top: 1px solid var(--line); font-size: .9rem; color: var(--muted); }
.archive h2 { font-family: var(--font-display); font-size: 1.05rem; color: var(--fg); margin: 0 0 8px; }
.archive ul { list-style: none; padding: 0; margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 6px 14px; }
.archive p { margin: 0 0 8px; max-width: 68ch; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
@media (max-width: 480px) {
  body { font-size: 15.5px; }
  .report h2 { font-size: 1.32rem; margin-top: 44px; }
}
"""

JS = """
(function () {
  var reports = Array.prototype.slice.call(document.querySelectorAll('article.report'));
  var select = document.getElementById('report-select');
  if (!reports.length || !select) return;
  function show(id, target) {
    reports.forEach(function (r) { r.hidden = r.id !== id; });
    select.value = id;
    if (target) { target.scrollIntoView(); } else { window.scrollTo(0, 0); }
  }
  function route() {
    var h = decodeURIComponent(location.hash.slice(1));
    var el = h ? document.getElementById(h) : null;
    var art = el ? el.closest('article.report') : null;
    if (!art) { show(reports[0].id, null); return; }
    show(art.id, el === art ? null : el);
  }
  select.addEventListener('change', function () { location.hash = select.value; });
  window.addEventListener('hashchange', route);
  if (location.hash) route();
})();
"""


def construire() -> Path:
    rapports = lister_rapports()
    if not rapports:
        sys.exit("Aucun rapport trouvé dans " + str(RAPPORTS))
    integres, anciens = rapports[:NB_INTEGRES], rapports[NB_INTEGRES:]

    options, articles = [], []
    for i, (jour, chemin) in enumerate(integres):
        ident = f"r-{jour.isoformat()}"
        corps, sommaire = rendre(jour, chemin)
        options.append(f'<option value="{ident}">{html.escape(date_fr(jour))}</option>')
        toc = "".join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in sommaire)
        cache = "" if i == 0 else " hidden"
        articles.append(
            f'<article class="report" id="{ident}"{cache}>\n{corps}\n'
            f'<p><a href="{GITHUB}{chemin.name}" target="_blank" rel="noopener">Voir ce rapport sur GitHub</a></p>\n'
            f'</article>'.replace("</h1>", f'</h1>\n<ul class="toc" aria-label="Sections">{toc}</ul>', 1)
        )

    liens_archives = "".join(
        f'<li><a href="#r-{j.isoformat()}">{html.escape(date_fr(j, False))}</a></li>' for j, _ in integres)
    liens_anciens = "".join(
        f'<li><a href="{GITHUB}{c.name}" target="_blank" rel="noopener">{html.escape(date_fr(j, False))}</a></li>'
        for j, c in anciens)
    bloc_anciens = (f"<p>Rapports plus anciens, sur GitHub :</p><ul>{liens_anciens}</ul>" if anciens else "")
    maj = date_fr(integres[0][0])

    page = f"""<title>Veille TikTok IA</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>{CSS}</style>
<header class="bar">
  <div class="bar-inner">
    <div class="brand"><span class="rec" aria-hidden="true"></span>Veille TikTok IA <small>FR · DE</small></div>
    <label class="picker" for="report-select">Rapport du
      <select id="report-select">{''.join(options)}</select>
    </label>
  </div>
</header>
<main class="col">
{chr(10).join(articles)}
<footer class="archive">
  <h2>Archives</h2>
  <ul>{liens_archives}</ul>
  {bloc_anciens}
  <p>Dernier rapport : {html.escape(maj)}. Rapport produit chaque matin vers 8 h (heure de Paris) par l'agent de veille ; les sources sont citées dans chaque section. Fichiers : <code>veille-tiktok/rapports/</code> dans le dépôt expresstransport.</p>
</footer>
</main>
<script>{JS}</script>
"""
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(page, encoding="utf-8")
    return SORTIE


if __name__ == "__main__":
    chemin = construire()
    print(f"Page écrite : {chemin} ({chemin.stat().st_size // 1024} Ko)")
