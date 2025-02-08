// Connexion à l'endpoint SSE
const script = 'une vidéo a propos de la vie des chats';
const evtSource = new EventSource(`/api/generate?prompt=${encodeURIComponent(script)}`);

evtSource.onmessage = function(event) {
    const outputDiv = document.getElementById('output');
    const data = event.data.toString();
    
    if (data.startsWith('[LOG] ')){
        outputDiv.innerHTML += '<span style="color: blue;">' + data.substring(6) + '</span><br>';
    } else if (data.startsWith('[FILE] ')){
        path = data.substring(7);
        outputDiv.innerHTML += '<a href="' + path + '" download>Download file</a><br>';
    }
    console.log(data);
};

evtSource.onerror = function(err) {
    console.error('Erreur SSE:', err);
    evtSource.close();
};
