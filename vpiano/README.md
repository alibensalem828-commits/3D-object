# vpiano — jouer une partition sur un piano virtuel

Petit projet Python qui **pilote ton clavier** pour jouer un morceau sur un piano
virtuel à l'écran (le genre d'appli où chaque touche du clavier = une note).

Le script n'a aucune idée de ce qu'est ton jeu : il envoie simplement les frappes
au système, donc elles arrivent dans **la fenêtre qui a le focus**. Tu lances le
script, tu cliques sur le piano, et ça joue tout seul.

---

## Installation

```bash
pip install -r vpiano/requirements.txt
```

`pynput` est le backend recommandé. Si jamais il ne marche pas chez toi,
installe `pyautogui` et lance avec `--backend pyautogui` (c'est plus lent).

Sur **macOS**, il faut autoriser ton terminal dans
*Réglages Système → Confidentialité et sécurité → Accessibilité*.
Sur **Linux/Wayland**, `pynput` ne fonctionne pas toujours : passe en X11 ou
utilise `pyautogui`.

## Utilisation

```bash
# voir les partitions disponibles
python -m vpiano --list

# essayer sans rien taper (affiche juste les touches dans le terminal)
python -m vpiano demo-gamme --dry-run

# pour de vrai : tu as 5 secondes pour cliquer sur la fenêtre du piano
python -m vpiano etude-mi-mineur

# variantes
python -m vpiano etude-mi-mineur --speed 1.5      # 50 % plus rapide
python -m vpiano etude-mi-mineur --tempo 200      # tempo imposé
python -m vpiano etude-mi-mineur --transpose 12   # une octave au-dessus
python -m vpiano etude-mi-mineur --loop 3         # en boucle
python -m vpiano ma_partition.txt                 # ton propre fichier
```

**Appuie sur `ÉCHAP` à tout moment pour couper.** Le script relâche alors toutes
les touches qu'il tenait (sinon tu te retrouves avec Shift bloqué).
`Ctrl+C` dans le terminal marche aussi.

> Commence toujours par `--dry-run` quand tu écris une partition : ça affiche la
> suite de touches sans rien envoyer au système.

---

## Le clavier

Le piano à l'écran fait 61 touches, de **do2 (C2)** à **do7 (C7)** :

```
blanches : 1234567890  qwertyuiop  asdfghjkl  zxcvbnm
noires   : !@ $%^  *( QWE  TY IOP  SD GHJ  LZ CVB
```

Une touche noire, c'est la même touche avec **Shift**. Le script gère ça tout
seul : tu écris `F#4`, il appuie sur Shift + la bonne touche.

Si une note sort des 61 touches (à cause d'un `--transpose` par exemple), elle
est ignorée et le script te prévient au démarrage.

---

## Écrire sa propre partition

Un fichier `.txt` tout bête. Les lignes vides, ce qui suit un `;`, et les lignes
qui commencent par `#` sont ignorés.

### Réglages

```
@title mon-morceau
@tempo 148        ; battements par minute
@unit 16          ; l'unité de base = une double-croche (4 = noire, 8 = croche)
@hold 0.8         ; portion du temps où la touche reste enfoncée (0.1 à 1.0)
```

`@hold` est ce qui change le feeling : `0.95` ça sonne legato, `0.4` ça sonne
staccato et ça détache bien les notes rapides.

### Les notes

| Écriture | Effet |
|---|---|
| `E4` | une note, qui dure une unité |
| `E4:4` | une note qui dure 4 unités |
| `E4:0.5` | une note deux fois plus courte (une triple-croche si `@unit 16`) |
| `[E3 G3 B3]` | un accord : toutes les touches ensemble |
| `[E3 G3 B3]:8` | un accord tenu 8 unités |
| `~` / `~:4` | un silence |
| `gliss(C4,C6,8)` | glissando touches blanches de C4 à C6, étalé sur 8 unités |
| `gliss#(C4,C6,8)` | pareil mais chromatique (avec les noires) |
| `... x4` | répète toute la ligne 4 fois |

Les bémols passent aussi : `Bb4` = `A#4`.

Les sections `:nom` ne servent qu'à l'affichage, pour voir où tu en es pendant
que ça joue.

### Exemple

```
@tempo 140
@unit 16

:refrain
[E2 B2]:2 E5:2 D5:2 B4:2 [E3 G3]:2 B4:2 D5:2 E5:2
E5:0.5 E6:0.5   x16
gliss(E3,E6,8) gliss(E6,E3,8)
[E2 B2 E3 G3 B3 E4]:16
```

---

## Partitions fournies

- **`demo-gamme`** — gamme, chromatique, arpège, glissando. Sert à vérifier que
  le mapping tombe bien sur les bonnes touches de ton jeu.
- **`etude-mi-mineur`** — une pièce originale en mi mineur écrite pour ce
  lecteur, dans l'esprit « rush » : ostinato en doubles-croches, martèlement de
  notes répétées à la double vitesse, glissandos et accords finaux. C'est elle
  qui montre ce que le moteur a dans le ventre.

### Et Rush E ?

Rush E est une composition protégée (Sheet Music Boss), donc je ne l'ai pas
recopiée ici. Le moteur, lui, est fait exactement pour ce genre de morceau — si
tu as la partition, tu la retranscris dans le format ci-dessus et tu la lances
comme n'importe quel autre fichier. Les ingrédients sont tous là : notes très
rapides (`:0.5`, `:0.25`), gros accords, glissandos, et `--speed` pour pousser
le tempo jusqu'à ce que ça casse.

---

## Limites

- La précision du timing dépend de l'OS. Au-delà de ~25 notes/seconde, certains
  jeux commencent à rater des frappes : baisse `--speed`, ou `@hold` pour que les
  touches se relâchent plus tôt.
- Un jeu qui bloque les frappes synthétiques (anti-cheat) ne verra rien passer.
  Ça marche sur les pianos web et les applis classiques.
- Les frappes vont à la fenêtre active : si tu cliques ailleurs pendant la
  lecture, tu écris des lettres au hasard dans ce que tu as sous les yeux.

## Structure

```
vpiano/
├── keymap.py     notes <-> touches du clavier (et glissandos)
├── sheet.py      lecture du format de partition
├── backends.py   pynput / pyautogui / dry-run
├── player.py     moteur de lecture, timing, touche panique
├── cli.py        interface en ligne de commande
└── songs/        les partitions
```
