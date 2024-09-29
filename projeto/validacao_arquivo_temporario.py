# após remodelar o banco de dados para criar o campo de CPF
# vamos fazer uma validação no back-end para verificar se o cpf está OK


import re

"""
import re: é usada para trabalhar com expressões regulares (regular expressions), 
uma ferramenta poderosa para busca e manipulação de strings com base em padrões. 
A biblioteca re permite realizar operações como correspondência, substituição e divisão 
de strings utilizando expressões regulares.
"""


@app.route('/criando_funcionario', methods=['POST'])
def criando_funcionario():
    cpf = request.form['cpf']

    # Expressão regular para validar o formato do CPF
    cpf_regex = r"\d{3}\.\d{3}\.\d{3}-\d{2}"

    if not re.match(cpf_regex, cpf):
        flash('CPF inválido. Formato correto: 000.000.000-00')
        return redirect(url_for('lista_de_funcionarios'))

    # Verificação de duplicidade no banco de dados
    funcionario_existente = Funcionarios.query.filter_by(cpf=cpf).first()

    if funcionario_existente:
        flash('Funcionário já cadastrado com este CPF.')
        return redirect(url_for('lista_de_funcionarios'))

    # Código para criar o novo funcionário...

    return redirect(url_for('lista_de_funcionarios'))
