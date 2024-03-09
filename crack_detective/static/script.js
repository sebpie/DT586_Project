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
                folderDropdown.innerHTML = '<option value="create">Create Folder</option>'; // Reset dropdown
    
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
        event.preventDefault(); // Prevent form submission
        
        // Get the folder name from the input field
        const folderName = document.getElementById('folder-name').value;

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
            document.getElementById('create-folder-popup').style.display = 'none'
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Event listener to close the delete-folder-popup
    document.getElementById('close-popup-delete').addEventListener('click', function() {
        document.getElementById('delete-folder-popup').style.display = 'none';
    });

    // Event listener for closing the folder creation popup
    document.getElementById('close-popup').addEventListener('click', function() {
        document.getElementById('create-folder-popup').style.display = 'none';
        updateFolderList(); // Refresh folder list
    });

    // Event listener for folder action dropdown
    document.getElementById('folder-action').addEventListener('change', function() {
        var selectedOption = this.value;
        if (selectedOption === 'create') {
            document.getElementById('create-folder-popup').style.display = 'flex';
        } else if (selectedOption === 'list') {
            // Show folder list
            document.getElementById('folder-list').style.display = 'block';
        } else {
            // Handle other actions here
            sendPutRequest(selectedOption);
        }
    });

    // Function to send a PUT request to the selected folder
  function sendPutRequest(folderName) {
    fetch('/folder/' + folderName, {
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

  
  //settings page
  
  document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the username passed from the Flask route
    var username = "{{ username }}";
    // Set the value of the username input field
    document.getElementById('username').value = username;
});