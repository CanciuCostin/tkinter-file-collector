let multer  = require('multer');
let express = require('express');
let app     = express();
let upload  = multer({ storage: multer.memoryStorage() });

app.post('/upload', upload.single('fileupload'), (req, res) => {
  console.log(req.body);
  console.log(req.file);

  res.send();
});

app.listen(8080);