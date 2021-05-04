refresher = setInterval(refresh, 1000)

// Captializes first letter in given string
function capitalize(string) { return string.charAt(0).toUpperCase() + string.slice(1); }

// I do this a whole lot so I just grab the element in the code
// The return is used if you want to do some extra work afterwards
function modify(id, newtext) {
    element = document.getElementById(id);
    if(element) { element.innerHTML = newtext; return true; }
    return false;
}

function mapVars(out){
    // Couldn't figure out how to do this in refresh but w/e
    // This maps each variable in the json to IDs in the html
    out["vars"].map( variable => {
            // extra check to see if we want a formatted version
            if(!modify(variable[0], variable[1])) {
                formatted = variable[0]+"_frmt";
                formattext = capitalize(variable[0]);
                // Kinda weird but in my code uptime is taken with how long it's been up for
                if(formattext == "Uptime_str") { formattext = "Uptime"; }
                
                // VARNAME: VARVALUE
                formattext += ": " + variable[1]
                modify(formatted, formattext)
    }})
    modify("local", ("Local: " + out["local"]))
    modify("remote", ("Remote: " + out["remote"]))

    out["shards"].map( shard => {
            modify(("shid"+shard[0]), ("Latency: " + shard[1].toFixed(2) + "ms"))
    })
}

function refresh(){
    fetch('/data')
        .then(res => res.json())
        .then(out => mapVars(out))
}