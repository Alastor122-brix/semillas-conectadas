from flask import Flask, render_template_string, jsonify, request
import random, re

app = Flask(__name__)

# ---------------------------------------------------------
# 1. BASE DE DATOS DE SEMILLAS (100 VARIADADES POR CULTIVO)
# ---------------------------------------------------------
REGIONES = ["Cusco", "Huánuco", "Puno", "Junín", "Ayacucho", "Arequipa", "Huancavelica", "Cajamarca", "Ancash", "La Libertad", "Ica"]
TIPOS = ["Nativa / Orgánica", "Criolla Tradicional", "Nativa Ancestral", "Seleccionada Local"]

CATALOGO_COMPLETO = {
    "maiz": {"titulo": "🌽 Semillas de Maíz y Cereales", "descripcion": "Catálogo completo de maíces nativos.", "variedades": []},
    "papa": {"titulo": "🥔 Semillas de Papa y Tubérculos", "descripcion": "Catálogo completo de papas nativas.", "variedades": []},
    "granos": {"titulo": "🌾 Granos y Cereales Andinos", "descripcion": "Catálogo completo de quinuas y cereales.", "variedades": []},
    "legumbres": {"titulo": "🫘 Legumbres y Menestras", "descripcion": "Catálogo completo de pallares y frijoles.", "variedades": []},
    "hortalizas": {"titulo": "🍅 Hortalizas y Ajíes", "descripcion": "Catálogo completo de ajíes y verduras.", "variedades": []}
}

for cat_id in CATALOGO_COMPLETO:
    for i in range(1, 101):
        region = random.choice(REGIONES)
        precio_val = round(random.uniform(7.5, 22.0), 2)
        CATALOGO_COMPLETO[cat_id]["variedades"].append({
            "id": i,
            "nombre": f"Variedad #{i} de {region}",
            "origen": region,
            "tipo": random.choice(TIPOS),
            "precio_num": precio_val,
            "precio": f"S/ {precio_val:.2f}"
        })

# ---------------------------------------------------------
# 2. SISTEMA DE RESEÑAS DESORDENADAS + INFINITE SCROLL
# ---------------------------------------------------------
NOMBRES = ["Carlos M.", "Lucía R.", "Jorge T.", "Elena P.", "Martín S.", "Rosa V.", "Diego L.", "Carmen F.", "Raúl K.", "Ana P.", "Mateo G.", "Sofia B."]
AGRICULTORES = ["Don Pedro Mamani (Cusco)", "Doña María Quispe (Huánuco)", "Cooperativa Urubamba", "Asociación Valle Sur", "Comunidad Mantaro"]
PLANTILLAS_COMEN = {
    5: ["¡Excelente calidad de semilla! Germinación sobre el 95%.", "Trato directo impecable, sin intermediarios.", "Llegó a tiempo y el producto superó mis expectativas."],
    4: ["Muy buena semilla. El envío se retrasó un día pero todo bien.", "Buena tasa de germinación y atención amable.", "Excelente relación calidad-precio."],
    3: ["El producto es aceptable, aunque el empaque puede mejorar.", "La semilla germinó bien pero faltó mejor comunicación.", "Cumple con lo básico para el cultivo."],
    2: ["Tuve problemas de germinación en parte del lote.", "El transporte maltrató los sacos durante el viaje.", "Demoró casi una semana en llegar a mi provincia."],
    1: ["El paquete llegó roto por la agencia de envíos.", "Muy baja respuesta del vendedor ante mis dudas.", "No recibí la variedad exacta que solicité."]
}

def generar_lote_resenas():
    resenas = []
    distribucion = [5]*40 + [4]*30 + [3]*15 + [2]*10 + [1]*5
    for i, estrellas in enumerate(distribucion, 1):
        resenas.append({
            "usuario": random.choice(NOMBRES),
            "agricultor": random.choice(AGRICULTORES),
            "estrellas": estrellas,
            "estrellas_texto": "⭐" * estrellas + "☆" * (5 - estrellas),
            "comentario": random.choice(PLANTILLAS_COMEN[estrellas])
        })
    random.shuffle(resenas)
    return resenas

BASE_RESENAS = generar_lote_resenas()

