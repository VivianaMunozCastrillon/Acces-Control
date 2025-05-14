document.addEventListener("DOMContentLoaded", function () {
    /* Declaración de la variable para la conexión WebSocket */
    let socket;

    /* Función para conectar al servidor WebSocket */
    function conectarWebSocket() {
        socket = new WebSocket("ws://172.20.3.119:3000");

        socket.onopen = function () {
            console.log("Conectado al servidor WebSocket");
            const wsStatus = document.getElementById("wsStatus");
            if (wsStatus) {
                wsStatus.textContent = "Conectado";
                wsStatus.style.color = "green";
            }
        };

        socket.onmessage = function (event) {
            const mensaje = event.data.toLowerCase();
            console.log("Mensaje recibido:", mensaje);

            const sensorD5 = document.getElementById("sensorD5");
            const sensorD6 = document.getElementById("sensorD6");
            const sensorD5Mensaje = document.getElementById("sensorD5Mensaje");
            const sensorD6Mensaje = document.getElementById("sensorD6Mensaje");

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
        }
     
      
        
            if (mensaje.includes("sensor d5 detecto un objeto")) {
                if (sensorD5) sensorD5.style.display = "block";
                if (sensorD5Mensaje) {
                    sensorD5Mensaje.textContent = "Movimiento detectado por el sensor D5";
                    sensorD5Mensaje.classList.remove("oculto");
                    sensorD5Mensaje.classList.add("alerta");
                }
            }
            
            if (mensaje.includes("sensor d5 sin deteccion")) {
                if (sensorD5) sensorD5.style.display = "none";
                if (sensorD5Mensaje) {
                    sensorD5Mensaje.textContent = "";
                    sensorD5Mensaje.classList.add("oculto");
                }
            }
        
            if (mensaje.includes("sensor d6 detecto un objeto")) {
                if (sensorD6) sensorD6.style.display = "block";
                if (sensorD6Mensaje) {
                    sensorD6Mensaje.textContent = "Movimiento detectado por el sensor D6";
                    sensorD6Mensaje.classList.remove("oculto");
                    sensorD6Mensaje.classList.add("alerta");
                }
            }
        
            if (mensaje.includes("sensor d6 sin deteccion")) {
                if (sensorD6) sensorD6.style.display = "none";
                if (sensorD6Mensaje) {
                    sensorD6Mensaje.textContent = "";
                    sensorD6Mensaje.classList.add("oculto");
                }
            }
            if (mensaje.startsWith("gpt_response:")) {
                const respuestaGPT = mensaje.slice("gpt_response:".length);
                const chatMessages = document.getElementById("chatMessages");
                if (chatMessages) {
                    chatMessages.innerHTML += `<p><strong>GPT:</strong> ${respuestaGPT}</p>`;
                    chatMessages.scrollTop = chatMessages.scrollHeight; // scroll automático
                }
            }
            
        };
        
        socket.onclose = function () {
            console.log("Desconectado, intentando reconectar...");
            const wsStatus = document.getElementById("wsStatus");
            if (wsStatus) {
                wsStatus.textContent = "Desconectado";
                wsStatus.style.color = "red";
            }
            setTimeout(conectarWebSocket, 3000);
        };

        socket.onerror = function (error) {
            console.error("Error en WebSocket:", error);
        };
    }

    conectarWebSocket();

    /* Función para enviar un mensaje al servidor WebSocket */
    window.enviarMensaje = function (mensaje) {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(mensaje);
            console.log("Mensaje enviado:", mensaje);
        } else {
            console.log("No se pudo enviar, WebSocket no está conectado.");
        }
    };

    /* Función para iniciar el reconocimiento facial */
    window.iniciarReconocimiento = function () {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                const video = document.getElementById("videoElement");
                if (video) {
                    video.srcObject = stream;
                    video.style.display = "block";
                    setTimeout(capturarImagen, 2000);
                }
            })
            .catch(function (error) {
                console.error("Error al acceder a la cámara:", error);
            });
    };

    /* Función para capturar una imagen del video */
    function capturarImagen() {
        const video = document.getElementById("videoElement");
        const canvas = document.getElementById("canvasElement");
        if (video && canvas) {
            const ctx = canvas.getContext("2d");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imagenBase64 = canvas.toDataURL("image/png");

            if (socket.readyState === WebSocket.OPEN) {
                socket.send(imagenBase64);
                console.log("Imagen enviada al servidor.");
            } else {
                console.log("No se pudo enviar la imagen, WebSocket no conectado.");
            }

            video.srcObject.getTracks().forEach(track => track.stop());
            video.style.display = "none";
        }
    }

    /* Función para mostrar u ocultar el chat */
    window.toggleChat = function () {
        let chatbox = document.getElementById("chatbox");
        if (chatbox) {
            chatbox.style.display = chatbox.style.display === "none" ? "block" : "none";
        }
    };

    /* Función para enviar mensajes al chat de GPT */
    window.enviarMensajeGPT = function () {
        let input = document.getElementById("chatInput");
        let mensaje = input?.value.trim();
        if (mensaje) {
            document.getElementById("chatMessages").innerHTML += `<p><strong>Tú:</strong> ${mensaje}</p>`;
            socket.send("gpt:" + mensaje);
            input.value = "";
        }
    };
});