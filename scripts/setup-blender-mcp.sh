#!/usr/bin/env bash
# Setup Blender MCP pour Claude Code (macOS / Linux)
# Usage :  bash scripts/setup-blender-mcp.sh

set -euo pipefail

echo "== 1/3 Installation de uv =="
if command -v uv >/dev/null 2>&1; then
  echo "uv déjà installé : $(uv --version)"
else
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  echo "uv installé. Ferme et rouvre ton terminal si 'uv' n'est pas reconnu."
fi

echo "== 2/3 Installation de l'add-on Blender =="
uvx blender-mcp install-addon

echo "== 3/3 Enregistrement du serveur MCP dans Claude Code =="
if command -v claude >/dev/null 2>&1; then
  # Le .mcp.json du dépôt suffit si tu lances Claude Code depuis ce dossier.
  # Cette ligne ajoute le serveur globalement, pour l'avoir partout.
  claude mcp add blender uvx blender-mcp
else
  echo "CLI 'claude' introuvable : le fichier .mcp.json du dépôt fera le travail."
fi

cat <<'EOF'

Terminé. Il reste 2 étapes manuelles dans Blender :
  1. Édition > Préférences > Add-ons : activer « Blender MCP »
  2. Dans la vue 3D : touche N > onglet « Blender MCP » > « Start MCP Server »
Puis dans Claude Code : /mcp pour vérifier que « blender » est connecté.
EOF
