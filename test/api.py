import requests
import os
import json
import base64 

imagen = "jhon1.jpeg"
# 4 Secuenta de ejecución 
with open(imagen, mode="rb") as f:
    file_base64 = base64.b64encode(f.read()).decode("utf-8")   

# "doc_type": puede ser acta u obra 
# "extract_meta": True es tru extrae campo sino solo paasa al ocr 
# "files" para procesar varios archivos
# el ID lo envía Jose Calderon 
body = {"doc_type": "acta",
        "extract_meta": True,
        "files": [
            {
              "id": "a1s2s4d5",
              "filename": os.path.basename(imagen),
              "filebase64": file_base64
            }]
        }

url = "http://34.70.237.129:80"

response = requests.post(f"{url}/tasks", json=body)

print(response.json())