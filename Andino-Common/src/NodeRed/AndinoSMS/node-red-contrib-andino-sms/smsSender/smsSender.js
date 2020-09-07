module.exports = function(RED) {
    "use strict";
    function smsSender(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
			var message = msg.payload;
			//set to text mode
			msg.payload="at+cmgf=1";
            this.send(msg);
			
		    //entering recipient number
            setTimeout(function(){
			    msg.payload="at+cmgs=\"" + msg.number + "\"";
			    this.send(msg);
            }, 20);
            
		
            //entering message
            setTimeout(function(){
			    var chr = String.fromCharCode(26);
                msg.payload = message + chr;
		        this.send(msg);
            }, 20);
		    
		
		    return null;
        });
    }
	
	function sendSms(msg) {
        // sms sender code
        /*
		var message = msg.payload;
        
        //changing modem to text mode
        setTimeout(function(){
        }, 500);
		msg.payload="at+cmgf=1";
        this.send(msg);
    
        //entering recipient number
        setTimeout(function(){
        }, 500);
        msg.payload="at+cmgs=\"" + msg.number + "\"";
        this.send(msg);
		
        //entering message
        setTimeout(function(){
        }, 500);
		var chr = String.fromCharCode(26);
        msg.payload = message + chr;
		this.send(msg);
		
		return null;
		*/
    }


RED.nodes.registerType("smsSender",smsSender);
}
