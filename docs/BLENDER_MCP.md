# Connecter Claude Code à Blender

## Comment ça marche (important)

`blender-mcp` fonctionne en **local** : l'add-on ouvre un socket dans Blender
(par défaut `localhost:9876`) et le serveur MCP lancé par Claude Code s'y connecte.
Les deux doivent tourner **sur la même machine**.

Conséquence : une session Claude Code **dans le cloud** (claude.ai/code, GitHub Action)
ne peut pas piloter ton Blender — son conteneur n'a aucun accès à ton PC.
Il faut lancer `claude` **depuis ton propre terminal**, dans ce dossier.

## Installation (une seule fois)

Windows (PowerShell) :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-blender-mcp.ps1
```

macOS / Linux :

```bash
bash scripts/setup-blender-mcp.sh
```

Le script installe `uv`, installe l'add-on Blender, et enregistre le serveur MCP.

### À la main, si tu préfères

```bash
# 1. uv
# Windows : powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS   : brew install uv
# Linux   : curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. serveur MCP
claude mcp add blender uvx blender-mcp

# 3. add-on Blender
uvx blender-mcp install-addon
```

## Côté Blender (à chaque session)

1. Blender 3.0 ou plus récent.
2. **Édition → Préférences → Add-ons** : activer « Blender MCP » (barre de recherche si besoin).
3. Dans la vue 3D : touche **N** → onglet **Blender MCP** → **Start MCP Server**.

## Côté Claude Code

```bash
cd /chemin/vers/3D-object
claude
```

Puis `/mcp` : `blender` doit apparaître comme connecté. Le fichier `.mcp.json`
à la racine du dépôt charge le serveur automatiquement, avec la télémétrie coupée
(`DISABLE_TELEMETRY=true`).

Test :

> crée une table en bois avec quatre pieds et un éclairage studio

## Avertissements

- L'outil exécute du **code Python arbitraire** dans Blender. **Sauvegarde ton .blend**
  avant de jouer.
- Travaille dans un fichier de test, pas dans un projet que tu ne veux pas perdre.

## Si ça bloque

| Symptôme | Piste |
| --- | --- |
| `uv` / `uvx` : commande introuvable | Rouvre le terminal ; sinon ajoute `~/.local/bin` (ou `%USERPROFILE%\.local\bin`) au PATH |
| `blender` absent de `/mcp` | Tu as lancé `claude` depuis un autre dossier, ou le serveur MCP n'est pas enregistré |
| « connection refused » | L'add-on n'est pas activé, ou « Start MCP Server » pas cliqué dans la vue 3D |
| Session cloud | Normal : relance `claude` en local (voir le premier paragraphe) |
| `$'\r': command not found` | Tu lances le `.sh` sur Windows : utilise le `.ps1`. Si tu veux vraiment bash, `git config core.autocrlf input` puis re-clone (le `.gitattributes` du dépôt corrige ça pour les nouveaux clones) |
