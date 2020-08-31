function smsProcessor(config) {
    RED.nodes.createNode(this,config);
    var number=context.get("number");
    var timestamp=context.get("timestamp")

    if(number===undefined){
        number=null;
    }

    //Check if number and timestamp are not empty (if previous message was SMS header), returns msg
    if(number!==null){
        msg.number=number;
        msg.timestamp=timestamp;
        msg.payload=msg.payload.substring(0, msg.payload.length-1);
    
        context.set("number", null);
        context.set("timestamp", null);
    
        this.send(msg);
        return null;
    }

    //Check if message payload is SMS header message, saves number and timestamp in context
    if(msg.payload.startsWith("+CMGL:")){
        var payloadData = msg.payload.split(',');
        number=payloadData[2].substring(1, payloadData[2].length-2);
        timestamp=(payloadData[4].substring(1) + " " + payloadData[5].substring(0, payloadData[5].length-6));
        context.set("number",number);
        context.set("timestamp",timestamp);
    }
    return null;

}

RED.nodes.registerType("SMS Processor",smsProcessor);