@app.route("/api/resenas")
def api_resenas():
    nuevas = generar_lote_resenas()
    return jsonify(nuevas[:15])

# ---------------------------------------------------------
# 3. MOTOR DE CHAT INTELIGENTE (RESPUESTAS NATURALES)
# ---------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def procesar_chat():
    data = request.get_json() or {}
    mensaje = data.get("mensaje", "").lower().strip()
    precio_unitario = float(data.get("precio_unitario", 12.00))
    producto = data.get("producto", "Semilla")

    numeros = re.findall(r'\d+', mensaje)
    kilos = float(numeros[0]) if numeros else None

    if kilos:
        total = kilos * precio_unitario
        respuesta = f"🌱 El costo total para <b>{int(kilos)} kg</b> de <b>{producto}</b> es de <b>S/ {total:.2f}</b>."
    elif "buenos dias" in mensaje or "buenos días" in mensaje:
        respuesta = f"☀️ ¡Buenos días! ¿Cuántos kilos de <b>{producto}</b> te gustaría cotizar?"
    elif "buenas tardes" in mensaje:
        respuesta = f"⛅ ¡Buenas tardes! Indícame la cantidad en kilos que necesitas de <b>{producto}</b> y con gusto te calculo el monto."
    elif "buenas noches" in mensaje:
        respuesta = f"🌙 ¡Buenas noches! Dime cuántos kilos deseas de <b>{producto}</b> para darte el precio exacto."
    elif "hola" in mensaje or "buenas" in mensaje:
        respuesta = f"👋 ¡Hola! ¿En qué puedo ayudarte con respecto a <b>{producto}</b>?"
    elif "envio" in mensaje or "envío" in mensaje or "provincia" in mensaje or "llegar" in mensaje:
        respuesta = "🚛 Realizamos envíos directos a todas las regiones del Perú a través de agencias de transporte."
    else:
        respuesta = f"Escribe la cantidad de kilos que deseas para <b>{producto}</b> y te daré la cotización al instante."

    return jsonify({"respuesta": respuesta})

