#http://localhost:8080/?src=en&dst=zh-Hant&target=Hello&file_name=hello_translation
#http://localhost:8080/list_blobs
#4.157.169.85:8080/?src=en&dst=zh-Hant&target=Hello&file_name=hello_translation
#4.157.169.85:8080/list_blobs
#%20

from flask import Flask, request, jsonify
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# 以下資訊可以從 Azure 翻譯服務取得(正式上線時不要直接把金鑰跟服務端點寫在程式碼裡)
REGION = '區域'  # 區域
KEY = '金鑰'  # 金鑰
ENDPOINT = '服務端點'  # 服務端點

# 設置 Azure Blob 存儲的連接字符串和容器名稱
AZURE_STORAGE_CONNECTION_STRING = "字符串"
CONTAINER_NAME = "容器名稱"

# 創建 BlobServiceClient 對象
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# 確保容器存在
container_client = blob_service_client.get_container_client(CONTAINER_NAME)
if not container_client.exists():
    container_client.create_container()

def upload_to_azure(blob_name, data):
    # 創建 BlobClient 對象
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    
    # 上傳數據
    blob_client.upload_blob(data, overwrite=True)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def translator():
    SRC = request.args.get('src')
    DST = request.args.get('dst')
    TARGET = request.args.get('target')
    FILE_NAME = request.args.get('file_name', 'translated_text')  # 默認檔案名為 translated_text

    client = TextTranslationClient(
        endpoint=ENDPOINT,
        credential=TranslatorCredential(KEY, REGION)
    )

    src = SRC  # 來源語言
    dst = [DST]  # 目標語言(可多個)
    targets = [InputTextItem(text=TARGET)]  # 目標文字(可多個)
    responses = client.translate(content=targets, to=dst, from_parameter=src)
    translation = responses[0].translations[0]
    translated_text = "[{}] {}".format(translation.to, translation.text)
    
    # 上傳翻譯結果到 Azure Blob 存儲
    blob_name = f"{FILE_NAME}.txt"
    upload_to_azure(blob_name, translated_text)
    
    return jsonify({"translated_text": translated_text, "blob_name": blob_name})

@app.route("/list_blobs", methods=['GET'])
def list_blobs():
    blob_list = container_client.list_blobs()
    blobs = [blob.name for blob in blob_list]
    return jsonify({"blobs": blobs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)