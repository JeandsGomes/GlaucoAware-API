from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
import os
import signal
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from pydantic import BaseModel
import bcrypt
from datetime import datetime

from mongo_db import SGBD

app = FastAPI()

# --------------------------------------------------------------
# Banco de dados
_bd = SGBD()
# --------------------------------------------------------------

# Classificação

# Carregar o modelo
interpreter = tf.lite.Interpreter(model_path='mobilenetV2.tflite')

# Iniciar o interpretador
interpreter.allocate_tensors()

# Obter detalhes do tensor de entrada
entrada_details = interpreter.get_input_details()
entrada_shape = entrada_details[0]['shape']
entrada_dtype = entrada_details[0]['dtype']

# print(f'entrada_details:{entrada_details}\n\n')
# print(f'entrada_shape:{entrada_shape}\n\n')
# print(f'entrada_dtype:{entrada_dtype}')

id_images_list = {
    '0': '/media/jeanderson/Tranqueiras1/Jeanderson/Projetos/Mestrado_EG/API_GlaucoAware/uploaded_BEH-183.png',
}

labels = ['0','1','_1',]

# Rota home
@app.get("/")
def home():
    return {"mensagem": "Ola mundo"}

# Classificar 1 imagem
@app.post("/test_classificar/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()

    image_path = f"uploaded_{file.filename}"

    with open(image_path, "wb") as f:
        f.write(contents)

    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.

    # Converter a entrada para o tipo de dados esperado pelo modelo, se necessário
    if entrada_dtype != type(img_array):
        entrada = img_array.astype(entrada_dtype)

    # Definir a entrada do modelo
    interpreter.set_tensor(entrada_details[0]['index'], entrada)

    # Executar a inferência
    interpreter.invoke()

    # Obter detalhes do tensor de saída
    saida_details = interpreter.get_output_details()

    # Obter a saída do modelo
    saida = interpreter.get_tensor(saida_details[0]['index'])

    # Interpretar o resultado (por exemplo, para classificação)
    classe_predita = np.argmax(saida)

    print('labels[classe_predita]:',type(labels[classe_predita]))
    print('saida[classe_predita]:',type(saida[0][classe_predita]))# type(saida[classe_predita]))

    return JSONResponse(content={'predicao':labels[classe_predita], 'confianca':str(saida[0])}, status_code=200)


@app.get("/test_busca/{id_image}")
async def get_image(id_image: str):
    # Caminho para a imagem que você quer retornar
    image_path = id_images_list[id_image]
    
    # Retornar a imagem usando FileResponse
    return FileResponse(image_path, media_type="image/png")

@app.get("/cad_mng/")
def cad_mng(email:str, nome:str, senha:str):
    # verificar se email já foi cadastrado
    query = {
        'Email': email,
    }
    checking_email = _bd.mng_colection.find_one(query)
    if checking_email is None:
        documento = {
            'Email': email,
            'Nome': nome,
            'senha': senha,
        }
        _bd.mng_colection.insert_one(documento)
        return {"mensagem": "OK: Meneger cadastrado"}
    else:
        return {"mensagem": "Error: Email ja cadastrado"}

# Busca de mng usando email e senha
@app.get("/busca_mng/")
def busca_mng(email:str):
    query = {
        'Email': email,
    }
    checking_email = _bd.mng_colection.find_one(query)
    if not checking_email is None:
        checking_email.pop('_id')
        checking_email.pop('senha')
        checking_email["mensagem"] = "OK: Meneger cadastrado"
        return checking_email
    else:
        return {"mensagem": "Error: Meneger não encontrado"}

# Busca de mng usando email e senha
@app.get("/login_mng/")
def login_mng(email:str, senha:str):
    # verificar se email já foi cadastrado
    query = {
        'Email': email,
    }
    checking_email = _bd.mng_colection.find_one(query)

    # TODO cripitografar a senha
    if not checking_email is None:
        matched = bcrypt.checkpw(senha.encode('UTF-8'), checking_email['senha'].encode('UTF-8'))
        if matched:
            # result = dict(checking_email)
            checking_email.pop('_id')
            checking_email["mensagem"] = "OK: Meneger cadastrado"
            print(f'checking_email: {checking_email}')  
            return checking_email
        else:
            return {"mensagem": "Error: Senha incorreta"}
    else:
        return {"mensagem": "Error: Email não encontrados"}

# Cadastrar e retornar o resultado de uma classificação
# image {'id_image','id_paciente',
# 'path_in_server','path_in_local_machine':, 
# 'data do cadastro', 'hora do cadastro'}
def classificação(image_path: str) -> dict:
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.

    # Converter a entrada para o tipo de dados esperado pelo modelo, se necessário
    if entrada_dtype != type(img_array):
        entrada = img_array.astype(entrada_dtype)

    # Definir a entrada do modelo
    interpreter.set_tensor(entrada_details[0]['index'], entrada)

    # Executar a inferência
    interpreter.invoke()

    # Obter detalhes do tensor de saída
    saida_details = interpreter.get_output_details()

    # Obter a saída do modelo
    saida = interpreter.get_tensor(saida_details[0]['index'])

    # Interpretar o resultado (por exemplo, para classificação)
    classe_predita = np.argmax(saida)

    return {'predicao':labels[classe_predita], 'confianca':str(saida[0])}

@app.post("/classification_image/")
async def classification_image(file: UploadFile = File(...)):
    # Realizar a classificação
    # salvando imagem recebida

    buffer_server = "buffer_server/"
    if not os.path.exists(buffer_server):
        os.mkdir(buffer_server)

    contents = await file.read()

    image_path = f"{buffer_server}{file.filename}"
    with open(image_path, "wb") as f:
        f.write(contents)
    dict_results = classificação(image_path)

    return {'predicao': dict_results['predicao'],
            'confianca': dict_results['confianca'], 
            "mensagem": "Ok"}

@app.post("/cad_image/")
async def cad_image(file: UploadFile = File(...),
                    id_paciente: str = Form(...),
                    email_mng: str = Form(...), 
                    path_in_local_machine: str = Form(...),):
    # try:
    # Salvar image
    # Criar uma pasta buffer-server
    buffer_server = "buffer_server/"
    # TODO verifcar se paciente já foi cadastrado antes
    query = {
        'id_paciente': id_paciente
    }
    checking_id = _bd._identity_colection.find_one(query)

    if checking_id is None:
        if not os.path.exists(buffer_server):
            os.mkdir(buffer_server)
        # salvando imagem recebida
        contents = await file.read()
        image_path = f"{buffer_server}{file.filename}"
        with open(image_path, "wb") as f:
            f.write(contents)

        # Realizar a classificação
        dict_results = classificação(image_path)

        agora = datetime.now()
        data_formatada = agora.strftime("%d/%m/%Y")
        hora_formatada = agora.strftime("%H:%M:%S")

        # Armazenar metadata no mongodb
        documento = {
            'email_mng': email_mng,
            'id_paciente': id_paciente,
            'path_in_local_machine': path_in_local_machine,
            'path_in_server': image_path,
            'predicao': dict_results['predicao'],
            'confianca': dict_results['confianca'],
            'data': data_formatada,
            'hora': hora_formatada
        }
        _bd._identity_colection.insert_one(documento)

        documento['mensagem'] = "OK: Paciente cadastrada"
        documento.pop('_id')
        return JSONResponse(documento)
    else:
        return {"mensagem": "Error: Imagem não cadastrada"}
    # except:
    #    return {"mensagem": "Error: Imagem cadastrada"}

# Busca de paciente
@app.get("/search_paciente/")
def search_paciente(email_mng:str, id_paciente:str):
    
    query = {
        'email_mng': email_mng,
        'id_paciente': id_paciente,
    }

    paciente = _bd._identity_colection.find_one(query)
    if not paciente is None:
        # print('paciente:',paciente)
        paciente.pop('_id')
        paciente["mensagem"] = "OK: Paciente encontrado"
        return paciente
    else:
        return {"mensagem": "Error: Paciente não encontrado encontrado"}
    
@app.get("/search_paciente_image/")
async def get_image(email_mng: str,
                    path_in_server: str):
    
    query = {
        'email_mng': email_mng,
        'path_in_server': path_in_server,
    }

    paciente = _bd._identity_colection.find_one(query)
    if not paciente is None:
        return FileResponse(path_in_server, media_type="image/png")
    else:
        return {"mensagem": "Error: Paciente não encontrado encontrado"}
    
@app.get("/editar_paciente/")
async def editar_paciente(query_id_paciente: str,
                    new_id_paciente: str):
    query = {"id_paciente":{"$eq": query_id_paciente}}
    present_data = _bd._identity_colection.find_one(query)
    if not present_data is None:
        new_data = {'$set':{"id_paciente": new_id_paciente}}
        _bd._identity_colection.update_one(present_data,new_data)
        return {"mensagem": "OK: Paciente edirtado"}
    else:
        return {"mensagem": "Error: Id de Paciente não encontrado"}
    
@app.get("/remove_paciente/")
async def remove_paciente(query_id_paciente: str):
    query = {"id_paciente": query_id_paciente}
    present_data = _bd._identity_colection.find_one(query)
    if not present_data is None:
        _bd._identity_colection.delete_one(query)
        return {"mensagem": "OK: Paciente removido"}
    else:
        return {"mensagem": "Error: Id de Paciente não encontrado"}

@app.get("/retorna_todos_pacientes/")
async def retorna_todos_pacientes():
    todos_os_pacientes = _bd._identity_colection.find()
    lista_pacientes = dict()
    for idx,paciente in enumerate(todos_os_pacientes):
        paciente.pop("_id")
        lista_pacientes[str(idx)] = paciente
    lista_pacientes["mensagem"] = "OK"
    return lista_pacientes