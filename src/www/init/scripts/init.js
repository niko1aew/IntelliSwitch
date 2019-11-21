const settingsForm = document.getElementById('settingsForm');
const subminBtn=document.getElementById('btnSubmit');
const settingsBlock = document.querySelector('.settings');
const rebootBlock = document.querySelector('.reboot');

settingsForm.addEventListener('submit', function(e) {
    e.preventDefault();

    subminBtn.innerText='Saved. Rebooting...';
    settingsBlock.style.display = 'none';
    rebootBlock.style.display = 'block';

    const formData = new FormData(this);
    const searchParams = new URLSearchParams();

    for (const pair of formData) {
        searchParams.append(pair[0], pair[1]);
    }
    
    const serverUrl = 'http://'+device_ip+'/init_settings';
    fetch(serverUrl, {
        method: 'post',
        body: searchParams,
    }).then((res)=>{
        if (res.text==="accepted"){
            window.location.href = 'http://'+device_ip+'/reboot';
        }
    })
})