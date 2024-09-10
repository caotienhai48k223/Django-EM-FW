const getCookie = (name) => {
  const cookies = document.cookie?.split(';') || []
  const cookie = cookies.find(c => c.trim().startsWith(`${name}=`))
  return cookie ? decodeURIComponent(cookie.trim().substring(name.length + 1)) : null
}

const csrftoken = getCookie('csrftoken')

const video = document.querySelector('#video-element')
const image = document.querySelector('#img-element')
const captureBtn = document.querySelector('#capture-btn')
const btnElm = document.querySelector('#button-element')
let base64data = ''

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({video: true})
  .then((stream) => {
    video.srcObject = stream
    const {height, width} = stream.getTracks()[0].getSettings()
    captureBtn.addEventListener('click', (e) => {
      captureBtn.classList.add('d-none')
      const track = stream.getVideoTracks()[0]
      const imageCapture = new ImageCapture(track)
      imageCapture.takePhoto().then((blob) => {
        const img = new Image(width, height)
        img.src = URL.createObjectURL(blob)
        image.append(img)
        video.classList.add('d-none')
        btnElm.classList.remove('d-none')
        btnElm.querySelector('#reload-btn').addEventListener('click', () => {
          window.location.reload()
        })
        const reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onloadend = () => {
          base64data = reader.result
        }
      }).catch((error) => {
          console.log('takephoto() error: ', error)
      })
    })

    btnElm.querySelector('#upload-btn').addEventListener('click', () => {
      if (base64data) {
        const fd = new FormData()
        fd.append('csrfmiddlewaretoken', csrftoken)
        fd.append('photo', base64data)

        $.ajax({
          type: 'POST',
          url: '/create-faceid/',
          enctype: 'multipart/form-data',
          data: fd,
          processData: false,
          contentType: false,
          success: (resp) => {
            if (resp.success) {
              window.location.href = resp.redirect_url;
            } else {
              alert('Tạo Face ID không thành công.');
              captureBtn.classList.remove('d-none');
              video.classList.remove('d-none');
              image.innerHTML = '';
            }
          },
          error: (err) => {
            console.log(err)
          }
        })
      } else {
        alert('Có lỗi xảy ra. Vui lòng thử lại.');
        console.log(err);
        captureBtn.classList.remove('d-none');
        video.classList.remove('d-none');
        image.innerHTML = '';
      }
    })

  })
  .catch((error) => {
    console.log('Something went wrong!', error)
  })
}