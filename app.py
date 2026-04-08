from flask import Flask, request, render_template_string, send_file, session
import pandas as pd
import io
import os

app = Flask(__name__)
app.secret_key = "academia_pro_123"

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

def corregir(respuestas, clave):
    c = i = b = 0
    detalle = {}
    colores = []

    for x in range(100):
        if respuestas[x] == "":
            b += 1
            colores.append("gray")
        elif respuestas[x] == clave[x]:
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
            if respuestas[j] == clave[j]:
                cont += 1

        detalle[curso] = cont
        inicio = fin

    return c,i,b,puntaje,detalle,colores

# ==============================
# HTML
# ==============================

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Simulacros PRO</title>

<style>
body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #1b5e20, #4caf50, #cddc39, #fff176);
    background-size: 400% 400%;
    animation: fondoAnimado 10s ease infinite;
    text-align:center;
    color:white;
}

@keyframes fondoAnimado {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.container {
    width:90%;
    max-width:1000px;
    margin:auto;
}

.card {
    background:white;
    color:#333;
    padding:20px;
    margin:20px;
    border-radius:15px;
    transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.2);
}

.file-input {
    display:inline-block;
    padding:10px 20px;
    background:#2e7d32;
    color:white;
    border-radius:8px;
    cursor:pointer;
}

input[type="file"] { display:none; }

select {
    padding:10px;
    border-radius:8px;
    margin:10px;
}

button {
    background:#2e7d32;
    color:white;
    padding:10px 20px;
    border:none;
    border-radius:8px;
    transition:0.3s;
}

button:hover {
    background:#1b5e20;
    transform: scale(1.05);
}

.grid {
    display:grid;
    grid-template-columns: repeat(4,1fr);
    gap:20px;
}

.columna { display:flex; flex-direction:column; }
.fila { display:flex; gap:5px; justify-content:center; }

input.resp {
    width:40px;
    height:40px;
    text-align:center;
    border-radius:8px;
    border:1px solid #ccc;
    font-weight:bold;
    transition:0.2s;
}

input.resp:focus {
    outline:none;
    border:2px solid #2e7d32;
    transform: scale(1.1);
}

