const fs = require("fs");
const line = require('@line/bot-sdk');
const express = require('express');
const yaml = require('js-yaml');
const cred = yaml.safeLoad(fs.readFileSync('../ref/credential.yml', 'utf8'));


//Create LINE SDK config
const config = {
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.CHANNEL_SECRET,
};

//Create LINE SDK client
const client = new line.Client(config);

//Create Express app
const app = express();

//Register a webhook handler with middleware
app.post('/callback', line.middleware(config), (req, res) => {
  Promise
    .all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

//Event handler
function handleEvent(event) {

  console.log(JSON.stringify(event));

  // if (event.type !== 'message' || event.message.type !== 'text') {
  //   // ignore non-text-message event
  //   return Promise.resolve(null);
  // }

  //Create a echoing text message
  const echo = { type: 'text', text: JSON.stringify(event) };
  // const echo = { type: 'text', text: event.message.text };

  //Use reply API
  return client.replyMessage(event.replyToken, echo);
}

//Listen on port
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`listening on ${port}`);
});


// const message = {
//   type: 'text',
//   text: 'Hello World!'
// };

// client.pushMessage('3.230.17.215', message)
//   .then(() => {
//     console.log('successful');
//   })
//   .catch((err) => {
//     console.error(err);
//   });
