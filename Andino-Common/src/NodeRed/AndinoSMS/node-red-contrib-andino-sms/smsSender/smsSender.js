/*
Andino SMS Sender - by Christian Drotleff @ ClearSystems
 */

module.exports = function(RED) {
    "use strict";
    function smsSender(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        var timeout = null;
        var timeout2 = null;
        node.on("input", function (msg) {

            //set to text mode
            let newMsg1 = {
                payload: {}
            };
            newMsg1.payload="at+cmgf=1";
            node.send(newMsg1);

            //enter recipient number
            clearTimeout(timeout);
            timeout = setTimeout(function(){
                let newMsg2 = {
                    payload: {}
                };
                newMsg2.payload="at+cmgs=\"" + msg.number + "\"";
                node.send(newMsg2);
            }, 500);

            //enter message
            clearTimeout(timeout2);
            timeout2 = setTimeout(function(){
                let newMsg3 = {
                    payload: {}
                };
                let chr = String.fromCharCode(26);
                newMsg3.payload = msg.payload + chr;
                node.send(newMsg3);
            }, 1000);

        });

        node.on('close', function() {
            if (timeout) {
                clearTimeout(timeout);
            }
            if (timeout2) {
                clearTimeout(timeout2);
            }
            node.status({});
        });
    }

RED.nodes.registerType("smsSender",smsSender);
}
