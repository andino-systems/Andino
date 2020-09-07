module.exports = function(RED) {
    "use strict";
    function smsSender(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            sendSms(msg);
        });
    }
	
	function sendSms(msg) {
        // sms sender code
        var message = msg.payload;
    
        //changing modem to text mode
        setTimeout(function(){
		    msg.payload="at+cmgf=1";
            this.send(msg);
        }, 500);
    
        //entering recipient number
        setTimeout(function(){
		    msg.payload="at+cmgs=\"" + msg.number + "\"";
            this.send(msg);
        }, 500);
    
        //entering message
        setTimeout(function(){
		    var chr = String.fromCharCode(26);
            msg.payload = message + chr;
			this.send(msg);
        }, 500);
		
		return null;
    }


RED.nodes.registerType("smsSender",smsSender);
}
