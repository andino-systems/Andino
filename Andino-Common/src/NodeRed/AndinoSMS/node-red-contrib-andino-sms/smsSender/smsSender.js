function smsSender(config) {
    RED.nodes.createNode(this,config);
    // sms sender code
    var message = msg.payload;

    //changing modem to text mode
    msg.payload="at+cmgf=1";
    this.send(msg);
    await sleep(300);

    //entering recipient number
    msg.payload="at+cmgs=\"" + msg.number + "\"";
    this.send(msg);
    await sleep(300);

    //entering message
    var chr = String.fromCharCode(26);
    msg.payload = message + chr;
    this.send(msg);
}

//sleep function
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

RED.nodes.registerType("SMS Sender",smsSender);
