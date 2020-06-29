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

var privateKey = fs.readFileSync('/etc/letsencrypt/live/procorecalendarintegrator.com/privkey.pem', 'utf-8');
var cert = fs.readFileSync('/etc/letsencrypt/live/procorecalendarintegrator.com/cert.pem', 'utf-8');
var ca = fs.readFileSync('/etc/letsencrypt/live/procorecalendarintegrator.com/chain.pem', 'utf-8');
var creds = {
    key: privateKey, 
    cert: cert,
    ca: ca
};

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
httpsServer.listen(443);
console.log('Running on PORT 443');
// app.listen(process.env.PORT || 3000, () => console.log(`Running on PORT ${process.env.PORT || 3000}`));
// Redirect from http port to https

http.createServer(function (req, res) {
    res.redirect('https://' + req.headers.host + req.url);
}).listen(80);
