//Node-Red Andino X1 Node - by Christian Drotleff @ ClearSystems GmbH, 2022

module.exports = function(RED) {
    "use strict";
    var valueContext = null;
	function AndinoX1Node(n) {
        RED.nodes.createNode(this,n);
        this.filter = n.filter || "events";
		this.chng = n.chng || "0";
        var node = this;
		valueContext = node.context();
		valueContext.set("counter", null);
		valueContext.set("states", null);
		valueContext.set("relaystates", null);
        this.on("input", function (msg) {
			switch(node.filter ) {
                case "events": doEvents(node, msg, );break;
                case "relay1": doRelais(node, msg, 1); break;
                case "relay2": doRelais(node, msg, 2); break;
				case "relay3": doRelais(node, msg, 3); break;
				case "temps": doTemps(node, msg); break;
            }
        });
    }

	//function for checking and processing event messages
    function doEvents(node, msg) {

        if(msg.payload.charAt(0)!=':'){
			return;
		}
		
		var p = msg.payload.split('{');

		if((p.length != 3) && (p.length != 4)){
			return;
		}

		var counter = p[1].replace('}','').split(',');
		var states  = p[2].replace('}','').split(',');

        var newMsg = {
            payload: {} };
		
		//pin counters
		var i = 1;
		counter.forEach( function(c) {
			if((valueContext.get("counter")!=null)&&((node.chng == "1")&&(valueContext.get("counter")[i-1] == c))){	
			}else{
				newMsg.payload["Counter"+i] = parseInt("0x"+c);	
			}
			i++;
		});

		//pin states
		i = 1;
		states.forEach( function(p) {
			if((valueContext.get("states")!=null)&&((node.chng == "1")&&(valueContext.get("states")[i-1] == p))){
			}else{
				newMsg.payload["Pin"+i] = parseInt("0x"+p);
			}
			i++;
    	});
   
		//relay states
		if(p.length == 4){
			var relaystates  = p[3].replace('}','').split(',');
			i = 1;
			relaystates.forEach( function(q) {
				if((valueContext.get("relaystates")!=null)&&((node.chng == "1")&&(valueContext.get("relaystates")[i-1] == q))){
				}else{
					newMsg.payload["RelayState"+i] = parseInt("0x"+q);
				}
				i++;
			});
			valueContext.set("relaystates", relaystates);
		}
		
		valueContext.set("counter", counter);
		valueContext.set("states", states);

		
		if(Object.keys(newMsg.payload).length != 0){
			node.send(newMsg);
		}
	}

    //function for converting boolean/int/Strings to relay control signal
	function doRelais(node, msg, relais) {
        var state = toBoolean(msg.payload);
        if (state == null)
            return;
        var newMsg =
        {
            payload: "REL" + relais + " " + ((state) ? "1" : "0") + "\r\n"
        }
        node.send(newMsg);
    }
	
	//function for checking temperature sensor messages
	function doTemps(node, msg) {
		
		var newMsg = {
            payload: {} };
		
		//check if message is temperature message, supports both old and new temperature message format (either !0000... or :0000@T...)
		if((msg.payload.charAt(0)!='!')&&(msg.payload.charAt(6)!='T')){
			return;
		}
		
		var qq = msg.payload.split('{');
		
		if(qq.length != 3){
			return;
		}
		
		//modify and split up the message
		var busnr = parseInt(qq[1]);
		var temps = qq[2].replace('}','').split(',');
		
		newMsg.payload["BusNr"] = busnr;
		var j = 0;
		temps.forEach( function(t) {
			newMsg.payload["Temperature"+j] = parseFloat(t);
			j++;
		});
		
		node.send(newMsg);
	}

    function toBoolean(source){
        if (typeof(source) == "boolean") {
            return source;
        }
        if (typeof(source) == "string") {
            switch (source.toLowerCase().trim()) {
            case "true":
            case "yes":
            case "1":
                return true;
            case "false":
            case "no":
            case "0":
                return false;
            default:
                return null;
            }
        }
        return null;
    }

    RED.nodes.registerType("AndinoX1", AndinoX1Node);
}
