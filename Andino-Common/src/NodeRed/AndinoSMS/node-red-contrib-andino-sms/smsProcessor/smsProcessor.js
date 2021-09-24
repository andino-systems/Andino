/*
Andino SMS Processor by Christian Drotleff @ Clear Szstems
 */

module.exports = function(RED) {
    "use strict";
	function smsProcessor(config) {
        RED.nodes.createNode(this,config);
		var node = this;
		node.context().set("test",1);
        node.on("input", function (msg) {
			node.process(msg, node);
        });
		
		node.process = function(msg, node){
            var number;
            var timestamp;
		    var myContext = node.context();
            
			number=myContext.get("number");
            timestamp=myContext.get("timestamp");
			
            if(number===undefined){
                number=null;
            }

            //Check if number and timestamp are not empty (if previous message was SMS header), returns msg
            if(number!==null){
                var newMsg = {
                    payload: {} 				
	    		};
	    		newMsg.number=number;
                newMsg.timestamp=timestamp;
                newMsg.payload=msg.payload.substring(0, msg.payload.length-1);
            
	    		myContext.set("number", null);
	    		myContext.set("timestamp", null);
        
                this.send(newMsg);
                return null;
            }

            //Check if message payload is SMS header message, saves number and timestamp in context
            if(msg.payload.startsWith("+CMGL:")){
                var payloadData = msg.payload.split(',');
                var newNumber=payloadData[2].substring(1, payloadData[2].length-2);
                var newTimestamp=(payloadData[4].substring(1) + " " + payloadData[5].substring(0, payloadData[5].length-6));
                myContext.set("number", newNumber);
                myContext.set("timestamp", newTimestamp);
            }
		
        return null;
	
	
	    };
		
    }
	
    
    RED.nodes.registerType("smsProcessor",smsProcessor);
}
