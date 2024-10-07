from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from models.conn import db 
from models.model import * 
import qrcode
from PIL import Image
from flask_migrate import Migrate
from routes.auth import auth as bp_auth
from routes.api import api as bp_api
import os
import base64
import io
import datetime
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, current_user
from flask_swagger import swagger
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['QR_UPLOAD_FOLDER'] = os.getenv('QR_UPLOAD_FOLDER')
app.register_blueprint(bp_auth,url_prefix="/auth")
app.register_blueprint(bp_api,url_prefix="/api")

@app.route('/swagger')
def swagger_spec():
    swag = swagger(app)
    swag['info']['title'] = "API"
    swag['info']['description'] = "This is the API documentation"
    return jsonify(swag)

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    
    return user

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/home',methods=['POST'])
@login_required
def set_link():
    url = request.form['url']
    back_color = request.form['coloresfondo']
    fill_color = request.form['coloreriempimento']
    box_size = request.form['grandezza']
    file = request.files['immagine']
    filename_public = None

    if not url:
        flash('Invalid url')
        return redirect('/')

    if not back_color:
        flash('Invalid colore di sfondo')
        return redirect('/')

    if not fill_color:
        flash('Invalid colore di riempimento')
        return redirect('/')
    
    if not box_size:
        box_size = 5

    if file.filename != '':     
        dt = datetime.datetime.now()
        filename = secure_filename(str(dt.microsecond)+"_"+file.filename)
        filename_public = filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
 
    QRimg = qr.make_image(
    fill_color=fill_color, back_color=back_color).convert('RGB')

    if file.filename != '':
        logo = Image.open(app.config['UPLOAD_FOLDER']+"/"+filename_public).convert("RGBA")
        
        basewidth = int(box_size)*10
        
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize))
 
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos, logo)

    buffered = io.BytesIO()
    QRimg.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    b64_string =img_base64

    qrcode_db = QrCode(link=url,background_color=back_color,fill_color=fill_color,size=box_size,file=filename_public,qr_base64=img_base64,user_id=current_user.id)
    db.session.add(qrcode_db) 
    db.session.commit()

    with open(app.config['QR_UPLOAD_FOLDER']+"qr"+str(qrcode_db.id)+".png",'wb') as file:
        file.write(base64.decodebytes(b64_string.encode()))

    return render_template('info.html',url=img_base64)

@app.route('/history')
@login_required
def history():
    qr_codes = db.session.execute(db.select(QrCode).filter_by(user_id=current_user.id)).scalars().all()
    return render_template('history.html',qrcodes=qr_codes)

@app.route('/download/<id>',methods=['POST'])
@login_required
def download(id):
    qr_codes = db.session.execute(db.select(QrCode).filter_by(id=id)).scalars().first()
    if qr_codes:
        if qr_codes.user_id == current_user.id:
            uploads = os.path.join(current_app.root_path, app.config['QR_UPLOAD_FOLDER'])
            return send_file(uploads+'qr'+id+".png", as_attachment=True)
        else:
            return "Non è un stato possibile scaricare il qr"
    else:
        return "Non è un stato possibile scaricare il qr"

db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)