import os
import psycopg2
from dotenv import load_dotenv
from flask import *
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)


db_url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(db_url)
CREATE_QUOTES_TABLE = """CREATE TABLE IF NOT EXISTS quotes 
                        (id SERIAL PRIMARY KEY, 
                        title VARCHAR(50),
                        category VARCHAR(50), 
                        quote TEXT,
                        author TEXT
                        );"""
with connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_QUOTES_TABLE)
        
@app.route("/api/upload",methods=["POST"])
def upload():
    try:
        data = request.get_json()
        category = data.get("category")
        quote = data.get("quote")
        author = data.get("author")
        title =  data.get("title")
        
        if not category or not quote or not author or not title:
            return jsonify({"error":"All fields (category,quote,author) required"}),400
        INSERT_DATAS = """INSERT INTO quotes
                (category,quote,author,title ) 
                VALUES (%s,%s,%s,%s)
                RETURNING id;
                """
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_DATAS, (category, quote, author,title ))
                new_id = cursor.fetchone()[0]
                return jsonify({"message": "Quote added successfully", "id": new_id}), 201
    except Exception as e:
        error_message = str(e)  
        error_code = e.args
        return jsonify({"error": error_message, "code": error_code}) 
    
@app.route("/api/update/<int:id>",methods=["POST"])
def update(id):
    try:
        data = request.get_json()
        new_category = data.get("category")
        new_quote = data.get("quote")
        new_author = data.get("author")
        new_title = data.get("title")
        UPDATE_QUOTE = """
            UPDATE quotes
            SET category=%s, quote = %s, author = %s, title =%s
            WHERE id = %s;
            """
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_QUOTE,(new_category,new_quote,new_author,new_title,id))
                connection.commit()
                if cursor.rowcount == 0:
                    return jsonify({"error": "No quote found with the provided id"}), 404
                
                return jsonify({"message": "Quote updated successfully"}), 200
    except Exception as e:
        error_message = str(e)  
        error_code = e.args
        return jsonify({"error": error_message, "code": error_code}) 
    
@app.route("/api/delete/<int:id>",methods=["DELETE"])
def delete(id):
    try:
        DELETE_QUOTE = "DELETE FROM quotes WHERE id=%s"
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_QUOTE,(id,))
                connection.commit()
            return jsonify({"message": "Quote deleted successfully"}), 200
    except Exception as e:
        error_message = str(e)
        error_code = e.args
        return jsonify({"message":error_message,"code":error_code})
    
   
@app.route("/api/quotes",methods=["GET"])
def quotes():
    try:
        GET_QUOTE = "SELECT id,category,quote,author,title FROM quotes "
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_QUOTE)
                quotes = cursor.fetchall()
        if quotes:
            return jsonify([{"id":quote[0],
                            "category":quote[1],
                            "quote":quote[2],
                            "author":quote[3],
                            "title":quote[4]}
                            for quote in quotes])
        else:
            return jsonify({"message":"No datas available"})
    except Exception as e: 
        error_message = str(e)  
        error_code = e.args
        return jsonify({"error": error_message, "code": error_code}) 
    
@app.route("/api/get_quote/<category>",methods=["GET"])
def get_quote(category):
    try:
        GET_QUOTE = "SELECT id,category,quote,author,title FROM quotes WHERE category=%s"
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_QUOTE,(category,))
                quotes = cursor.fetchall()
        if quotes:
            return jsonify([{"id":quote[0],
                            "category":quote[1],
                            "quote":quote[2],
                            "author":quote[3],
                            "title":quote[4]}
                            for quote in quotes])
        else:
            return jsonify({"message":"No datas available"})
    except Exception as e: 
        error_message = str(e)  
        error_code = e.args
        return jsonify({"error": error_message, "code": error_code}) 


