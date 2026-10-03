# Projet : multi-outil type Flipper Zero, fait maison

But : construire un multi-outil open source inspiré du Flipper Zero, pour
**moins cher** et en **apprenant** (soudure, électronique, firmware), avec le
**boîtier imprimé** sur la Creality K1C. Projet maker / éducatif.

> Important : un Flipper Zero n'est **pas** un Raspberry Pi.
> - Flipper = outil radio/NFC/infrarouge de poche (microcontrôleur).
> - Raspberry Pi = mini-ordinateur Linux complet.
> Les réunir dans un boîtier existe (projet HackBat) mais c'est avancé.
> Plan conseillé : d'abord cloner le Flipper, le Pi en v2.

## Ce qu'est un Flipper, en modules

Chaque fonction = un petit module. C'est ce qui rend le clone faisable.

| Module | Fonction | Prix indicatif (AliExpress) |
| --- | --- | --- |
| ESP32-S3 (dev board) | cerveau, WiFi + Bluetooth intégrés | 6–10 € |
| CC1101 | radio sub-GHz (433/868 MHz) | 3–5 € |
| PN532 | NFC / RFID 13,56 MHz | 4–7 € |
| LED IR + récepteur IR (TSOP) | infrarouge | 1–2 € |
| Écran OLED SSD1306 ou TFT ST7789 | affichage | 4–9 € |
| Batterie LiPo + module TP4056 | alimentation + charge USB | 5–8 € |
| Boutons tactiles, fils Dupont, perfboard | assemblage | ~5 € |

**Total modules : ~35–55 €** selon la source. Boîtier imprimé : négligeable (PLA).
Pour comparaison, un Flipper Zero neuf tourne autour de 169 €.

AliExpress = le moins cher mais 2–4 semaines de délai. Amazon/Mouser = plus cher,
reçu en quelques jours.

## Les deux voies

### Voie A — carte toute faite (rapide, sans câblage)

**LilyGo T-Embed CC1101** (~55–65 €). Tous les modules déjà soudés sur une
seule carte. On branche en USB, on flashe un firmware, c'est fini.

- Firmwares : **Bruce** ou **CapibaraZero** (open source).
- À faire soi-même : le **boîtier imprimé**.
- Ce qu'on apprend : le flashage de firmware (côté logiciel).
- Résultat en une soirée.

### Voie B — modules séparés (vrai « fait maison », soudure)

Base **FlopperZiro** (Arduino) ou un ESP32-S3 + modules du tableau ci-dessus,
soudés/câblés à la main sur une perfboard.

- Ce qu'on apprend : soudure + électronique + firmware.
- Moins cher, plus long, bien plus formateur.
- Le boîtier imprimé doit loger tous les modules → on le dessine après avoir
  les composants en main (pour mesurer).

## Plan conseillé

1. **Voie A d'abord** : résultat qui marche vite, on apprend le firmware sans stress.
2. **Voie B ensuite** : le vrai projet de soudure, une fois le logiciel maîtrisé.
3. **Boîtier** : dans les deux cas, c'est le livrable de ce dépôt (Blender → K1C).

## Projets open source à reprendre

| Projet | Base | Lien |
| --- | --- | --- |
| Bruce firmware | ESP32 / LilyGo T-Embed | github → pr3y/Bruce |
| CapibaraZero | ESP32-S3 | github → CapibaraZero |
| FlopperZiro | Arduino + modules | github.com/lraton/FlopperZiro |
| HackBat (Flipper + Pi) | RP2040 + ESP8266 | projet HackBat (CNX Software) |
| ESP32-DIV | un seul ESP32 | hackster.io (CiferTech) |

(Vérifier les dépôts à jour avant d'acheter : le matériel compatible évolue vite.)

## Boîtier — ce que ce dépôt doit produire

- Mesurer chaque module (pied à coulisse) **avant** de modéliser : largeur,
  longueur, hauteur, position des trous de vis / USB / écran.
- Dessiner une coque en deux parties (haut / bas) qui clipse ou se visse.
- Découpes : écran, port USB-C, boutons, LED, antenne.
- Respecter les règles d'impression du `CLAUDE.md` (parois ≥ 1,2 mm, maillage
  fermé, etc.).
- Imprimer, ajuster, réimprimer. Le premier boîtier n'est jamais le bon — c'est
  normal et pas cher en PLA.

## Cadre

Projet perso d'apprentissage et d'impression 3D. Les outils de ce type servent
à tester **son propre** matériel et réseau, ou à apprendre l'électronique et la
radio. Respecter la loi locale sur les fréquences radio et ne tester que ce qui
t'appartient.
