from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(3,50)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit   = SubmitField("Entrar")

class RegisterForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(3,50)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(6,128)])
    confirm  = PasswordField("Repite Contraseña",
                              validators=[DataRequired(), EqualTo("password")])
    submit   = SubmitField("Crear cuenta")
