# Veille TikTok IA

Agent de veille quotidienne pour trouver des opportunités rentables sur TikTok (vidéos 3D et IA en français et en allemand), avec Claude Code, Blender, Python, FFmpeg et ElevenLabs.

- **Page de lecture (toujours le dernier rapport, avec les 14 précédents) :** https://claude.ai/artifact/Jc8iTq2FDgoFqYGKuj2dEN
- **Procédure suivie par l'agent :** [`MISSION.md`](MISSION.md)
- **Rapports datés :** [`rapports/`](rapports/)

## Fonctionnement

Chaque jour, une tâche planifiée relance la conversation Claude Code qui a créé ce dossier, vers 7 h 35 (heure de Paris), pour que le rapport soit prêt vers 8 h. L'agent :

1. lit la mémoire (`memoire/`) et les derniers rapports ;
2. fait la recherche du jour (TikTok, YouTube, Instagram, Reddit, GitHub, éditeurs IA, outils 3D, monétisation) ;
3. écrit `rapports/AAAA-MM-JJ.md` (sections A à F, plus G le dimanche) ;
4. met à jour `memoire/historique.md` ;
5. reconstruit la page avec `outils/construire_page.py` et la republie à la même adresse ;
6. pousse les fichiers sur la branche `claude/cool-lamport-e46u76` et envoie une notification courte.

L'agent ne publie aucune vidéo, n'achète rien et n'installe aucun logiciel payant.

## Fichiers

| Fichier | Rôle |
|---|---|
| `MISSION.md` | Cahier des charges et procédure quotidienne |
| `rapports/` | Un rapport Markdown par jour |
| `memoire/historique.md` | Ce qui a déjà été proposé (pour ne pas se répéter) |
| `memoire/performances.csv` | Tes statistiques réelles, à remplir |
| `outils/construire_page.py` | Transforme les rapports en page web (`pip install markdown`) |
| `page/veille.html` | Page générée, publiée sur claude.ai |

## Améliorer les recommandations

Ajoute une ligne par vidéo publiée dans `memoire/performances.csv` (vues, vues qualifiées, rétention, RPM, revenus, coûts, temps de production), ou écris tes chiffres directement dans la conversation. L'agent s'en sert pour recalibrer sa grille de notation. Sans ces données, il ne prétend jamais connaître tes statistiques.

## Modifier ou arrêter la veille

Écris-le simplement dans la conversation (« décale à 7 h », « arrête la veille », « ajoute telle source »). Les tâches planifiées apparaissent aussi dans la liste des tâches planifiées de ton compte Claude.

## Limites connues

L'environnement cloud bloque la lecture directe de certains sites (TikTok, blender.org, Reddit…). L'agent passe alors par la recherche web et l'indique dans chaque rapport. Pour lever cette limite, il faut autoriser ces sites dans les réglages réseau de l'environnement.