.green { background:#b6fcb6; }
.red { background:#ffb3b3; }
.gray { background:#eee; }

table {
    margin:auto;
    border-collapse:collapse;
    width:90%;
}

th {
    background:#2e7d32;
    color:white;
}

tr:nth-child(even) {
    background:#f2f2f2;
}

</style>

<script>
function subir(form){ form.submit(); }

function mover(e, next){
    let val = e.value.toUpperCase();
    e.value = val;

    if(["A","B","C","D","E"].includes(val)){
        e.style.border = "2px solid green";
        let nextInput = document.getElementsByName("p"+next)[0];
        if(nextInput){ nextInput.focus(); }
    } else if(val !== ""){
        e.style.border = "2px solid red";
    }

    actualizarBarra();
}

function actualizarBarra(){
    let inputs = document.querySelectorAll("input.resp");
    let llenos = 0;

    inputs.forEach(i=>{
        if(i.value !== "") llenos++;
    });

    let porcentaje = Math.round((llenos/100)*100);

    let barra = document.getElementById("barra");
    if(barra){
        barra.style.width = porcentaje + "%";
        barra.innerText = porcentaje + "%";
    }
}
</script>

</head>

<body>

<h1>📊 Corrector de Simulacros</h1>

<div class="container">

<div class="card">
<form method="POST" enctype="multipart/form-data">

<h3>Subir CLAVES</h3>
<label class="file-input">
Seleccionar archivo
<input type="file" name="clave" onchange="subir(this.form)">
</label>

<h3>Subir ALUMNOS</h3>
<label class="file-input">
Seleccionar archivo
<input type="file" name="alumnos" onchange="subir(this.form)">
</label>

<br><br>

{% if alumnos %}
<select name="nombre">
{% for a in alumnos %}
<option>{{a}}</option>
{% endfor %}
</select>
{% endif %}

{% if aulas %}
<select name="aula">
{% for a in aulas %}
<option>{{a}}</option>
{% endfor %}
</select>
{% endif %}

<!-- BARRA -->
<div style="margin:20px;">
    <div style="background:#ddd; border-radius:20px;">
        <div id="barra" style="
            width:0%;
            background:#2e7d32;
            color:white;
            padding:5px;
            border-radius:20px;
        ">0%</div>
    </div>
</div>

<div class="grid">
{% for col in range(4) %}
<div class="columna">
{% for i in range(col*25+1, col*25+26) %}
<div class="fila">
<span>{{i}}</span>
<input name="p{{i}}" maxlength="1"
class="resp {{colores[i-1] if colores else ''}}"
onkeyup="mover(this, {{i+1}})">
</div>
{% endfor %}
</div>
{% endfor %}
</div>

<br>
<button type="submit">Corregir</button>

</form>
</div>

{% if resultado %}
<div class="card">

<h2>Resultado</h2>
<p>✔ Correctas: {{resultado[0]}}</p>
<p>❌ Incorrectas: {{resultado[1]}}</p>
<p>⚪ Blanco: {{resultado[2]}}</p>
<p>🎯 Puntaje: {{resultado[3]}}</p>

<h3>Por Curso</h3>
<ul>
{% for c in detalle %}
<li>{{c}}: {{detalle[c]}}</li>
{% endfor %}
</ul>

<h3>📋 Alumnos corregidos</h3>
<table border="1">
<tr>
<th>Nombre</th><th>Aula</th><th>Puntaje</th>
</tr>
{% for r in resultados %}
<tr>
<td>{{r["Nombre"]}}</td>
<td>{{r["Aula"]}}</td>
<td>{{r["Puntaje"]}}</td>
</tr>
{% endfor %}
</table>

<h3>🏆 Ranking por Aula</h3>

{% for aula in ranking %}
<h4>{{aula}}</h4>

<table border="1">
<tr>
<th>#</th><th>Nombre</th><th>Puntaje</th>
</tr>

{% for r in ranking[aula] %}
<tr>
<td>{{loop.index}}</td>
<td>{{r["Nombre"]}}</td>
<td>{{r["Puntaje"]}}</td>
</tr>
{% endfor %}
</table>
{% endfor %}

<br>
<a href="/excel"><button>Descargar Excel</button></a>

</div>
{% endif %}

</div>

</body>
</html>
"""

# ==============================
# RUTA PRINCIPAL
# ==============================

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        session.clear()

    if "resultados" not in session:
        session["resultados"] = []

    resultado = None
    detalle = {}
    colores = None

    if request.method == "POST":

        archivo_clave = request.files.get("clave")
        if archivo_clave and archivo_clave.filename != "":
            df = pd.read_excel(archivo_clave)
            session["clave"] = df[df.columns[0]].astype(str).str.upper().tolist()

        archivo_alumnos = request.files.get("alumnos")
        if archivo_alumnos and archivo_alumnos.filename != "":
            df = pd.read_excel(archivo_alumnos)
            session["alumnos"] = df[df.columns[0]].tolist()
            session["aulas"] = df[df.columns[1]].unique().tolist()

        if "clave" in session and "nombre" in request.form:

            respuestas = [request.form.get(f"p{i}", "").upper() for i in range(1,101)]

            c,i,b,p,detalle,colores = corregir(respuestas, session["clave"])
            resultado = (c,i,b,p)

            datos = session["resultados"]
            datos.append({
                "Nombre": request.form["nombre"],
                "Aula": request.form["aula"],
                "Correctas": c,
                "Incorrectas": i,
                "Blanco": b,
                "Puntaje": p,
                **detalle
            })
            session["resultados"] = datos

    ranking = {}
    for r in session.get("resultados", []):
        aula = r["Aula"]
        if aula not in ranking:
            ranking[aula] = []
        ranking[aula].append(r)

    for aula in ranking:
        ranking[aula] = sorted(ranking[aula], key=lambda x: x["Puntaje"], reverse=True)

    return render_template_string(HTML,
        alumnos=session.get("alumnos"),
        aulas=session.get("aulas"),
        resultado=resultado,
        detalle=detalle,
        colores=colores,
        resultados=session.get("resultados", []),
        ranking=ranking
    )

# ==============================
# EXPORTAR EXCEL
# ==============================

@app.route("/excel")
def excel():
    df = pd.DataFrame(session.get("resultados", []))

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output, download_name="RESULTADOS.xlsx", as_attachment=True)

# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
