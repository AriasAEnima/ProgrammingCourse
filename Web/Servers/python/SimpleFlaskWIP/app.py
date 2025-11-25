from flask import Flask, request

app = Flask(__name__)

app_name = {"spanish": "muebles",
            "english": "forniture"}

@app.route('/')
def home():
    language = request.args.get("language","english")
    return "<h1> Home app "+app_name[language] + "</h1>" 


## REST ENDPOINTS

furnitures ={ "1": {"name": "Mesa Redonda", "width": 150 , "depth": 150 , "heigh": 150, "price": 110000},
        "2": {"name": "Mesa Rectangular", "width": 150 , "depth": 60 , "heigh": 120, "price": 120000},
        "3": {"name": "Silla triangular", "width": 85 , "depth": 65 , "heigh": 130, "price": 60000} }

@app.route('/api/furniture/<string:id>/')
def get_furniture(id):    
    if id in furnitures:
        return furnitures[id], 200
    else:
        return {"messsage": "forniture with "+id+" not found"}, 404
    
@app.route('/api/furnitures/')
def get_furnitures(): 
    width = request.args.get("width",0)
    heigh =  request.args.get("heigh",0)   
    filtered = list(filter(lambda key : furnitures[key]["width"] >= int(width) 
                           and furnitures[key]["heigh"] >= int(heigh) , furnitures))
    return list(map(lambda k: furnitures[k], filtered))

@app.route('/api/furniture/', methods = ["POST"])
def post_furniture(): 
    body = request.json
    furniture_id = str(body["id"])
    if furniture_id in furnitures:
        return {"message": "Fornture with id "+furniture_id + " already exist" }, 409    
    else:
        del body["id"] 
        furnitures[furniture_id] = body
        return furnitures[furniture_id], 201
    
@app.route('/api/furniture/<string:id>', methods = ["DELETE"])
def delete_furniture(id): 
    if id not in furnitures:
        return {},208
    else:
        del furnitures[id]
        return {},200
   
   
  
if __name__ == '__main__':
    app.run(debug=True,port=8001, host='0.0.0.0')