# ---------------------------------------------------------
# 4. RUTAS PRINCIPALES Y PLANTILLAS
# ---------------------------------------------------------
@app.route("/")
def inicio():
    plantilla = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Semillas Conectadas - Inicio</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
            header { background-color: #1b5e20; color: white; padding: 20px; text-align: center; border-radius: 8px; }
            h1 { margin: 0; font-size: 19px; }
            .subtitulo { color: #a5d6a7; font-size: 13px; margin-top: 5px; }
            .seccion { background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .grid-categoria { display: flex; gap: 15px; justify-content: center; margin-top: 15px; flex-wrap: wrap; }
            .tarjeta-cat { background: white; border: 2px solid #a5d6a7; border-radius: 12px; padding: 15px; width: 170px; text-align: center; }
            .icono-semilla { font-size: 35px; margin: 5px 0; }
            .btn { display: inline-block; background-color: #2e7d32; color: white; padding: 8px 12px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; font-size: 12px; }
            .resumen-box { background: #e8f5e9; padding: 15px; border-radius: 6px; border-left: 5px solid #2e7d32; }
            .grid-resenas { max-height: 350px; overflow-y: scroll; padding-right: 10px; border: 1px solid #ddd; padding: 10px; border-radius: 6px; }
            .review-card { border-bottom: 1px solid #eee; padding: 10px 0; font-size: 13px; }
            .badge-5 { color: #2e7d32; font-weight: bold; }
            .badge-3 { color: #f57c00; font-weight: bold; }
            .badge-1 { color: #d32f2f; font-weight: bold; }
        </style>
    </head>
    <body>

        <header>
            <h1>Diseño de una Página Web para Conectar con Pequeños Agricultores y Reducir la Dependencia a las Grandes Empresas de Semillas</h1>
            <div class="subtitulo">Plataforma Agrícola Directa — Ciencia y Tecnología | 2do "C"</div>
        </header>

        <!-- BOTONES DE NAVEGACIÓN -->
        <div class="seccion">
            <h2 style="text-align: center; color: #1b5e20; margin-top: 0;">🌱 Explorar Catálogo (100 Variedades por Tipo)</h2>
            <div class="grid-categoria">
                <div class="tarjeta-cat"><div class="icono-semilla">🌽</div><h3>Maíz</h3><p>100 Variedades</p><a href="/categoria/maiz" class="btn">Ver Semillas</a></div>
                <div class="tarjeta-cat"><div class="icono-semilla">🥔</div><h3>Papa</h3><p>100 Variedades</p><a href="/categoria/papa" class="btn">Ver Semillas</a></div>
                <div class="tarjeta-cat"><div class="icono-semilla">🌾</div><h3>Granos</h3><p>100 Variedades</p><a href="/categoria/granos" class="btn">Ver Semillas</a></div>
                <div class="tarjeta-cat"><div class="icono-semilla">🫘</div><h3>Legumbres</h3><p>100 Variedades</p><a href="/categoria/legumbres" class="btn">Ver Semillas</a></div>
                <div class="tarjeta-cat"><div class="icono-semilla">🍅</div><h3>Hortalizas</h3><p>100 Variedades</p><a href="/categoria/hortalizas" class="btn">Ver Semillas</a></div>
            </div>
        </div>

        <!-- COMENTARIOS EN EL INICIO -->
        <div class="seccion">
            <h3>📊 Resumen Transparente del Sistema de Reseñas</h3>
            <div class="resumen-box">
                <p><strong>Distribución de Opiniones Registradas:</strong></p>
                <ul>
                    <li class="badge-5">⭐⭐⭐⭐⭐ Excelente (5/5): 40%</li>
                    <li class="badge-5">⭐⭐⭐⭐ Bueno (4/5): 30%</li>
                    <li class="badge-3">⭐⭐⭐ Regular (3/5): 15%</li>
                    <li class="badge-3">⭐⭐ Malo (2/5): 10%</li>
                    <li class="badge-1">⭐ Pésimo (1/5): 5%</li>
                </ul>
            </div>

            <h3 style="margin-top: 20px;">💬 Comentarios de Compradores (Scroll Infinito)</h3>
            <div class="grid-resenas" id="contenedorResenas">
                {% for r in resenas %}
                <div class="review-card">
                    <strong>{{ r.usuario }}</strong> a <em>{{ r.agricultor }}</em> — 
                    <span class="{% if r.estrellas >= 4 %}badge-5{% elif r.estrellas >= 2 %}badge-3{% else %}badge-1{% endif %}">
                        {{ r.estrellas_texto }} ({{ r.estrellas }}/5)
                    </span>
                    <br>{{ r.comentario }}
                </div>
                {% endfor %}
            </div>
        </div>

        <script>
            const contenedor = document.getElementById('contenedorResenas');
            let cargando = false;

            contenedor.addEventListener('scroll', () => {
                if (contenedor.scrollTop + contenedor.clientHeight >= contenedor.scrollHeight - 10 && !cargando) {
                    cargando = true;
                    fetch('/api/resenas')
                        .then(res => res.json())
                        .then(data => {
                            data.forEach(r => {
                                const div = document.createElement('div');
                                div.className = 'review-card';
                                const claseEstrellas = r.estrellas >= 4 ? 'badge-5' : (r.estrellas >= 2 ? 'badge-3' : 'badge-1');
                                div.innerHTML = `<strong>${r.usuario}</strong> a <em>${r.agricultor}</em> — 
                                    <span class="${claseEstrellas}">${r.estrellas_texto} (${r.estrellas}/5)</span>
                                    <br>${r.comentario}`;
                                contenedor.appendChild(div);
                            });
                            cargando = false;
                        });
                }
            });
        </script>

    </body>
    </html>
    """
    return render_template_string(plantilla, resenas=BASE_RESENAS)

@app.route("/categoria/<nombre_cat>")
def ver_categoria(nombre_cat):
    categoria = CATALOGO_COMPLETO.get(nombre_cat)
    if not categoria:
        return "Categoría no encontrada", 404

    plantilla_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>{{ categoria.titulo }}</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px; }
            h1 { color: #1b5e20; }
            .btn-volver { display: inline-block; background: #555; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; margin-bottom: 15px; font-weight: bold; }
            .tabla-contenedor { max-height: 500px; overflow-y: scroll; border: 1px solid #ccc; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; background: white; }
            th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #ddd; font-size: 13px; }
            th { background-color: #2e7d32; color: white; position: sticky; top: 0; }
            .btn-chat { background: #2e7d32; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px; }
            
            /* MODAL FLOTANTE DEL CHAT DENTRO DE LAS VARIADADES */
            #modal-chat { display: none; position: fixed; bottom: 20px; right: 20px; width: 320px; background: white; border: 2px solid #1b5e20; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 100; overflow: hidden; }
            #chat-header { background: #1b5e20; color: white; padding: 10px; font-weight: bold; font-size: 13px; display: flex; justify-content: space-between; }
            #chat-mensajes { height: 200px; overflow-y: auto; padding: 10px; font-size: 13px; background: #fafafa; }
            .msg { margin-bottom: 8px; padding: 6px; border-radius: 6px; }
            .msg-user { background: #e1f5fe; text-align: right; }
            .msg-bot { background: #e8f5e9; border-left: 3px solid #2e7d32; }
            #chat-input-box { display: flex; border-top: 1px solid #ccc; }
            #chat-input { flex: 1; border: none; padding: 8px; font-size: 12px; }
            #btn-send { background: #2e7d32; color: white; border: none; padding: 0 12px; cursor: pointer; }
        </style>
    </head>
    <body>
        <a href="/" class="btn-volver">← Volver al Inicio</a>
        <h1>{{ categoria.titulo }}</h1>
        <p>{{ categoria.descripcion }}</p>

        <div class="tabla-contenedor">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Variedad de Semilla</th>
                        <th>Origen</th>
                        <th>Tipo</th>
                        <th>Precio/Kg</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in categoria.variedades %}
                    <tr>
                        <td>{{ item.id }}</td>
                        <td><strong>{{ item.nombre }}</strong></td>
                        <td>{{ item.origen }}</td>
                        <td>{{ item.tipo }}</td>
                        <td>{{ item.precio }}</td>
                        <td>
                            <button class="btn-chat" onclick="abrirChat('{{ item.nombre }}', '{{ item.precio_num }}')">💬 Chatear / Cotizar</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- MODAL DEL CHAT -->
        <div id="modal-chat">
            <div id="chat-header">
                <span id="chat-titulo-prod">Chat con Vendedor</span>
                <span style="cursor:pointer;" onclick="cerrarChat()">✖</span>
            </div>
            <div id="chat-mensajes"></div>
            <div id="chat-input-box">
                <input type="text" id="chat-input" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter') enviarMsg()">
                <button id="btn-send" onclick="enviarMsg()">Enviar</button>
            </div>
        </div>

        <script>
            let productoActual = '';
            let precioActual = 0;

            function abrirChat(nombre, precio) {
                productoActual = nombre;
                precioActual = parseFloat(precio);
                document.getElementById('modal-chat').style.display = 'block';
                document.getElementById('chat-titulo-prod').textContent = nombre;
                const msgs = document.getElementById('chat-mensajes');
                msgs.innerHTML = `<div class="msg msg-bot">👋 ¡Hola! Bienvenido. Estás consultando por <b>${nombre}</b>. ¿Cuántos kilos te gustaría cotizar?</div>`;
            }

            function cerrarChat() {
                document.getElementById('modal-chat').style.display = 'none';
            }

            function enviarMsg() {
                const input = document.getElementById('chat-input');
                const texto = input.value.trim();
                if (!texto) return;

                const msgs = document.getElementById('chat-mensajes');
                const divUser = document.createElement('div');
                divUser.className = 'msg msg-user';
                divUser.textContent = texto;
                msgs.appendChild(divUser);
                input.value = '';

                fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: texto, precio_unitario: precioActual, producto: productoActual })
                })
                .then(res => res.json())
                .then(data => {
                    const divBot = document.createElement('div');
                    divBot.className = 'msg msg-bot';
                    divBot.innerHTML = data.respuesta;
                    msgs.appendChild(divBot);
                    msgs.scrollTop = msgs.scrollHeight;
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(plantilla_html, categoria=categoria)

if __name__ == "__main__":
    app.run(debug=True)