from flask import Flask, render_template, redirect, render_template, send_file, request
import sqlite3


app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return '<a href="/register">Register</a>'

@app.route('/register')
def register():
    return redirect(f'https://t.me/burnoutslidingtreesbot?start=register')

@app.route('/account/<int:telegram_id>')
def account(telegram_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE telegram_id=?', (telegram_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data is None:
        return 'User not found'

    user_info = {
        'name': user_data[1],
        'nickname': user_data[2],
        'photo': user_data[3],
        'user_id': user_data[4]
    }
    
    return render_template('account.html', user_info=user_info, url=user_data[3])

@app.route('/photo_image')
def photo_image():
    filename = request.args.get("filename")
    return send_file(filename, mimetype='image/jpg')

if __name__ == '__main__':
    app.run()



