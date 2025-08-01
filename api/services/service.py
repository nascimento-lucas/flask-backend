import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# === USUÁRIO ===

def cadastraUsuario(data):
    try:
        usuario = consultarUsuarioPorNumeroCracha(data["numeroCracha"])
        payload = {
            "nome": data["nome"],
            "valor": float(data["valor"]),
        }

        if usuario:
            # Atualiza
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/usuarios?numero_cracha=eq.{data['numeroCracha']}",
                headers=HEADERS,
                json=payload
            )
            if response.status_code == 204:
                return "Usuário atualizado com sucesso!"
        else:
            # Cria novo
            payload["numero_cracha"] = data["numeroCracha"]
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/usuarios",
                headers=HEADERS,
                json=payload
            )
            if response.status_code in (200, 201):
                return "Usuário cadastrado com sucesso!"
        return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao cadastrar usuário: {str(e)}"

def consultaUsuarios():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios?select=*",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return f"Erro: {str(e)}"

def consultarUsuarioPorNumeroCracha(numero_cracha):
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios?numero_cracha=eq.{numero_cracha}&select=*",
            headers=HEADERS
        )
        usuarios = response.json()
        return usuarios[0] if usuarios else None
    except Exception as e:
        return f"Erro: {str(e)}"

def adicionarValorUsuario(numero_cracha, valor):
    try:
        usuario = consultarUsuarioPorNumeroCracha(numero_cracha)
        if not usuario:
            return "Usuário não encontrado."
        novo_valor = usuario["valor"] + float(valor)
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios?numero_cracha=eq.{numero_cracha}",
            headers=HEADERS,
            json={"valor": novo_valor}
        )
        if response.status_code == 204:
            return "Valor adicionado com sucesso!"
        return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao adicionar valor: {str(e)}"

def listarUsuariosEmDivida():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/usuarios?select=*",
            headers=HEADERS
        )
        usuarios = response.json()
        return [usuario for usuario in usuarios if usuario["valor"] < 0]
    except Exception as e:
        return f"Erro: {str(e)}"    

# === ARTIGOS RELIGIOSOS ===

def venderArtigoReligioso(data):
    artigo_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/artigos_religiosos?id=eq.{data['id']}&select=*",
        headers=HEADERS
    )
    artigo_json = artigo_resp.json()
    artigo = artigo_json[0] if artigo_json else None

    if not artigo:
        raise Exception("Artigo não encontrado.")
    if artigo["quantidade"] < int(data["quantidade"]):
        raise Exception("Estoque insuficiente.")

    usuario = consultarUsuarioPorNumeroCracha(data["numeroCracha"])
    if not usuario:
        raise Exception("Usuário não encontrado.")

    total = float(artigo["valor"]) * int(data["quantidade"])

    # Atualiza estoque
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/artigos_religiosos?id=eq.{data['id']}",
        headers=HEADERS,
        json={"quantidade": artigo["quantidade"] - int(data["quantidade"])}
    )

    # Atualiza saldo
    novo_saldo = usuario["valor"] - total
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/usuarios?numero_cracha=eq.{data['numeroCracha']}",
        headers=HEADERS,
        json={"valor": novo_saldo}
    )

    # Registra venda com informações adicionais
    requests.post(
        f"{SUPABASE_URL}/rest/v1/vendas",
        headers=HEADERS,
        json={
            "tipo": "produto",
            "id_artigo": data["id"],
            "numero_cracha": data["numeroCracha"],
            "nome_usuario": usuario["nome"],
            "nome_produto": artigo["nome"],
            "valor": total
        }
    )

    return "Venda realizada com sucesso!"

def consultarVendas():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/vendas?select=*",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return f"Erro: {str(e)}"

# === ALIMENTOS ===

