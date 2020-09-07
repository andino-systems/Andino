module.exports = function(RED) {
    "use strict";
    function smsProcessor(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            process(msg);
        })
    }
	
	function process(msg){
	    var nodeContext = this.context();
        var number=nodeContext.get("number");
        var timestamp=nodeContext.get("timestamp");
		
		if(number===undefined){
            number=null;
        }
    
        //Check if number and timestamp are not empty (if previous message was SMS header), returns msg
        if(number!==null){
            msg.number=number;
            msg.timestamp=timestamp;
            msg.payload=msg.payload.substring(0, msg.payload.length-1);
        
            nodeContext.set("number", null);
            nodeContext.set("timestamp", null);
        
            this.send(msg);
            return null;
        }

        //Check if message payload is SMS header message, saves number and timestamp in context
        if(msg.payload.startsWith("+CMGL:")){
            var payloadData = msg.payload.split(',');
            number=payloadData[2].substring(1, payloadData[2].length-2);
            timestamp=(payloadData[4].substring(1) + " " + payloadData[5].substring(0, payloadData[5].length-6));
            nodeContext.set("number",number);
            nodeContext.set("timestamp",timestamp);
        }
        return null;
	
	
	}
    RED.nodes.registerType("smsProcessor",smsProcessor);
}
