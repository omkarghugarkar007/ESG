// On message send loader event
var submitButton = document.getElementById("submit-button");
var loader = document.getElementById("loader-wrap");

if (loader && submitButton) {
  submitButton.addEventListener("keyup", function(event) {
      if (event.key === "Enter") {
          loader.style.display = 'flex';
      }
  });

  submitButton.addEventListener("click", function(event) {
    console.log('clicked button')
      loader.style.display = 'flex';
  });
}

function showMoreInfo(event) {
  var showMoreElement = event.target;
  var idx = showMoreElement.ariaLabel;
  var arrowUp = document.querySelector("#arrowDown" + idx);
  var arrowDown = document.querySelector("#arrowUp" + idx);
  var infoWrap = document.querySelector("#infoWrap" + idx);

  if (arrowUp && arrowDown && infoWrap) {
    console.log('arrowUp', arrowUp)
    console.log('arrowDown', arrowDown)
    if (arrowUp.style.display != 'block'){
      arrowDown.style.display = 'none';
      arrowUp.style.display = 'block';
      infoWrap.style.display = 'flex';
    } else {
      arrowDown.style.display = 'block';
      arrowUp.style.display = 'none';
      infoWrap.style.display = 'none';
    }
  }
}

// On doc upload event
var form = document.querySelector("#upload-form");
var fileInput = document.querySelector(".file-input");
var progressArea = document.querySelector(".progress-area");
var uploadedArea = document.querySelector(".uploaded-area");
var csrfToken = document.getElementsByName("csrfmiddlewaretoken");
var loaderWrap = document.querySelector(".loader-wrap");

if (form) {
  form.addEventListener("click", () =>{
    fileInput.click();
  });
  
  fileInput.onchange = ({target})=>{
    let alllowed_mimetypes = ['application/pdf'];
    let allowed_size_mb = 5;

    let files = target.files;
    if (files.length === 0) {
      alert('No file upoaded');
      return
    }
    for (idx=0; idx < files.length; idx++) {
      let file = target.files[idx];
      console.log(file.type);
      if(!alllowed_mimetypes.includes(file.type)) {
        alert('Error: Only pdf files are supported');
        return
      }
      if(file.size <= allowed_size_mb * 1024 * 1024){
        let fileName = file.name;
        if(fileName.length >= 12){
          let splitName = fileName.split('.');
          fileName = splitName[0].substring(0, 13) + "... ." + splitName[1];
        }
        loaderWrap.style.display = 'flex';
        uploadFile(fileName);
      } else {
        alert('Error: file size exceeded for ' + file.name);
        return
      }
    }
    
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  function uploadFile(name){
      let xhr = new XMLHttpRequest();
      xhr.open("POST", "");
      xhr.setRequestHeader("x-requested-with", "XMLHttpRequest")
      xhr.setRequestHeader("x-requested-with", "XMLHttpRequest")
      xhr.upload.addEventListener("progress", ({loaded, total}) =>{
          let fileLoaded = Math.floor((loaded / total) * 100);
          let fileTotal = Math.floor(total / 1000);
          let fileSize;
          (fileTotal < 1024) ? fileSize = fileTotal + " KB" : fileSize = (loaded / (1024*1024)).toFixed(2) + " MB";
          let progressHTML = `<li class="row">
                              <i class="fas fa-file-alt"></i>
                              <div class="content">
                                  <div class="details">
                                  <span class="name">${name} • Uploading</span>
                                  <span class="percent">${fileLoaded}%</span>
                                  </div>
                                  <div class="progress-bar">
                                  <div class="progress" style="width: ${fileLoaded}%"></div>
                                  </div>
                              </div>
                              </li>`;
          uploadedArea.classList.add("onprogress");
          progressArea.innerHTML = progressHTML;
          if(loaded == total){
          progressArea.innerHTML = "";
          let uploadedHTML = `<li class="row">
                                  <div class="content upload">
                                  <i class="fas fa-file-alt"></i>
                                  <div class="details">
                                      <span class="name">${name} • Uploaded</span>
                                      <span class="size">${fileSize}</span>
                                  </div>
                                  </div>
                                  <i class="fas fa-check"></i>
                              </li>`;
          uploadedArea.classList.remove("onprogress");
          uploadedArea.insertAdjacentHTML("afterbegin", uploadedHTML);
          }
      });
      let data = new FormData(form);
      xhr.send(data);

      xhr.onreadystatechange = () => {
        if (xhr.readyState === xhr.HEADERS_RECEIVED) {
          loaderWrap.style.display = 'none';
        }
      };
  }
}

var responseBtn = document.querySelector('.generate-btn');
if (responseBtn) {
  responseBtn.addEventListener("click", function(event) {
    location.reload();
  });
}

var printBtn = document.querySelector('.print-btn');
if (printBtn) {
  printBtn.addEventListener("click", function(event) {
    window.print()
  });
}

var responseElement = document.getElementById('response');
if (responseElement) {
  var response = JSON.parse(responseElement.textContent);
  for (var i = 0; i <= response.length; i++) {
    if (response[i].data.length !== 0) {
      var chartId = `myChart${i+1}`;
      var ctx = document.getElementById(chartId).getContext('2d');
      var myChart = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: response[i].labels,
              datasets: [{
                  label: 'Happiness',
                  data: response[i].data,
                  backgroundColor: [
                    '#4b427669',
                    '#4b427669',
                    '#4b427669',
                    '#4b427669',
                    '#4b427669',
                    '#4b427669'
                  ],
                  // borderColor: [
                  //     'rgba(255, 99, 132, 1)',
                  //     'rgba(54, 162, 235, 1)',
                  //     'rgba(255, 206, 86, 1)',
                  //     'rgba(75, 192, 192, 1)',
                  //     'rgba(153, 102, 255, 1)',
                  //     'rgba(255, 159, 64, 1)'
                  // ],
                  // borderWidth: 1
              }]
          },
          options: {
              scales: {
                  y: {
                      beginAtZero: true
                  }
              }
          }
      });
    }
  }
}
