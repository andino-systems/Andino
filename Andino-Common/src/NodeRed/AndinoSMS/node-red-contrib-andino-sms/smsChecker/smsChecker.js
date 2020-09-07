module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            checkSms(msg);
        });
    }
	
	
    function checkSms(msg) {
	    //set modem to text mode
        setTimeout(function(){
		    //msg.payload="at+cmgf=1";
            this.send(msg);
        }, 500);

        //send sms check message
        msg.payload="at+cmgl=\"REC UNREAD\"";
        this.send(msg);
        return null;
    }
RED.nodes.registerType("smsChecker",smsChecker);
}
