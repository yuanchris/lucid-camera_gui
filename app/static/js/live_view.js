var image = document.getElementById('image');
var socket = io();
socket.on('connect', function() {
    console.log('connect');
    setInterval(function(){
        socket.emit('tracking', {data: 'tacked board website connected!'});
        // console.log('send tracking');
    }, 200);
    // console.log('send tracking')
});

socket.on('send_track', function(msg) {
    // console.log(msg);
    console.log(typeof msg);

    var arrayBuffer = msg;

    image.src = "data:image/jpeg;base64," + encode(new Uint8Array(arrayBuffer));    
});





// let ws = new WebSocket('ws://127.0.0.1:8061')
// ws.binaryType = 'arraybuffer';
// ws.onmessage = function (event) {
    
//     var arrayBuffer = event.data;
//     console.log(arrayBuffer)
//     console.log(typeof arrayBuffer)
//     image.src = "data:image/jpeg;base64," + encode(new Uint8Array(arrayBuffer));
// };


function encode (input) {
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;

    while (i < input.length) {
        chr1 = input[i++];
        chr2 = i < input.length ? input[i++] : Number.NaN; // Not sure if the index
        chr3 = i < input.length ? input[i++] : Number.NaN; // checks are needed here

        enc1 = chr1 >> 2;
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
        enc4 = chr3 & 63;

        if (isNaN(chr2)) {
            enc3 = enc4 = 64;
        } else if (isNaN(chr3)) {
            enc4 = 64;
        }
        output += keyStr.charAt(enc1) + keyStr.charAt(enc2) +
                  keyStr.charAt(enc3) + keyStr.charAt(enc4);
    }
    return output;
}