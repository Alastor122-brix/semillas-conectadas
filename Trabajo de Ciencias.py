import random
import re
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Base de datos de regiones y tipos
REGIONES = ["Cusco", "Puno", "Junín", "Huánuco", "Ica", "Arequipa", "Cajamarca", "La Libertad", "San Martín", "Ayacucho"]
TIPOS_SEMILLA = ["Nativa Orgánica", "Criolla Tradicional", "Seleccionada de Granja", "Mejorada Local"]

# Especialistas por categoría
ESPECIALISTAS = {
    "Maíz": ["Mateo Quispe", "Lucía Huamán", "Efraín Gonzales"],
    "Papas Nativas": ["Rosa Condori", "Don Pedro Vilca", "Juana Flores"],
    "Granos Andinos": ["Juan Carlos Mamani", "Yolanda Choque", "Tomás Castillo"],
    "Legumbres": ["Carlos Benites", "Elena Rojas", "Hernán Silva"],
    "Café y Cacao": ["Nélida Arango", "Gerson Campos", "Beatriz Mendoza"]
}

CATEGORIAS_INFO = {
    "Maíz": {"emoji": "🌽", "nombres": ["Blanco Gigante", "Amarillo Duro", "Morado", "Chulpi", "Chala", "Cabanza", "Confite", "Kculli", "Paro", "Sacsa"]},
    "Papas Nativas": {"emoji": "🥔", "nombres": ["Huayro", "Canchán", "Amarilla Tumbay", "Peruanita", "Camotillo", "Tumbay", "Huamantanga", "Yana Shungo", "Puka Shungo", "Sirenita"]},
    "Granos Andinos": {"emoji": "🌾", "nombres": ["Quinua Blanca Junín", "Quinua Roja Pasankalla", "Quinua Negra Collana", "Kiwicha Oscar Blanco", "Cañihua Cupi", "Tarwi Zapatos", "Quinua Amarilla Sacaca", "Kiwicha Centenario", "Quinua Choclito", "Cañihua Ramis"]},
    "Legumbres": {"emoji": "🫘", "nombres": ["Frijol Canario", "Frijol Panamito", "Haba Amarilla", "Pallar de Ica", "Lenteja Criolla", "Arveja Verde", "Frijol Castropampa", "Frijol Caballero", "Haba Gigante", "Garbanzo Blanco"]},
    "Café y Cacao": {"emoji": "☕", "nombres": ["Café Caturra", "Café Typica", "Café Bourbon", "Café Geisha", "Cacao Chuncho", "Cacao Blanco de Piura", "Cacao CCN-51", "Café Catimor", "Café Pache", "Cacao Criollo de Satipo"]}
}

CATEGORIAS = {}
for cat, info in CATEGORIAS_INFO.items():
    lista_productos = []
    nombres_base = info["nombres"]
    for i in range(1, 101):
        nombre_base = nombres_base[(i - 1) % len(nombres_base)]
        region = REGIONES[(i - 1) % len(REGIONES)]
        tipo = TIPOS_SEMILLA[(i - 1) % len(TIPOS_SEMILLA)]
        
        variedad_nombre = f"{nombre_base} {tipo.split()[0]} - Lote {i}" if i > 10 else f"{nombre_base} de {region}"
        precio = round(8.0 + (i * 0.25) % 18, 2)
        
        lista_productos.append({
            "id": i,
            "nombre": variedad_nombre,
            "region": region,
            "tipo": tipo,
            "precio": precio,
            "disponibilidad": "Disponible" if i % 7 != 0 else "Pocas Unidades"
        })
    CATEGORIAS[cat] = lista_productos

