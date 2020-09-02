module.exports = function(RED) {
    "use strict";
    function smsChecker(config) {
	    RED.nodes.createNode(this,config);

        //set modem to text mode
        msg.payload="at+cmgf=1";
        this.send(msg);
        new Promise(resolve => setTimeout(resolve, 300));
    
        //send sms check message
        msg.payload="at+cmgl=\"REC UNREAD\"";
        this.send(msg);
    }
RED.nodes.registerType("smsChecker",smsChecker);
}
