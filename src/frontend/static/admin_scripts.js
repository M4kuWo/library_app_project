// Define the server base URL
const SERVER = 'http://127.0.0.1:5000'; // Update this if your server runs on a different port

// Function to store the token in localStorage
const storeToken = (token) => {
    localStorage.setItem('userToken', token);
};

// Function to get the JWT token from localStorage
const getTokenFromLocalStorage = () => {
    const token = localStorage.getItem('userToken');
    if (token) {
        console.log("Token found:", token); // Log the token found
        return token;
    }
    console.log("No token found"); // Log if no token is found
    return null;
};

// Function to decode the JWT token
const decodeToken = (token) => {
    if (token) {
        const tokenPayload = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(tokenPayload));

        const currentTime = Math.floor(Date.now() / 1000); // Get current time in seconds
        if (decodedPayload.exp && decodedPayload.exp < currentTime) {
            console.log('Token expired');
            localStorage.removeItem('userToken'); // Optionally remove the expired token
            window.location.href = 'login.html'; // Redirect to login page
        }
        return decodedPayload;
    }
    return null;
};

const axiosWithAuth = async (method, url, data = {}, config = {}) => {
    const token = getTokenFromLocalStorage();
    if (!token) {
        throw new Error('No token found');
    }

    try {
        return await axios({
            method: method,
            url: `${SERVER}${url}`,
            data: method === 'GET' ? null : data, // Only pass data for non-GET requests
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json', // Ensure content type is JSON
                ...config.headers // Merge with any additional headers
            },
            ...config // Spread other config options like params for query strings
        });
    } catch (error) {
        console.error('API request error:', error);
        throw error; // Re-throw error to handle in the calling function
    }
};

// Not implemented yet
const showToast = (message, type = 'success') => {
    const toastHTML = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    document.getElementById('toast-container').innerHTML += toastHTML; // Ensure you have a container for toast
};

// Function to update sidebar with user information
const updateSidebarUserInfo = (userInfo) => {
    if (userInfo) {
        // Update the name, email, and profile in the sidebar
        document.querySelector('.name').innerText = userInfo.name;
        document.querySelector('.email').innerText = userInfo.email;

        // Profile badge update
        let profileBadge = document.querySelector('.profile-badge');
        switch (userInfo.profile) {
            case 1:
                profileBadge.innerText = "Superadmin";
                profileBadge.style.backgroundColor = "#27ae60"; // Green for Superadmin
                break;
            case 2:
                profileBadge.innerText = "Admin";
                profileBadge.style.backgroundColor = "#f39c12"; // Orange for Admin
                break;
            case 3:
                profileBadge.innerText = "User";
                profileBadge.style.backgroundColor = "#3498db"; // Blue for User
                break;
            default:
                profileBadge.innerText = "Unknown";
                profileBadge.style.backgroundColor = "#e74c3c"; // Red for unknown profiles
        }
    } else {
        console.error("User info is null or undefined."); // Log if user info is missing
    }
};

// Main function to load user info into the sidebar
const loadUserInfo = () => {
    const token = getTokenFromLocalStorage();
    if (token) {
        const decodedToken = decodeToken(token);
        console.log("Decoded Token:", decodedToken); // Log the decoded token
        const userInfo = decodedToken ? decodedToken.sub : null; // Extract 'sub' field from the token payload
        updateSidebarUserInfo(userInfo);
    } else {
        console.error("No token found"); // Log if no token is available
    }
};

// Function to show the search bar and checkboxes
const showSearchBar = () => {
    // Check if search bar already exists
    let searchBar = document.getElementById('user-searchbar');
    if (!searchBar) {
        // Create search bar HTML if it does not exist
        const searchBarHTML = `
            <div id="user-searchbar" class="input-group mb-3">
                <input type="text" class="form-control" id="search-input" placeholder="Search Users...">
                <button class="btn btn-primary" type="button" id="search-button">Search</button>
                <button class="btn btn-success" type="button" id="add-user-btn">+ Add User</button>
            </div>
            <div id="checkbox-container" class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="show-hidden" checked>
                    <label class="form-check-label" for="show-hidden">Show Hidden</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hidden-only">
                    <label class="form-check-label" for="hidden-only">Hidden Only</label>
                </div>
            </div>
        `;
        
        // Insert the search bar and checkboxes into the workbench (or other suitable container)
        document.getElementById('workbench').insertAdjacentHTML('afterbegin', searchBarHTML);

        // Attach event listener to search button
        document.getElementById('search-button').addEventListener('click', () => {
            const searchQuery = document.getElementById('search-input').value;
            searchUsers(searchQuery);
        });

        // Attach event listeners for checkboxes (they will filter the users already displayed)
        document.getElementById('show-hidden').addEventListener('change', filterUsers);
        document.getElementById('hidden-only').addEventListener('change', filterUsers);
        
        // Attach event listener to the "+ Add User" button
        document.getElementById('add-user-btn').addEventListener('click', showCreateUserForm);
    }
};

