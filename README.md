# Smode Clear Script Cache

*[Version française](README.fr.md)*

> **Experimental, not an official Smode tool.** Built by trial and error against the Oil API (see [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Tested on Smode Compose R15.

Smode keeps imported Python modules and Script code in memory: after editing a `.py` file you have to re-import
it. This Script **clears the Python cache and reloads your Scripts from their `.py` files**:

- purges the user modules from `sys.modules` (Smode, standard library and site-packages are protected) and re-imports
  them;
- optionally deletes the `__pycache__` folders;
- reloads the **code of the Scripts in the open project** from the `.py` files of your script folders (matched by the
  title of the header box, or by the Script name), so there is nothing to re-import.

## Install

1. Drag `ClearScriptCache_GYOMH.py` into your Smode project, **Launch Mode = Manual**.
2. Open it and set `SCRIPT_DIRS` at the top to the folder(s) containing your `.py` files (the most recent file wins).
3. Execute it whenever you have edited a script.

Other options: `NAME_FILTER` (only purge modules containing this text), `CLEAR_PYCACHE`, `RELOAD`, `RELOAD_SCRIPTS`,
`SKIP_SCRIPTS` (Script names never reloaded, e.g. a bridge running at every update).

## License

MIT — see [LICENSE](LICENSE).
