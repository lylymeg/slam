# 🤖 Robotics LiDAR SLAM & Autonomous Mapping Simulation (Pygame)

Une simulation robotique représentant le fonctionnement d'un capteur **LiDAR (360°)** et d'un algorithme de **cartographie SLAM** (*Simultaneous Localization and Mapping*), développée en **Python** avec **Pygame**.

---

## 📸 Fonctionnalités

- 🛰️ **LiDAR 360° en temps réel :** Le robot émet des dizaines de télémètres laser pour détecter la distance exacte des obstacles environnants.
- 🗺️ **Cartographie SLAM progressive :** Construis et réaffiche l'environnement inconnu (points violets) au fur et à mesure que le robot explore la carte.
- 🕹️ **Pilotage interactif :** Prends les commandes du robot avec les touches fléchées pour cartographier les zones d'ombre.
- 🔄 **Réinitialisation de carte :** Efface la mémoire de la carte reconstruite à tout moment avec la touche `R`.

---

## 🚀 Lancement

```bash
pip install pygame
python main.py