# Setup Blender MCP pour Claude Code (Windows / PowerShell)
# Usage :  powershell -ExecutionPolicy Bypass -File scripts\setup-blender-mcp.ps1

$ErrorActionPreference = "Stop"

Write-Host "== 1/3 Installation de uv ==" -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "uv deja installe : $((uv --version))"
} else {
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "uv installe. Ferme et rouvre ton terminal si 'uv' n'est pas reconnu." -ForegroundColor Yellow
}

Write-Host "== 2/3 Installation de l'add-on Blender ==" -ForegroundColor Cyan
uvx mcp-for-blender install-addon

Write-Host "== 3/3 Enregistrement du serveur MCP dans Claude Code ==" -ForegroundColor Cyan
if (Get-Command claude -ErrorAction SilentlyContinue) {
    # Le .mcp.json du depot suffit si tu lances Claude Code depuis ce dossier.
    # Cette ligne ajoute le serveur globalement, pour l'avoir partout.
    claude mcp add blender uvx mcp-for-blender
} else {
    Write-Host "CLI 'claude' introuvable : le fichier .mcp.json du depot fera le travail." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Termine. Il reste 2 etapes manuelles dans Blender :" -ForegroundColor Green
Write-Host "  1. Edition > Preferences > Add-ons : activer 'Interface: MCP for Blender'"
Write-Host "  2. Dans la vue 3D : touche N > onglet 'BlenderMCP' > 'Start MCP Server'"
Write-Host "Puis dans Claude Code : /mcp pour verifier que 'blender' est connecte."
