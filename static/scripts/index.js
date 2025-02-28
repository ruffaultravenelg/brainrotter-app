const generateBtn = document.getElementById('generateBtn');
const promptInput = document.getElementById('promptInput');

generateBtn.onclick = ()=>{
    if (promptInput.value !== ''){
        window.location.href = `/generate?prompt=${promptInput.value}`;
    }
}

promptInput.onkeyup = (event)=>{
    if (event.key === 'Enter'){
        generateBtn.click();
    }
}