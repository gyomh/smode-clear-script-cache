# Smode Clear Script Cache

*[English version](README.md)*

> **Expérimental, pas un outil officiel Smode.** Construit par essais et erreurs sur l'API Oil (voir [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Testé sur Smode Compose R15.

Smode garde en mémoire les modules Python importés et le code des Scripts : après avoir modifié un fichier `.py`, il
faut le réimporter. Ce Script **vide le cache Python et recharge vos Scripts depuis leurs fichiers `.py`** :

- purge les modules utilisateur de `sys.modules` (Smode, bibliothèque standard et site-packages sont protégés) et les
  réimporte ;
- supprime en option les dossiers `__pycache__` ;
- recharge le **code des Scripts du projet ouvert** depuis les `.py` de vos dossiers de scripts (appariement par le
  titre de la boîte d'en-tête, ou par le nom du Script) : rien à réimporter.

## Installation

1. Glissez `ClearScriptCache_GYOMH.py` dans votre projet Smode, **Launch Mode = Manual**.
2. Ouvrez-le et renseignez `SCRIPT_DIRS` en haut avec le ou les dossiers contenant vos `.py` (le fichier le plus
   récent gagne).
3. Exécutez-le chaque fois que vous avez modifié un script.

Autres options : `NAME_FILTER` (ne purger que les modules contenant ce texte), `CLEAR_PYCACHE`, `RELOAD`,
`RELOAD_SCRIPTS`, `SKIP_SCRIPTS` (noms de Scripts jamais rechargés, ex. un pont qui tourne en At Every Update).

## Licence

MIT — voir [LICENSE](LICENSE).
