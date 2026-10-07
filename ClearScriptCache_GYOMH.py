#    #########      ###         ###      #########      #########         ###############
# ###               ######   ######   ###         ###   ###      ###      ###
# ###               ###   ###   ###   ###         ###   ###         ###   ###
#    #########      ###   ###   ###   ###         ###   ###         ###   ############
#             ###   ###         ###   ###         ###   ###         ###   ###
#             ###   ###         ###   ###         ###   ###      ###      ###
# ############      ###         ###      #########      #########         ###############
#
# -------------------- "Guillaume Henrion aka [GYOMH]" "06/10/2026" --------------------
# __________________________________________ ___________________________________________
# |                                       | |                                         |
# |    CLEAR SCRIPT CACHE                 | |  Vide le cache Python des scripts :     |
# |       V1.2                            | |  - Purge sys.modules des modules        |
# |                                       | |    utilisateur (hors Smode / stdlib)    |
# |_______________________________________| |_________________________________________|
# |    Instructions :                     | |  - Recharge les modules purges          |
# | 1- (Optionnel) Regler NAME_FILTER     | |  - RECHARGE LE CODE DES SCRIPTS du      |
# |    et SCRIPT_DIRS (dossiers .py)      | |    projet depuis leur fichier .py       |
# | 2- Execute (Launch Mode = Manual)     | |    (apparie par le titre de la boite    |
# | 3- Les scripts sont rechargees seuls  | |    d en-tete) : plus d import a la main |
# |    (rien a reimporter)                | |  - Option : supprime les __pycache__    |
# |_______________________________________| |_________________________________________|
#
# HISTORIQUE
# V1.0 - 06/10/2026 - Version initiale : purge sys.modules + invalidate_caches
#                      + suppression optionnelle des __pycache__.
# V1.1 - 06/10/2026 - Rechargement automatique des modules purges (option RELOAD).
# V1.2 - 06/10/2026 - Recharge aussi le CODE des Scripts du projet depuis les fichiers .py de SCRIPT_DIRS
#                      (Smode ne garde pas le chemin source : appariement par le titre de la boite d'en-tete
#                      ou, a defaut, par le nom du Script). Option RELOAD_SCRIPTS / SKIP_SCRIPTS.
#

import sys
import os
import shutil
import re
import importlib

# ----------------------------- CONFIG -----------------------------
NAME_FILTER = ""            # sous-chaine (insensible a la casse) du nom de module ; "" = tous les modules utilisateur
CLEAR_PYCACHE = True        # supprime aussi les dossiers __pycache__ des modules purges
RELOAD = True               # reimporte les modules purges apres la purge (pas besoin de les reimporter a la main)
RELOAD_SCRIPTS = True       # recharge le code des Scripts du projet depuis leur fichier .py
SCRIPT_DIRS = []            # dossiers contenant vos .py, ex. [r"C:\Users\you\Documents\smode scripts"] (le plus recent gagne)
SKIP_SCRIPTS = ("smode_bridge",)   # noms de Scripts a ne jamais recharger (le pont MCP tourne en At Every Update)
# ------------------------------------------------------------------


def _is_protected(name, mod):
    """Modules a ne jamais purger : Smode, bindings C++, stdlib, site-packages, builtins."""
    if name in ("__main__", "sys", "builtins") or name.startswith(("Smode", "_cpp")):
        return True
    path = getattr(mod, "__file__", None)
    if not path:                       # builtin / frozen / namespace
        return True
    p = os.path.normcase(os.path.abspath(path))
    if "site-packages" in p:
        return True
    for base in (sys.prefix, sys.base_prefix, getattr(sys, "base_exec_prefix", sys.prefix)):
        b = os.path.normcase(os.path.abspath(os.path.join(base, "Lib")))
        if p.startswith(b + os.sep):
            return True
    # Dossier d'installation Smode (Lib, python\Lib, DLLs...)
    for entry in sys.path:
        if entry and "Smode" in entry and p.startswith(os.path.normcase(os.path.abspath(entry)) + os.sep) \
                and ("Lib" in entry or "DLLs" in entry):
            return True
    return False


