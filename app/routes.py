from app import app
from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, Appointment1, Appointment2, Appointment3
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Services, Specialists, Specialization, Doctor, Ticket, SuperUser




# главная страница
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


# вход для пациента
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
        if form.role.data == True:
            user = Doctor.get_by_login(form.username.data)
            SuperUser._flag = 'doc'
        else:
            user = User.get_by_sertificate(form.username.data)
            SuperUser._flag = 'client'

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect("/login")
        print("имя найденного пользователя")
        print(user.name)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = "/index"
        return redirect(next_page)
    return render_template('client_login.html', title = 'Личный кабинет пациента', form=form)



# регистрация в системе для пациента
@app.route("/registration", methods = ['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(sertificate = form.username.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}',
                birthdate =  f'{form.year.data}-{form.month.data}-{form.day.data}')
        user.set_password(form.password1.data)
        user.adduser()
        flash('Вы создали нового пользователя')
        return redirect(url_for('login'))
    return render_template('registration.html', title = 'Регистрация в системе', form=form)

#просмотр страниц с контактами
@app.route("/contacts", methods = ['GET'])
def contacts():
    return render_template('contacts.html', title = 'Контакты')

#просмотр страниц с услугами
@app.route("/services", methods = ['GET', 'POST'])
def services():
    serv = Services.get_services()
    return render_template('services.html', title = 'Список предоставляемых услуг', serv = serv)


#просмотр страницы со специалистами
@app.route("/specialists", methods = ['GET'])
def specialists():
    #ПЕРЕДЕЛАТЬ СЕЛЕКТ!!!
    spec = Specialists.get_specialist()
    return render_template('specialists.html', title = 'Персонал клиники', spec = spec)


#просмотр страницы со специалистами
@app.route("/clinic_work", methods = ['GET'])
def clinic_work():
    return render_template('clinic_work.html', title = 'Режим работы')

@app.route("/appointment1/<username>", methods = ['GET', 'POST'])
@login_required
def appointment1(username):
    form = Appointment1()
    specializations = Specialization.get_specializations()
    
    if specializations is None:
        specializations = []
    #print("Вот из этого списка выбираем")
    #print("----------------------------")
    #print(specializations)
    form.specialization.choices = specializations
    if form.validate_on_submit():
        print("-----------------------------------------")
        spec_id = form.specialization.data
        print(spec_id)
        return redirect(url_for('appointment2', spec_id=spec_id, username=username))
    return render_template('appointment1.html', form=form, title = 'Запись на прием')

@app.route("/appointment2/<username>/<spec_id>" , methods = ['GET', 'POST'])
@login_required
def appointment2(spec_id, username):
    form = Appointment2()
    specialist = Specialists.get_spec_by_specialization_id(spec_id)
    if specialist is None:
        specialist = []
    form.specialist.choices = specialist
    if form.validate_on_submit():
        doc_id = form.specialist.data
        print(doc_id)
        return redirect(url_for("appointment3", spec_id = spec_id, doc_id=doc_id, username=username))
    return render_template('appointment2.html', form=form, title = 'Запись на прием')

@app.route("/appointment3/<username>/<spec_id>/<doc_id>", methods = ['GET', 'POST'])
@login_required
def appointment3(spec_id, doc_id, username):
    form = Appointment3()
    if form.validate_on_submit():
        date = f'{form.year.data}-{form.month.data}-{form.day.data}'
        time = form.time.data
        d_login = Specialists.get_doc_login_by_doc_id(doc_id)
        cl_id = User.get_id_by_sertificate(username)
        Ticket.add_ticket(date, time, username, cl_id, doc_id, d_login)
        return redirect(url_for('index'))
    return render_template('appointment3.html', form=form, title = 'Запись на прием')
    

    




# мой профиль пациента
@app.route("/client/<username>", methods = ['GET'])
@login_required
def client(username):
    user = User.get_by_sertificate(username)
    return render_template('client.html', title = 'Личный кабинет пациента', user=user)


# мой профиль врача
@app.route("/doctor/<username>", methods = ['GET', 'POST'])
@login_required
def doctor(username):
    user = Doctor.get_by_login(username)
    return render_template('doctor.html', title = 'Личный кабинет врача', user=user)


# выйти из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/index")