const showCreateUserForm = async () => {
    // Check if create user form already exists
    let createUserForm = document.getElementById('add-user-form');
    if (!createUserForm) {
        // Create add user form HTML if it does not exist
        const createUserFormHTML = `
            <div id="add-user-form" class="card" style="display: none;">
                <div class="card-body">
                    <h5 class="card-title">Add New User</h5>
                    <form id="new-user-form">
                        <div class="mb-3">
                            <label for="user-name" class="form-label">Name</label>
                            <input type="text" id="user-name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="user-email" class="form-label">Email</label>
                            <input type="email" id="user-email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="user-password" class="form-label">Password</label>
                            <input type="password" id="user-password" class="form-control" required>
                            <div class="form-text">At least 8 characters, one lowercase, one uppercase, and one symbol.</div>
                        </div>
                        <div class="mb-3">
                            <label for="user-city" class="form-label">City</label>
                            <select id="user-city" class="form-control" required>
                                <option value="">Select a city</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="user-age" class="form-label">Age</label>
                            <input type="number" id="user-age" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="user-profile" class="form-label">Profile</label>
                            <select id="user-profile" class="form-control" required>
                                <option value="">Select a profile</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-success">Create</button>
                        <button type="button" id="cancel-btn" class="btn btn-danger">Cancel</button>
                    </form>
                </div>
            </div>
        `;

        // Insert the create user form into the workbench (or other suitable container)
        document.getElementById('workbench').insertAdjacentHTML('beforeend', createUserFormHTML);

        // Attach event listener for the cancel button
        document.getElementById('cancel-btn').addEventListener('click', () => {
            document.getElementById('add-user-form').style.display = 'none'; // Hide the add user form
            getUsers(); // Refresh the user list to discard unsaved changes
        });

        // Fetch cities and profiles data for dropdowns
        try {
            const citiesResponse = await axiosWithAuth('GET', '/api/cities/');
            const profilesResponse = await axiosWithAuth('GET', '/api/user_profiles/');
            
            const cities = citiesResponse.data;
            const profiles = profilesResponse.data;

            // Populate city dropdown
            const cityOptions = cities.map(city => `<option value="${city.id}">${city.name}</option>`).join('');
            document.getElementById('user-city').innerHTML += cityOptions;

            // Populate profile dropdown
            const profileOptions = profiles.map(profile => `<option value="${profile.id}">${profile.name}</option>`).join('');
            document.getElementById('user-profile').innerHTML += profileOptions;

        } catch (error) {
            console.error('Error fetching cities or profiles:', error);
        }

        // Attach event listener for the new user form submission
        document.getElementById('new-user-form').addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
            
            const name = document.getElementById('user-name').value;
            const email = document.getElementById('user-email').value;
            const password = document.getElementById('user-password').value;
            const city = parseInt(document.getElementById('user-city').value);
            const age = parseInt(document.getElementById('user-age').value);
            const profile = parseInt(document.getElementById('user-profile').value);
            
            // Password validation check
            const passwordRequirements = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$/; // At least 8 characters, one lowercase, one uppercase, one special character
            if (!passwordRequirements.test(password)) {
                alert('Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one special character.');
                return; // Prevent submission if password doesn't meet requirements
            }

            const userData = { name, email, password, city, age, profile }; // Prepare the data to be sent

            // Send POST request using axiosWithAuth
            try {
                const response = await axiosWithAuth('POST', '/api/users/create_user', userData);
                console.log('User created:', response.data);
                await getUsers(); // Refresh the user list
                document.getElementById('add-user-form').style.display = 'none'; // Hide the form
            } catch (error) {
                console.error('Error creating user:', error);
            }
        });
    }

    // Show the create user form
    document.getElementById('add-user-form').style.display = 'block';
};

// Function to get all users with showHidden = 1 parameter
const getUsers = async () => {
    try {
        // Fetch all users (including hidden ones) from the API using axiosWithAuth
        const response = await axiosWithAuth('GET', '/api/users/', {}, {
            params: { showHidden: 1 } // Always retrieve all users, including hidden ones
        });

        if (response.status === 200) {
            const users = response.data;
            populateUsers(users); // Populate users list on UI
            filterUsers(); // Apply filtering based on checkbox states
        } else {
            console.error('Error fetching users:', response.data.error);
            showToast('Error fetching users', 'error'); // Show toast notification for error
        }
    } catch (error) {
        console.error('Fetch error:', error);
        showToast('Error fetching users', 'error'); // Show toast notification for fetch error
    }
};

