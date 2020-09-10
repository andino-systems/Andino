module.exports = function(RED) {
    "use strict";
    function smsSender(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
			var message = msg.payload;
			var newMsg1 = {
                payload: {} 
			};

			//set to text mode
			newMsg1.payload="at+cmgf=1";
            this.send(newMsg1);
			
		    //entering recipient number
			var newMsg2 = {
                    payload: {} 
			    };
			    newMsg2.payload="at+cmgs=\"" + msg.number + "\"";
			    this.send(newMsg2);
            
		
            //entering message
            var newMsg3 = {
                    payload: {} 
			    };
			    var chr = String.fromCharCode(26);
                newMsg3.payload = message + chr;
		        this.send(newMsg3);

		    return null;
        });
    }

RED.nodes.registerType("smsSender",smsSender);
}
