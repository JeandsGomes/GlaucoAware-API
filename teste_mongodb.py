from mongo_db import SGBD

_bd = SGBD()

def insercao_Maneger():
    documento = {
        'ID': 99,
        'Email': 'email_test@gmail.com',
        'Nome': 'User_Name',
        'senha': 'teste'
    }
    _bd.mng_colection.insert_one(documento)
    print('Inserção feita com sucesso')
# def insercao_Metadata_Images():
#    pass

def encontrar_um_individuo():
    query = {
        'ID': 10,
    }
    result = _bd.mng_colection.find_one(query)
    print('Resultado da busca:',result)

def inserir_varios():
    for idx in range(10):
        if _bd.mng_colection.find_one({'ID': idx}) is None:
            documento = {
                'ID': idx,
                'Email': 'email_test@gmail.com',
                'Nome': 'User_Name',
                'senha': 'teste'
            }
            _bd.mng_colection.insert_one(documento)

# Buscar todos
def buscar_todos():
    query = {'Email': 'email_test@gmail.com'}
    result = _bd.mng_colection.find(query)
    for documento in result:
        print(documento)


# remover 1
def remover_um():
    query = {'ID': 99}
    _bd.mng_colection.delete_one(query)

def main():
    insercao_Maneger()

if __name__=="__main__":
    main()