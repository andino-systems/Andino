module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            checkSms(msg);
        });
		
        //set modem to text mode
		msg.payload="at+cmgf=1";
        this.send(msg);
        

        //send sms check message
        setTimeout(function(){
		    msg.payload="at+cmgl=\"REC UNREAD\"";
            this.send(msg);
            return null;
        }, 500);
    }
RED.nodes.registerType("smsChecker",smsChecker);
}
