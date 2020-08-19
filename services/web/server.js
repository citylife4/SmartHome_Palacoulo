'use strict';

const express = require('express');
const basicAuth = require('express-basic-auth')

var fs = require('fs');
var http = require('http');
var https = require('https');

var net = require('net');

const options = {
    cert: fs.readFileSync('/usr/src/.ssh/server.crt'),    
    key: fs.readFileSync('/usr/src/.ssh/server.key'),      
};

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

// App
const app = express();
var path = require('path');

app.use(express.static(path.join(__dirname, "/public_html/assets")));
app.use(express.static(path.join(__dirname, "/public_html/css")));

app.use(basicAuth({
    users: { 'admin': 'supersecret' },
    challenge: true,
}))

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/public_html/index.html'));
});

app.get('/json_data/data.json', function(req, res) {
    res.sendFile(path.join(__dirname + '/public_html/json_data/data.json'));
});

//var server = https.createServer(options, app);
var server = https.createServer(options,app);

server.listen(PORT, () => {
  console.log("server starting on port : " + PORT)
});

console.log(`Running on http://${HOST}:${PORT}`);

// add a document to the DB collection recording the click event
app.post('/clicked', (req, res) => {

    var client = new net.Socket();
    client.connect(45321, 'localhost', function() {
        console.log('Connected');
        client.write('ag_1_1_13_0');
    });

    client.on('data', function(data) {
        console.log('Received: ' + data);
        client.destroy(); // kill client after server's response
    });
});
