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
        const tokenPayload = token.split('.')[1]; // Get the payload part of the JWT
        return JSON.parse(atob(tokenPayload)); // Decode base64 and parse JSON
    }
    return null;
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

// Handle login (example code to store the token after successful login)
const handleLogin = async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await axios.post(`${SERVER}/login`, {
            email,
            password
        });

        const data = response.data;
        if (response.status === 200) {
            // Store the token in localStorage
            storeToken(data.access_token);
            alert('Login successful');
            // Reload the page or navigate to a new page
        } else {
            alert('Login failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error during login:', error);
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
            </div>
            <div id="checkbox-container" class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="show-hidden">
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

        // Attach event listeners for checkboxes
        document.getElementById('show-hidden').addEventListener('change', (e) => {
            const hiddenOnlyCheckbox = document.getElementById('hidden-only');
            if (hiddenOnlyCheckbox.checked) {
                hiddenOnlyCheckbox.checked = false; // Uncheck hidden only if show hidden is checked
            }
            const showHidden = e.target.checked ? 1 : 0;
            getUsers(showHidden, hiddenOnlyCheckbox.checked ? 1 : 0); // Fetch users based on checkbox states
        });


        
        document.getElementById('hidden-only').addEventListener('change', (e) => {
            const showHiddenCheckbox = document.getElementById('show-hidden');

            if (e.target.checked) {
                showHiddenCheckbox.checked = true; // Automatically check the show hidden checkbox
                showHiddenCheckbox.disabled = true; // Disable the show hidden checkbox
            } else {
                showHiddenCheckbox.disabled = false; // Enable show hidden checkbox
            }

            // Update the parameters based on current states of both checkboxes
            const showHidden = showHiddenCheckbox.checked ? 1 : 0; // Get the current state of show hidden
            const hiddenOnly = e.target.checked ? 1 : 0; // Current state of hidden only
            
            getUsers(showHidden, hiddenOnly); // Fetch users based on updated states
        });
    }
};

// Function to get all users
const getUsers = async (showHidden = 0, hiddenOnly = 0) => {
    const token = getTokenFromLocalStorage();
    if (!token) {
        console.error("No token found.");
        return;
    }

    try {
        // Fetch the users from the API using Axios
        const response = await axios.get(`${SERVER}/api/users/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            params: {
                showHidden: showHidden,
                hiddenOnly: hiddenOnly
            }
        });

        if (response.status === 200) {
            const users = response.data;
            populateUsers(users);
        } else {
            console.error('Error fetching users:', response.data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
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
        // Create user card using Bootstrap classes
        const userCard = `
            <div class="col-md-4">
                <div class="user-card card">
                    <div class="card-body text-center">
                        <!-- Placeholder for avatar image -->
                        <div class="user-avatar-placeholder mb-3"></div>
                        
                        <h5 class="card-title">${user.name}</h5>
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

// Run on page load
window.onload = loadUserInfo;

document.getElementById('users-link').addEventListener('click', async (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    showSearchBar(); // Show search bar and checkboxes
    await getUsers(); // Fetch and display users
});
