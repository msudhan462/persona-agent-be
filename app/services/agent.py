from groq import Groq
import traceback
from app.db import mongo, pc
from app.services.ai import get_embeddings
from fastapi.responses import StreamingResponse, JSONResponse
from uuid import uuid4
from app.services.utils import get_datetime
from fastapi.encoders import jsonable_encoder

mongo_db = mongo.MongoDB()


class Agent:

    def connect(self, body, current_user):

        try:
            persona_id = body.persona_id

            dt = get_datetime()
            records = {
                "persona_id":persona_id,
                "connect":True,
                "disconnect":False,
                "email":current_user['email'],
                "datetime":dt
            }
            
            r = mongo_db.insert(db="persona",collection="connections", records=records)
        
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully stored',"data":records}),
                status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to connect to the agent'}),
                status_code=400
            )


    def disconnect(self, body, current_user):
        
        try:
            persona_id = body.persona_id
            dt = get_datetime()

            records = {
                "persona_id":persona_id,
                "connect":False,
                "disconnect":True,
                "email":current_user['email'],
                "datetime":dt
            }
            
            r = mongo_db.insert(db="persona",collection="connections", records=records)
            
            return JSONResponse(
                    content=jsonable_encoder({'message': 'Successfully stored',"data":records}),
                    status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to disconnect to the agent'}),
                status_code=400
            )



    def connect_status(self, body, current_user):
        
        try:
            persona_id = body.persona_id

            filters = {
                "persona_id":persona_id,
                "email":current_user['email']
            }
            
            records = list(mongo_db.find(db="persona",collection="connections", filters = filters, many=False, projection={"_id":0}))
            if records:
                record = records[0]
                connect = record.get('connect', None) or None
                if connect:
                    JSONResponse(
                    content=jsonable_encoder({"data":{'message': 'connected',"data":{"status":True}}}),
                    status_code=200
                )
                    
                disconnect = record.get('disconnect', None) or None
                if disconnect:
                    JSONResponse(
                    content=jsonable_encoder({"data":{'message': 'disconnected',"data":{"status":False}}}),
                    status_code=200
                )
            return JSONResponse(
                    content=jsonable_encoder({"data":{'message': 'disconnected',"data":{"status":False}}}),
                    status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the connection status of the agent'}),
                status_code=400
            )

    def report(self, body, current_user):
        
        try:
            persona_id = body.persona_id  
            conversation_id = body.conversation_id   
            report_message = body.report_message

            dt = get_datetime()

            record = {
                "type": "agent",
                "persona_id" : persona_id,
                "conversation_id" : conversation_id,
                "report_message" : report_message,
                "email":current_user['email'],
                "datetime":dt
            }
            r = mongo_db.insert(db="persona",collection="reports", records=record)
            print(r)
            return JSONResponse(
                        content=jsonable_encoder({'message': 'Successfully stored',"data":record}),
                        status_code=200
                    )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to report the agent'}),
                status_code=400
            )
    def block(self, body, current_user):
        
        try:
            persona_id = body.persona_id

            dt = get_datetime()

            records = {
                "persona_id":persona_id,
                "block":True,
                "unblock":False,
                "email":current_user['email'],
                "datetime":dt
            }
            
            r = mongo_db.insert(db="persona",collection="block_list", records=records)
            
            return JSONResponse(
                        content=jsonable_encoder({'message': 'Successfully stored',"data":records}),
                        status_code=200
                    )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to block the agent'}),
                status_code=400
            )

    def unblock(self, body, current_user):
        
        try:
            persona_id = body.persona_id
            dt = get_datetime()

            records = {
                "persona_id":persona_id,
                "block":False,
                "unblock":True,
                "email":current_user['email'],
                "datetime":dt
            }
            
            r = mongo_db.insert(db="persona",collection="block_list", records=records)
            
            return JSONResponse(
                            content=jsonable_encoder({'message': 'Successfully stored',"data":records}),
                            status_code=200
                        )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to unblock the agent'}),
                status_code=400
            )

    def block_status(self, body, current_user):
        
        try:
            persona_id = body.persona_id
            
            filters = {
                "persona_id":persona_id,
                "email":current_user['email']
            }
            
            records = list(mongo_db.find(db="persona",collection="block_list", filters = filters, many=False, projection={"_id":0}))
            if records:
                record = records[0]
                connect = record.get('block', None) or None
                if connect:
                    return JSONResponse(
                                content=jsonable_encoder({"data":{'message': 'unblocked',"data":{"status":True}}}),
                                status_code=200
                            )
                
                disconnect = record.get('unblock', None) or None
                if disconnect:
                    return JSONResponse(
                                content=jsonable_encoder({"data":{'message': 'blocked',"data":{"status":False}}}),
                                status_code=200
                            )
                    
            return JSONResponse(
                                content=jsonable_encoder({"data":{'message': 'blocked',"data":{"status":False}}}),
                                status_code=200
                            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the the status of block'}),
                status_code=400
            )
        
    def current_status(self, body, current_user):
        
        # update the system message by calling function

        try:
            feeling = body.feeling
            status = body.status
            dt = get_datetime()

            records = {
                "feeling":feeling,
                "status":status,
                "email":current_user['email'],
                "datetime":dt
            }
            
            r = mongo_db.insert(db="persona",collection="status", records=records)
            
            return JSONResponse(
                            content=jsonable_encoder({'message': 'Successfully stored',"data":records}),
                            status_code=200
                        )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to unblock the agent'}),
                status_code=400
            )
        

agent = Agent()