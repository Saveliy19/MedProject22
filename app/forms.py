'''
файл хранения классов веб-форм
'''


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import User
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Номер полиса или логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    role = BooleanField('Я врач')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


# форма регистрации пациента
class RegistrationForm(FlaskForm):
    lastname = StringField('Фамилия', validators=[DataRequired()])
    firstname = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    birthdate = DateField('Дата рождения', format = '%Y-%m-%d')
    sex = SelectField('Пол', choices=[(1,'Муж'), (2,'Жен')])
    username = StringField('Номер полиса', validators=[DataRequired()])
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.get_by_sertificate(username.data)
        if user is not None:
            raise ValidationError('Пожалуйста, введите номер полиса, принадлежащий Вам!')
        return

# форма редактирования профиля
class EditProfileForm(FlaskForm):
    password = PasswordField('Старый пароль', validators=[DataRequired()])
    newpassword1 = PasswordField('Новый пароль', validators=[DataRequired()])
    newpassword2 = PasswordField('Повторите новый пароль', validators=[DataRequired(), EqualTo('newpassword1')])
    submit = SubmitField('Завершить редактирование')


class Appointment1(FlaskForm):
    specialization = SelectField('Выберите профиль врача') #coerce=int
    submit = SubmitField('Далее')

class Appointment2(FlaskForm):
    specialist = SelectField('Выберите специалиста')
    submit = SubmitField('Далее')

class Appointment3(FlaskForm):
    day = DateField('День приема', format = '%Y-%m-%d')
    time = TimeField('Выберите время приема')
    submit = SubmitField('Подтвердить запись')

    '''def validate_day(self, day):
        if int(day.data) < int(datetime.date()):
            raise ValidationError('Вы можете записаться на прием не ранее, чем на завтрашний день!')
        return

    def validate_time(self, time):
        if int(time.data) < 9 or int(time.data) > 19:
            raise ValidationError('Просмотрите часы работы клиники!')
        return'''
class Appointment4(FlaskForm):
    service = SelectField('Выберите услугу')
    submit = SubmitField('Далее')

class Priem(FlaskForm):
    description = TextAreaField('Введите данный в медицинскую карту пациента', validators=[DataRequired()])
    submit = SubmitField('Закончить прием')

class DeleteTicket(FlaskForm):
    submit = SubmitField('Отменить запись')
