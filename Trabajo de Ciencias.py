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
            header { background: #2e7d32; color: white; padding: 25px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
            h1 { margin: 0; font-size: 2.2em; }
            p.subtitulo { margin-top: 5px; font-size: 1.1em; opacity: 0.9; }
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

            .fuentes-seccion { background: #ffffff; border: 1px solid #c8e6c9; border-radius: 12px; padding: 20px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.03); margin-bottom: 30px; }
            .fuentes-seccion h4 { color: #1b5e20; margin-top: 0; margin-bottom: 10px; font-size: 1.1em; }
            .fuentes-list { margin: 0; padding-left: 20px; color: #555; font-size: 0.9em; line-height: 1.6; }
        </style>
    </head>
    <body>
        <header>
            <h1>Plataforma Semillas Conectadas 🌱</h1>
            <p class="subtitulo">Conectando Pequeños Agricultores Directamente con el Mercado</p>
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

            <div class="fuentes-seccion">
                <h4>📚 Fuentes Bibliográficas y Científicas de Información</h4>
                <ul class="fuentes-list">
                    <li><strong>Wikipedia (Enciclopedia Libre):</strong> Datos sobre la taxonomía, origen geográfico y características botánicas generales de las especies agrícolas.</li>
                    <li><strong>INIA (Instituto Nacional de Innovación Agraria del Perú):</strong> Información técnica sobre la adaptabilidad de cultivos nativos y conservación de semillas criollas.</li>
                    <li><strong>CIP (Centro Internacional de la Papa):</strong> Investigaciones sobre la diversidad genética y la agrobiodiversidad de las papas nativas e insumos andinos.</li>
                </ul>
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
                    <input type="text" id="inputMsg" placeholder="Escribe tu consulta o cantidad (ej. 15 kg)..." onkeypress="if(event.key==='Enter') enviarMensaje()">
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
                
                document.getElementById('tituloProducto').innerText = especialistaActual + ' (Asesor IA)';
                const msgs = document.getElementById('chatMsgs');
                msgs.innerHTML = `<div class="msg msg-bot">¡Hola! Soy <strong>${especialistaActual}</strong>, especialista en <strong>${nombre}</strong>.<br>El precio base es de <strong>S/ ${precio.toFixed(2)} / kg</strong>.<br>¿En qué puedo ayudarte hoy? Puedes pedirme cotización por kilos, consultar sobre envíos, garantía o calidad.</div>`;
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

# Motor de IA contextualizado con variaciones dinámicas
@app.route('/api/chat', methods=['POST'])
def api_chat():
    datos = request.json
    mensaje = datos.get('mensaje', '').lower()
    precio = datos.get('precio_unitario', 10.0)
    producto = datos.get('producto', 'Semilla')
    especialista = datos.get('especialista', 'Asesor')

    numeros = re.findall(r'\d+', mensaje)

    # 1. Cotización si ingresa kilos o un número
    if numeros:
        kilos = int(numeros[0])
        subtotal = kilos * precio
        envio = 0.0 if kilos >= 20 else 15.0
        total = subtotal + envio
        
        respuestas_cotizacion = [
            f"Perfecto. Para un pedido de <strong>{kilos} kg</strong> de {producto}:<br>"
            f"• Subtotal: S/ {subtotal:.2f}<br>"
            f"• Flete/Envío: S/ {envio:.2f} {'(¡Envío gratis por pedir +20 kg!)' if envio == 0 else ''}<br>"
            f"• <strong>Monto Final: S/ {total:.2f}</strong><br>"
            f"¿Te gustaría proceder a coordinar el despacho?",
            
            f"Excelente elección. Elaborando la cotización para <strong>{kilos} kg</strong>:<br>"
            f"• Precio por kg: S/ {precio:.2f}<br>"
            f"• Costo total de semillas: S/ {subtotal:.2f}<br>"
            f"• Cargo de envío: S/ {envio:.2f}<br>"
            f"• <strong>Total estimado: S/ {total:.2f}</strong><br>"
            f"Quedo atento a tus indicaciones para reservar este lote.",

            f"Entendido. Un lote de <strong>{kilos} kg</strong> de {producto} suma:<br>"
            f"• Subtotal: S/ {subtotal:.2f}<br>"
            f"• Transporte regional: S/ {envio:.2f}<br>"
            f"• <strong>Total a pagar: S/ {total:.2f}</strong><br>"
            f"¿A qué provincia o distrito requerirías el envío?"
        ]
        return jsonify({"respuesta": random.choice(respuestas_cotizacion)})

    # 2. Consultas sobre envíos o transporte
    elif any(k in mensaje for k in ["envio", "flete", "llegar", "transporte", "provincia", "donde"]):
        respuestas_envio = [
            f"Realizamos despachos directos desde el campo a cualquier provincia del Perú. El envío demora entre 24 y 48 horas. Cuesta S/ 15.00, pero si pides a partir de 20 kg el flete es <strong>totalmente gratis</strong>.",
            f"Coordinamos con agencias de transporte a nivel nacional (Shalom, Marvisur, Olva). El tiempo promedio de entrega es de 1 a 2 días hábiles según la región.",
            f"Hacemos envíos directos a todas las regiones del país. Recuerda que para compras de 20 kg a más el envío no tiene costo adicional."
        ]
        return jsonify({"respuesta": random.choice(respuestas_envio)})

    # 3. Saludos
    elif any(k in mensaje for k in ["hola", "buenas", "que tal", "saludos", "inicio"]):
        respuestas_saludo = [
            f"¡Hola! Saludos. Soy {especialista}. ¿En qué te puedo asesorar respecto al cultivo o pedido de {producto}?",
            f"¡Buenas! Un gusto saludarte. Quedo a tu disposición para brindarte detalles sobre el rendimiento o cotizaciones de {producto}.",
            f"¡Hola! Qué gusto saludarte. ¿Deseas cotizar alguna cantidad específica o tienes consultas sobre la germinación de este lote?"
        ]
        return jsonify({"respuesta": random.choice(respuestas_saludo)})

    # 4. Consultas sobre garantía, germinación o calidad
    elif any(k in mensaje for k in ["calidad", "garantia", "germinacion", "rendimiento", "bueno", "nativa", "original"]):
        respuestas_calidad = [
            f"Nuestras semillas de {producto} tienen una tasa de germinación superior al 88%. Son cosechadas de manera artesanal y libre de transgénicos.",
            f"Garantizamos un origen 100% nativo y libre de intermediarios. Cada lote cuenta con registro de origen y alto rendimiento por hectárea.",
            f"Todas las variedades pasan por selección manual. Te garantizamos la máxima frescura y pureza genética en este lote."
        ]
        return jsonify({"respuesta": random.choice(respuestas_calidad)})

    # 5. Métodos de pago o descuentos
    elif any(k in mensaje for k in ["pago", "descuento", "precio", "yape", "tarjeta", "efectivo"]):
        respuestas_pago = [
            f"Aceptamos transferencias bancarias, Yape, Plin y pagos contra entrega coordinados con la agencia. Para compras mayores a 50 kg ofrecemos un 5% de descuento adicional.",
            f"El precio base es de S/ {precio:.2f} por kg. Puedes pagar directamente vía Yape/Plin o transferencia. Si compras por volumen podemos aplicar una tarifa mayorista.",
            f"Manejamos precios de comercio justo directo. Puedes cancelar por medio de transferencia electrónica o billeteras digitales."
        ]
        return jsonify({"respuesta": random.choice(respuestas_pago)})

    # 6. Respuesta general / fallback aleatorio si no reconoce
    else:
        respuestas_general = [
            f"Entiendo tu consulta sobre <strong>{producto}</strong>. Para darte el presupuesto exacto con transporte, ¿cuántos kilos calculas que vas a necesitar?",
            f"Gracias por escribir. Si tienes dudas sobre el rendimiento de {producto} o deseas calcular el total de tu pedido, indícame la cantidad en kilos.",
            f"Con gusto te brindo asistencia. ¿Deseas conocer la disponibilidad de stock o cotizar un lote de {producto}?"
        ]
        return jsonify({"respuesta": random.choice(respuestas_general)})

if __name__ == "__main__":
    app.run(debug=True)
