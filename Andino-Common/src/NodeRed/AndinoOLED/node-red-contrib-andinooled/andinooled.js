
module.exports = function(RED) {
    "use strict";
	
	function AndinoOLEDNode(n) {
        RED.nodes.createNode(this,n);
        var node = this;
		
		node.dual = n.dual || "0";
		node.mode1 = n.mode1 || "10";
		node.mode2 = n.mode2 || "10";
        node.on("input", function (msg) {
            
			node.lines1 = msg.lines1;
			node.lines2 = msg.lines2;
			
			switch(node.dual) {
                case "1": process(node, true, node.mode1, node.mode2);break;
                case "0": process(node, false, node.mode1, node.mode2); break;
            }
        });
    }
	
	function process(node, dual, mode1, mode2) {

		var lines1 = node.lines1;
		var lines2 = node.lines2;
		var dl = "$#"
		
		//placeholder scrolling array (for later version)
		var scrolling1 = ["0", "0", "0", "0", "0", "0"];
		var scrolling2 = ["0", "0", "0", "0", "0", "0"];
		
		//add mode1 to output
		var output = mode1 + dl;
		
		//add mode2 to output
		if(dual){
			output = output + mode2 + dl;
		}else{
			output = output + "-1" + dl;
		}
		
		//add lines1 & scrolling1 to output
		for(let i = 0; i < 6; i++){
			output = output + lines1[i] + dl + scrolling1[i] + dl;
		}
		
		//add lines2 & scrolling2 to output
		for(let i = 0; i < 6; i++){
			output = output + lines2[i] + dl + scrolling2[i] + dl;
		}
		
		//create new Message object
		var newMsg = {
            payload: {} 
		};
		newMsg.payload = output.substring(0, (output.length-2));
		node.send(newMsg);
	}

    RED.nodes.registerType("AndinoOLED", AndinoOLEDNode);
}
