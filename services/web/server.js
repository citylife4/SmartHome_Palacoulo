'use strict';

const express = require('express');
const basicAuth = require('express-basic-auth')

var fs = require('fs');
var http = require('http');
var https = require('https');
var privateKey  = fs.readFileSync('/usr/src/.ssh/server.key', 'utf8');
var certificate = fs.readFileSync('/usr/src/.ssh/server.crt', 'utf8');

var credentials = {key: privateKey, cert: certificate};
var net = require('net');

const options = {
    cert: fs.readFileSync('/usr/src/.ssh/server.crt'),    
    key: fs.readFileSync('/usr/src/.ssh/server.key'),      

    //pfs: fs.readFileSync('./server/security-certificate/cert.p12'),   // didn't work

    //passphrase: 'secrete'
};

// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

// App
const app = express();
var path = require('path');

app.use(express.static(path.join(__dirname, "/public_html/assets")));

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

var server = https.createServer(options, app);

server.listen(PORT, () => {
  console.log("server starting on port : " + PORT)
});

console.log(`Running on http://${HOST}:${PORT}`);

// add a document to the DB collection recording the click event
app.post('/clicked', (req, res) => {

    var client = new net.Socket();
    client.connect(45321, '192.168.5.15', function() {
        console.log('Connected');
        client.write('ag_1_1_13_0');
    });

    client.on('data', function(data) {
        console.log('Received: ' + data);
        client.destroy(); // kill client after server's response
    });
});