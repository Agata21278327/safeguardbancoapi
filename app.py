import json

import sqlalchemy
from flask import Flask, Response, request
from flask_pydantic_spec import FlaskPydanticSpec
from flask_restful import Api, Resource
from sqlalchemy import select, exc
from sqlalchemy.exc import IntegrityError

from models import Epi, Entrega, Funcionario, db_session

app = Flask(__name__)
api = Api(app)

# documentação
spec = FlaskPydanticSpec('flask',
                         title='Safe Guard',
                         version='1.0.0')
spec.register(app)


@app.route('/addFuncionario', methods=['POST'])
def add_funcionario():
    '''1-Adiciona um funcionario
    2- Adiciona uma funcionario no banco de dados
    3- Podendo ser alterado futuramente e deletado do banco de dados
    adicione: nome(String) e cpf(string)
    ex: POST /addFuncionario'''
    try:
        funcionario = Funcionario(nome=request.form['nome'],
                                  cpf=request.form['cpf'])
        db_session.add(funcionario)
        funcionario.save()
        final = {
            'status': 'success',
            'nome': funcionario.nome,
            'cpf': funcionario.cpf
        }
        return app.response_class(response=json.dumps(final),
                                  status=201,
                                  mimetype='application/json')
    except IntegrityError:
        final = {
            'status': 'error',
            'message': 'erro verifique se o cpf já está cadastradao no banco de dados'
        }
        return app.response_class(response=json.dumps(final),
                                  # Bad Request é o status 400, de acordo com a situação é o mais adequado
                                  status=400,
                                  mimetype='application/json')


@app.route('/selectFuncionario', methods=['GET'])
def consultar_funcionario():
    '''1-lista dos funcionarios cadastradas
    2- Consultar funcionarios no banco de dados
    3- Lista todos os funcionarios cadastradas assim tendo uma melhor visão dos funcionarios
    ex: /selectFuncionario'''
    try:
        funcionario = Funcionario.query.all()
        result = []
        for consultar in funcionario:
            result.append(consultar.serialize_funcionario())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'error',
            'message': 'erro verifique se ha algum funcionario cadastrado no banco de dados'
        }
        return app.response_class(response=final,
                                  # Bad Request é o status 400, de acordo com a situação é o mais adequado
                                  status=400,
                                  mimetype='application/json')


@app.route('/updateFuncionario/<int:id>', methods=['PUT'])
def update_fun(id):
    '''1- Atualiza o funcionario no banco de dados
       2- Permite alterar os dados do funcionario no banco e entre outras informações de tal
       adicione na rota o id(Int) do funcionario que deseja atualizar, mudando o nome(string) e cpf(int,unique)
       ex:/updateFuncionario/2'''
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        funcionario.nome = request.form['nome_']
        funcionario.cpf = request.form['cpf']
        db_session.commit()
        final = {
            'status': 'success',
            'nome': funcionario.nome,
            'cpf': funcionario.cpf
        }
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'error',
            'mensagem': 'erro ao atualizar os dados do funcionario desejado'
        }
        return app.response_class(response=json.dumps(final),
                                  # Not Modified é usado para fins de cache. Ele informa ao cliente que a resposta não foi modificada
                                  status=304,
                                  mimetype='application/json')


@app.route('/deleteFuncionario/<int:id>', methods=['DELETE'])
def delete(id):
    '''1- Deleta o funcionario
    2- Deleta o funcionario do banco de dados apagando seu histórico de registro
    3- não podendo trazer de volta
    adicione o id(int) do funcionario na rota
    ex:/deleteFuncionario/1'''
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        final = {
            'status': 'removido',
            'nome': funcionario.nome,
            'cpf': funcionario.cpf
        }
        db_session.delete(funcionario)
        db_session.commit()
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'funcionario nao deletado'
        }
        return app.response_class(response=json.dumps(final),
                                  status=200,
                                  mimetype='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'funcionario nao deletado'
        }
        return app.response_class(response=json.dumps(final),
                                  status=200,
                                  mimetype='application/json')