COMENARIOS_POR_ESTRELLA = {
    "⭐⭐⭐⭐⭐": [
        "Excelente calidad germinativa, rindió muy bien en la cosecha.",
        "Semilla 100% nativa de gran resistencia a las plagas.",
        "El envío llegó a tiempo y la atención del agricultor fue impecable.",
        "Muy contento con el rendimiento por hectárea, totalmente recomendado."
    ],
    "⭐⭐⭐⭐": [
        "Buena calidad de semilla, germinó la gran mayoría sin problema.",
        "Llegó un día después de lo previsto, pero el producto es de primera.",
        "Muy buen grano y bien empaquetado. Buen servicio general."
    ],
    "⭐⭐⭐": [
        "El producto es bueno pero la agencia de transporte demoró en coordinar.",
        "Germinación regular, algunas semillas tardaron por el clima seco.",
        "Atención aceptable, aunque tardaron un poco en responder mis dudas."
    ],
    "⭐⭐": [
        "Hubo demoras con el flete hacia mi localidad y el empaque llegó algo maltratado.",
        "No rindió lo esperado en mi zona, requiere mejor análisis de suelo."
    ],
    "⭐": [
        "El envío tardó más de 5 días en llegar a mi provincia por mala logística local.",
        "Tuve inconvenientes con el punto de entrega en la agencia de transporte."
    ]
}

NOMBRES_AUTORES = [
    "Mateo Quispe (Agricultor de Cusco)", "María Condori (Compradora de Lima)",
    "Juan Carlos Mamani (Productor de Junín)", "Lucía Huamán (Cajamarca)",
    "Asociación AgroEcológica Valle Sagrado", "Cooperativa Agrícola Puno",
    "Don Pedro Vilca (Arequipa)", "Comunidad Campesina Huánuco",
    "Carlos Benites (La Libertad)", "Elena Rojas (San Martín)"
]