def venderAlimento(data):
    try:
        alimento_resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/alimentos?id=eq.{data['id']}&select=*",
            headers=HEADERS
        )
        alimento_json = alimento_resp.json()
        alimento = alimento_json[0] if alimento_json else None

        if not alimento:
            raise Exception("Alimento não encontrado.")
        if alimento["quantidade"] < int(data["quantidade"]):
            raise Exception("Estoque de alimento insuficiente.")

        usuario = consultarUsuarioPorNumeroCracha(data["numeroCracha"])
        if not usuario:
            raise Exception("Usuário não encontrado.")

        total = float(alimento["valor"]) * int(data["quantidade"])

        # Atualiza estoque
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/alimentos?id=eq.{alimento['id']}",
            headers=HEADERS,
            json={"quantidade": alimento["quantidade"] - int(data["quantidade"])}
        )

        # Atualiza saldo
        novo_saldo = usuario["valor"] - total
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/usuarios?numero_cracha=eq.{data['numeroCracha']}",
            headers=HEADERS,
            json={"valor": novo_saldo}
        )

        # Registra venda com informações adicionais
        requests.post(
            f"{SUPABASE_URL}/rest/v1/vendas",
            headers=HEADERS,
            json={
                "tipo": "alimento",
                "id_artigo": data["id"],  # ou id_alimento, se quiser separar no Supabase
                "numero_cracha": data["numeroCracha"],
                "nome_usuario": usuario["nome"],
                "nome_produto": alimento["nome"],
                "valor": total
            }
        )

        return "Venda de alimento realizada com sucesso!"
    except Exception as e:
        raise e



def buscarProdutoPorId(id):
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/artigos_religiosos?id=eq.{id}&select=*",
            headers=HEADERS
        )
        produtos = response.json()
        return produtos[0] if produtos else None
    except Exception as e:
        return f"Erro: {str(e)}"

def buscarAlimentoPorId(id):
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/alimentos?id=eq.{id}&select=*",
            headers=HEADERS
        )
        alimentos = response.json()
        return alimentos[0] if alimentos else None
    except Exception as e:
        return f"Erro: {str(e)}"
    
def listarProdutos():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/artigos_religiosos?select=*",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return f"Erro ao listar produtos: {str(e)}"
    
def listarAlimentos():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/alimentos?select=*",
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return f"Erro ao listar alimentos: {str(e)}"
    
def cadastrarProduto(data):
    try:
        # Consulta o artigo pelo ID
        response_get = requests.get(
            f"{SUPABASE_URL}/rest/v1/artigos_religiosos?id=eq.{data['id']}&select=*",
            headers=HEADERS
        )
        artigo = response_get.json()[0] if response_get.json() else None

        payload = {
            "nome": data["nome"],
            "descricao": data["descricao"],
            "quantidade": int(data["quantidade"]),
            "valor": float(data["valor"]),
        }

        if artigo:
            # Atualiza artigo
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/artigos_religiosos?id=eq.{data['id']}",
                headers=HEADERS,
                json=payload
            )
            if response.status_code == 204:
                return "Produto atualizado com sucesso!"
        else:
            # Cria novo artigo
            payload["id"] = data["id"]
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/artigos_religiosos",
                headers=HEADERS,
                json=payload
            )
            if response.status_code in (200, 201):
                return "Produto cadastrado com sucesso!"

        return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao cadastrar produto: {str(e)}"



def cadastrarAlimento(data):
    try:
        # Consulta o alimento pelo ID
        response_get = requests.get(
            f"{SUPABASE_URL}/rest/v1/alimentos?id=eq.{data['id']}&select=*",
            headers=HEADERS
        )
        alimento = response_get.json()[0] if response_get.json() else None

        payload = {
            "nome": data["nome"],
            "id": data["id"],
            "quantidade": int(data["quantidade"]),
            "valor": float(data["valor"]),
        }

        if alimento:
            # Atualiza alimento
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/alimentos?id=eq.{data['id']}",
                headers=HEADERS,
                json=payload
            )
            if response.status_code == 204:
                return "Alimento atualizado com sucesso!"
        else:
            # Cria novo alimento
            payload["id"] = data["id"]
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/alimentos",
                headers=HEADERS,
                json=payload
            )
            if response.status_code in (200, 201):
                return "Alimento cadastrado com sucesso!"

        return f"Erro: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao cadastrar alimento: {str(e)}"

        
        
        
        