@app.route('/addEpi', methods=['POST'])
def add_epi():
    '''1-Adiciona um epi
    2- Adiciona um epi no banco de dados
    3- Podendo ser alterado futuramente e deletado do banco de dados
    adicione o nome do epi(string), descrição(string) e validade(string)
    '''
    epi = Epi(nome=request.form['nome'],
              descricao=request.form['descrição'],
              validade=request.form['validade'])
    db_session.add(epi)
    epi.save()
    final = {
        'status': 'success',
        'nome': epi.nome,
        'descrição': epi.descricao,
        'validade': epi.validade
    }
    return app.response_class(response=json.dumps(final),
                              status=201,
                              mimetype='application/json')


@app.route('/selectEpi', methods=['GET'])
def consultar_epi():
    '''1- Lista epis
    2- Lista todos os epis registrados no banco de dados, ajudando a se organizar
    ex: /selectEpi
    '''
    try:
        consultar_epi = Epi.query.all()
        result = []
        for consultar in consultar_epi:
            result.append(consultar.serialize_epi())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'Verifique se á algum epi registrado no banco de dados'
        }
        return app.response_class(response=json.dumps(final),
                                  # Bad Request é o status 400, de acordo com a situação é o mais adequado
                                  status=400,
                                  mimetype='application/json')


@app.route('/updateEpi/<int:id>', methods=['PUT'])
def update_epi(id):
    '''1- Atualiza epi
    2- Podendo mudar seu nome cpf e endereco, poderem não pode ser utilizado o cpf anterior
    adicione na rota o id(int) do epi que deseja alterar, mudando o nome(string), descrição(string) e validade do epi(string)
    ex: /updateEpi/1'''
    try:
        epi = select(Epi).where(Epi.id == id)
        epi = db_session.execute(epi).scalar()
        epi.nome = request.form['nome']
        epi.descricao = request.form['descricao']
        epi.validade = request.form['validade']
        db_session.commit()
        final = {
            'status': 'success',
            'nome': epi.nome,
            'descrição': epi.descricao,
            'validade': epi.validade
        }
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'error',
            'message': 'erro ao atualizar verifique se o id ja foi utilizado'
        }
        return app.response_class(response=final,
                                  # Internal Server Error 500, ja tem um item com esse id cadastrado no caso
                                  status=500,
                                  mimetype="application/json")


@app.route('/deleteEpi/<int:id>', methods=['DELETE'])
def delete_epi(id):
    '''1- Deleta o epi
    2- Apagando as informações e registros do epi
    adicione o id(int) do epi na rota e será deletado
    ex: /deleteEpi'''
    try:
        epi = select(Epi).where(Epi.id == id)
        epi = db_session.execute(epi).scalar()
        final = {
            'status': 'removido',
            'nome': epi.nome,
            'descrição': epi.descricao
        }
        db_session.delete(epi)
        db_session.commit()
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'epi nao deletada'
        }
        return app.response_class(response=json.dumps(final),
                                  status=500,
                                  mimetype='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'epi nao deletada'
        }

        return app.response_class(
            response=json.dumps(final),
            status=500,
            mimetype='application/json'
        )
    except exc.UnmappedInstanceError:
        final = {
            'status': 'erro',
            'mensagem': 'epi nao encontrada'
        }

        return app.response_class(
            response=json.dumps(final),
            status=500,
            mimetype='application/json'
        )


