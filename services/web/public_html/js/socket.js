var net = require('net');

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