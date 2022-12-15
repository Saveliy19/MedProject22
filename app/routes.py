'''routes.py
Файл для работы с переходами между страницами
'''




from app import app
from flask import render_template, flash, redirect, url_for, session
from flask import request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, Appointment1, Appointment2, Appointment3, Priem, EditProfileForm, Appointment4, DeleteTicket
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Services, Specialists, Specialization, Doctor, Ticket, Note
from datetime import datetime




# главная страница
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


# вход пользователя
@app.route("/login", methods = ['GET', 'POST'])
def login():
    # если пользователь аутентифицирован
    if current_user.is_authenticated:
        return redirect("/index")
    # определяем необходимую форму из файла forms
    form = LoginForm()
    # если не возникло проблем с валидаторами, определенными в файле forms
    if form.validate_on_submit():
        # если поставлена галочка я врач
        if form.role.data == True:
            # задаем переменной роль в сессии значение доктор
            # это нужно для определения, из какой таблицы получать пользователя в методе loas user
            session['role'] = 'doc'
            user = Doctor.get_by_login(form.username.data)
            #SuperUser._flag = 'doc'
        else:
            # если не поставлена галочка, значит роль пользователя - клиент
            session['role'] = 'cl'
            user = User.get_by_sertificate(form.username.data)
            #SuperUser._flag = 'client'

        # если не нашелся пользователь с таким логином или пароль пользователя неверный
        if user is None or not user.check_password(form.password.data):
            # выдать ошибку на экран
            flash('Введен неправильный логин или пароль')
            return redirect("/login")
        print("имя найденного пользователя")
        print(user.name)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = "/index"
        return redirect(next_page)
    return render_template('client_login.html', title = 'Личный кабинет пациента', form=form)

@app.route("/edit_profile/<login>", methods = ['GET', 'POST'])
@login_required
def edit_profile(login):
    form = EditProfileForm()
    if form.validate_on_submit():
        if session['role'] == 'cl':
            user = User.get_by_sertificate(login)
            user.set_password(form.newpassword1.data)
            user.update_password_hash()
        elif session['role'] == 'doc':
            user = Doctor.get_by_login(login)
            user.password = form.newpassword1.data
            user.update_password()
        print('Пароль изменен')
        return redirect(url_for('index'))
    return render_template('edit_profile.html', title = 'Редактировать данные профиля', form=form)

# регистрация в системе для пациента
@app.route("/registration", methods = ['GET', 'POST'])
def registration():
    sd = ''
    form = RegistrationForm()
    if form.validate_on_submit():
        for s in form.sex.choices:
            if str(s[0]) == str(form.sex.data):
                sd = s[1]
        user = User(sertificate = form.username.data,
                name = f'{form.lastname.data} {form.firstname.data} {form.patronymic.data}',
                birthdate =  f'{form.birthdate.data}', sex = f'{sd}')
        user.set_password(form.password1.data)
        print(sd)
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

#смотрим, какие специалисты ведут прием по данной услуге
@app.route("/services/<service>", methods = ['GET', 'POST'])
@login_required
def service_name_specialists(service):
    specialists = Specialists.get_specialists_by_service(service)
    return render_template('specialists_by_service.html', title = 'Персонал клиники', specialists=specialists, service=f'{service}'.lower())


#просмотр страницы со специалистами
@app.route("/specialists", methods = ['GET', 'POST'])
def specialists():
    spec = Specialists.get_specialist()
    return render_template('specialists.html', title = 'Персонал клиники', spec = spec)

#смотрим по каким специальностям работает данный специалист
@app.route("/specialists/<name>", methods = ['GET', 'POST'])
@login_required
def specialist_name_services(name):
    services = Services.get_services_by_doc_name(name)
    return render_template('services_by_doc.html', title = 'Список предоставляемых услуг', services = services, name=name)



#просмотр страницы со специалистами
@app.route("/clinic_work", methods = ['GET'])
def clinic_work():
    return render_template('clinic_work.html', title = 'Режим работы')

@login_required
@app.route("/appointment1/<username>", methods = ['GET', 'POST'])
def appointment1(username):
    form = Appointment1()
    specializations = Specialization.get_specializations()
    
    if specializations is None:
        specializations = []
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
        return redirect(url_for("appointment4", spec_id = spec_id, doc_id=doc_id, username=username))
    return render_template('appointment2.html', form=form, title = 'Запись на прием')

