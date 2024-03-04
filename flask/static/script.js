//home page

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('folder-action').addEventListener('change', function() {
    var selectedOption = this.value;
    if (selectedOption === 'create') {
      document.getElementById('create-folder-popup').style.display = 'flex';
    } else {
      document.getElementById('create-folder-popup').style.display = 'none';
    }
  });

  document.getElementById('create-folder-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    
    // Get the folder name from the input field
    const folderName = document.getElementById('folder-name').value;

    // Send a POST request to the Flask endpoint
    fetch('/create_folder', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ folder_name: folderName })
    })
    .then(response => response.json())
    .then(data => {
      
      document.getElementById('response-message').innerText = data.message || data.error;
    })
    .catch(error => {
      console.error('Error:', error);
    });
  });

  // Close the popup when the close button is clicked
  document.getElementById('close-popup').addEventListener('click', function() {
    document.getElementById('create-folder-popup').style.display = 'none';
    updateFolderList();
  });

  

  document.getElementById('folder-action').addEventListener('change', function() {
    var selectedOption = this.value;
    if (selectedOption === 'list') {
      document.getElementById('folder-list').style.display = 'block';
    } else {
      document.getElementById('folder-list').style.display = 'none';
    }
  });

  // Fetching the list of folders from the server 
  fetch('/list_folders')
    .then(response => response.json())
    .then(data => {
      const foldersList = document.getElementById('folders');
      if (data.folders && data.folders.length > 0) {
       
        foldersList.innerHTML = '';
       
        data.folders.forEach(folder => {
          const listItem = document.createElement('li');
          listItem.classList.add('folder-item');
          const folderIcon = document.createElement('i');
          folderIcon.classList.add('fa', 'fa-folder', 'folder-icon');
          const folderName = document.createElement('span');
          folderName.classList.add('folder-name');
          folderName.textContent = folder;
          listItem.appendChild(folderIcon);
          listItem.appendChild(folderName);
                      
          // Adding the delete icon
          const deleteIcon = document.createElement('i');
          deleteIcon.classList.add('fa', 'fa-trash', 'delete-icon');
          listItem.appendChild(deleteIcon);

          foldersList.appendChild(listItem);
        });
      } else {
        // No folders found
        foldersList.innerHTML = '<li>No folders found</li>';
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });

    updateFolderList();


  // Function to update the list of folders
// Function to update the list of folders
function updateFolderList() {
    axios.get('/list_folders')
        .then(response => {
            const foldersList = document.getElementById('folders');
            foldersList.innerHTML = '';

            if (response.data.folders && response.data.folders.length > 0) {
                response.data.folders.forEach(folder => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('folder-item');

                    // Create folder icon
                    const folderIcon = document.createElement('i');
                    folderIcon.classList.add('fa', 'fa-folder', 'folder-icon');

                    // Create folder name span
                    const folderName = document.createElement('span');
                    folderName.classList.add('folder-name');
                    folderName.textContent = folder;

                    listItem.appendChild(folderIcon);
                    listItem.appendChild(folderName);

                    // Adding the delete icon
                    const deleteIcon = document.createElement('i');
                    deleteIcon.classList.add('fa', 'fa-trash', 'delete-icon');
                    listItem.appendChild(deleteIcon);

                    foldersList.appendChild(listItem);
                });

                // Add event listener to newly created delete icons
                addDeleteIconEventListeners();
            } else {
                foldersList.innerHTML = '<li>No folders found</li>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

document.getElementById('delete-folder-form').addEventListener('submit', function(event) {
    event.preventDefault(); 
    
    // Get the folder name from the input field
    const folderName = document.getElementById('delete-folder-name').value;

    // Send a POST request to the Flask endpoint to delete the folder
    axios.post('/delete_folder', { folder_name: folderName })
      .then(response => {
        // Display response message
        document.getElementById('response-message').innerText = response.data.message || response.data.error;
        // Update the folder list
        updateFolderList();
      })
      .catch(error => {
        console.error('Error:', error);
      });
  });


// Add event listener to delete icons
document.addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('delete-icon')) {
 
      document.getElementById('delete-folder-popup').style.display = 'flex';
     
    }
 
  });
  updateFolderList();

      // Add event listener to close the delete-folder-popup
      document.getElementById('close-popup-delete').addEventListener('click', function() {
    // Hide the delete-folder-popup
    document.getElementById('delete-folder-popup').style.display = 'none';
  });
  updateFolderList();
});


//settings page

document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the username passed from the Flask route
    var username = "{{ username }}";
    // Set the value of the username input field
    document.getElementById('username').value = username;
});