/*
Andino SMS Checker - by Christian Drotleff @ Clear Systems
 */

module.exports = function(RED) {
    "use strict";
	function smsChecker(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        var timeout = null;
        this.on("input", function (msg) {
            //set to text mode
			let newMsg = {
				payload: {}
			};
			newMsg.payload="at+cmgf=1";
			node.send(newMsg);
			
			//send sms read request
			clearTimeout(timeout);
			timeout = setTimeout(function(){
				let newMsg1 = {
					payload: {}
				};
				newMsg1.payload="at+cmgl=\"REC UNREAD\"";
				node.send(newMsg1);
				return null;
			}, 500);



		});
    }

RED.nodes.registerType("smsChecker",smsChecker);
}
