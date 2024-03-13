document.addEventListener('DOMContentLoaded', function() {
    // Function to add event listeners to delete icons
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
                const folderDropdown = document.getElementById('folder-action'); // Get the dropdown
    
                foldersList.innerHTML = '';
                // folderDropdown.innerHTML = '<option value="create">Create Folder</option>'; 
    
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

// Event listener for closing the folder creation popup
document.getElementById('close-popup').addEventListener('click', function() {
    const folderNameInput = document.getElementById('folder-name');
    const responseMessage = document.getElementById('response-message');

    folderNameInput.value = ''; // Clearing the input field
    responseMessage.innerText = ''; // Clearing the response message

    

    document.getElementById('create-folder-popup').style.display = 'none';
    updateFolderList();
});
    // Event listener for folder action dropdown
// Event listener for folder action dropdown
document.getElementById('folder-action').addEventListener('change', function() {
    var selectedOption = this.value;
    if (selectedOption === 'create') {
        showCreateFolderPopup();
        console.log("open create folder");
    } else if (selectedOption === 'list') {
        console.log("list folder");
        // Show folder list
        document.getElementById('folder-list').style.display = 'block';
    } else {
        // Clear the create folder popup and send the captured image to the selected folder
        document.getElementById('create-folder-popup').style.display = 'none';
        sendCapturedImage(selectedOption); 
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
                updateFolderList(); // Refresh folder list after deletion
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    // Fetch folders when the page loads
    updateFolderList();
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('capture-btn').addEventListener('click', function() {
        // Get the selected folder name from the dropdown
        const selectedFolder = document.getElementById('folder-action').value;
        const img = document.querySelector('.image-cont img'); 
        
        const canvas = document.createElement('canvas');
        canvas.width = img.width; 
        canvas.height = img.height; 
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/jpeg');
        
        // Send the captured screenshot to the folder for save
        fetch('/api/output', {
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

// Function to display a notification message
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
    }, 5000); 
}




  
  //settings page
  
  document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the username passed from the Flask route
    var username = "{{ username }}";
    // Set the value of the username input field
    document.getElementById('username').value = username;
});

//gallery page

const images = ["../static/images/image1.jpg", "../static/images/image2.jpg", 
"../static/images/image3.jpg","../static/images/image4.jpg","../static/images/image5.jpg",
"../static/images/image6.jpg"]; // Add more images as needed
let currentIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
  const galleryImages = document.querySelectorAll('.gallery-image');

  galleryImages.forEach(function(image, index) {
    image.addEventListener('click', function() {
      currentIndex = index;
      openOverlay(images[currentIndex]);
    });
  });

  // Listen for keyboard events
  document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
      prevImage();
    } else if (event.key === 'ArrowRight') {
      nextImage();
    }
  });
});

function openOverlay(src) {
  const overlay = document.getElementById('overlay');
  const mainImageOverlay = document.getElementById('mainImageOverlay');

  mainImageOverlay.src = src;
  overlay.style.display = 'block';
}

function closeOverlay() {
  const overlay = document.getElementById('overlay');
  overlay.style.display = 'none';
}

function prevImage() {
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  document.getElementById('mainImageOverlay').src = images[currentIndex];
}

function nextImage() {
  currentIndex = (currentIndex + 1) % images.length;
  document.getElementById('mainImageOverlay').src = images[currentIndex];
}