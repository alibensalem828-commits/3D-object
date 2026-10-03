# De Blender à la Creality K1C

Le piège : un modèle beau au rendu est rarement imprimable. Le slicer ne voit
pas des « surfaces », il voit des **volumes fermés**. Voici le chemin complet.

## 1. Régler les unités (à faire une fois par fichier)

Blender travaille en mètres. Pour modéliser en millimètres :

`Scene Properties` (icône cône+sphère) → `Units` :

- Unit System : **Metric**
- Unit Scale : **0.001**
- Length : **Millimeters**

Tu tapes alors `60` pour 60 mm. Sans ça, tu modélises des objets de 60 mètres
et l'export sort n'importe quoi.

## 2. Activer le 3D-Print Toolbox

Livré avec Blender, désactivé par défaut :

`Edit → Preferences → Add-ons` → chercher `3D Print` → cocher
**Mesh: 3D-Print Toolbox**.

Il ajoute un onglet **3D-Print** dans la barre latérale du viewport (touche N).
Bouton **Check All** : il liste les problèmes (non-manifold, faces d'épaisseur
nulle, porte-à-faux, intersections) et te laisse sélectionner la géométrie
fautive d'un clic.

C'est l'outil le plus important de toute la chaîne. Ne jamais exporter sans
l'avoir passé.

## 3. Les erreurs qui reviennent tout le temps

| Problème | Symptôme dans le slicer | Correctif Blender |
| --- | --- | --- |
| Maillage non fermé | trous, zones transparentes | Edit Mode → `Select → All by Trait → Non Manifold`, puis combler |
| Normales inversées | intérieur/extérieur inversés | Edit Mode → tout sélectionner → **Maj+N** |
| Face d'épaisseur nulle | la paroi disparaît | modificateur **Solidify**, épaisseur ≥ 1,2 mm |
| Booléen non appliqué | géométrie fantôme | appliquer le modificateur avant export |
| Échelle non appliquée | pièce 1000× trop grande/petite | **Ctrl+A → All Transforms** |
| Doublons de sommets | arêtes bizarres | Edit Mode → **M → By Distance** |

## 4. Contraintes physiques FDM

- **Épaisseur mini** : 1,2 mm (3 × la buse de 0,4). En dessous, c'est fragile.
- **Porte-à-faux** : au-delà de **45°** de la verticale, il faut des supports.
  Mieux vaut chanfreiner ou réorienter la pièce.
- **Détails** : rien de plus fin que 0,4 mm ne sortira — c'est la largeur de la buse.
- **Trous** : prévoir +0,2 à +0,4 mm de diamètre, le plastique se rétracte.
  Un trou de 5 mm se dessine à 5,3 mm.
- **Assise** : il faut une face plane posée sur le plateau, sinon brim ou raft
  obligatoires.
- **Volume** : 220 × 220 × 250 mm. Viser 210 × 210 × 240 pour garder une marge.

## 5. Export

Objet sélectionné, puis `File → Export → STL (.stl)`.

Dans le panneau de droite de la fenêtre d'export :

- **Selection Only** : coché (sinon tu exportes la caméra et la lampe)
- **Scale** : `1` si tu as réglé les unités à l'étape 1
- Format : **Binary** (fichier bien plus léger)

Ranger dans `exports/`, avec un nom qui dit les dimensions :
`support-casque-180x90x120.stl`.

## 6. Slicer

Deux options pour la K1C :

- **Creality Print** — l'officiel, profil K1C intégré, envoi direct par le
  réseau vers l'imprimante.
- **OrcaSlicer** — nettement meilleur, profil K1C inclus, calibrations intégrées
  (flow, pressure advance). C'est celui que recommande la plupart des
  utilisateurs K1C.

Réglages de départ raisonnables en PLA :

| Réglage | Valeur |
| --- | --- |
| Hauteur de couche | 0,2 mm |
| Parois | 3 |
| Remplissage | 15 % (gyroid) |
| Buse | 220 °C |
| Plateau | 60 °C |
| Vitesse | commencer modéré, la K1C monte très haut mais la qualité souffre |

Pour le PETG : buse 240 °C, plateau 80 °C, ventilation réduite.
Pour les composites fibre de carbone : la buse acier trempé de la K1C est faite
pour ça, mais il faut sécher le filament.

## 7. Workflow conseillé avec Claude Code

1. Décris la pièce **avec ses dimensions en mm** et son usage.
2. Laisse-le modéliser, puis demande-lui de lancer `Check All` du 3D-Print
   Toolbox et de te donner les chiffres.
3. Fais-lui corriger ce qui sort, et seulement ensuite exporter.
4. Ouvre le STL dans le slicer et **regarde l'aperçu couche par couche** avant
   de lancer : c'est là qu'on voit les supports absurdes et les parois manquantes.

Ne jamais lancer une impression de 6 heures sans avoir regardé l'aperçu.
