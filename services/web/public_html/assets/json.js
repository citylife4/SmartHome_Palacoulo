function loadJSON(callback) {

    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', 'json_data/data.json', true);
    xobj.onreadystatechange = function() {
        if (xobj.readyState == 4 && xobj.status == "200") {

            // .open will NOT return a value but simply returns undefined in async mode so use a callback
            callback(xobj.responseText);

        }
    }
    xobj.send(null);

}

// Call to function with anonymous callback
loadJSON(function(response) {
    // Do Something with the response e.g.
    jsonresponse = JSON.parse(response);
    var i, len, text;
    mlen = jsonresponse.GPIOS.length-1;
    // Assuming json data is wrapped in square brackets as Drew suggests
    for ( len = mlen, text="" ; len >= 0; len--) { 
        text +=
        jsonresponse.GPIOS[len].data + " " + jsonresponse.GPIOS[len].value + "<br>";;
    }
    if (  jsonresponse.GPIOS[mlen].value == 1 ){
        document.getElementById("opened").innerHTML = "Garagem está Fechada"
    } else {
        document.getElementById("opened").innerHTML = "Garagem está Aberta"
    }
    document.getElementById("id01").innerHTML = text
});