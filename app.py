from flask import Flask, request, render_template, send_file
import pandas as pd
import io
import os

app = Flask(__name__)

# ==============================
# DATA GLOBAL
# ==============================

clave_global = []
alumnos_global = []
aulas_global = []
resultado_global = None
detalle_global = {}

# ==============================
# CURSOS
# ==============================

cursos = {
    "Actitudinales": 4,
    "Habilidad Verbal": 14,
    "Habilidad Matemática": 12,
    "Aritmética": 4,
    "Geometría": 4,
    "Álgebra": 4,
    "Trigonometría": 4,
    "Lenguaje": 7,
    "Literatura": 4,
    "Economía": 4,
    "Cívica": 4,
    "Historia del Perú": 4,
    "Historia Universal": 4,
    "Geografía": 4,
    "Psicología": 4,
    "Filosofía": 4,
    "Física": 5,
    "Química": 5,
    "Biología": 5
}

# ==============================
# CORREGIR
# ==============================

def corregir(respuestas):
    global detalle_global

    c = i = b = 0
    detalle = {}

    for x in range(100):
        if respuestas[x] == "":
            b += 1
        elif respuestas[x] == clave_global[x]:
            c += 1
        else:
            i += 1

    puntaje = c*20 - i*5

    inicio = 0
    for curso, cantidad in cursos.items():
        fin = inicio + cantidad
        cont = 0

        for j in range(inicio, fin):
            if respuestas[j] == clave_global[j]:
                cont += 1

        detalle[curso] = cont
        inicio = fin

    detalle_global = detalle
    return c,i,b,puntaje,detalle

# ==============================
# RUTA
# ==============================

@app.route("/", methods=["GET","POST"])
def index():
    global clave_global, alumnos_global, aulas_global, resultado_global

    if request.method == "POST":

        # CLAVE
        if "clave" in request.files:
            f = request.files["clave"]
            if f.filename != "":
                df = pd.read_excel(f, header=None)

                col = df.iloc[:,0].dropna()
                col = col.astype(str).str.strip().str.upper()
                col = col[col.isin(["A","B","C","D","E"])]

                clave_global = col.tolist()

                if len(clave_global) != 100:
                    return f"Error: {len(clave_global)} respuestas detectadas"

        # ALUMNOS
        if "alumnos" in request.files:
            f = request.files["alumnos"]
            if f.filename != "":
                df = pd.read_excel(f, header=None)
                alumnos_global = df.iloc[:,0].tolist()
                aulas_global = df.iloc[:,1].unique().tolist()

        # CORREGIR
        if "nombre" in request.form and len(clave_global) == 100:
            respuestas = [request.form.get(f"p{i}","").upper() for i in range(1,101)]

            c,i,b,p,detalle = corregir(respuestas)
            resultado_global = (c,i,b,p)

    return render_template("index.html",
        alumnos=alumnos_global,
        aulas=aulas_global,
        cursos=cursos,
        resultado=resultado_global,
        detalle=detalle_global
    )

# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
