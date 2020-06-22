const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const fs = require('fs');
const http = require('http');
const https = require('https');

const proxy = require('http-proxy').createProxyServer({
    host: 'http://api:5000'
});

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));

var privateKey = fs.readFileSync('secrets/node-selfsigned.key', 'utf-8');
var cert = fs.readFileSync('secrets/node-selfsigned.crt', 'utf-8');
var creds = {key: privateKey, cert: cert};

app.use(express.static(path.join(__dirname, 'build')));

app.use('/api', function(req, res, next) {
    proxy.web(req, res, {
        target: 'http://api:5000'
    }, next);
});

app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

var httpsServer = https.createServer(creds, app)
httpsServer.listen(3000);
console.log('Running on PORT 3000');
// app.listen(process.env.PORT || 3000, () => console.log(`Running on PORT ${process.env.PORT || 3000}`));