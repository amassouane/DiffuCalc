from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import math
from flask_mail import Mail, Message
import requests
import os  # Import pour les variables d'environnement
from dotenv import load_dotenv  # Pour charger les variables d'environnement

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Ajouter la configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # Utilise SQLite par défaut
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactiver le suivi des modifications pour éviter les avertissements

db = SQLAlchemy(app)  # Initialiser SQLAlchemy après avoir configuré l'application
mail = Mail(app)

# Ajouter la configuration de la clé secrète
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Utilise une clé par défaut si non définie

s = URLSafeTimedSerializer(app.secret_key)

# Charger la clé secrète reCAPTCHA depuis une variable d'environnement
SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupérer la réponse reCAPTCHA du formulaire
        recaptcha_response = request.form.get('g-recaptcha-response')
        data = {
            'secret': SECRET_KEY,
            'response': recaptcha_response
        }
        # Vérifier la réponse avec l'API reCAPTCHA
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result.get('success'):
            # Si reCAPTCHA est validé, traiter les données du formulaire
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            if User.query.filter_by(email=email).first():
                flash("Cet email existe déjà.", "danger")
            else:
                user = User(email=email, password=password)
                db.session.add(user)
                db.session.commit()
                flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('login'))  # Redirection vers la page de connexion
        else:
            # Si reCAPTCHA échoue
            flash("Erreur : reCAPTCHA invalide. Réessayez.", "danger")

    # Pass the reCAPTCHA site key to the template
    recaptcha_site_key = os.getenv('RECAPTCHA_SITE_KEY', 'default_site_key')
    return render_template('register.html', recaptcha_site_key=recaptcha_site_key)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Connecté avec succès.", "success")
            return redirect(url_for('diffusion'))  # Redirection vers la page de calcul après connexion
        else:
            flash("Identifiants incorrects.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Déconnecté avec succès.", "info")
    return redirect(url_for('home'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='reset-password')
            reset_link = url_for('reset_token', token=token, _external=True)

            try:
                msg = Message('Réinitialisation de votre mot de passe',
                              recipients=[email])
                msg.body = f"Pour réinitialiser votre mot de passe, cliquez sur le lien suivant : {reset_link}"
                try:
                    msg.html = render_template('email/reset_password.html', reset_link=reset_link)
                except Exception as e:
                    flash("Erreur : le fichier email/reset_password.html est introuvable ou invalide.", "danger")
                    return redirect(url_for('reset_request'))
                mail.send(msg)
                flash("Un email de réinitialisation a été envoyé.", "info")
            except Exception as e:
                flash(f"Erreur lors de l'envoi de l'email : {e}", "danger")
        else:
            flash("Email non trouvé.", "danger")
    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)
    except:
        flash("Lien invalide ou expiré.", "danger")
        return redirect(url_for('reset_request'))

    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            new_password = request.form['password']
            if (len(new_password) < 8 or
                not any(char.isupper() for char in new_password) or
                not any(char.isdigit() for char in new_password) or
                not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in new_password)):
                flash("Le mot de passe doit contenir au moins 8 caractères, une majuscule, un chiffre et un symbole.", "danger")
                return render_template('reset_token.html')  # Stay on the same page
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Mot de passe mis à jour.", "success")
            return redirect(url_for('login'))
    return render_template('reset_token.html')

@app.route('/diffusion', methods=['GET', 'POST'])
def diffusion():
    if 'user_id' not in session:  # Vérifier si l'utilisateur est connecté
        flash("Veuillez vous connecter pour accéder à cette page.", "warning")
        return redirect(url_for('login'))

    default_values = {
        'x_A': '0.25',
        'D_AB_0': '2.1e-5',
        'D_BA_0': '2.67e-5',
        'q_A': '1.432',
        'q_B': '1.4',
        'r_A': '1.4311',
        'r_B': '0.92',
        'a_AB': '-10.7575',
        'a_BA': '194.5302',
        'T': '313.13',
        'D_exp': '1.33e-5'
    }

    if request.method == 'POST':
        try:
            data = {k: float(request.form[k].replace(',', '.')) for k in default_values}
            x_B = 1 - data['x_A']
            y_A = data['r_A'] ** (1/3)
            y_B = data['r_B'] ** (1/3)
            phi_A = (data['x_A'] * y_A) / (data['x_A'] * y_A + x_B * y_B)
            phi_B = (x_B * y_B) / (data['x_A'] * y_A + x_B * y_B)
            theta_A = (data['x_A'] * data['q_A']) / (data['x_A'] * data['q_A'] + x_B * data['q_B'])
            theta_B = (x_B * data['q_B']) / (data['x_A'] * data['q_A'] + x_B * data['q_B'])
            tau_AB = math.exp(-data['a_AB'] / data['T'])
            tau_BA = math.exp(-data['a_BA'] / data['T'])
            theta_AA = (theta_A * 1.0) / (theta_A * 1.0 + theta_B * tau_BA)
            theta_BB = (theta_B * 1.0) / (theta_A * tau_AB + theta_B * 1.0)
            theta_AB = (theta_A * tau_AB) / (theta_A * tau_AB + theta_B * 1.0)
            theta_BA = (theta_B * tau_BA) / (theta_A * 1.0 + theta_B * tau_BA)

            ln_D = (
                (data['x_A'] * math.log(data['D_BA_0']) + x_B * math.log(data['D_AB_0'])) +
                2 * (data['x_A'] * math.log(data['x_A'] / phi_A) + x_B * math.log(x_B / phi_B)) +
                2 * data['x_A'] * x_B * (
                    (phi_A / data['x_A']) * (1 - (y_A / y_B)) + (phi_B / x_B) * (1 - (y_B / y_A))
                ) +
                data['x_A'] * data['q_B'] * ((1 - theta_AB**2) * math.log(tau_AB) + (1 - theta_AA**2) * tau_BA * math.log(tau_BA)) +
                x_B * data['q_A'] * ((1 - theta_BA**2) * math.log(tau_BA) + (1 - theta_BB**2) * tau_AB * math.log(tau_AB))
            )

            D_calc = math.exp(ln_D)
            erreur = abs((D_calc - data['D_exp']) / data['D_exp']) * 100

            return render_template("result.html",
                                   D_calc=D_calc,
                                   D_exp=data['D_exp'],
                                   erreur=erreur,
                                   theta_AA=theta_AA,
                                   theta_AB=theta_AB,
                                   theta_BA=theta_BA,
                                   theta_BB=theta_BB)
        except ValueError as ve:
            flash("Erreur de saisie : Veuillez vérifier les valeurs entrées.", "danger")
        except KeyError as ke:
            flash("Erreur : Une valeur attendue est manquante.", "danger")
        except Exception as e:
            flash("Erreur de calcul : Une erreur inattendue s'est produite.", "danger")
            print(f"Erreur détaillée : {e}")  # Pour le débogage uniquement

    return render_template('diffusion.html', default=default_values)

@app.route('/explanation')
def explanation():
    return render_template('explanation.html')

if __name__ == '__main__':
    # Configuration du host et du port
    host = '0.0.0.0'  # Écoute sur toutes les interfaces
    port = 5000       # Port par défaut
    
    print(f"🚀 L'application est disponible ici : http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}")
    print(f"📡 Accessible sur le réseau local via l'IP de votre machine")
    
    app.run(host=host, port=port, debug=True)