// Function to search for users based on search query and showHidden = 1 parameter
const searchUsers = async (searchQuery) => {
    try {
        // Make an API call to search for users with showHidden and searchQuery
        const response = await axiosWithAuth('GET', '/api/users/', {}, {
            params: {
                showHidden: 1, // Always include hidden users
                search: searchQuery // Pass the search query
            }
        });

        if (response.status === 200) {
            const users = response.data;
            populateUsers(users); // Populate users with search results
            filterUsers(); // Apply filter to reflect checkbox state
        } else {
            console.error('Error searching users:', response.data.error);
            showToast('Error searching users', 'error'); // Show toast notification for error
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search error', 'error'); // Show toast notification for fetch error
    }
};


// Function to populate the users in the DOM
const populateUsers = (users) => {
    const usersContainer = document.getElementById('users-container');
    usersContainer.innerHTML = ''; // Clear any existing content

    if (users.length === 0) {
        usersContainer.innerHTML = '<p>No users found.</p>';
        return;
    }

    users.forEach(user => {
        // Conditionally render the "Restore" button if the user is hidden, otherwise show the "Delete" button
        const actionButton = user.hidden ? `
            <button class="btn btn-link text-warning" title="Restore User" onclick="restoreUser(${user.id})">
                <i class="fas fa-undo"></i>
            </button>
        ` : `
            <button class="btn btn-link text-danger" title="Delete User" onclick="deleteUser(${user.id})">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;

        // Create user card using Bootstrap classes
        const userCard = `
            <div class="col-md-4 user-card" data-id="${user.id}" data-hidden="${user.hidden}">
                <div class="card">
                    <div class="card-body text-center">
                        <div class="user-avatar-placeholder mb-3"></div>
                        
                        <!-- Buttons positioned between the avatar and the name -->
                        <div class="button-container mb-3">
                            <button class="btn btn-link" title="Edit User" onclick="editUser(${user.id})">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            ${actionButton} <!-- Show either "Restore" or "Delete" button -->
                        </div>

                        <h5 class="card-title">${user.name}</h5>
                        <p class="card-title">ID: ${user.id}</p>
                        <p class="card-text">Email: ${user.email}</p>
                        <p class="card-text">City: ${user.city || 'N/A'}</p>
                        <p class="card-text">Age: ${user.age || 'N/A'}</p>
                        <p class="card-text">Profile: ${user.profile || 'N/A'}</p>
                        <p class="card-text">Hidden: ${user.hidden ? 'Yes' : 'No'}</p>
                    </div>
                </div>
            </div>
        `;

        // Append the user card to the container
        usersContainer.innerHTML += userCard;
    });

    // Make the users container visible
    usersContainer.style.display = 'flex';
};

// Function to restore a user
const restoreUser = async (userId) => {
    try {
        const response = await axiosWithAuth('PUT', `/api/users/${userId}`, { hidden: 0 });

        if (response.status === 200) {
            console.log('User restored successfully:', response.data);
            showToast('User restored successfully', 'success');
            
            // Remove the user from the displayed list or update the UI
            const userCard = document.querySelector(`.user-card[data-id="${userId}"]`);
            if (userCard) {
                userCard.remove(); // Remove the card from the DOM
            }
        } else {
            console.error('Error restoring user:', response.data.error);
            showToast('Error restoring user', 'error');
        }
    } catch (error) {
        console.error('Restore error:', error);
        showToast('Error restoring user', 'error');
    }
};

// Function to edit a user
const editUser = async (userId) => {
    try {
        // Check if the user is hidden by looking at the user's card in the DOM
        const userCard = document.querySelector(`.user-card[data-id="${userId}"]`);
        const isHidden = userCard ? userCard.getAttribute('data-hidden') === '1' : false;

        // Fetch user details by ID (include showHidden if the user is hidden)
        const userResponse = await axiosWithAuth('GET', `/api/users/${userId}`, {}, {
            params: { showHidden: isHidden ? 1 : 0 } // Conditionally add showHidden=1
        });

        if (userResponse.status === 200) {
            const user = userResponse.data;

            // Fetch cities
            const citiesResponse = await axiosWithAuth('GET', '/api/cities/');

            // Fetch user profiles
            const profilesResponse = await axiosWithAuth('GET', '/api/user_profiles/');

            const cities = citiesResponse.data;
            const profiles = profilesResponse.data;

            // Create dropdown options for cities
            const cityOptions = cities.map(city => `<option value="${city.id}" ${city.id === user.city ? 'selected' : ''}>${city.name}</option>`).join('');
            
            // Create dropdown options for profiles
            const profileOptions = profiles.map(profile => `<option value="${profile.id}" ${profile.id === user.profile ? 'selected' : ''}>${profile.name}</option>`).join('');

            if (userCard) {
                // Replace user card with editable form including dropdowns
                const userCardHTML = `
                    <div class="col-md-4 user-card" data-id="${user.id}">
                        <div class="card">
                            <div class="card-body text-center">
                                <div class="user-avatar-placeholder mb-3"></div>
                                <h5 class="card-title">
                                    <input type="text" value="${user.name}" id="edit-name-${user.id}" />
                                </h5>
                                <p class="card-text">
                                    Email: <input type="email" value="${user.email}" id="edit-email-${user.id}" />
                                </p>
                                <p class="card-text">
                                    City: <select id="edit-city-${user.id}">${cityOptions}</select>
                                </p>
                                <p class="card-text">
                                    Age: <input type="number" value="${user.age || ''}" id="edit-age-${user.id}" />
                                </p>
                                <p class="card-text">
                                    Profile: <select id="edit-profile-${user.id}">${profileOptions}</select>
                                </p>
                                <button class="btn btn-success" onclick="updateUser(${user.id})">Update</button>
                                <button class="btn btn-danger" onclick="cancelEdit(${user.id})">Cancel</button>
                            </div>
                        </div>
                    </div>
                `;
                // Replace the card with the form
                userCard.outerHTML = userCardHTML;
            } else {
                console.error(`User card for ID ${userId} not found.`);
            }
        } else {
            console.error('Error fetching user details:', userResponse.data.error);
        }
    } catch (error) {
        console.error('Error fetching user:', error);
    }
};

// Function to handle updating the user details
const updateUser = async (userId) => {
    try {
        // Gather updated data from the input fields
        const name = document.getElementById(`edit-name-${userId}`).value;
        const email = document.getElementById(`edit-email-${userId}`).value;
        const city = document.getElementById(`edit-city-${userId}`).value; // Get selected city ID
        const age = document.getElementById(`edit-age-${userId}`).value;
        const profile = document.getElementById(`edit-profile-${userId}`).value; // Get selected profile ID

        // Prepare the data to be sent
        const updatedUserData = {
            name,
            email,
            city, // Send city ID
            age,
            profile // Send profile ID
        };

        // Send the PUT request to update user
        const response = await axiosWithAuth('PUT', `/api/users/${userId}`, updatedUserData);

        if (response.status === 200) {
            // Successfully updated user
            console.log('User updated successfully:', response.data);
            await getUsers(); // Fetch updated user list
        } else {
            console.error('Error updating user:', response.data.error);
        }
    } catch (error) {
        console.error('Update error:', error);
    }
};

// Function to handle canceling the edit
const cancelEdit = (userId) => {
    // Simply refresh the users list to revert to the original state
    getUsers();
};

// Function to delete a user
const deleteUser = async (userId) => {
    if (confirm("Are you sure you want to delete this user?")) {
        try {
            // Send the DELETE request to delete the user
            await axiosWithAuth('DELETE', `/api/users/${userId}`);

            // Fetch and repopulate users after deletion
            await getUsers();
        } catch (error) {
            console.error('Error deleting user:', error);
        }
    }
};


// Function to filter users based on the state of checkboxes
const filterUsers = () => {
    const showHiddenCheckbox = document.getElementById('show-hidden');
    const hiddenOnlyCheckbox = document.getElementById('hidden-only');
    const userCards = document.querySelectorAll('.user-card');

    // Disable "Show Hidden" checkbox if "Hidden Only" is checked
    if (hiddenOnlyCheckbox.checked) {
        showHiddenCheckbox.checked = true; // Check it
        showHiddenCheckbox.disabled = true; // Disable it
    } else {
        showHiddenCheckbox.disabled = false; // Re-enable it
    }

    userCards.forEach(card => {
        const isHidden = card.getAttribute('data-hidden') === 'true';

        if (hiddenOnlyCheckbox.checked) {
            // Show only hidden users
            card.style.display = isHidden ? 'block' : 'none';
        } else if (showHiddenCheckbox.checked) {
            // Show all users
            card.style.display = 'block';
        } else {
            // Show only non-hidden users
            card.style.display = isHidden ? 'none' : 'block';
        }
    });
};

// Run on page load
window.onload = loadUserInfo;

document.getElementById('users-link').addEventListener('click', async (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    showSearchBar(); // Show search bar and checkboxes
    await getUsers(); // Fetch and display users
});
