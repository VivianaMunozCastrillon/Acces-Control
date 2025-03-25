/* Declaración de la variable para la conexión WebSocket */
let socket;

/* Función para conectar al servidor WebSocket */
function conectarWebSocket() {
    socket = new WebSocket("ws://192.168.0.3:3000"); // Dirección del servidor WebSocket

    /* Evento que se ejecuta cuando la conexión se establece correctamente */
    socket.onopen = function() {
        console.log("Conectado al servidor WebSocket");
        document.getElementById("wsStatus").textContent = "Conectado";
        document.getElementById("wsStatus").style.color = "green";
    };

    /* Evento que se ejecuta cuando se recibe un mensaje del servidor */
    socket.onmessage = function(event) {
        const mensaje = event.data; // Almacena el mensaje recibido
        console.log("Mensaje recibido:", mensaje);
    
        /* Verifica el mensaje recibido y actualiza el estado del servo */
        if (mensaje === "1") {
            document.getElementById("servoStatus").textContent = "Servo Abierto";
            document.getElementById("servoStatus").style.color = "orange";
        } else if (mensaje === "0") {
            document.getElementById("servoStatus").textContent = "Servo Cerrado";
            document.getElementById("servoStatus").style.color = "red";
        } else if (mensaje.startsWith("gpt_response:")) {
            let response = mensaje.replace("gpt_response:", "");
            document.getElementById("chatMessages").innerHTML += `<p><strong>GPT:</strong> ${response}</p>`;
        } else if (mensaje.includes("Sensor D5") || mensaje.includes("Sensor D6")) {
            // Aquí se maneja el mensaje de los sensores
            document.getElementById("sensorStatus").textContent = mensaje;
            document.getElementById("sensorStatus").style.color = "orange";
        }
    };    

    /* Evento que se ejecuta cuando la conexión se cierra */
    socket.onclose = function() {
        console.log("Desconectado, intentando reconectar...");
        document.getElementById("wsStatus").textContent = "Desconectado";
        document.getElementById("wsStatus").style.color = "red";
        setTimeout(conectarWebSocket, 3000); // Intenta reconectar después de 3 segundos
    };

    /* Evento que se ejecuta cuando ocurre un error en la conexión */
    socket.onerror = function(error) {
        console.error("Error en WebSocket:", error);
    };
}

/* Llama a la función para conectar al WebSocket */
conectarWebSocket();

/* Función para enviar un mensaje al servidor WebSocket */
function enviarMensaje(mensaje) {
    if (socket.readyState === WebSocket.OPEN) { // Verifica si la conexión está abierta
        socket.send(mensaje);
        console.log("Mensaje enviado:", mensaje);
    } else {
        console.log("No se pudo enviar, WebSocket no está conectado.");
    }
}

/* Función para iniciar el reconocimiento facial */
function iniciarReconocimiento() {
    navigator.mediaDevices.getUserMedia({ video: true }) // Accede a la cámara
    .then(function(stream) {
        const video = document.getElementById("videoElement");
        video.srcObject = stream; // Muestra el video en la página
        video.style.display = "block";

        setTimeout(() => {
            capturarImagen(); // Captura la imagen después de 2 segundos
        }, 2000);
    })
    .catch(function(error) {
        console.error("Error al acceder a la cámara:", error);
    });
}

/* Función para capturar una imagen del video */
function capturarImagen() {
    const video = document.getElementById("videoElement");
    const canvas = document.getElementById("canvasElement");
    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth; // Ajusta el tamaño del canvas
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height); // Dibuja la imagen en el canvas

    const imagenBase64 = canvas.toDataURL("image/png"); // Convierte la imagen a base64

    if (socket.readyState === WebSocket.OPEN) { // Verifica si la conexión está abierta
        socket.send(imagenBase64); // Envía la imagen al servidor
        console.log("Imagen enviada al servidor.");
    } else {
        console.log("No se pudo enviar la imagen, WebSocket no conectado.");
    }

    video.srcObject.getTracks().forEach(track => track.stop()); // Apaga la cámara después de capturar
    video.style.display = "none";
}

/* Función para mostrar u ocultar el chat */
function toggleChat() {
    let chatbox = document.getElementById("chatbox");
    chatbox.style.display = chatbox.style.display === "none" ? "block" : "none";
}

/* Función para enviar mensajes al chat de GPT */
function enviarMensajeGPT() {
    let input = document.getElementById("chatInput");
    let mensaje = input.value.trim(); // Obtiene el mensaje y elimina espacios extra
    if (mensaje) {
        document.getElementById("chatMessages").innerHTML += `<p><strong>Tú:</strong> ${mensaje}</p>`;
        socket.send("gpt:" + mensaje); // Envía el mensaje al servidor
        input.value = ""; // Limpia el campo de texto
    }
}
