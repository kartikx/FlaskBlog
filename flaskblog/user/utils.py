import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail

def save_picture(form_picture):

    #Randomizing file name, to prevent overwrites.
    # ? Is this correct? Isn't there still a possibility to overwrite?
    f_name = secrets.token_hex(8)

    # Using an unnamed variable as splitext returns the fname and the ext
    _, f_ext = os.path.splitext(form_picture.filename)

    picture_fn = f_name + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profilepics', picture_fn)
    
    # Resizing the image to save space
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Instead of saving the original picture,
    # Save the resized picture instead.
    i.save(picture_path)
    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for("user.reset_password", token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)
