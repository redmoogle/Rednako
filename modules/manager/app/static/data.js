refresher = setInterval(refresh, 1000)

function capitalize(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function mapVars(out){
    out["vars"].map(
        variables => {
            toreplace = document.getElementById(variables[0])
            if(toreplace){
                toreplace.innerText = variables[1]
           }
           else {
                toreplace = document.getElementById(variables[0]+"_frmt")
                if(toreplace){
                    // Weird format
                    format = capitalize(variables[0])
                    if(format == "Uptime_str"){
                        format = "Uptime"
                    }
                    toreplace.innerText = format + ": " + variables[1]
                }
           }
        }
    )
    local = document.getElementById("local")
    if(local){
        local.innerText = "Local: " + out["local"]
    }
    remote = document.getElementById("remote")
    if(remote){
        remote.innerText = "Remote: " + out["remote"]
    }
    Object.keys(out["cogs"]).map(
        cog => {
            cogstuff = out["cogs"][cog]
            cogID = document.getElementById(cog)
            if(cogID){
                cogID.innerText = cog
            }
        }
    )

    out["shards"].map(
        shard => {
            toreplace = document.getElementById("shid"+shard[0])
            if(toreplace){
                toreplace.innerText = "Latency: " + shard[1].toFixed(2) + "ms"
            }
        }
    )
}

function refresh(){
    fetch('/data')
        .then(res => res.json())
        .then(out => mapVars(out))
}