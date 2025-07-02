from fastapi import FastAPI, UploadFile, File, HTTPException, status
from dotenv import load_dotenv
import boto3
import uuid
import os
import mimetypes
from loguru import logger

load_dotenv()

app = FastAPI()

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BUCKET = os.getenv("AWS_BUCKET_NAME")

@app.get("/")
def get_root():
    return {"message": "Hello World!!!"}

s3_client = boto3.client(
    "s3",
    region_name=REGION,
)

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    detected_mime_type = mimetypes.guess_type(file.filename)[0]
    content_type = file.content_type or detected_mime_type or 'application/octet-stream'
    
    file_key = f"{uuid.uuid4()}_{file.filename}"
    s3_client.upload_fileobj(file.file, BUCKET, file_key, 
                           ExtraArgs={'ContentType': content_type})
    
    return {"key": file_key}

@app.get("/download-url/{filename}")
def get_presigned_url(filename: str):
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": filename, "ResponseContentDisposition": "inline"},
            ExpiresIn=3600 
        )
        return {"url": presigned_url}
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/delete/{filename}")
def delete_file(filename: str):
    try:
        s3_client.delete_object(Bucket=BUCKET, Key=filename)
        return {"message": f"File {filename} deleted successfully."}
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))