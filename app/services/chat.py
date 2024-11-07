from groq import Groq
import traceback
from app.db import mongo, pc
from app.services.ai import get_embeddings
from fastapi.responses import StreamingResponse, JSONResponse
from uuid import uuid4
from app.services.utils import get_datetime
from fastapi.encoders import jsonable_encoder



mongo_db = mongo.MongoDB()

client = Groq(api_key="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")
    
class Chat():

    def __init__(self) -> None:
        pass
        
    def get_chat_history(self, persona_id, conversation_id, projection={"_id":0}):
        filters = {
            "persona_id": persona_id, 
            "conversation_id": conversation_id
        } 
        res = mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection)
        res = list(res)
        return res

    def stream(self, body, current_user):

        
        """
        Not secured
        """
        print("In interaction...........")
        print()

        prompt = body.prompt
        persona_id = body.persona_id
        conversation_id = body.conversation_id

        projection = {
            "_id":0,
            "content":1,
            "role":1
        }
        history = self.get_chat_history(persona_id, conversation_id, projection)

        dt = get_datetime()
        message_id = str(uuid4())
        record = {
            "message_id":message_id,
            "email":current_user['email'],
            "role": "user",
            "content": prompt,
            "persona_id": persona_id, 
            "conversation_id": conversation_id,
            "datetime":dt
        }   
        r = mongo_db.insert(db="persona",collection="conversations", records=record)
        embd = get_embeddings(prompt)[0].tolist()
        filters = {"persona": {"$eq": persona_id}}
        context = pc.vector_db.search(embd, filters=filters)

        text = ""
        for c in context["matches"]:
            text += c['metadata']['text'] + "\n\n"
        

        system = {"role": "system", "content": "You are an AI Agent named Jarvis, responding on behalf of Sachin Tendulkar. You are responsible for tailoring responses to the user's specific questions. Begin by answering user queries based on your own persona. After addressing the question, rarely ask exactly one relevant follow-up question that aligns with the user's queries to keep the conversation engaging, but the follow-up question must never align with the user's persona. Ensure that the follow-up question is relevant to the user's question. Always maintain a polite, funny and respectful tone, and be precise when responding."}
        query = {"role": "user", "content": f"Please Answer the query based on My Persona and history\n# My Persona::{text}\n\nQuery::{prompt}\n\nAnswer::"}
        messages = [system]+history+[query]
        
        # print(messages)
        date_time = get_datetime()
        def stream_response():
            
            completion = client.chat.completions.create(
                model="gemma2-9b-it",
                # model="gemma-7b-it",
                messages=messages,
                temperature=1,
                max_tokens=8192,
                top_p=1,
                stream=True
            )
            total_response = ""
            for chunk in completion:
                ch = str(chunk.choices[0].delta.content)
                if ch =="None":
                    ch = ""
                total_response += ch
                yield ch
            print(total_response)
            record = {
                "message_id":message_id,
                "email":current_user['email'],
                "role": "assistant",
                "content": total_response,
                "persona_id": persona_id, 
                "conversation_id": conversation_id,
                "datetime":date_time
            }
            mongo_db.insert(db="persona",collection="conversations", records=record)


        return StreamingResponse(stream_response(), media_type='text/event-stream')
    
    def report(self, body, current_user):
        try:

            persona_id = body.persona_id    
            conversation_id = body.conversation_id
            message_id = body.message_id
            report_message = body.report_message

            dt = get_datetime()
            record = {
                "type": "chat",
                "persona_id" : persona_id,
                "conversation_id" : conversation_id,
                "message_id" : message_id,
                "report_message" : report_message,
                "email":current_user['email'],
                "datetime":dt
            }
            print(record)
            r = mongo_db.insert(db="persona",collection="reports", records=record)
            
            if "_id" in record:
                del record['_id']

            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully stored',"data":record}),
                status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the report'}),
                status_code=400
                )

    def save_reaction(self, body, current_user):
        
        try:
            persona_id = body.persona_id 
            conversation_id = body.conversation_id 
            message_id = body.message_id
            reaction = body.reaction

            dt = get_datetime()
            record = {
                "type": "chat",
                "persona_id" : persona_id,
                "conversation_id" : conversation_id,
                "message_id" : message_id,
                "reaction" : reaction,
                "email":current_user['email'],
                "datetime":dt
            }
            r = mongo_db.insert(db="persona",collection="reactions", records=record)
            print(r)
            return JSONResponse(
                    content=jsonable_encoder({'message': 'Successfully stored',"data":record}),
                    status_code=200
                    )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the reaction'}),
                status_code=400
            )

    def get_reaction(self, body, current_user):
        
        try:
            persona_id = body.persona_id 
            conversation_id = body.conversation_id

            filters = {
                "persona_id" : persona_id,
                "conversation_id" : conversation_id,
                "email":current_user['email']
            }
            reactions_li = list(mongo_db.find(db="persona", collection="reactions", filters=filters, many=True, projection={"_id:0"}))

            def stream_reactions():

                for chunk in reactions_li:
                    print(chunk)
                    yield chunk

            return StreamingResponse(stream_reactions(), media_type='text/event-stream')

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the reactions'}),
                status_code=400
            )
    
    def save_dislikes(self, body, current_user):

        try:
            persona_id = body.persona_id    
            conversation_id = body.conversation_id    
            message_id = body.message_id

            dt = get_datetime()
            record = {
                "persona_id" : persona_id, 
                "conversation_id" : conversation_id, 
                "message_id" : message_id, 
                "like" : False,
                "dislike" : True,
                "email":current_user['email'],
                "datetime":dt
            }
            r = mongo_db.insert(db="persona",collection="likes_and_dislikes", records=record)
            print(r)
            return JSONResponse(
                    content=jsonable_encoder({'message': 'Successfully stored',"data":record}),
                    status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the dislike'}),
                status_code=400
            )

    def save_likes(self, body, current_user):
        try:
            persona_id = body.persona_id    
            conversation_id = body.conversation_id    
            message_id = body.message_id

            dt = get_datetime()
            record = {
                "persona_id" : persona_id, 
                "conversation_id" : conversation_id, 
                "message_id" : message_id, 
                "like" : True,
                "dislike" : False,
                "email":current_user['email'],
                "datetime":dt
            }
            r = mongo_db.insert(db="persona",collection="likes_and_dislikes", records=record)
            print(r)
            return JSONResponse(
                    content=jsonable_encoder({'message': 'Successfully stored',"data":record}),
                    status_code=200
                )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to store the like'}),
                status_code=400
            )

    def get_likes_and_dislikes(self, body, current_user):

        try:
            persona_id = body.persona_id    
            conversation_id = body.conversation_id

            filters = {
                "persona_id" : persona_id, 
                "conversation_id" : conversation_id, 
                "email":current_user['email']
            }
            likes_dislikes_li = mongo_db.find(db="persona",collection="likes_and_dislikes", filters=filters, many= True, projection={"_id":0})
            
            def stream_likes():
                
                for chunk in likes_dislikes_li:
                    yield chunk

            return StreamingResponse(stream_likes(), media_type='text/event-stream')
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the like and dislikes'}),
                status_code=400
            )

    def list_interactions(self, current_user):

        try:
            # pagination should be implemeted

            email = current_user['email']   

            filters = {
                "email":email
            }
            projection = {
                "_id":0,
                "persona_id":1
            }

            records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection))
            
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully listed the interacted agent',"data":records}),
                status_code=200
            )
    
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get interacted agents'}),
                status_code=400
            )
    
    def list_agents(self, body, current_user):

        try:
            # pagination

            persona_id = body.persona_id

            filters = {
                "persona_id":persona_id
            }
            projection = {
                "_id":0,
                "persona_id":1
            }
            
            records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection))
            
            return JSONResponse(
                content=jsonable_encoder({'message': 'Successfully your agent',"data":records}),
                status_code=200
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return JSONResponse(
                content=jsonable_encoder({'message': 'unable to get the your interacted agents'}),
                status_code=400
            )


chat = Chat()