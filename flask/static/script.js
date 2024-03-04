// Function to add event listeners to delete icons
function addDeleteIconEventListeners() {
  document.querySelectorAll('.delete-icon').forEach(deleteIcon => {
      deleteIcon.addEventListener('click', deleteFolder);
  });
}

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

// Delete folder function
function deleteFolder(event) {
  if (event.target && event.target.classList.contains('delete-icon')) {
      const folderName = event.target.dataset.folderName;
      const confirmDelete = confirm('Are you sure you want to delete the folder ' + folderName + '?');
      if (confirmDelete) {
          fetch('/delete_folder', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  folder_name: folderName
              })
          })
          .then(response => response.json())
          .then(data => {
              alert(data.message); 
              updateFolderList(); 
          })
          .catch(error => console.error('Error deleting folder:', error));
      }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Event listener for folder action dropdown
  document.getElementById('folder-action').addEventListener('change', function() {
      var selectedOption = this.value;
      if (selectedOption === 'create') {
          document.getElementById('create-folder-popup').style.display = 'flex';
      } else {
          document.getElementById('create-folder-popup').style.display = 'none';
      }
  });

  // Event listener for folder creation form submission
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
          updateFolderList(); // Refresh folder list after creation
      })
      .catch(error => {
          console.error('Error:', error);
      });
  });

  // Event listener for closing the folder creation popup
  document.getElementById('close-popup').addEventListener('click', function() {
      document.getElementById('create-folder-popup').style.display = 'none';
      updateFolderList(); // Refresh folder list
  });

  // Event listener for folder action dropdown (list folders)
  document.getElementById('folder-action').addEventListener('change', function() {
      var selectedOption = this.value;
      if (selectedOption === 'list') {
          document.getElementById('folder-list').style.display = 'block';
      } else {
          document.getElementById('folder-list').style.display = 'none';
      }
  });

  // Fetching the list of folders from the server 
  function fetchFolders() {
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
                      deleteIcon.dataset.folderName = folder; // Store folder name in dataset
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

  // Event listener for folder deletion form submission
  document.getElementById('delete-folder-form').addEventListener('submit', function(event) {
      event.preventDefault(); 
      // Get the folder name from the input field
      const folderName = document.getElementById('delete-folder-name').value;

      // Send a POST request to the Flask endpoint to delete the folder
      axios.post('/delete_folder', { folder_name: folderName })
          .then(response => {
              document.getElementById('response-message').innerText = response.data.message || response.data.error;
              updateFolderList(); // Refresh folder list after deletion
          })
          .catch(error => {
              console.error('Error:', error);
          });
  });

  // Event listener to close the delete-folder-popup
  document.getElementById('close-popup-delete').addEventListener('click', function() {
      document.getElementById('delete-folder-popup').style.display = 'none';
  });

  // Fetch folders when the page loads
  fetchFolders();
});


//settings page

document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the username passed from the Flask route
    var username = "{{ username }}";
    // Set the value of the username input field
    document.getElementById('username').value = username;
});