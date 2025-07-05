# XML Converter script to gather inventory data from a structured directory
# The script reads a directory structure where each sector has subdirectories for users,
# and each user directory contains a text file with the equipment name and JPEG photos.
# It generates an inventory JSON file and copies the photos to a specified output directory.

# XML Converter é um script para coletar dados de inventário de um diretório estruturado.
# O script lê uma estrutura de diretório onde cada setor tem subdiretórios para usuários
# e cada diretório de usuário contém um arquivo de texto com o nome do equipamento e fotos JPEG.
# Gera um arquivo JSON de inventário e copia as fotos para um diretório de saída especificado.

# by: Flavio Brandão

import os
import json
import shutil
from dotenv import load_dotenv
import xml.etree.ElementTree as ET


# Carrega variáveis do .env
#Load .env file
load_dotenv()

# read the directory from the environment variable
# Lê o diretório raiz da variável de ambiente
entrada_base = os.getenv("path.env")

saida_base = "Inventario"
os.makedirs(saida_base, exist_ok=True)
# Read a the .env file to get the base path for sectors
# Lê mapeamento dos setores do .env

setores_env = os.getenv("SETORES", "")
setores = {}
if setores_env:
    for item in setores_env.split(","):
        # Limit the split to the first ':'
        # Limita o split ao primeiro ':'
        k, v = item.split(":", 1)   
        setores[k.strip()] = v.strip()

# Starts the inventory structure
# Inicializa estrutura de inventário
inventario = []

# Iterates over sectors and users
# Itera sobre os setores e usuários
for setor_nome in os.listdir(entrada_base):
    setor_path = os.path.join(entrada_base, setor_nome)
    if not os.path.isdir(setor_path):
        continue
    
    # Default prefix for unknown sector    
    # Código padrão para setor desconhecido    

    prefixo_setor = setores.get(setor_nome, "UNKN")  

    for usuario in os.listdir(setor_path):
        usuario_path = os.path.join(setor_path, usuario)
        if not os.path.isdir(usuario_path):
            continue

        # Read the user's equipment name from a text file
        # Lê nome do equipamento

        equipamento_nome = ""
        for arquivo in os.listdir(usuario_path):
            if arquivo.endswith(".txt"):
                with open(os.path.join(usuario_path, arquivo), 'r', encoding='utf-8') as f:
                    equipamento_nome = f.read().strip()
                break
        if not equipamento_nome:
            equipamento_nome = "NÃO INFORMADO"

        # Process the user's photosJPEG
        # Processa fotos JPEG

        fotos_indexadas = []
        contador_foto = 1
        for arquivo in os.listdir(usuario_path):
            if arquivo.lower().endswith((".jpeg", ".jpg")):
                extensao = os.path.splitext(arquivo)[1]
                usuario_id = ''.join(e for e in usuario if e.isalnum())
                nome_foto_novo = f"{prefixo_setor}_{usuario_id}_{str(contador_foto).zfill(3)}{extensao}"
                origem = os.path.join(usuario_path, arquivo)
                destino = os.path.join(saida_base, nome_foto_novo)
                shutil.copy2(origem, destino)
                fotos_indexadas.append(nome_foto_novo)
                contador_foto += 1

        # Adds entry to the inventory
        # Adiciona entrada no inventário
        inventario.append({
            "setor": setor_nome,
            "usuario": usuario,
            "equipamento": equipamento_nome,
            "fotos": fotos_indexadas
            
        })



# After filling the inventory list, before saving the JSON:
# Após preencher a lista inventario, antes de salvar o JSON:

# Read the order of sectors from the .env file
# Extrai a ordem dos setores do .env
setores_ordem = [k.strip() for k in setores_env.split(",") if ":" in k for k, _ in [item.split(":", 1)]]

# Define a function to get the index of the sector in the order, or a high value if not present
# Função para obter o índice do setor na ordem, ou um valor alto se não estiver
def setor_index(item):
    try:
        return setores_ordem.index(item["setor"])
    except ValueError:
        return len(setores_ordem)

# Define a function to sort the inventory by sector order
# Ordena o inventario pela ordem dos setores
inventario.sort(key=setor_index)

#Saves the inventory to a JSON File
# Salva o inventário em JSON
with open(os.path.join(saida_base, "inventario.json"), "w", encoding="utf-8") as f:
    json.dump(inventario, f, ensure_ascii=False, indent=4)

print(f"Inventário criado com sucesso em: {saida_base}")

# Salva o inventário em XML
# Saves the inventory to an XML file
root = ET.Element("inventario")

for item in inventario:
    entry = ET.SubElement(root, "item")
    ET.SubElement(entry, "setor").text = item["setor"]
    ET.SubElement(entry, "usuario").text = item["usuario"]
    ET.SubElement(entry, "equipamento").text = item["equipamento"]
    fotos_elem = ET.SubElement(entry, "fotos")
    for foto in item["fotos"]:
        ET.SubElement(fotos_elem, "foto").text = foto

tree = ET.ElementTree(root)
xml_path = os.path.join(saida_base, "inventario.xml")
tree.write(xml_path, encoding="utf-8", xml_declaration=True)

print("Inventário XML criado com sucesso em: {xml_path}".format)

