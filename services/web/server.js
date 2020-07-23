'use strict';

const express = require('express');
var net = require('net');

// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

// App
const app = express();
app.get('/', (req, res) => {
  res.send('Hello World');
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

function send_ping() {
    var client = new net.Socket();
    client.connect(45321, '192.168.5.15', function() {
        console.log('Connected');
        client.write('ag_1_1_13_0');
    });

    client.on('data', function(data) {
        console.log('Received: ' + data);
        client.destroy(); // kill client after server's response
    });
}