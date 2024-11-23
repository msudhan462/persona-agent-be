
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import traceback
from app.db import mongo
from app.db.pc import vector_db
from app.services.ai import get_embeddings
from fastapi.responses import JSONResponse
from uuid import uuid4
from app.services.utils import get_datetime
from fastapi.encoders import jsonable_encoder
from app.services.qa import personas_qa
import os

from dotenv import load_dotenv
load_dotenv('app/.env')

mongo_db = mongo.MongoDB()



# AWS S3 Configuration
S3_BUCKET = 'persona-agent'
S3_REGION = 'us-east-1'
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')


# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

from fastapi import UploadFile

class Data:

    def upload_file(self, file:UploadFile, current_user):

        
        try:
        
            # If the user does not select a file
            if file.filename == '':
                return JSONResponse(
                        content=jsonable_encoder({'message': 'No selected file'}),
                        status_code=400
                    )
            
            # If the file is allowed, upload it to S3
            if file and allowed_file(file.filename):
                filename = file.filename
                
                try:
                    # Upload file to S3
                    s3_client.upload_fileobj(
                        file.file,                  # The file to upload
                        S3_BUCKET,             # The S3 bucket name
                        filename,              # The S3 object name (same as filename)
                    )
                    
                    # Generate S3 file URL
                    file_url = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}'
                    
                    file_id = str(uuid4())
                    row_id = str(uuid4())
                    data = {
                            "s3_bucket":S3_BUCKET,
                            "s3_region":S3_REGION,
                            "filename":filename,
                            'file_url': file_url,
                            "file_id":file_id
                        }
                    dt = get_datetime()
                    record = {
                        "id":row_id,
                        "type": "file",
                        "data":data,
                        "is_deleted": False,
                        "email":current_user['email'],
                        "datetime":dt
                    }
                    r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)
                    print(r)
                    return JSONResponse(
                        content=jsonable_encoder({'message': f'Successfully stored {filename}'}),
                        status_code=201
                    )

                except (NoCredentialsError, PartialCredentialsError) as e:   
                    print(traceback.format_exc())

                    return JSONResponse(
                        content=jsonable_encoder({'message':'Credentials not available or incomplete'}),
                        status_code=403
                    )
                
                except Exception as e:
                    print(traceback.format_exc())

                    return JSONResponse(
                        content=jsonable_encoder({'message':f'An error occurred: {str(e)}'}),
                        status_code=500
                    )
            else:
                return JSONResponse(
                    content=jsonable_encoder({'message':'File extension not allowed'}),
                    status_code=415
                )

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to upload the file'}),
                status_code=400
            )

    def qa(self, body, current_user):

        try:
            qtype = body.qtype
            question = body.question
            answer = body.answer
            question_number = body.question_number

            if qtype in {"system_qa","bg_qa"}:
                data = {
                        "question_number":question_number,
                        "qtype":qtype,
                        "question":question,
                        "answer":answer
                    }
                
                dt = get_datetime()
                row_id = str(uuid4())
                record = {
                    "id":row_id,
                    "type": "qa",
                    "data":data,
                    "email":current_user['email'],
                    "datetime":dt
                }
                r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)                
                print(r)

                # text = f"{question}\n{answer}"

                # emds = get_embeddings(text)[0]
                # id = uuid4()
                # data = {
                #     "id":str(id),
                #     "values":emds,
                #     "metadata":{
                #         "text":text, 
                #         "question_number":question_number,
                #         "qtype":qtype
                #         }
                # }
                # vector_db.insert(data)

                return JSONResponse(
                        content=jsonable_encoder({'message': 'Successfully stored',"data":data}),
                        status_code=200
                    )


            else:
                return JSONResponse(
                        content=jsonable_encoder({'message': f'qtype = {qtype} is not supported!'}),
                        status_code=400
                    )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the qa'}),
                status_code=400
            )



    def text(self, body, current_user):
        
        try:
            text = body.text

            dt = get_datetime()
            row_id = str(uuid4())
            record = {
                "id":row_id,
                "type": "text",
                "data":{
                    "text":text
                },
                "email":current_user['email'],
                "datetime":dt,
                'is_deleted': False
            }
            r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)
            print(r)

            if "_id" in record:
                del record['_id']

            return JSONResponse(
                content=jsonable_encoder({'message': "Successfully stored","data":record }),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the text'}),
                status_code=400
            )

    def list_files(self, current_user):

        try:
            email = current_user['email']
            filters = {
                "email": email,
                "is_deleted": False,
                "type": "file"
            }
            records = mongo_db.find(db="persona",collection="data_ingestion", filters= filters, many=True, projection={"_id":0})
            records = list(records)   
            print(records) 
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully fetcted',"data":records}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get files'}),
                status_code=400 
            )
    
    def get_qa(self, body, current_user):
        try:
            qtype = body.qtype
            question_number = body.question_number
            question = body.question

            filters = {
                "email": current_user['email'],
                "type": "qa",
                "data":{
                    "qtype":qtype,
                    "question":question,
                    "question_number":question_number
                }
            }

            records = mongo_db.find(db="persona",collection="data_ingestion", filters= filters, many=True, projection={"_id":0})
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully fetcted',"data":records}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to q and a'}),
                status_code=400
            )
    
    def get_qa_all(self, current_user):

        try:
            filters = {
                "email": current_user['email'],
                "type": "qa"
            }

            records = mongo_db.find(db="persona",collection="data_ingestion", filters= filters, many=True, projection={"_id":0})

            data = dict()
            for r in records: # assume user saved only 15 QA's
                qn = r['data']['question_number']
                data.update({int(qn):{
                    "qn":qn,
                    "answer":r['data']['answer'],
                    'question':r['data']['question'],
                    'qtype':r['data']['qtype']
                }})
            data = {**personas_qa,**data}
            final_data = [ value for key, value in dict(sorted(data.items())).items()]
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully fetcted',"data":final_data}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to q and a'}),
                status_code=400
            )
    def get_text(self, current_user):
        try:

            filters = {
                "type": "text",
                "email": current_user['email'],
                "is_deleted": False
            }
            print(filters)

            records = mongo_db.find(db="persona",collection="data_ingestion", filters= filters, many=True, projection={"_id":0})
            records = list(records)
            print("GET TEXT", records)
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully fetcted',"data":records}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the text'}),
                status_code=400
            )
    
    def delete_text(self, body, current_user):
        try:

            filters = {
                "id":body.id,
                "type": "text",
                "email": current_user['email']
            }
            print(filters)
            records = { "$set": { "is_deleted": True } }

            is_deleted = mongo_db.update(db="persona",collection="data_ingestion", filters= filters, records=records)
            print(is_deleted)
            
            filters.update({
              "is_deleted": True  
            })

            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully deleted',"data":filters}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to delete file'}),
                status_code=400
            )


    def delete_file(self, body, current_user):
        try:

            filters = {
                "type": "file",
                "email": current_user['email'],
                "data.file_id":body.file_id
            }
            print(filters)
            records = { "$set": { "is_deleted": True } }

            is_deleted = mongo_db.update(db="persona",collection="data_ingestion", filters= filters, records=records)
            print(is_deleted)
            
            filters.update({
              "is_deleted": True  
            })

            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully deleted',"data":filters}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to delete file'}),
                status_code=400
            )


data = Data()

# data_ingestion
#     {
#         "type":"text/file/qa/wiki"
#         "data":{
#             ""
#         }
#     }