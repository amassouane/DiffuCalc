import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('a4d81e99b3e041cbb792c50469c9aa83d1fc4a5b93c2437aaf8bc832e947317f')
SQLALCHEMY_DATABASE_URI = os.getenv('sqlite:///users.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuration email (remplace par tes infos)
# Assurez-vous que les informations suivantes sont correctes :
# - MAIL_USERNAME : votre adresse email
# - MAIL_PASSWORD : le mot de passe ou le token d'application généré pour votre email
# - MAIL_SERVER et MAIL_PORT : les paramètres SMTP de votre fournisseur d'email
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv('yasch228@gmail.com')  # Replace with your email
MAIL_PASSWORD = os.getenv('gqqe rlma njtt ehrr')  # Replace with your email password
MAIL_DEFAULT_SENDER = (os.getenv('DiffuCalc'), os.getenv('yasch228@gmail.com'))