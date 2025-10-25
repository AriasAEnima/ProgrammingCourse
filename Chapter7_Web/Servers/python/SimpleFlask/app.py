from flask import Flask, request

app = Flask(__name__)

@app.route('/shapes/status/500',methods = ["GET"])
def get_shapes_200():
    return "Hola ya no soy shapes" , 500

@app.route('/shapes/status/200',methods = ["GET"])
def get_shapes_500():
    return "Hola ya no soy shapes" , 200

@app.route('/shapes/<string:shape_id>/',methods = ["GET"])
def get_shapes(shape_id):
    if int(shape_id) % 2 == 0:
        return "Es par"
    else:
        return "Es impar"
    
desks = [
    {"id": 1,
    "name": "Mesa Venture",
     "width": 125,
     "height": 225},
     {"id": 2,
    "name": "Mesa Koto",
     "width": 200,
     "height": 223},
     {"id": 3,
       "name": "Mesa Amatista",
     "width": 200,
     "height": 300}]
    
@app.route('/desk/<string:desk_id>/',methods = ["GET"])
def get_desk(desk_id):
    ans = list(filter(lambda x: x["id"]==int(desk_id), desks))
    if len(ans)>0:
        return ans[0] , 200 
    else:
        print("ERROR")
        return {"mensaje": "Mesa no existe"}, 404
    
@app.route('/desk',methods = ["GET"])
def get_all_desks():
   width_query_param= request.args.get("width")
   height_query_param= request.args.get("height")
   print(f"width {width_query_param}, height {height_query_param}")
   ans = desks
   if width_query_param is not None:
    ans = list(filter(lambda x: x["width"]>=int(width_query_param), ans))
   if height_query_param is not None:
    ans = list(filter(lambda x: x["height"]>=int(height_query_param), ans))

   return ans , 200

@app.route('/desk',methods = ["POST"])
def post_desk():
   print(f"Body: {request.json}")
   body = request.json
   new_desk = {"id": body["id"],
    "name": body["name"],
     "width": body["width"],
     "height": body["height"]}
   desks.append(new_desk)
   return new_desk , 200
    

if __name__ == '__main__':
    app.run(
        host= '0.0.0.0',
        port= 8003,
        debug = True
    )