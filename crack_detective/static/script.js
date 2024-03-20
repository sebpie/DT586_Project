document.addEventListener('DOMContentLoaded', function() {
    function addDeleteIconEventListeners() {
        document.querySelectorAll('.delete-icon').forEach(deleteIcon => {
            deleteIcon.addEventListener('click', deleteFolder);
        });
    }

    function updateFolderList() {
        fetch('/api/folders')
            .then(response => response.json())
            .then(data => {
                const foldersList = document.getElementById('folders');
                const folderDropdown = document.getElementById('folder-action'); 
    
                foldersList.innerHTML = '';
                folderDropdown.innerHTML = ''; 
                let showListOption = document.createElement('option');
                showListOption.value = 'list';
                showListOption.textContent = 'Show List';
                if (!folderDropdown.querySelector('option[value="list"]')) {
                    folderDropdown.appendChild(showListOption);
                }
    
                if (data.folders && data.folders.length > 0) {
                    data.folders.forEach(folder => {
                        const listItem = document.createElement('li');
                        listItem.classList.add('folder-item');
    
                        // Create folder icon
                        const folderIcon = document.createElement('i');
                        folderIcon.classList.add('fa', 'fa-folder', 'folder-icon');
    
                        const folderName = document.createElement('span');
                        folderName.classList.add('folder-name');
                        folderName.textContent = folder;
    
                        listItem.appendChild(folderIcon);
                        listItem.appendChild(folderName);
    
                        const deleteIcon = document.createElement('i');
                        deleteIcon.classList.add('fa', 'fa-trash', 'delete-icon');
                        deleteIcon.dataset.folderName = folder;
                        listItem.appendChild(deleteIcon);
    
                        foldersList.appendChild(listItem);
    
                        // Add folder to dropdown
                        const option = document.createElement('option');
                        option.value = folder;
                        option.textContent = folder;
                        folderDropdown.appendChild(option);
                    });
                } else {
                    foldersList.innerHTML = '<li>No folders found</li>';
                }
    
                // Event listener for folder action dropdown
                folderDropdown.addEventListener('click', function(event) {
                    if (event.target.value === 'create') {
                        showCreateFolderPopup();
                        console.log("open create folder");
                        const folderNameInput = document.getElementById('folder-name');
                        const responseMessage = document.getElementById('response-message');
    
                        folderNameInput.value = ''; 
                        responseMessage.innerText = ''; 
                    }
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    

    // Event listener for folder creation form submission
    document.getElementById('create-folder-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const folderNameInput = document.getElementById('folder-name');
        const responseMessage = document.getElementById('response-message');

        const folderName = folderNameInput.value;
        folderNameInput.value = '';
        responseMessage.innerText = '';

        // Send a POST request to the Flask endpoint
        fetch('/api/folders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ folder_name: folderName })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response-message').innerText = data.message || data.error;
            updateFolderList(); // Refresh folder list after creation
            document.getElementById('create-folder-popup').style.display = 'none';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    document.getElementById('create-folder-btn').addEventListener('click', function() {
        document.getElementById('response-message').innerText = '';
        showCreateFolderPopup();
    });

    // Event listener to close the delete-folder-popup
    document.getElementById('close-popup-delete').addEventListener('click', function() {
        document.getElementById('delete-folder-popup').style.display = 'none';
        updateFolderList();
    });


document.getElementById('close-popup').addEventListener('click', function() {
    const folderNameInput = document.getElementById('folder-name');
    const responseMessage = document.getElementById('response-message');

    folderNameInput.value = ''; 
    responseMessage.innerText = ''; 



    document.getElementById('create-folder-popup').style.display = 'none';
    updateFolderList();
});

// Event listener for folder action dropdown
document.getElementById('folder-action').addEventListener('change', function() {
    var selectedOption = this.value;
    if (selectedOption === 'create') {
        showCreateFolderPopup();
        console.log("open create folder");
    } else if (selectedOption === 'list') {
        console.log("list folder");
        document.getElementById('folder-list').style.display = 'block';
    } else {
        // Clear the create folder popup and send the captured image to the selected folder
        document.getElementById('create-folder-popup').style.display = 'none';
        // sendCapturedImage(selectedOption);
    }
});


    function showCreateFolderPopup() {
        document.getElementById('create-folder-popup').style.display = 'flex';
    }

    // to rename folders in gallery management
  function sendPutRequest(folderName) {
    fetch('/api/folders/' + folderName, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ folder_name: folderName })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
}

    // Function to handle folder deletion
    function deleteFolder() {
        const folderName = this.dataset.folderName;
        const confirmation = confirm(`Are you sure you want to delete the folder "${folderName}"?`);

        if (confirmation) {
            fetch(`/api/folders/${folderName}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                updateFolderList(); 
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

   
    updateFolderList();
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('capture-btn').addEventListener('click', function() {
   
        const selectedFolder = document.getElementById('folder-action').value;
        const img = document.querySelector('.image-cont img');

        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/jpeg');

        // Send the captured screenshot to the folder for save
        fetch('/api/take_picture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                folder_name: selectedFolder,
                screenshot_data: dataURL
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showNotification(data.message);
            } else {

                showNotification('Error: Image could not be saved');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error: Failed to send image data');
        });
    });
});

// display a notification message
function showNotification(message) {
    // Create a notification element
    const notification = document.createElement('div');
    notification.classList.add('notification');
    const isSuccess = message.toLowerCase().includes('success');
    if (isSuccess) {
        notification.style.color = 'green';
    } else {
        notification.style.color = 'red';
    }

    notification.textContent = message;
    const container = document.querySelector('.container');

    // Append the notification to the container
    container.appendChild(notification);
    setTimeout(function() {
        container.removeChild(notification);
    }, 10000);
}





  //settings page

//   document.addEventListener('DOMContentLoaded', function() {
//     var username = "{{ username }}";
//     document.getElementById('username').value = username;
// });

//gallery page


let currentIndex = 0;
let images = [];

document.addEventListener('DOMContentLoaded', function() {
    function addFolderEventListeners() {
        document.querySelectorAll('.folder-icon').forEach(folder => {
            folder.addEventListener('click', function() {
                const folderName = this.querySelector('h6').textContent;
                loadImages(folderName);
            });
        });
    }

    function loadImages(folderName) {
        fetch(`/api/folders/${folderName}`)
            .then(response => response.json())
            .then(data => {
                console.log('Images Data:', data); 
                
                const imagesContainer = document.querySelector('.images-container');
                imagesContainer.innerHTML = '';
                images = []; 

                document.querySelectorAll('.folder-icon').forEach(folder => {
                    folder.style.display = 'none';
                });

                if (data.images && data.images.length > 0) {
                    data.images.forEach(filename => {
                        const filenameParts = filename.split('/');
                        const correctedFilename = filenameParts[filenameParts.length - 1];
                        
                        const img = document.createElement('img');
                        img.src = `/api/folders/${folderName}/${correctedFilename}`; 
                        img.alt = 'Image';
                        img.classList.add('gallery-image');
                        imagesContainer.appendChild(img);
                        images.push(img.src );
                        
                        
                        img.addEventListener('click', function() {
                            console.log("clicked image")
                            const imageUrl = this.src; 
                            console.log(imageUrl)
                            openOverlay(imageUrl); 
                        });
                    });
                } else {
                    imagesContainer.innerHTML = '<h6 class = "text-center">No images found in this folder</h6>';
                }

                // back button
                const backButton = document.getElementById('back-button');
                backButton.style.display = 'inline-block';
                
                
                backButton.addEventListener('click', function() {
                   
                    document.querySelectorAll('.folder-icon').forEach(folder => {
                        folder.style.display = 'block';
                    });
                  
                    backButton.style.display = 'none';
                  
                    imagesContainer.innerHTML = '';
                    images = [];
                });
            })
            .catch(error => {
                console.error('Error:', error); 
            });
    }
    
    // Call the function to add event listeners to folders
    addFolderEventListeners();
});



function openOverlay(imageUrl) {
    console.log(imageUrl)
    const overlay = document.getElementById('overlay');
    const fullSizeImage = document.getElementById('mainImageOverlay');

    fullSizeImage.src = imageUrl;
    overlay.style.display = 'block'; 
}


function closeOverlay() {
const overlay = document.getElementById('overlay');
overlay.style.display = 'none';
}

// keyboard events
document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
        prevImage();
    } else if (event.key === 'ArrowRight') {
        nextImage();
    }
});
function prevImage() {
    console.log("prev clicked")
currentIndex = (currentIndex - 1 + images.length) % images.length;
console.log(currentIndex)
document.getElementById('mainImageOverlay').src = images[currentIndex];
}

function nextImage() {
    console.log("next clicked")
currentIndex = (currentIndex + 1 + images.length) % images.length;
console.log(currentIndex)
document.getElementById('mainImageOverlay').src = images[currentIndex];
}


document.addEventListener('DOMContentLoaded', function() {
    const fullScreenBtn = document.getElementById('full-screen-btn');
    const uploadContainer = document.getElementById('upload-container');
    let isFullScreen = false;

    // Function to toggle full screen mode
    function toggleFullScreen() {
        if (!isFullScreen) {
            if (uploadContainer.requestFullscreen) {
                uploadContainer.requestFullscreen();
            } else if (uploadContainer.webkitRequestFullscreen) { 
                uploadContainer.webkitRequestFullscreen();
            } else if (uploadContainer.msRequestFullscreen) { 
                uploadContainer.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { 
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { 
                document.msExitFullscreen();
            }
        }

        isFullScreen = !isFullScreen;
    }

    // for full screen button
    fullScreenBtn.addEventListener('click', toggleFullScreen);

    //  for exiting full screen mode 
    document.addEventListener('fullscreenchange', function(event) {
        if (!document.fullscreenElement) {
            isFullScreen = false;
        }
    });

    document.addEventListener('webkitfullscreenchange', function(event) {
        if (!document.webkitFullscreenElement) {
            isFullScreen = false;
        }
    });

    document.addEventListener('msfullscreenchange', function(event) {
        if (!document.msFullscreenElement) {
            isFullScreen = false;
        }
    });
});

// settings.html 

    function changePassword() {
        var notification = document.getElementById('notification');
        var username = document.getElementById('username').value;
        var newPassword = document.getElementById('newPassword').value;
        var confirmNewPassword = document.getElementById('confirmNewPassword').value;
    

        var xhr = new XMLHttpRequest();
    
        // Configure request
        xhr.open("POST", "/change_password_without_auth", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
       
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.error || newPassword !== confirmNewPassword) {
                        
                        notification.textContent = response.error || "Passwords do not match";
                        notification.style.color = '#d04646'; 
                        notification.style.background = '#fff0f3'; 
                        notification.style.padding = '5px'; 
                    } else {
                      
                        notification.textContent = response.message;
                        notification.style.color = '#0b500b'; 
                        notification.style.background = '#c1e3b9'; 
                        notification.style.padding = '10px';
                    }
                } else {
                   
                    notification.textContent = "An error occurred while processing your request.";
                    notification.style.color = '#d04646'; 
                    notification.style.background = '#fff0f3'; 
                    notification.style.padding = '5px'; 
                }
                notification.style.display = 'block';
    
                // Hide the notification after 10 seconds
                setTimeout(function () {
                    notification.style.display = 'none';
                }, 4000);
            }
        };
    
        // Send the request with the form data
        xhr.send("username=" + username + "&newPassword=" + newPassword + "&confirmNewPassword=" + confirmNewPassword);
    }