purged, dirs = [], set()
flt = NAME_FILTER.lower()
for name, mod in list(sys.modules.items()):
    if _is_protected(name, mod):
        continue
    if flt and flt not in name.lower():
        continue
    path = getattr(mod, "__file__", None)
    if path:
        dirs.add(os.path.dirname(os.path.abspath(path)))
    del sys.modules[name]
    purged.append(name)

importlib.invalidate_caches()

pycache_removed = 0
if CLEAR_PYCACHE:
    for d in dirs:
        pc = os.path.join(d, "__pycache__")
        if os.path.isdir(pc):
            shutil.rmtree(pc, ignore_errors=True)
            pycache_removed += 1

reloaded, failed = [], {}
if RELOAD:
    for n in sorted(purged):
        if n in sys.modules:           # deja reimporte comme dependance d'un autre module
            reloaded.append(n)
            continue
        try:
            importlib.import_module(n)
            reloaded.append(n)
        except Exception as e:
            failed[n] = "%s: %s" % (type(e).__name__, e)



def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def _title(code):
    """Titre de la boite d'en-tete (ex. 'IK RIG') ou None."""
    for line in code.split("\n")[:40]:
        m = re.match(r"#\s*\|\s{2,}([A-Z][A-Z0-9 _\-]*?)\s{2,}\|", line)
        if m:
            return m.group(1).strip()
    return None


def _collect_tools():
    """Tous les PythonScriptTool du projet (scene, compos, groupes, layers imbriques)."""
    out = []

    def visit(o, depth=0):
        if o is None or depth > 25:
            return
        for attr in ("tools", "layers", "contentMaps"):
            try:
                items = list(getattr(o, attr))
            except Exception:
                continue
            for c in items:
                try:
                    if c.getOilClassName() == "PythonScriptTool":
                        if not any(c is t for t in out):
                            out.append(c)
                        continue
                except Exception:
                    pass
                visit(c, depth + 1)
        try:
            visit(o.generator, depth + 1)
        except Exception:
            pass

    prj = script.project
    visit(prj.masterScene)
    visit(prj.pipeline)
    return out


scripts_updated, scripts_same, scripts_nofile = [], [], []
if RELOAD_SCRIPTS:
    by_title, by_stem = {}, {}
    for d in SCRIPT_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.lower().endswith(".py"):
                continue
            fp = os.path.join(d, fn)
            t = _title(_read(fp))
            for table, key in ((by_title, t), (by_stem, os.path.splitext(fn)[0].lower())):
                if key and (key not in table or os.path.getmtime(fp) > os.path.getmtime(table[key])):
                    table[key] = fp
    for tool in _collect_tools():
        try:
            if tool is script:
                continue                       # ne pas se recharger soi-meme en cours d'execution
            name = tool.label.get()
            cur = tool.script.sourceCode.get().replace("\r\n", "\n")
        except Exception:
            continue
        if any(name.lower().startswith(x.lower()) for x in SKIP_SCRIPTS):
            continue
        fp = by_title.get(_title(cur)) or by_stem.get(name.lower())
        if not fp:
            scripts_nofile.append(name)
            continue
        new = _read(fp)
        if new == cur:
            scripts_same.append(name)
        else:
            tool.script.sourceCode.set(new)
            scripts_updated.append("%s <- %s" % (name, fp))

print("[ClearScriptCache] %d module(s) purge(s), %d __pycache__ supprime(s), %d recharge(s), %d echec(s)"
      % (len(purged), pycache_removed, len(reloaded), len(failed)))
for n in sorted(purged):
    print("  - " + n + ("  [recharge]" if n in reloaded else ""))
for n, err in failed.items():
    print("  ! echec rechargement " + n + " -> " + err)
if RELOAD_SCRIPTS:
    print("[ClearScriptCache] scripts : %d recharge(s), %d deja a jour, %d sans fichier"
          % (len(scripts_updated), len(scripts_same), len(scripts_nofile)))
    for n in scripts_updated:
        print("  ~ " + n)
    for n in scripts_nofile:
        print("  ? fichier introuvable pour : " + n)
result = {"purged": sorted(purged), "pycache_removed": pycache_removed,
          "reloaded": sorted(reloaded), "failed": failed,
          "scripts_updated": scripts_updated, "scripts_same": scripts_same, "scripts_nofile": scripts_nofile}
