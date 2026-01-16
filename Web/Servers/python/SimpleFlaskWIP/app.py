from flask import Flask, request


app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1> Hola Mundo </h1>"

@app.route('/hello/<string:name>')
def grettings(name):
    return "<h1> Hola Mundo "+ name +  "</h1>"


#https://www.alkosto.com/fuente

#https://www.alkosto.com/?fuente=google&medio=cpc&campaign=AK_COL_SEM_PEF_CPC_PB_AON_TLP_TLP_Brand-General-AON_PAC&keyword=alkosto&gad_source=1&gad_campaignid=2018735487&gbraid=0AAAAADlnVbhjpa2yNJXbRpygnnsX8VizY&gclid=CjwKCAiAvaLLBhBFEiwAYCNTf7C40kfNPJpky3V0zSRGu-gSyhJjIbLtlSTqw3Q8kPaLJiK2O4N3lBoCGjoQAvD_BwE
#https://listado.mercadolibre.com.co/laptop#D[A:laptop]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v=lapto&as.comp_id=SUG
#https://www.amazon.com/s?k=laptop&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1FUXXWEL7GE7T&sprefix=laptop%2Caps%2C167&ref=nb_sb_noss_1

saludo = {"ES": "Hola Mundo",
          "EN": "Hello World"}

@app.route('/dynamic-hello/<string:name>/')
def data(name):
    language = request.args.get("language", "EN")
    uppercase = request.args.get("uppercase", False)
    phase = saludo[language] + " " + name
    if uppercase == "True" or uppercase == "true":
        phase = phase.upper()
    return "<h1>" + phase + "</h1>"

pets = {"Tito": {"especie": "Hamster", "Edad": 2},
        "Lorenzo": {"especie": "Gato", "Edad": 8},
        "Caramelo": {"especie": "Perro", "Edad": 7}}

# Filtrar por especie
@app.route('/pet/<string:name>')
def get_pets(name):
    if name in pets:
        return pets[name], 200
    else:
        return {"message": "Pet not found"}, 404

@app.route('/large-process/')
def get_pets():
    # ....
    return {"message": "request accepted"}, 201

if __name__ == '__main__':
    app.run(debug=True,
            port=8002, 
            host='0.0.0.0')