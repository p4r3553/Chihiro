# 🐉 Chihiro - ELF Reverse Engineering Toolkit

Chihiro est un outil Python de rétro-ingénierie pour binaires ELF (Executable and Linkable Format), avec une interface graphique complète. Il intègre plusieurs fonctions d'analyse statique et dynamique, dont un débogueur GDB intégré.

---

## ✨ Fonctionnalités

### 📂 Analyse statique
- Lecture et extraction d'informations ELF
- Table des symboles (`.symtab`, `.dynsym`)
- Désassemblage de la section `.text`
- Extraction de chaînes ASCII
- Visualisation de CFG (Control Flow Graph)

### 🐞 Débogueur GDB intégré
- Interface graphique GDB avec :
  - Points d’arrêt (breakpoints)
  - Exécution, pas-à-pas (step, next)
  - Affichage des registres
  - Recherche dans la sortie GDB
  - Clear terminal, scroll toggle, etc.

---

## 📦 Installation

### Prérequis

- Python 3.10+
- Linux (supporte ELF & GDB)
- `gdb` installé
- `capstone` (pour le désassemblage)

### Installer les dépendances :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt update
sudo apt install gdb
sudo apt install graphviz libgraphviz-dev

python -m ui.gui
./chihiro [FILES] --info --?
