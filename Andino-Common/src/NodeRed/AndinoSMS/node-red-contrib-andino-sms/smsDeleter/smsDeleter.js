module.exports = function(RED) {
    "use strict";
    function smsListener(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            for (i = 1; i < 26; i++) {
				var newMsg = {
                    payload: {} 				
	    		};
				newMsg.payload = "AT+CMGD=" + i;
				this.send(newMsg);
			}
        });
        
    }
	
RED.nodes.registerType("smsDeleter",smsDeleter);
}
