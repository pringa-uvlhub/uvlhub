from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user

from itsdangerous import SignatureExpired
from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm
from app.modules.auth.services import AuthenticationService, send_reset_email
from app.modules.profile.services import UserProfileService
from app.modules.auth.repositories import UserRepository

from datetime import datetime

from app.modules.auth.forms import ForgotPasswordForm, ResetPasswordForm
from app.modules.auth.models import User
from app import db

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        name = form.name.data
        surname = form.surname.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f'Email {email} in use')

        try:
            user_data = {
                'email': email,
                'password': password,
                'name': name,
                'surname': surname
            }
            authentication_service.send_verification_email(user_data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f'Error creating user: {exc}')

        return redirect(url_for('auth.confirmation'))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route('/confirmation/')
def confirmation():
    return render_template('auth/confirmation.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if authentication_service.login(form.email.data, form.password.data):
            return redirect(url_for('public.index'))

        return render_template("auth/login_form.html", form=form, error='Invalid credentials')

    return render_template('auth/login_form.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Desencriptar el token y recuperar los datos del usuario
        user_data = authentication_service.serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except SignatureExpired:
        flash('The confirmation link has expired.', 'error')
        return redirect(url_for('auth.show_signup_form'))
    except Exception:
        flash('Invalid confirmation token.', 'error')
        return redirect(url_for('auth.show_signup_form'))
    try:
        # Crear el usuario en la base de datos
        user = authentication_service.create_with_profile(**user_data)
        login_user(user)
        return redirect(url_for('public.index'))
    except Exception as e:
        flash(f"Error creating user: {str(e)}", "error")
        return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        user = UserRepository().get_by_email(email)
        print(user)
        if not user:
            flash("El correo electrónico no existe en el sistema.", "error")
            return redirect(url_for('auth.forgot_password'))

        if user:
            token = user.generate_reset_token()
            # Enviar el correo con el enlace de restablecimiento
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_reset_email(user.email, reset_url)
            flash('Se ha enviado un enlace de restablecimiento a tu correo.', 'info')
        else:
            flash('Si el correo existe, recibirás un enlace de restablecimiento.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    user = User.verify_reset_token(token)
    if not user or user.reset_token_expiration < datetime.now():
        flash('El enlace de restablecimiento es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Tu contraseña ha sido actualizada con éxito.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)