@app.route("/appointment3/<username>/<spec_id>/<doc_id>/<service>", methods = ['GET', 'POST'])
@login_required
def appointment3(spec_id, doc_id, username, service):
    form = Appointment3()
    if form.validate_on_submit():
        date = form.day.data
        time = form.time.data
        d_login = Specialists.get_doc_login_by_doc_id(doc_id)
        cl_id = User.get_id_by_sertificate(username)
        Ticket.add_ticket(date, time, username, cl_id, doc_id, d_login)
        ticket_id = Ticket.get_ticket_by_docid_pat_dat(doc_id, username, date)
        Ticket.add_ticket_for_service(service, ticket_id)
        return redirect(url_for('index'))
    return render_template('appointment3.html', form=form, title = 'Запись на прием')

@app.route("/appointment4/<username>/<spec_id>/<doc_id>", methods = ['GET', 'POST'])
@login_required
def appointment4(username, spec_id, doc_id):
    serv = ''
    form = Appointment4()
    services = Services.get_services_by_doc_id(doc_id)
    if services is None:
        services = []
    form.service.choices = services
    if form.validate_on_submit():
        for s in form.service.choices:
            if str(s[0]) == str(form.service.data):
                serv = s[1]
        return redirect(url_for('appointment3', username=username, spec_id=spec_id, doc_id=doc_id, service=serv))
    return render_template('appointment4.html', form=form, title='Запись на прием')
        

    
@app.route("/2appointmen2/<username>/<service>", methods = ['GET', 'POST'])
@login_required
def second_appointment2(username, service):
    form = Appointment2()
    specialist = Specialists.get_specialists_by_service(service)
    if specialist is None:
        specialist = []
    form.specialist.choices = specialist
    if form.validate_on_submit():
        doc_id = form.specialist.data
        print(doc_id)
        return redirect(url_for("second_appointment3", service=service, doc_id=doc_id, username=username))
    return render_template('appointment2.html', form=form, title = 'Запись на прием')

@app.route("/2appointment/<username>/<service>/<doc_id>", methods = ['GET', 'POST'])
@login_required
def second_appointment3(username, service, doc_id):
    form = Appointment3()
    if form.validate_on_submit():
        date = form.day.data
        time = form.time.data
        d_login = Specialists.get_doc_login_by_doc_id(doc_id)
        cl_id = User.get_id_by_sertificate(username)
        Ticket.add_ticket(date, time, username, cl_id, doc_id, d_login)
        ticket_id = Ticket.get_ticket_by_docid_pat_dat(doc_id, username, date)
        print('----------------')
        print(ticket_id)
        print('----------------')
        Ticket.add_ticket_for_service(service, ticket_id)
        return redirect(url_for('index'))
    return render_template('appointment3.html', form=form, title = 'Запись на прием')

# мой профиль пациента
@app.route("/client/<username>", methods = ['GET'])
@login_required
def client(username):
    user = User.get_by_sertificate(username)
    ticket_lst = Ticket.get_ticket_by_CLIENT(username)
    return render_template('client.html', title = 'Личный кабинет пациента', user=user, ticket_lst=ticket_lst)

@app.route("/delete_ticket/<username>/<date>/<time>/<doctor>", methods=['GET','POST'])
@login_required
def delete_ticket(username, date, time, doctor):
    form = DeleteTicket()
    if form.validate_on_submit():
        Ticket.delete_ticket(username, date, time)
        return redirect(url_for('index'))
    return render_template('delete_ticket.html', form=form, title='Отмена записи', date = date, time=time, doctor=doctor)


@app.route("/medical_card/<username>", methods = ['GET', 'POST'])
@login_required
def medical_card(username):
    notes = Note.get_notes_by_client_sertificate(username)
    return render_template('medical_card.html', title = 'Медицинская карта', notes = notes)


# мой профиль врача
@app.route("/doctor/<username>", methods = ['GET', 'POST'])
@login_required
def doctor(username):
    user = Doctor.get_by_login(username)
    ticket_lst = Ticket.get_ticket_by_DOC(username)
    return render_template('doctor.html', title = 'Личный кабинет врача', user=user, ticket_lst=ticket_lst)

@app.route("/doctor/<username>/<client>", methods = ['GET', 'POST'])
@login_required
def priem(username, client):
    form = Priem()
    if form.validate_on_submit():
        description = form.description.data
        client_id = User.get_id_by_username(client)
        sertificate = User.get_sertificate_by_id(client_id)
        day = datetime.date(datetime.now())
        ticket_id = Ticket.get_ticket_by_doclog_pat_dat(username, client, day)
        Ticket.set_status_for_ticket_by_id(ticket_id, 'true')
        Note.add_note(description, ticket_id, client_id, sertificate)
        return redirect(url_for('doctor', username=current_user.login))
    return render_template('priem.html', form=form, title = 'Прием пациента')


# выйти из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/index")