# 3D-object

Modélisation Blender pilotée par Claude Code via MCP, avec pour cible
**l'impression 3D sur une Creality K1C**.

Setup de la connexion Blender : voir `docs/BLENDER_MCP.md`.
Règles d'impression détaillées : voir `docs/IMPRESSION_3D.md`.

## Objectif par défaut

Sauf mention contraire de l'utilisateur, tout modèle créé ici doit être
**imprimable**, pas seulement beau au rendu. Un maillage qui ne passe pas les
règles ci-dessous n'est pas un livrable.

## Contraintes machine (Creality K1C)

| Paramètre | Valeur |
| --- | --- |
| Volume d'impression | 220 × 220 × 250 mm |
| Buse | 0,4 mm acier trempé (standard) |
| Extrudeur | direct drive, caisson fermé |
| Hauteur de couche usuelle | 0,2 mm (plage 0,1 – 0,3) |
| Matériaux | PLA, PETG, ABS, ASA, TPU, composites fibre de carbone |

Marge de sécurité : viser **210 × 210 × 240 mm** maximum, jamais le volume brut.

## Règles de modélisation non négociables

1. **Échelle.** 1 unité Blender = 1 mètre. Travailler en mm et régler
   `Scene Properties → Units → Unit Scale = 0.001`, ou modéliser à l'échelle
   mètre puis exporter avec `Scale = 1000`. Toujours annoncer les dimensions
   finales en mm à l'utilisateur.
2. **Maillage fermé (manifold).** Aucun trou, aucune arête non-manifold, aucune
   face intérieure. Chaque volume doit être étanche.
3. **Pas de surface d'épaisseur nulle.** Un plan ou une face isolée n'est pas
   imprimable. Tout doit avoir une épaisseur réelle (modificateur Solidify si
   besoin).
4. **Épaisseur minimale 1,2 mm** (3 passes de buse). En dessous, la pièce est
   fragile ou le slicer ignore la paroi. 0,8 mm absolu pour un détail non porteur.
5. **Normales vers l'extérieur.** `Mesh → Normals → Recalculate Outside`
   (Maj+N en Edit Mode) avant tout export.
6. **Pas de géométrie qui s'interpénètre sans être fusionnée.** Appliquer les
   booléens, pas les laisser en modificateur.
7. **Appliquer les transformations** avant export : `Object → Apply → All
   Transforms` (Ctrl+A). Une échelle non appliquée fausse l'export.
8. **Porte-à-faux.** Au-delà de 45° par rapport à la verticale, il faut des
   supports. Préférer redessiner la pièce (chanfreins, orientation) plutôt que
   d'imposer des supports.
9. **Première couche.** Prévoir une face plane posée sur le plateau. Une pièce
   en équilibre sur une pointe ne s'imprime pas.

## Vérification avant de déclarer le modèle prêt

Exécuter dans Blender, via l'outil MCP, et rapporter les chiffres :

- nombre d'arêtes non-manifold (doit être 0)
- dimensions de la bounding box en mm
- nombre de triangles (au-delà de ~500 k, décimer)

L'add-on **3D-Print Toolbox** (livré avec Blender, à activer dans les
préférences) fait ces contrôles ; l'utiliser quand il est disponible.

## Export

- Format : **STL** (binaire) ou **3MF** si disponible.
- Dossier : `exports/` à la racine du dépôt, nom explicite en minuscules avec
  tirets, suffixé des dimensions — par ex. `support-casque-180x90x120.stl`.
- Exporter la **sélection uniquement**, pas toute la scène (ni caméra ni lampe).
- Les `.stl` et `.blend` ne sont pas versionnés (voir `.gitignore`) : ce sont
  des binaires lourds.

## Conventions de travail

- Sauvegarder le `.blend` dans `models/` avant toute opération destructrice.
- Nommer les objets explicitement dans l'outliner, jamais `Cube.001`.
- Supprimer le cube par défaut avant de commencer une nouvelle pièce.
- Répondre à l'utilisateur en français.
