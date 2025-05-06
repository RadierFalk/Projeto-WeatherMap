from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")


def buscar_clima_por_cidade(cidade):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br"
    r = requests.get(url)
    if r.status_code == 200:
        dados = r.json()
        return extrair_dados_clima(dados)
    return None

def buscar_clima_por_coordenadas(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
    r = requests.get(url)
    if r.status_code == 200:
        dados = r.json()
        return extrair_dados_clima(dados)
    return None

def extrair_dados_clima(dados):
    temp = dados['main']['temp']
    feels_like = dados['main']['feels_like']
    umidade = dados['main']['humidity']
    visibilidade = dados.get('visibility', 0) / 1000
    descricao = dados['weather'][0]['description'].capitalize()
    lat = dados['coord']['lat']
    lon = dados['coord']['lon']
    return temp, feels_like, umidade, visibilidade, descricao, lat, lon

def buscar_qualidade_ar(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        dados = r.json()['list'][0]
        qualidade = dados['main']['aqi']
        descricao_aqi = {
            1: "Boa",
            2: "Razoável",
            3: "Moderada",
            4: "Ruim",
            5: "Muito Ruim"
        }
        gases = dados['components']
        return descricao_aqi.get(qualidade, "Desconhecida"), gases
    return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    contexto = {}
    if request.method == "POST":
        metodo = request.form.get("metodo")

        if metodo == "cidade":
            cidade = request.form["cidade"]
            resultado = buscar_clima_por_cidade(cidade)
        elif metodo == "coordenadas":
            lat = request.form["latitude"]
            lon = request.form["longitude"]
            resultado = buscar_clima_por_coordenadas(lat, lon)
            cidade = f"Lat: {lat}, Lon: {lon}"
        else:
            resultado = None

        if resultado:
            temp, feels_like, umidade, visib, desc, lat, lon = resultado
            qualidade_ar, gases = buscar_qualidade_ar(lat, lon)

            contexto = {
                "cidade": cidade,
                "temperatura": temp,
                "feels_like": feels_like,
                "umidade": umidade,
                "visibilidade": visib,
                "descricao": desc,
                "qualidade_ar": qualidade_ar,
                "gases": gases
            }
        else:
            contexto["erro"] = "Erro ao buscar dados. Verifique os valores inseridos."
    return render_template("index.html", **contexto)

if __name__ == "__main__":
    app.run(debug=True)