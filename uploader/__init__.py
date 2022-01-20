import os, logging, requests, json

import azure.functions as func


AZURE_STORAGE_CONNECTION_STRING     = os.environ['AZURE_STORAGE_CONNECTION_STRING']
BLOB_CONTAINER_NAME                 = os.environ['BLOB_CONTAINER_NAME']
API_USER                            = os.environ['API_USER']
API_SECRET                          = os.environ['API_SECRET']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    file_name, file = req.files['image'].filename, req.files['image']

    if file_name and file:

        try:

            return func.HttpResponse(analyse_image(upload_file(file_name, file)), status_code=200)

        except Exception as e:

            return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

    else:

        return func.HttpResponse(
            json.dumps({"error": "form data should include both `file_name` and `image` attributes"}),
             status_code=400
        )


def analyse_image(url: str) -> str:

    params = {
                'url': f'{url}',
                'models': 'nudity,wad,offensive,text-content,gore',
                'api_user': API_USER,
                'api_secret': API_SECRET
            }
    r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)

    if r.status_code != 200:
        raise Exception(r.text)
    return r.text
    


def upload_file(file_name, file):
    from azure.storage.blob import BlobServiceClient, __version__
    
    logging.info("Azure Blob Storage v" + __version__ + " - uplaoding executed file")

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    # Craete the blob client
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=file_name)

    # finally upload to blob storage
    blob_client.upload_blob(file)
    logging.info(f"Succesfully uploaded the file {file_name} to Azure blob storage. Container: {BLOB_CONTAINER_NAME}")

    # return public accessible url
    return blob_client.url
