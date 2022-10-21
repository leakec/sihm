//const http = require('http')
//const fs = require('fs')
//
//const host = 'localhost';
//const port = 8000;
//
//const server = http.createServer((req, res) => {
//  res.writeHead(200, { 'content-type': 'text/html' })
//  fs.createReadStream('test.html').pipe(res)
//})
//
//server.listen(port, host, () => {
//    console.log(`Server is running on http://${host}:${port}`);
//});
//

const express = require('express')
const app = express()
const path = require('path')

app.use(express.static(__dirname + '/public'))
app.use('/build/', express.static(path.join(__dirname, 'node_modules/three/build')));
app.use('/jsm/', express.static(path.join(__dirname, 'node_modules/three/examples/jsm')));

app.listen(3000, () =>
  console.log('Visit http://127.0.0.1:3000')
);
