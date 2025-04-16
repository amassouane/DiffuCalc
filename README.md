# 🌡️ Coefficient de Diffusion - Modèle Hsu et Chen

Cette application web permet de **calculer le coefficient de diffusion mutuelle (`D_AB`) entre deux liquides**, comme le **méthanol et l’eau**, en appliquant le **modèle thermodynamique de Hsu et Chen**.

Elle intègre une interface utilisateur sécurisée avec connexion/inscription, système de mot de passe avec reCAPTCHA, et un calcul scientifique détaillé basé sur les propriétés moléculaires et les interactions spécifiques.


---

## 🧪 Description scientifique

Cette application calcule le coefficient de diffusion (<strong>D_AB</strong>) entre deux liquides (ex : méthanol et eau) à l’aide du **modèle thermodynamique de Hsu et Chen**.

> À partir des **fractions molaires**, des **paramètres moléculaires** (rayons, surfaces), et des **coefficients d’interaction**, elle estime la vitesse de diffusion des composants d’un mélange liquide.

🔹 Elle affiche le résultat **en cm²/s** et le compare à une valeur expérimentale donnée pour calculer **l’erreur relative**.

> Cette approche **évite d’utiliser le facteur de correction thermodynamique** souvent requis dans les méthodes classiques.

---

## 🔧 Fonctionnalités

- 🔐 Authentification sécurisée (Flask, sessions, hashage des mots de passe)
- ✅ Protection anti-bot avec **Google reCAPTCHA**
- 🔁 Réinitialisation de mot de passe par email (via Flask-Mail)
- 🧠 Calcul scientifique du coefficient de diffusion avec explication détaillée
- 🧮 Affichage clair des résultats et erreurs de prédiction
- 📱 Interface responsive (HTML + Jinja2)

---

## 🛠️ Technologies utilisées

- Python + Flask
- SQLAlchemy (Base de données SQLite)
- Flask-Mail (envoi d’email)
- Google reCAPTCHA (anti-robot)
- Jinja2 (templates dynamiques)
- HTML / CSS
- dotenv (variables d’environnement)

---

## 🚀 Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/choumaishanae/ton-projet.git
cd DiffuCalc