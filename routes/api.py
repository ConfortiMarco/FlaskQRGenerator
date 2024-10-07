from flask import Flask, render_template, request, jsonify, Blueprint
from models.conn import db 
from models.model import * 
import qrcode
from PIL import Image
import os
import base64
import io
import datetime
from werkzeug.utils import secure_filename


api = Blueprint('api', __name__)

@api.route('/')
def home():
    api_key = ApiKey.query.filter_by(value=request.headers.get('X-API-Key')).first()
    if api_key: 
        user = api_key.user
        return f'Accesso per {user.username} tramite API key'
    else:
        return 'chiave non valida'

@api.route('/createQR',methods=['POST'])
def set_link():
    api_key = ApiKey.query.filter_by(value=request.headers.get('X-API-Key')).first()
    if api_key:
        url = request.form['url']
        back_color = request.form['coloresfondo']
        fill_color = request.form['coloreriempimento']
        box_size = request.form['grandezza']
        file = request.files['immagine']
        filename_public = None

        if not url:
            return "error no url"

        if not back_color:
            return "error no url"

        if not fill_color:
            return "error no url"
    
        if file.filename != '':     
            dt = datetime.datetime.now()
            filename = secure_filename(str(dt.microsecond)+"_"+file.filename)
            filename_public = filename
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
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
            logo = Image.open(current_app.config['UPLOAD_FOLDER']+"/"+filename_public).convert("RGBA")
            
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

        qrcode_db = QrCode(link=url,background_color=back_color,fill_color=fill_color,size=box_size,file=filename_public,qr_base64=img_base64,user_id=api_key.user_id)
        db.session.add(qrcode_db) 
        db.session.commit()
        return img_base64
    else:
        return "chiave non valida"

@api.route('/history')
def history():
    api_key = ApiKey.query.filter_by(value=request.headers.get('X-API-Key')).first()
    if api_key:
        qr_codes = db.session.execute(db.select(QrCode).filter_by(user_id=api_key.user_id)).scalars().all()
        qr_cs = [qr_code.to_dict() for qr_code in qr_codes]
        return jsonify(qr_cs)
    else:
        return 'chiave non valida'
