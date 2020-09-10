module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            //set to text mode
			var node = this;
			textMode(node, msg);
			
			//send sms read request
			var newMsg1 = {
                    payload: {} 
			    };
            newMsg1.payload="at+cmgl=\"REC UNREAD\"";
		    node.send(newMsg1);
		    return null;
		});
    }
	
	function textMode(node, msg){
        var newMsg = {
            payload: {} 
		};
		newMsg.payload="at+cmgf=1";
        node.send(newMsg);
	}	
    
	
	
RED.nodes.registerType("smsChecker",smsChecker);
}
