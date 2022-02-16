from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EmailType
from wtforms import Form, StringField, validators


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "random string"

db = SQLAlchemy(app)


class Students(db.Model):
    id = db.Column("student_id", db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    surname = db.Column(db.String(25))
    email = db.Column(EmailType)

    def __init__(self, name, surname, email):
        self.name = name
        self.surname = surname
        self.email = email


class AddForm(Form):
    name = StringField("Name", [validators.Length(min=2, max=25)])
    surname = StringField("Surname", [validators.Length(min=2, max=25)])
    email = StringField("Email Address", [validators.Length(min=6, max=35)])


@app.route("/", methods=["GET", "POST"])
def show_all():
    form = AddForm(request.form)
    if request.method == "POST":
        print("ARGS: ", request.args)
        print("JSON: ", request.json)
        is_delete = request.args.get("delete")
        is_update = request.args.get("update")
        if is_delete and is_update:
            print("Can not update and delete at one time")
            return redirect(url_for("show_all"))

        if is_delete:
            body = request.json
            user_id = body.get("id")
            try:
                Students.query.filter_by(id=int(user_id)).delete()
                db.session.commit()
            except Exception as e:
                print(f"An exception occurred while delete: {e!r}")
            return redirect(url_for("show_all"))
        elif is_update:
            body = request.json
            user_id = body.get("id")
            name = body.get("name")
            surname = body.get("surname")
            email = body.get("email")
            try:
                stud = Students.query.filter_by(id=int(user_id)).first()
                stud.name = name
                stud.surname = surname
                stud.email = email
                db.session.commit()
            except Exception as e:
                print(f"An exception occurred while update: {e!r}")
            return redirect(url_for("show_all"))
        else:
            if form.validate():
                student = Students(form.name.data, form.surname.data, form.email.data)
                db.session.add(student)
                db.session.commit()
                flash("Form is valid!")
                return redirect(url_for("show_all"))
            render_template("main_page.html", form=form)
    return render_template("main_page.html", students=Students.query.all(), form=form)


if __name__ == "__main__":
    db.create_all()
    student = Students("Denis", "Vankov", "ivankovden99@gmail.com")
    db.session.add(student)
    db.session.commit()
    app.run(host="0.0.0.0", port=8000, debug=True)
