from flask import Flask, render_template


app = Flask(__name__)


@app.route('/cadastro')
def cadastro_funcionario():
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
