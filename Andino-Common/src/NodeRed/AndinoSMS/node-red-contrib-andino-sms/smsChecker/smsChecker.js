module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        this.on("input", function (msg) {
            var node = this;
			textMode(node, msg);
			setTimeout(function(node, msg){
		    msg.payload="at+cmgl=\"REC UNREAD\"";
		    node.send(msg);
			}, 1000);
		    return null;
		});
    }
	
	function textMode(node, msg){
        msg.payload="at+cmgf=1";
        node.send(msg);
	}	
    
	
	
RED.nodes.registerType("smsChecker",smsChecker);
}