@app.route('/')
def inicio():
    plantilla_inicio = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Semillas Conectadas - Comercio Justo Directo</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; color: #333; }
            header { background: #2e7d32; color: white; padding: 25px 20px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
            h1 { margin: 0; font-size: 2.2em; }
            p.subtitulo { margin-top: 5px; font-size: 1.1em; opacity: 0.9; }
            
            .header-fuentes {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 12px 20px;
                margin: 15px auto 0 auto;
                max-width: 800px;
                text-align: left;
                font-size: 0.9em;
            }
            .header-fuentes h4 { margin: 0 0 5px 0; color: #e8f5e9; font-size: 1em; }
            .header-fuentes ul { margin: 0; padding-left: 20px; color: #f1f8f5; }

            .container { max-width: 1050px; margin: 30px auto; padding: 0 20px; }

            .grid-categorias { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .card-categoria { background: white; border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; border-top: 5px solid #2e7d32; }
            .card-categoria:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
            .card-categoria .emoji { font-size: 2.8em; margin-bottom: 10px; }
            .card-categoria h3 { color: #2e7d32; margin: 5px 0 10px 0; font-size: 1.4em; }
            .btn-ver { display: inline-block; background: #2e7d32; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }
            .btn-ver:hover { background: #1b5e20; }
            
            .resumen-estadistica { background: #e8f5e9; border-left: 5px solid #2e7d32; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
            .resumen-titulo { font-weight: bold; font-size: 1.15em; color: #1b5e20; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
            .stat-line { margin: 6px 0; font-size: 0.95em; }
            .stat-excelente { color: #2e7d32; font-weight: bold; }
            .stat-bueno { color: #388e3c; font-weight: bold; }
            .stat-regular { color: #f57c00; font-weight: bold; }
            .stat-malo { color: #e65100; font-weight: bold; }
            .stat-pesimo { color: #d32f2f; font-weight: bold; }

            .resenas-seccion { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 40px; }
            .resena-item { padding: 15px; border-bottom: 1px solid #eee; }
            .resena-item:last-child { border-bottom: none; }
            .resena-autor { font-weight: bold; color: #2e7d32; }
            .resena-texto { margin: 5px 0 0 0; color: #555; }
        </style>
    </head>
    <body>
        <header>
            <h1>Plataforma Semillas Conectadas 🌱</h1>
            <p class="subtitulo">Conectando Pequeños Agricultores Directamente con el Mercado</p>
            
            <div class="header-fuentes">
                <h4>📚 Fuentes Bibliográficas y Científicas del Proyecto:</h4>
                <ul>
                    <li><strong>Wikipedia:</strong> Taxonomía, origen botánico y caracterización general de especies.</li>
                    <li><strong>INIA (Instituto Nacional de Innovación Agraria):</strong> Adaptabilidad técnica y conservación de semillas criollas.</li>
                    <li><strong>CIP (Centro Internacional de la Papa):</strong> Diversidad genética de cultivos nativos andinos.</li>
                </ul>
            </div>
        </header>
        <div class="container">
            
            <div class="resumen-estadistica">
                <div class="resumen-titulo">📊 Resumen Transparente del Sistema de Reseñas</div>
                <div style="font-weight: bold; margin-bottom: 8px;">Distribución de Opiniones Registradas:</div>
                <div class="stat-line">• ⭐⭐⭐⭐⭐ <span class="stat-excelente">Excelente (5/5): 40%</span></div>
                <div class="stat-line">• ⭐⭐⭐⭐ <span class="stat-bueno">Bueno (4/5): 30%</span></div>
                <div class="stat-line">• ⭐⭐⭐ <span class="stat-regular">Regular (3/5): 15%</span></div>
                <div class="stat-line">• ⭐⭐ <span class="stat-malo">Malo (2/5): 10%</span></div>
                <div class="stat-line">• ⭐ <span class="stat-pesimo">Pésimo (1/5): 5%</span></div>
            </div>

            <h2 style="text-align: center; color: #2e7d32; margin-bottom: 25px;">Explorar Catálogo de Semillas por Categoría</h2>
            
            <div class="grid-categorias">
                {% for cat, info in categorias.items() %}
                <div class="card-categoria">
                    <div class="emoji">{{ info.emoji }}</div>
                    <h3>{{ cat }}</h3>
                    <p style="color:#666;">100 variedades nativas y criollas con certificación de origen.</p>
                    <a href="/categoria/{{ cat }}" class="btn-ver">{{ info.emoji }} Explorar {{ cat }}</a>
                </div>
                {% endfor %}
            </div>

            <div class="resenas-seccion">
                <h3 style="color: #2e7d32; margin-top:0; border-bottom: 2px solid #e8f5e9; padding-bottom: 10px;">💬 Opiniones de Agricultores y Compradores (Scroll Infinito)</h3>
                <div id="resenas-lista"></div>
            </div>
        </div>

        <script>
            const comentariosMap = {{ comentarios_map | tojson }};
            const autoresEjemplo = {{ autores | tojson }};
            const contenedorResenas = document.getElementById('resenas-lista');

            const secuenciaEstrellas = ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"];
            let indiceSecuencia = 0;

            function agregarResenas(cantidad) {
                for (let i = 0; i < cantidad; i++) {
                    const estrellas = secuenciaEstrellas[indiceSecuencia % secuenciaEstrellas.length];
                    indiceSecuencia++;

                    const listaTextos = comentariosMap[estrellas];
                    const texto = listaTextos[Math.floor(Math.random() * listaTextos.length)];
                    const autor = autoresEjemplo[Math.floor(Math.random() * autoresEjemplo.length)];
                    
                    const div = document.createElement('div');
                    div.className = 'resena-item';
                    div.innerHTML = `<span class="resena-autor">${estrellas} ${autor}:</span> <p class="resena-texto">"${texto}"</p>`;
                    contenedorResenas.appendChild(div);
                }
            }

            agregarResenas(5);

            window.addEventListener('scroll', () => {
                if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 150) {
                    agregarResenas(5);
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(plantilla_inicio, categorias=CATEGORIAS_INFO, comentarios_map=COMENARIOS_POR_ESTRELLA, autores=NOMBRES_AUTORES)

@app.route('/categoria/<nombre_cat>')
def ver_categoria(nombre_cat):
    if nombre_cat not in CATEGORIAS:
        return "Categoría no encontrada", 404
        
    categoria_productos = CATEGORIAS[nombre_cat]
    emoji_cat = CATEGORIAS_INFO[nombre_cat]["emoji"]
    especialistas_cat = ESPECIALISTAS.get(nombre_cat, ["Asesor Agrícola"])
    
    plantilla_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ emoji }} {{ categoria }} - Semillas Conectadas</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; }
            header { background: #2e7d32; color: white; padding: 15px; text-align: center; }
            .container { max-width: 1100px; margin: 20px auto; padding: 0 15px; }
            .btn-volver { display: inline-block; background: #555; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
            .btn-volver:hover { background: #333; }
            table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #2e7d32; color: white; }
            tr:hover { background-color: #f1f8f5; }
            .btn-chat { background: #2e7d32; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .btn-chat:hover { background: #1b5e20; }
            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
            .modal-content { background: white; width: 90%; max-width: 500px; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; height: 500px; }
            .modal-header { background: #2e7d32; color: white; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
            .cerrar-modal { cursor: pointer; font-size: 20px; }
            .chat-messages { flex: 1; padding: 15px; overflow-y: auto; background: #fafafa; display: flex; flex-direction: column; gap: 10px; }
            .msg { padding: 10px 14px; border-radius: 8px; max-width: 80%; line-height: 1.4; }
            .msg-bot { background: #e8f5e9; color: #1b5e20; align-self: flex-start; border: 1px solid #c8e6c9; }
            .msg-user { background: #2e7d32; color: white; align-self: flex-end; }
            .chat-input { display: flex; border-top: 1px solid #ddd; padding: 10px; background: white; }
            .chat-input input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; outline: none; }
            .chat-input button { background: #2e7d32; color: white; border: none; padding: 10px 15px; margin-left: 8px; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h1>{{ emoji }} Categoría: {{ categoria }} (100 Variedades)</h1>
        </header>
        <div class="container">
            <a href="/" class="btn-volver">← Volver al Inicio</a>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Nombre / Variedad</th>
                        <th>Región / Origen</th>
                        <th>Tipo de Semilla</th>
                        <th>Precio / Kg</th>
                        <th>Estado</th>
                        <th>Consulta</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in productos %}
                    <tr>
                        <td>{{ p.id }}</td>
                        <td><strong>{{ p.nombre }}</strong></td>
                        <td>📍 {{ p.region }}</td>
                        <td>{{ p.tipo }}</td>
                        <td>S/ {{ "%.2f"|format(p.precio) }}</td>
                        <td><span style="color: {{ 'green' if p.disponibilidad == 'Disponible' else 'orange' }}; font-weight: bold;">{{ p.disponibilidad }}</span></td>
                        <td><button class="btn-chat" onclick="abrirChat('{{ p.nombre }}', {{ p.precio }}, {{ loop.index0 }})">💬 Consultar</button></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div id="modalChat" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <span id="tituloProducto">Consulta de Producto</span>
                    <span class="cerrar-modal" onclick="cerrarChat()">&times;</span>
                </div>
                <div id="chatMsgs" class="chat-messages"></div>
                <div class="chat-input">
                    <input type="text" id="inputMsg" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter') enviarMensaje()">
                    <button onclick="enviarMensaje()">Enviar</button>
                </div>
            </div>
        </div>

        <script>
            const listaEspecialistas = {{ especialistas | tojson }};
            let productoActual = '';
            let precioActual = 0;
            let especialistaActual = '';

            function abrirChat(nombre, precio, index) {
                productoActual = nombre;
                precioActual = precio;
                especialistaActual = listaEspecialistas[index % listaEspecialistas.length];
                
                document.getElementById('tituloProducto').innerText = especialistaActual + ' (Especialista)';
                const msgs = document.getElementById('chatMsgs');
                msgs.innerHTML = `<div class="msg msg-bot">¡Hola! Soy <strong>${especialistaActual}</strong>, productor de <strong>${nombre}</strong>. ¿En qué te puedo ayudar hoy?</div>`;
                document.getElementById('modalChat').style.display = 'flex';
            }

            function cerrarChat() {
                document.getElementById('modalChat').style.display = 'none';
            }

            function enviarMensaje() {
                const input = document.getElementById('inputMsg');
                const texto = input.value.trim();
                if (!texto) return;

                const msgs = document.getElementById('chatMsgs');
                const divUser = document.createElement('div');
                divUser.className = 'msg msg-user';
                divUser.textContent = texto;
                msgs.appendChild(divUser);
                input.value = '';

                fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: texto, precio_unitario: precioActual, producto: productoActual, especialista: especialistaActual })
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
    return render_template_string(plantilla_html, categoria=nombre_cat, productos=categoria_productos, emoji=emoji_cat, especialistas=especialistas_cat)

# Motor con reglas ultra-claras
@app.route('/api/chat', methods=['POST'])
def api_chat():
    datos = request.json
    mensaje = datos.get('mensaje', '').lower()
    precio = datos.get('precio_unitario', 10.0)
    producto = datos.get('producto', 'Semilla')
    especialista = datos.get('especialista', 'Asesor')

    numeros = re.findall(r'\d+', mensaje)

    # 1. PREGUNTA SOBRE PESO / PESAN / KILO INDIVIDUAL (Resuelve "cuanto pesa" o "cuanto pesa cada uno")
    if any(k in mensaje for k in ["pesa", "peso", "pesan", "gramos", "cada uno", "unidad"]):
        return jsonify({"respuesta": f"Cada unidad o tubérculo/semilla de **{producto}** tiene un peso promedio individual de **150g a 300g** según el lote. Para la venta comercial, despachamos en paquetes por kilo (S/ {precio:.2f} el kg) o en sacos mayores."})

    # 2. PREGUNTAS SOBRE PRECIO Y COSTOS (Ej: "cuanto vale", "cuanto cuesta", "precio")
    elif any(k in mensaje for k in ["vale", "cuesta", "precio", "costo", "soles", "cuanto sale"]):
        if numeros:
            kilos = int(numeros[0])
            subtotal = kilos * precio
            envio = 0.0 if kilos >= 20 else 15.0
            total = subtotal + envio
            return jsonify({"respuesta": f"El kilo de **{producto}** está **S/ {precio:.2f}**.<br>Para **{kilos} kg**:<br>• Subtotal: S/ {subtotal:.2f}<br>• Envío: S/ {envio:.2f}<br>• **Total: S/ {total:.2f}**"})
        else:
            return jsonify({"respuesta": f"El precio de **{producto}** es de **S/ {precio:.2f} por kilo**. ¿Cuántos kilos deseas cotizar?"})

    # 3. COTIZACIÓN POR NÚMERO DIRECTO (Ej: "10" o "15 kg")
    elif numeros:
        kilos = int(numeros[0])
        subtotal = kilos * precio
        envio = 0.0 if kilos >= 20 else 15.0
        total = subtotal + envio
        return jsonify({"respuesta": f"Para un pedido de **{kilos} kg** de **{producto}**:<br>• Subtotal: S/ {subtotal:.2f}<br>• Envío: S/ {envio:.2f} {'(¡Envío gratis!)' if envio == 0 else ''}<br>• **Total estimado: S/ {total:.2f}**"})

    # 4. PRESENTACIONES / PRESENTACIÓN DE EMPAQUE
    elif any(k in mensaje for k in ["presentacion", "presentaciones", "saco", "sacos", "bolsa", "embalaje"]):
        return jsonify({"respuesta": f"Vendemos **{producto}** en sacos o bolsas selladas de **1 kg, 5 kg, 10 kg y 50 kg**."})

    # 5. TAMAÑO / FORMA / ASPECTO
    elif any(k in mensaje for k in ["tamaño", "tamano", "grande", "mediano", "pequeño", "pequeños", "grandes", "medianos"]):
        return jsonify({"respuesta": f"Los ejemplares de **{producto}** son de tamaño **mediano a grande**, seleccionados limpios a mano."})

    # 6. SALUDOS / ESTADO ÁNIMO
    elif any(k in mensaje for k in ["como estas", "cómo estás", "que tal", "qué tal"]):
        return jsonify({"respuesta": f"¡Hola! Todo excelente por aquí con los lotes de {producto}. ¿En qué te ayudo?"})

    elif any(k in mensaje for k in ["quien eres", "quién eres", "eres una ia", "quien habla"]):
        return jsonify({"respuesta": f"Soy {especialista}, agricultor de la red para el lote de {producto}."})

    elif any(k in mensaje for k in ["hola", "buenas", "saludos"]):
        return jsonify({"respuesta": f"¡Hola! Un gusto saludarte. Dime qué duda tienes sobre {producto}."})

    # 7. ENVÍOS Y TRANSPORTES
    elif any(k in mensaje for k in ["envio", "flete", "llegar", "transporte", "provincia", "agencia"]):
        return jsonify({"respuesta": f"Despachamos a todo el Perú por Shalom o Marvisur. El flete es de S/ 15.00 o **GRATIS** desde 20 kg."})

    # 8. DEFAULT NATURAL
    else:
        return jsonify({"respuesta": f"Respecto a tu consulta sobre **{producto}**: el lote está disponible a **S/ {precio:.2f} por kilo**. ¿Quieres cotizar kilos o preguntar por el envío?"})

if __name__ == "__main__":
    app.run(debug=True)
