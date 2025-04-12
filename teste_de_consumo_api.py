import requests
import os
import cv2
import random
import shutil
import bcrypt

def classificacao_de_images():
    # URL da API que você quer consumir
    url_classificacao = "http://127.0.0.1:8000/test_classificar"

    image_path = "/media/jeanderson/Tranqueiras1/Jeanderson/Projetos/Mestrado_EG/teste/1/BEH-10.png"

    # Abrir o arquivo de imagem em modo binário
    with open(image_path, "rb") as image_file:
        # Criar um dicionário de arquivos, onde a chave é o nome do campo esperado pela API e o valor é o arquivo
        files = {"file": image_file}

        # Fazer a requisição GET com cabeçalhos
        response = requests.post(url_classificacao, files=files)

    # Verificar se a requisição foi bem-sucedida (status code 200)
    if response.status_code == 200:
        # Obter os dados da resposta no formato JSON
        data = response.json()
        print(data)
    else:
        print(f"Erro na requisição: {response.status_code}")

def buscar_uma_image():
    # URL da API que retorna a imagem
    id_image = 0
    url = f"http://127.0.0.1:8000/test_busca/{id_image}"

    # Fazer a requisição GET
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Caminho onde a imagem será salva
        file_path = "downloaded_image.png"
        
        # Abrir um arquivo em modo de escrita binária e salvar o conteúdo da resposta
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        print(f"Imagem salva em {file_path}")
    else:
        print(f"Erro na requisição: {response.status_code}")

# DONE Cadastro de um mng
# DONE Cadastro não possivel por utilizar email ja cadastrado
def cadastrar_mng():
    url = "http://127.0.0.1:8000/cad_mng"
    new_mng = {
        'email': '1',
        'nome': 'User_Name',
        'senha': bcrypt.hashpw('123'.encode('UTF-8'), bcrypt.gensalt(10)),
    }
    response = requests.get(url, params=new_mng)
    print(response.json())

# DONE Busca de um Meneger cadastrado >> Login
def login_mng():
    url = "http://127.0.0.1:8000/login_mng"
    login = {
        'email': 'email_test_1@gmail.com',
        'senha': 'teste',
    }
    response = requests.get(url, params=login)
    print(response.json())

# DONE Teste login invalido
def invalid_login_mng():
    url = "http://127.0.0.1:8000/login_mng"
    login = {
        'email': 'email_test_2@gmail.com',
        'senha': 'teste_2',
    }
    response = requests.get(url, params=login)
    print(response.json())

# DONE Cadastrar Imagem
# DONE Não cadastrar pacientes repetidos
def cad_image():
    id_paciente = 1
    # Verificar se a pasta buffer exite
    # Verificar se a pasta existe
    folder_path = 'buffer'
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f'A pasta "{folder_path}" existe.')
    else:
        os.mkdir(folder_path)
        print(f'A pasta "{folder_path}" foi criada.')

    # Caminho do arquivo original
    image_path = "/media/jeanderson/Tranqueiras1/Jeanderson/Projetos/Mestrado_EG/teste/1/BEH-10.png"

    # Abrir o arquivo de imagem em modo binário
    with open(image_path, "rb") as image_file:
        # Criar um dicionário de arquivos, onde a chave é o nome do campo esperado pela API e o valor é o arquivo
        
        random_integer = random.randint(1, 5000)
        print('random_bytes:',str(random_integer))

        # Caminho e novo nome para o arquivo copiado
        # TODO colocar a data hora min e segundo e colocar um sleep de 1seg
        dst_path = f"buffer/{id_paciente}_{random_integer}.png"


        # Copiar e renomear o arquivo
        try:
            shutil.copy(image_path, dst_path)
        except FileNotFoundError:
            print(f'O arquivo {image_path} não foi encontrado.')
        except Exception as e:
            print(f'Ocorreu um erro: {e}')

        url_classificacao = "http://127.0.0.1:8000/cad_image"
        files = {"file": image_file,}
        data = {"id_paciente":id_paciente,
                "email_mng": 'email_test_2@gmail.com',
                "path_in_local_machine":dst_path,}

        # Fazer a requisição GET com cabeçalhos
        response = requests.post(url_classificacao, files=files, data=data)

        print(response.json())

# Buscar uma imagem
# {'email_mng': 'email_test_2@gmail.com', 'id_paciente': 1, 'path_in_local_machine': 'buffer/3571.png', 'path_in_server': 'buffer_server/BEH-10.png', 'predicao': '1', 'confianca': '[0.08403261 0.8625282  0.05343914]', 'mensagem': 'OK: Imagem cadastrada'}
def search_image():
    # DONE Buscar a image
    query = {'email_mng': 'email_test_2@gmail.com', 'id_paciente': 1}
    url = "http://127.0.0.1:8000/search_paciente"
    response_metadata = requests.get(url, params=query).json()
    print('result busca de paciente:',response_metadata)
    # Verificar se a iomagem já não existe no bufer
    # Existe
    if os.path.exists(response_metadata['path_in_local_machine']):
        # Usar a imagem que esta no buffer
        print('local_path:',response_metadata['path_in_local_machine'])
    # Não existe
    else:
        # Solicitar a imagem
        query_image = {'email_mng': 'email_test_2@gmail.com', 
                       'path_in_server': response_metadata['path_in_server'],}
        url = "http://127.0.0.1:8000/search_paciente_image"

        response_img = requests.get(url, params=query_image)
        
        # Abrir um arquivo em modo de escrita binária e salvar o conteúdo da resposta
        with open(response_metadata['path_in_local_machine'], "wb") as f:
            f.write(response_img.content)

        print('local_path:',response_metadata['path_in_local_machine'])

# DONE atualizar_paciente
def atualizar_paciente():
    data = {'query_id_paciente': 10, 
            'new_id_paciente': 11}
    url = "http://127.0.0.1:8000/editar_paciente"
    response = requests.get(url, params=data)
    print(response.json())


# DONE remove_paciente
def remove_paciente():
    data = {'query_id_paciente': 11}
    url = "http://127.0.0.1:8000/remove_paciente"
    response = requests.get(url, params=data)
    print(response.json())

# DONE Retornar todos os pacientes
def retorna_todos_pacientes():
    url = "http://127.0.0.1:8000/retorna_todos_pacientes"
    response = requests.get(url)
    print(response.json())

def main():
    cad_image()

if __name__ == "__main__":
    main()