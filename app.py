from flask import Flask, request, render_template_string, send_file
import pandas as pd
import io
import os

app = Flask(__name__)

# ==============================
# DATA GLOBAL (NO SESSION ❗)
# ==============================

clave_global = []
alumnos_global = []
aulas_global = []
resultados_global = []

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
    c = i = b = 0
    detalle = {}
    colores = []

    for x in range(100):
        if respuestas[x] == "":
            b += 1
            colores.append("gray")
        elif respuestas[x] == clave_global[x]:
            c += 1
            colores.append("green")
        else:
            i += 1
            colores.append("red")

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

    return c,i,b,puntaje,detalle,colores

# ==============================
# HTML PRO
# ==============================

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Simulacros PRO</title>

<style>
body {
    margin:0;
    font-family:'Segoe UI';
    display:flex;
}

/* SIDEBAR */
.sidebar {
    width:250px;
    background:#1b5e20;
    color:white;
    height:100vh;
    padding:20px;
}

.logo {
    font-size:20px;
    font-weight:bold;
    margin-bottom:30px;
}

.menu div {
    margin:15px 0;
    padding:10px;
    background:#2e7d32;
    border-radius:8px;
}

/* MAIN */
.main {
    flex:1;
    padding:20px;
    background:#f5f5f5;
}

.top {
    display:flex;
    gap:10px;
    margin-bottom:20px;
}

select, button {
    padding:10px;
    border-radius:8px;
    border:none;
}

button {
    background:#2e7d32;
    color:white;
}

/* CARDS */
.grid {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:20px;
}

.card {
    background:white;
    border-radius:15px;
    padding:15px;
}

.card h3 {
    background:#2e7d32;
    color:white;
    padding:10px;
    border-radius:10px;
}

/* INPUTS */
.inputs {
    display:flex;
    flex-wrap:wrap;
    gap:5px;
    margin-top:10px;
}

input {
    width:35px;
    height:35px;
    text-align:center;
    border-radius:6px;
}

/* PROGRESS */
.progress {
    height:10px;
    background:#ccc;
    margin-top:10px;
    border-radius:10px;
}

.bar {
    height:10px;
    background:#4caf50;
    width:0%;
    border-radius:10px;
}
</style>

<script>
function mover(e,next){
    let v = e.value.toUpperCase();
    e.value = v;

    if(["A","B","C","D","E"].includes(v)){
        let n = document.getElementsByName("p"+next)[0];
        if(n) n.focus();
    }

    actualizar();
}

function actualizar(){
    let inputs = document.querySelectorAll("input");
    let llenos = 0;

    inputs.forEach(i=>{
        if(i.value!="") llenos++;
    });

    let p = Math.round((llenos/100)*100);
    document.getElementById("bar").style.width = p+"%";
}
</script>

</head>

<body>

<div class="sidebar">
    <div class="logo">JFK Simulacros</div>

    <form method="POST" enctype="multipart/form-data">
        <p>Claves</p>
        <input type="file" name="clave" onchange="this.form.submit()">

        <p>Alumnos</p>
        <input type="file" name="alumnos" onchange="this.form.submit()">
    </form>

    <div class="progress">
        <div class="bar" id="bar"></div>
    </div>
</div>

<div class="main">

<form method="POST">

<div class="top">
<select name="nombre">
{% for a in alumnos %}
<option>{{a}}</option>
{% endfor %}
</select>

<select name="aula">
{% for a in aulas %}
<option>{{a}}</option>
{% endfor %}
</select>

<button>Corregir</button>
</div>

<div class="grid">

{% set i = 1 %}
{% for curso, cant in cursos.items() %}
<div class="card">
<h3>{{curso}}</h3>

<div class="inputs">
{% for j in range(cant) %}
<input name="p{{i}}" maxlength="1" onkeyup="mover(this, {{i+1}})">
{% set i = i + 1 %}
{% endfor %}
</div>

</div>
{% endfor %}

</div>

</form>

{% if resultado %}
<h2>Puntaje: {{resultado[3]}}</h2>
{% endif %}

</div>

</body>
</html>
"""

# ==============================
# RUTA
# ==============================

@app.route("/", methods=["GET","POST"])
def index():
    global clave_global, alumnos_global, aulas_global, resultados_global

    resultado = None

    if request.method == "POST":

        if "clave" in request.files:
            f = request.files["clave"]
            if f.filename != "":
                df = pd.read_excel(f)
                clave_global = df.iloc[:,0].astype(str).str.upper().tolist()

                if len(clave_global) != 100:
                    return "Error: clave debe tener 100 respuestas"

        if "alumnos" in request.files:
            f = request.files["alumnos"]
            if f.filename != "":
                df = pd.read_excel(f)
                alumnos_global = df.iloc[:,0].tolist()
                aulas_global = df.iloc[:,1].unique().tolist()

        if "nombre" in request.form and len(clave_global)==100:

            respuestas = [request.form.get(f"p{i}","").upper() for i in range(1,101)]

            c,i,b,p,detalle,colores = corregir(respuestas)
            resultado = (c,i,b,p)

            resultados_global.append({
                "Nombre": request.form["nombre"],
                "Aula": request.form["aula"],
                "Puntaje": p
            })

    return render_template_string(HTML,
        alumnos=alumnos_global,
        aulas=aulas_global,
        cursos=cursos,
        resultado=resultado
    )

# ==============================
# EXCEL
# ==============================

@app.route("/excel")
def excel():
    df = pd.DataFrame(resultados_global)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="resultados.xlsx", as_attachment=True)

# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
