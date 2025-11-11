import os
from google.cloud import secretmanager

def get_secret(secret_id, project_id, version):
    if not project_id:
        project_id = os.getenv("PROJECT_ID")
    
    if not project_id:
        raise ValueError("PROJECT_ID not set")
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error getting secret {secret_id}: {e}")
        raise