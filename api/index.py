from flask import Flask, jsonify, request
from flask_cors import CORS

from api.services.service import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://trindasbox.vercel.app"}})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Flask funcionando na Vercel!"})

@app.route("/vendas", methods=["GET"])
def listar_vendas():
    vendas = consultarVendas()
    return jsonify(vendas)

# USUÁRIOS
@app.route("/novousuario", methods=["POST"])
def novousuario():
    data = request.get_json()
    mensagem = cadastraUsuario(data)
    return jsonify({"message": mensagem})

@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = consultaUsuarios()
    return jsonify(usuarios)

@app.route("/usuario/<numero_cracha>", methods=["GET"])
def buscar_usuario(numero_cracha):
    usuario = consultarUsuarioPorNumeroCracha(numero_cracha)
    return jsonify(usuario)

@app.route("/usuario/adicionarvalor", methods=["POST"])
def adicionar_valor_usuario():
    data = request.get_json()
    mensagem = adicionarValorUsuario(data["numeroCracha"], data["valor"])
    return jsonify({"message": mensagem})



# ARTIGOS RELIGIOSOS

@app.route("/venderproduto", methods=["POST"])
def vender_produto():
    try:
        data = request.get_json()
        mensagem = venderArtigoReligioso(data)
        return jsonify({"message": mensagem}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400



# ALIMENTOS
''
@app.route("/venderalimento", methods=["POST"])
def vender_alimento():
    try:
        data = request.get_json()
        mensagem = venderAlimento(data)
        return jsonify({"message": mensagem}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/produto/<id>", methods=["GET"])
def rota_buscar_produto(id):
    resultado = buscarProdutoPorId(id)
    if isinstance(resultado, dict):
        return jsonify(resultado)
    return jsonify({"erro": resultado}), 404


@app.route("/alimento/<id>", methods=["GET"])
def rota_buscar_alimento(id):
    resultado = buscarAlimentoPorId(id)
    if isinstance(resultado, dict):
        return jsonify(resultado)
    return jsonify({"erro": resultado}), 404

@app.route("/usuario/divida", methods=["GET"])
def rota_listar_usuarios_em_divida():
    resultado = listarUsuariosEmDivida()
    if isinstance(resultado, list):
        return jsonify(resultado)
    return jsonify({"erro": resultado}), 404

@app.route("/produtos", methods=["GET"])
def rota_listar_produtos():
    resultado = listarProdutos()
    if isinstance(resultado, list):
        return jsonify(resultado)
    return jsonify({"erro": resultado}), 500

@app.route("/alimentos", methods=["GET"])
def rota_listar_alimentos():
    resultado = listarAlimentos()
    if isinstance(resultado, list):
        return jsonify(resultado)
    return jsonify({"erro": resultado}), 500

@app.route("/novoproduto", methods=["POST"])
def adicionarProduto():
    data = request.get_json()
    mensagem = cadastrarProduto(data)
    return jsonify({"message": mensagem})

@app.route("/novoalimento", methods=["POST"])
def adicionarAlimento():
    data = request.get_json()
    mensagem = cadastrarAlimento(data)
    return jsonify({"message": mensagem})




