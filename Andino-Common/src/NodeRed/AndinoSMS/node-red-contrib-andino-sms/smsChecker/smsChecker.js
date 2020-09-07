module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            checkSms(msg);
        });
    }
	
	
    function checkSms(msg) {
	    RED.nodes.createNode(this,config);

        //set modem to text mode
        setTimeout(function(){
		    msg.payload="at+cmgf=1";
            node.send(msg);
        }, 500);

        //send sms check message
        msg.payload="at+cmgl=\"REC UNREAD\"";
        node.send(msg);
        return null;
    }
RED.nodes.registerType("smsChecker",smsChecker);
}