@app.route('/addEntrega', methods=['POST'])
def epi():
    '''1- Cria uma entrega
   2- Cadastra um entrega no banco de dados
   3- preencha todos dados
   adicione os campos de data de entrega(string), ca(Int), periodo(int),
   id do funcionario(int) e id do epi(int)
   ex: /addEntrega'''
    try:
        entrega = Entrega(
            data_entrega=request.form['data_de_entrega'],
            ca=request.form['ca'],
            periodo=request.form['periodo'],
            funcionario_id=int(request.form['funcionario_id']),
            epi_id=int(request.form['epi_id'])
        )
        db_session.add(entrega)
        entrega.save()
        final = {
            'status': 'success',
            'data de entrega': entrega.data_entrega,
            'ca': entrega.ca,
            'periodo': entrega.periodo,
            'funcionario id': entrega.funcionario_id,
            'epi id': entrega.epi_id
        }
        return app.response_class(response=json.dumps(final),
                                  status=201,
                                  mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
         final = {
             'status': 'error',
             'message': 'erro verifique a entrega'
         }
         return app.response_class(response=json.dumps(final),
                                   # Internal Server Error 500, ja tem um item com esse id cadastrado no caso o (cpf)
                                   status=500,
                                   mimetype='application/json')


@app.route('/selectEntrega', methods=['GET'])
def consultar_entrega():
    '''1- Lista as entregas
    2- Lista todas as entregas registradas no banco de dados, ajudando a se organizar
    ex: /selectEntrega'''
    try:
        consultar_entrega = Entrega.query.all()
        result = []
        for consultar in consultar_entrega:
            result.append(consultar.serialize_entrega())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'Verifique se ha alguma entrega registrada no banco de dados'
        }
        return app.response_class(response=json.dumps(final),
                                  # Bad Request é o status 400, de acordo com a situação é o mais adequado
                                  status=400,
                                  mimetype='application/json')


@app.route('/updateEntrega/<int:id>', methods=['PUT'])
def update_entrega(id):
    '''1- Atualiza entrega
    2- Podendo mudar a data de entrega
    adicione o id(Int) da entrega na rota e mude os campos de data de entrega(string),
    ca(int), periodo(int), id funcionario(int) e id epi(Int)
    ex: /updateEntrega/23'''
    entrega = select(Entrega).where(Entrega.id == id)
    entrega = db_session.execute(entrega).scalar()
    entrega.data_entrega = request.form['data de entrega']
    entrega.ca = request.form['ca']
    entrega.periodo = request.form['periodo']
    entrega.funcionario_id = request.form['funcionario id']
    entrega.epi_id = request.form['epi id']
    db_session.commit()
    final = {
        'status': 'success',
        'data de entrega': entrega.data_entrega,
        'ca': entrega.ca,
        'periodo': entrega.periodo,
        'funcionario id': entrega.funcionario_id,
        'epi id': entrega.epi_id
    }
    return Response(response=json.dumps(final),
                    status=201,
                    mimetype='application/json')


@app.route('/deleteEntrega/<int:id>', methods=['DELETE'])
def delete_entrega(id):
    '''1- Deleta Entrega
    2- Apagando as informações e registros das entregas
    adicione o id(int) da entrega na rota e deleta
    ex: /deleteEntrega/20'''
    try:
        entrega = select(Entrega).where(Entrega.id == id)
        entrega = db_session.execute(entrega).scalar()
        final = {
            'status': 'removido',
            'data de entrega': entrega.data_entrega,
            'ca': entrega.ca,
            'periodo': entrega.periodo,
            'funcionario id': entrega.funcionario_id,
            'epi id': entrega.epi_id
        }
        db_session.delete(entrega)
        db_session.commit()
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'entrega nao deletada'
        }
        return app.response_class(response=json.dumps(final),
                                  status=500,
                                  mimetype='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'entrega nao deletada'
        }

        return app.response_class(
            response=json.dumps(final),
            status=500,
            mimetype='application/json'
        )
    except exc.UnmappedInstanceError:
        final = {
            'status': 'erro',
            'mensagem': 'entrega nao encontrada'
        }

        return app.response_class(
            response=json.dumps(final),
            status=500,
            mimetype='application/json'
        )


if __name__ == '__main__':
    app.run(debug=True)
