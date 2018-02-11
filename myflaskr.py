#！/usr/bin/env python
#-*- coding utf8 -*-
import os
from flask import Flask
from flask import request #请求上下文对象
from flask import render_template #模板
from flask import url_for,redirect

from flask.ext.script import Manager,Shell


from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from  wtforms.validators import DataRequired

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand #引入数据库迁移组件



class CNameFrom(Form):
    name = StringField('name?',validators=[DataRequired()])
    submit = SubmitField('Submit')


app = Flask(__name__)
manager = Manager(app)

def make_shell_context():
    return dict(app=app,db=db)
manager.add_command("shell",Shell(make_context=make_shell_context))
#基础配置
basedir = os.path.abspath(os.path.dirname(__file__))
dbfilePath = 'testdb.db'
print(basedir)
app.config["SECRET_KEY"] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'testdb.db'
print("app.config['SQLALCHEMY_DATABASE_URI'] = ", app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_CONNIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
print('db1 = ', db)
#定义数据库模型
class TableModelUser(db.Model):
    __tablename__='User'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    classId = db.Column(db.Integer, db.ForeignKey('Classes.id'))
    age = db.Column(db.Integer, default=0)

    def __reper__(self):
        return '<TableModelUser %r>' % self.username
class TableModelClass(db.Model):
    __tablename__ = 'Classes'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    classname = db.Column(db.String(20),unique=True,nullable=False)
    users = db.relationship('TableModelUser', backref='Classes')


#引入数据库迁移组建，修改数据库
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@app.route('/')
def root():
    login_url = url_for('index')#参数为函数名，不是装饰器的参数值
    return redirect(login_url)

@app.route('/index1')
def index():
    user_agent = request.headers.get('User-Agent')
    return 'this is index page browser is %s' %user_agent

@app.route('/user/<name>')
def user(name):
    return 'hello %s' % name
@app.route('/hello')
def hello():
    name = 'propitious'
    return render_template('hello.html', varName=name)

@app.before_first_request # 在第一次请求前执行，可以在这里尝试初始化数据库等操作。
def beforFirstReq():
    print('dbfilePath=',dbfilePath)
    if not os.path.exists(dbfilePath):
        print('db2 = ', db)
        db.create_all()
        classes01 = TableModelClass(classname='C01')
        classes02 = TableModelClass(classname='C02')
        user01 = TableModelUser(username='name01', Classes=classes01)
        user02 = TableModelUser(username='name02', Classes=classes01)
        user03 = TableModelUser(username='name03', Classes=classes02)
        db.session.add_all([classes01, classes02, user01, user02, user03])
        db.session.commit()
        print('============create table=========== ')
    else:
        print('============no need create table=============== ')

    print('init db ok!')

@app.errorhandler(404)
def show404err(e):
    return render_template('404.html'),404

def showUrlFor():
    return "this is urlfor text!"

@app.route('/userInfo/<name>')
def userInfo(name):
    age = 21
    return render_template('userInfo.html', name, age)
@app.route('/do',methods=['GET','POST'])
def showWTF():
    form = CNameFrom(request.form)
    name = 'x'
    if not form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('wtfForm.html', title='WTF', form=form, name=name)


@app.route("/class/<id>")
def getClassbyName(id):
    classes = TableModelClass.query.filter(id==id)
    print('classes = ', classes)
    print('classes count = ', classes.count())
    retStr = ''
    x = 0
    while x < classes.count():
        retStr += classes[x].classname + ','
        x += 1;
    return retStr

@app.route("/usr/<id>")
def getUserById(id):
    users = db.session.query(TableModelUser.username, TableModelClass.classname).filter(TableModelUser.id==id, TableModelUser.classId==TableModelClass.id)
    print('users = ', users)
    print('users count = ', users.count())
    print(users.all())
    retStr = ''
    for x in users:
        retStr += x[0] + '|'
        retStr += x[1] + ','
    return retStr

if __name__ == '__main__':
    app.run(debug=True)
