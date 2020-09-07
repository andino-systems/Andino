module.exports = function(RED) {
    "use strict";
    function smsListener(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            //check if message is new sms indicator
            if(msg.payload.startsWith("+CMTI:")){
                this.send msg;
				return null;
            }else{
               return null;
            }
        });
        
    }
	
RED.nodes.registerType("smsListener",smsListener);
}
