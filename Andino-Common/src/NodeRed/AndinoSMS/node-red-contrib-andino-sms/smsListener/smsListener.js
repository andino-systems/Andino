module.exports = function(RED) {
    "use strict";
    function smsListener(config) {
        RED.nodes.createNode(this,config);
    
        //check if message is new sms indicator
        if(msg.payload.startsWith("+CMTI:")){
            this.send msg;
        }else{
           return null;
        }
    }
RED.nodes.registerType("smsListener",smsListener);
}
