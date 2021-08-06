

async function get_all(data){
    const gain = document.querySelector('#gain');
    const exposure_time= document.querySelector('#exposure_time');
    const exposure_time_max = document.querySelector('#exposure_time_max');
    const fps_value = document.querySelector('#fps_value');
    
    gain.value = data.gain;
    exposure_time.value = data.exposure_time.toFixed(1);
    exposure_time_max.innerHTML = `min = ${data.exposure_time_min.toFixed(1)}, max = ${data.exposure_time_max.toFixed(1)}`;
    fps_value.innerHTML = data.fps.toFixed(2);
}


// control camera
async function start() {
    const show_server = document.querySelector('#show_server');
    const show_preview = document.querySelector('#show_preview');
    const show_para = document.querySelector('#show_parameters');
    show_preview.innerHTML = 'status:'
    show_para.innerHTML = 'status:'
    const message = await fetch('start_camera', {
        method: 'GET',
    }).then((res => res.json()))  
    console.log(message);

    if (message.error){
        show_server.innerHTML = 'status: start-' + message.error;
    } else {

        console.log('start camera');
        show_server.innerHTML = 'status: start camera';
        get_all(message.data)
    }
}
async function stop() {
    const show_server = document.querySelector('#show_server');
    const show_preview = document.querySelector('#show_preview');
    const show_para = document.querySelector('#show_parameters');
    show_preview.innerHTML = 'status:'
    show_para.innerHTML = 'status:'
    const message = await fetch('stop_camera', {
        method: 'GET',
    }).then((res => res.json()))  
    console.log(message);
    if (message.error){
        show_server.innerHTML = 'status: stop-' + message.error;
    } else {
        console.log('stopped camera');
        show_server.innerHTML = 'status: stopped camera';
    }
}
// control preview
async function start_preview() {
    // const show_server = document.querySelector('#show_server');
    // const show_preview = document.querySelector('#show_preview');
    // const show_para = document.querySelector('#show_parameters');
    // show_server.innerHTML = 'status:'
    // show_para.innerHTML = 'status:'
    // const message = await fetch('start_preview', {
    //     method: 'GET',
    // }).then((res => res.json()))  
    // console.log(message);

    window.open("view.html", "LiveView", "height=700,width=1200");
    // if (message.error){
    //     show_preview.innerHTML = 'status:' + message.error;
    // } else {
    //     console.log('started preview ');
    //     show_preview.innerHTML = 'status: started preview ';
    //     get_all(message.data)
    // }
    

}


async function submit_change() {
    const show_server = document.querySelector('#show_server');
    const show_preview = document.querySelector('#show_preview');
    const show_para = document.querySelector('#show_parameters');
    show_server.innerHTML = 'status:'
    show_preview.innerHTML = 'status:'



    const camera_width = document.querySelector('#camera_width');
    const camera_height = document.querySelector('#camera_height');
    const gain = document.querySelector('#gain');
    const exposure_time = document.querySelector('#exposure_time');
    const data = {'camera_width':camera_width.value, 'camera_height':camera_height.value,
                    'gain':gain.value, 'exposure_time': exposure_time.value};

    console.log(data)
    const message = await fetch('submit_change', {
        method: 'POST',
        body: JSON.stringify(data), // data can be `string` or {object}
        headers: {
            'Content-Type': 'application/json'
          }, 
    }).then((res => res.json()))  
    console.log(message)
    if (message.error){
        show_para.innerHTML = 'status:' + message.error;
    } else {
        show_para.innerHTML = 'status: modified successfully';
    }
}

async function to_default() {
    const show_server = document.querySelector('#show_server');
    const show_preview = document.querySelector('#show_preview');
    const show_para = document.querySelector('#show_parameters');
    show_server.innerHTML = 'status:'
    show_preview.innerHTML = 'status:'
    const camera_width = document.querySelector('#camera_width');
    const camera_height = document.querySelector('#camera_height');
    const gain = document.querySelector('#gain');
    const exposure_time = document.querySelector('#exposure_time');

    camera_width.value = 4096
    camera_height.value = 2160
    gain.value = 0.0
    
    show_para.innerHTML = 'status: set to default';

}

async function change(){
    const show_para = document.querySelector('#show_parameters');
    show_para.innerHTML = 'status:';
}