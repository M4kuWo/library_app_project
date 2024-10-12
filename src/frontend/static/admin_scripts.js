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

// Function to wipe the workbench clean before adding new content
const wipeMainContent = () => {
    const maincontent = document.getElementById('main-content');
    workbench.innerHTML = ``  // Clear all content in the main content div
};

// Function to show the search bar and checkboxes
const showUserSearchBar = () => {
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

const showCitySearchBar = () => {
    // Check if the city search bar already exists
    let searchBar = document.getElementById('city-searchbar');
    if (!searchBar) {
        const searchBarHTML = `
            <div id="city-searchbar" class="input-group mb-3">
                <input type="text" class="form-control" id="city-search-input" placeholder="Search Cities...">
                <button class="btn btn-primary" type="button" id="search-city-button">Search</button>
            </div>
            <div id="checkbox-container" class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="show-hidden-cities" checked>
                    <label class="form-check-label" for="show-hidden-cities">Show Hidden</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hidden-only-cities">
                    <label class="form-check-label" for="hidden-only-cities">Hidden Only</label>
                </div>
            </div>
        `;

        // Insert the search bar into the workbench
        document.getElementById('workbench').insertAdjacentHTML('afterbegin', searchBarHTML);

        // Attach event listener to the search button
        document.getElementById('search-city-button').addEventListener('click', () => {
            const searchQuery = document.getElementById('city-search-input').value;
            searchCities(searchQuery);
        });

        // Attach event listeners for checkboxes (you can implement filterCities function similar to filterBooks and filterUsers)
        document.getElementById('show-hidden-cities').addEventListener('change', filterCities);
        document.getElementById('hidden-only-cities').addEventListener('change', filterCities);
    }
};

const showBookSearchBar = () => {
    // Check if the book search bar already exists
    let searchBar = document.getElementById('book-searchbar');
    if (!searchBar) {
        const searchBarHTML = `
            <div id="book-searchbar" class="input-group mb-3">
                <input type="text" class="form-control" id="book-search-input" placeholder="Search Books...">
                <button class="btn btn-primary" type="button" id="search-book-button">Search</button>
                <button class="btn btn-success" type="button" id="add-book-btn">+ Add Book</button>
            </div>
            <div id="checkbox-container" class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="show-hidden-books" checked>
                    <label class="form-check-label" for="show-hidden-books">Show Hidden</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hidden-only-books">
                    <label class="form-check-label" for="hidden-only-books">Hidden Only</label>
                </div>
            </div>
        `;

        // Insert the search bar into the workbench
        document.getElementById('workbench').insertAdjacentHTML('afterbegin', searchBarHTML);

        // Attach event listeners to search button and checkboxes
        document.getElementById('search-book-button').addEventListener('click', () => {
            const searchQuery = document.getElementById('book-search-input').value;
            searchBooks(searchQuery);
        });
        document.getElementById('show-hidden-books').addEventListener('change', filterBooks);
        document.getElementById('hidden-only-books').addEventListener('change', filterBooks);

        // Attach event listener to the "+ Add Book" button
        document.getElementById('add-book-btn').addEventListener('click', showCreateBookForm);
    }
};

const showCategorySearchBar = () => {
    // Check if the category search bar already exists
    let searchBar = document.getElementById('category-searchbar');
    if (!searchBar) {
        const searchBarHTML = `
            <div id="category-searchbar" class="input-group mb-3">
                <input type="text" class="form-control" id="category-search-input" placeholder="Search Categories...">
                <button class="btn btn-primary" type="button" id="search-category-button">Search</button>
                <button class="btn btn-success" type="button" id="add-category-btn">+ Add Category</button>
            </div>
            <div id="checkbox-container" class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="show-hidden-categories" checked>
                    <label class="form-check-label" for="show-hidden-categories">Show Hidden</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="hidden-only-categories">
                    <label class="form-check-label" for="hidden-only-categories">Hidden Only</label>
                </div>
            </div>
        `;

        // Insert the search bar into the workbench
        document.getElementById('workbench').insertAdjacentHTML('afterbegin', searchBarHTML);

        // Attach event listeners to search button and checkboxes
        document.getElementById('search-category-button').addEventListener('click', () => {
            const searchQuery = document.getElementById('category-search-input').value;
            searchCategories(searchQuery);
        });
        document.getElementById('show-hidden-categories').addEventListener('change', filterCategories);
        document.getElementById('hidden-only-categories').addEventListener('change', filterCategories);

        // Attach event listener to the "+ Add Category" button
        document.getElementById('add-category-btn').addEventListener('click', showCreateCategoryForm);
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

const showCreateBookForm = async () => {
    // Check if form already exists
    let createBookForm = document.getElementById('add-book-form');
    if (!createBookForm) {
        // Fetch categories
        const categoriesResponse = await axiosWithAuth('GET', '/api/categories/');
        const categories = categoriesResponse.data;

        // Create category dropdown options
        const categoryOptions = categories.map(category => `<option value="${category.id}">${category.category}</option>`).join('');

        const createBookFormHTML = `
            <div id="add-book-form" class="card">
                <div class="card-body">
                    <h5 class="card-title">Add New Book</h5>
                    <form id="new-book-form">
                        <div class="mb-3">
                            <label for="book-title" class="form-label">Title</label>
                            <input type="text" id="book-title" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="book-author" class="form-label">Author</label>
                            <input type="text" id="book-author" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="book-category" class="form-label">Category</label>
                            <select id="book-category" class="form-control" required>
                                ${categoryOptions}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="book-pages" class="form-label">Number of Pages</label>
                            <input type="number" id="book-pages" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="book-year" class="form-label">Year Published</label>
                            <input type="number" id="book-year" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-success">Create</button>
                        <button type="button" id="cancel-book-btn" class="btn btn-danger">Cancel</button>
                    </form>
                </div>
            </div>
        `;

        // Insert the form into the workbench
        document.getElementById('workbench').insertAdjacentHTML('beforeend', createBookFormHTML);

        // Cancel button
        document.getElementById('cancel-book-btn').addEventListener('click', () => {
            document.getElementById('add-book-form').remove();  // Remove the form
        });

        // Handle form submission
        document.getElementById('new-book-form').addEventListener('submit', async function (event) {
            event.preventDefault();  // Prevent default submission

            const title = document.getElementById('book-title').value;
            const author = document.getElementById('book-author').value;
            const category = parseInt(document.getElementById('book-category').value);
            const numberOfPages = parseInt(document.getElementById('book-pages').value);
            const yearPublished = parseInt(document.getElementById('book-year').value);

            const bookData = { title, author, category, number_of_pages: numberOfPages, year_published: yearPublished };

            try {
                const response = await axiosWithAuth('POST', '/api/books/', bookData);
                console.log('Book created:', response.data);
                await getBooks();  // Refresh the book list
                document.getElementById('add-book-form').remove();  // Remove the form after submission
            } catch (error) {
                console.error('Error creating book:', error);
            }
        });
    }
};

const showCreateCategoryForm = async () => {
    // Check if the form already exists
    let createCategoryForm = document.getElementById('add-category-form');
    if (!createCategoryForm) {
        const createCategoryFormHTML = `
            <div id="add-category-form" class="card">
                <div class="card-body">
                    <h5 class="card-title">Add New Category</h5>
                    <form id="new-category-form">
                        <div class="mb-3">
                            <label for="category-name" class="form-label">Category</label> <!-- Changed label -->
                            <input type="text" id="category-name" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-success">Create</button>
                        <button type="button" id="cancel-category-btn" class="btn btn-danger">Cancel</button>
                    </form>
                </div>
            </div>
        `;

        // Insert the form into the workbench
        document.getElementById('workbench').insertAdjacentHTML('beforeend', createCategoryFormHTML);

        // Cancel button
        document.getElementById('cancel-category-btn').addEventListener('click', () => {
            document.getElementById('add-category-form').remove();  // Remove the form
        });

        // Handle form submission
        document.getElementById('new-category-form').addEventListener('submit', async function (event) {
            event.preventDefault();  // Prevent default submission

            const name = document.getElementById('category-name').value;

            const categoryData = { category: name }; // Prepare the data to be sent with the correct field name

            try {
                const response = await axiosWithAuth('POST', '/api/categories/', categoryData);
                console.log('Category created:', response.data);
                await getCategories();  // Refresh the category list
                document.getElementById('add-category-form').remove();  // Remove the form after submission
            } catch (error) {
                console.error('Error creating category:', error);
            }
        });
    }
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

// Function to get cities
const getCities = async () => {
    try {
        const response = await axiosWithAuth('GET', '/api/cities/');
        if (response.status === 200) {
            const cities = response.data;  // Assuming response.data is an array of cities
            populateCities(cities);  // Populate cities on the UI
        } else {
            console.error('Error fetching cities:', response.data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
};

// Function to populate cities in a table
const populateCities = (cities) => {
    if (!cities || !Array.isArray(cities)) {
        console.error('Invalid cities data:', cities);
        document.getElementById('cards-container').innerHTML = '<p>Error loading cities.</p>';
        return;
    }

    const citiesContainer = document.getElementById('cards-container');
    citiesContainer.innerHTML = '';  // Clear previous content

    if (cities.length === 0) {
        citiesContainer.innerHTML = '<p>No cities found.</p>';
        return;
    }

    // Create the table structure
    const tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>City</th>
                </tr>
            </thead>
            <tbody>
                ${cities.map(city => `
                    <tr class="city-row" data-id="${city.id}">
                        <td>${city.id}</td>
                        <td>${city.name}</td>  <!-- Assuming each city object has a 'name' property -->
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Insert the table into the container
    citiesContainer.innerHTML = tableHTML;
};

const populateBookTypes = (bookTypes) => {
    // Check for valid data
    if (!bookTypes || !Array.isArray(bookTypes)) {
        console.error('Invalid book types data:', bookTypes);
        document.getElementById('cards-container').innerHTML = '<p>Error loading book types.</p>';
        return;
    }

    const bookTypesContainer = document.getElementById('cards-container');
    bookTypesContainer.innerHTML = '';  // Clear previous content

    if (bookTypes.length === 0) {
        bookTypesContainer.innerHTML = '<p>No book types found.</p>';
        return;
    }

    // Create the table structure
    const tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Max Loan Duration (Days)</th>
                </tr>
            </thead>
            <tbody>
                ${bookTypes.map(type => `
                    <tr>
                        <td>${type.id}</td>
                        <td>${type.type}</td>
                        <td>${type.max_loan_duration}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Insert the table into the container
    bookTypesContainer.innerHTML = tableHTML;
};

const getBooks = async () => {
    try {
        // Fetch books with showHidden=1
        const response = await axiosWithAuth('GET', '/api/books/', {}, {
            params: { showHidden: 1 }  // Always retrieve hidden and non-hidden books
        });

        if (response.status === 200) {
            const books = response.data.books;
            populateBooks(books);  // Populate books on the UI with category names
            filterBooks();  // Apply filtering based on checkbox states
        } else {
            console.error('Error fetching books:', response.data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
};

const getCategories = async () => {
    try {
        // Fetch categories with showHidden=1
        const response = await axiosWithAuth('GET', '/api/categories/', {}, {
            params: { showHidden: 1 }  // Always retrieve hidden and non-hidden categories
        });

        if (response.status === 200) {
            const categories = response.data; // Use response.data directly as it is an array
            populateCategories(categories);  // Populate categories on the UI
            filterCategories();  // Apply filtering based on checkbox states
        } else {
            console.error('Error fetching categories:', response.data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
};

const getBookTypes = async () => {
    try {
        const response = await axiosWithAuth('GET', '/api/book_types/', {}, {
            // params: { showHidden: 1 }  // Fetch all book types including hidden ones
        });

        if (response.status === 200) {
            const bookTypes = response.data;  // Use the correct property based on your response
            populateBookTypes(bookTypes);  // Populate the UI with book types
        } else {
            console.error('Error fetching book types:', response.data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
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

const searchBooks = async (searchQuery) => {
    try {
        const response = await axiosWithAuth('GET', '/api/books/', {}, {
            params: {
                showHidden: 1,  // Always include hidden books
                search: searchQuery  // Search query
            }
        });

        if (response.status === 200) {
            const books = response.data.books;
            populateBooks(books);
            filterBooks();  // Filter based on checkbox state
        } else {
            console.error('Error searching books:', response.data.error);
        }
    } catch (error) {
        console.error('Search error:', error);
    }
};

const searchCategories = async (searchQuery) => {
    try {
        const response = await axiosWithAuth('GET', '/api/categories/', {}, {
            params: {
                showHidden: 1,  // Always include hidden categories
                search: searchQuery  // Search query
            }
        });

        if (response.status === 200) {
            const categories = response.data; // Adjust based on your response structure
            populateCategories(categories);
            filterCategories();  // Filter based on checkbox state
        } else {
            console.error('Error searching categories:', response.data.error);
        }
    } catch (error) {
        console.error('Search error:', error);
    }
};

// Function to populate the users in the DOM
const populateUsers = (users) => {
    const usersContainer = document.getElementById('cards-container');
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

const populateBooks = (books) => {
    const booksContainer = document.getElementById('cards-container');
    booksContainer.innerHTML = '';  // Clear previous content

    if (books.length === 0) {
        booksContainer.innerHTML = '<p>No books found.</p>';
        return;
    }

    books.forEach(book => {
        const actionButton = book.hidden ? `
            <button class="btn btn-link text-warning" title="Restore Book" onclick="restoreBook(${book.id})">
                <i class="fas fa-undo"></i>
            </button>
        ` : `
            <button class="btn btn-link text-danger" title="Delete Book" onclick="deleteBook(${book.id})">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;

        // Check for cover image, use a placeholder if none is available
        const coverImageUrl = book.cover_image ? book.cover_image : 'no_cover_yet_image.png'; // Use placeholder

        const bookCard = `
            <div class="col-md-4 book-card" data-id="${book.id}" data-hidden="${book.hidden ? 'true' : 'false'}">
                <div class="card">
                    <div class="card-body text-center">
                        <img src="${coverImageUrl}" alt="Book Cover" class="book-cover" onerror="this.src='no_cover_yet_image.png';" />
                        
                        <!-- Buttons positioned between the cover and the title -->
                        <div class="button-container mb-3">
                            <button class="btn btn-link" title="Edit Book" onclick="editBook(${book.id})">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            ${actionButton}
                        </div>

                        <h5 class="card-title">${book.title}</h5>
                        <p class="card-id">ID: ${book.id}</p>
                        <p class="card-author">Author: ${book.author}</p>
                        <p class="card-text">Year Published: ${book.year_published}</p>
                        <p class="card-text">Pages: ${book.number_of_pages}</p>
                        <p class="card-text">Category: ${book.category}</p>
                        <p class="card-text">Hidden: ${book.hidden ? 'Yes' : 'No'}</p>
                    </div>
                </div>
            </div>
        `;
        booksContainer.innerHTML += bookCard;
    });

    booksContainer.style.display = 'flex';  // Ensure it's visible
};

const populateCategories = (categories) => {
    if (!categories || !Array.isArray(categories)) {
        console.error('Invalid categories data:', categories);
        document.getElementById('cards-container').innerHTML = '<p>Error loading categories.</p>';
        return;
    }

    const categoriesContainer = document.getElementById('cards-container');
    categoriesContainer.innerHTML = '';  // Clear previous content

    if (categories.length === 0) {
        categoriesContainer.innerHTML = '<p>No categories found.</p>';
        return;
    }

    // Create the table structure
    const tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Category</th>
                    <th>Hidden</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${categories.map(category => `
                    <tr class="category-row" data-id="${category.id}">
                        <td>${category.id}</td>
                        <td>${category.category}</td>
                        <td>${category.hidden ? 'Yes' : 'No'}</td>
                        <td>
                            <button class="btn btn-link" title="Edit Category" onclick="editCategory(${category.id})">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                            ${category.hidden ? `
                                <button class="btn btn-link text-warning" title="Restore Category" onclick="restoreCategory(${category.id})">
                                    <i class="fas fa-undo"></i>
                                </button>` : `
                                <button class="btn btn-link text-danger" title="Delete Category" onclick="deleteCategory(${category.id})">
                                    <i class="fas fa-trash-alt"></i>
                                </button>`}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Insert the table into the container
    categoriesContainer.innerHTML = tableHTML;
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

const restoreBook = async (bookId) => {
    try {
        const response = await axiosWithAuth('PUT', `/api/books/${bookId}`, { hidden: 0 });

        if (response.status === 200) {
            console.log('Book restored successfully:', response.data);
            showToast('Book restored successfully', 'success');
            
            // Remove the book from the displayed list or update the UI
            const bookCard = document.querySelector(`.book-card[data-id="${bookId}"]`);
            if (bookCard) {
                bookCard.remove(); // Remove the card from the DOM
            }
        } else {
            console.error('Error restoring book:', response.data.error);
            showToast('Error restoring book', 'error');
        }
    } catch (error) {
        console.error('Restore error:', error);
        showToast('Error restoring book', 'error');
    }
};

const restoreCategory = async (categoryId) => {
    try {
        const response = await axiosWithAuth('PUT', `/api/categories/${categoryId}`, { hidden: 0 });

        if (response.status === 200) {
            console.log('Category restored successfully:', response.data);
            showToast('Category restored successfully', 'success');

            // Remove the category from the displayed list or update the UI
            const categoryRow = document.querySelector(`.category-row[data-id="${categoryId}"]`);
            if (categoryRow) {
                categoryRow.remove(); // Remove the row from the DOM
            }
        } else {
            console.error('Error restoring category:', response.data.error);
            showToast('Error restoring category', 'error');
        }
    } catch (error) {
        console.error('Restore error:', error);
        showToast('Error restoring category', 'error');
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
            params: { showHidden: 1 } 
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
                                <button class="btn btn-danger" onclick="cancelEdit('user', ${user.id})">Cancel</button>
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

const editBook = async (bookId) => {
    try {
        // Check if the book is hidden by looking at the book's card in the DOM
        const bookCard = document.querySelector(`.book-card[data-id="${bookId}"]`);
        const isHidden = bookCard ? bookCard.getAttribute('data-hidden') === 'true' : false;

        // Fetch book details by ID (include showHidden if the book is hidden)
        const bookResponse = await axiosWithAuth('GET', `/api/books/${bookId}`, {}, {
            params: { showHidden: isHidden ? 1 : 0 } // Conditionally add showHidden=1
        });

        if (bookResponse.status === 200) {
            const book = bookResponse.data;

            // Fetch categories
            const categoriesResponse = await axiosWithAuth('GET', '/api/categories/');
            const categories = categoriesResponse.data;

            // Create dropdown options for categories
            const categoryOptions = categories.map(category => 
                `<option value="${category.id}" ${category.id === book.category ? 'selected' : ''}>${category.category}</option>`
            ).join('');

            if (bookCard) {
                // Replace book card with editable form including dropdown for categories
                const bookCardHTML = `
                    <div class="col-md-4 book-card" data-id="${book.id}">
                        <div class="card">
                            <div class="card-body text-center">
                                <img src="${book.cover_image ? book.cover_image : 'no_cover_yet_image.png'}" alt="Book Cover" class="book-cover" onerror="this.src='no_cover_yet_image.png';" />

                                <h5 class="card-title">
                                    <input type="text" value="${book.title}" id="edit-title-${book.id}" />
                                </h5>
                                <p class="card-text">
                                    Author: <input type="text" value="${book.author}" id="edit-author-${book.id}" />
                                </p>
                                <p class="card-text">
                                    Year Published: <input type="number" value="${book.year_published}" id="edit-year-${book.id}" />
                                </p>
                                <p class="card-text">
                                    Pages: <input type="number" value="${book.number_of_pages}" id="edit-pages-${book.id}" />
                                </p>
                                <p class="card-text">
                                    Category: <select id="edit-category-${book.id}">${categoryOptions}</select>
                                </p>
                                <button class="btn btn-success" onclick="updateBook(${book.id})">Update</button>
                                <button class="btn btn-danger" onclick="cancelEdit('book', ${book.id})">Cancel</button>
                            </div>
                        </div>
                    </div>
                `;
                // Replace the card with the form
                bookCard.outerHTML = bookCardHTML;
            } else {
                console.error(`Book card for ID ${bookId} not found.`);
            }
        } else {
            console.error('Error fetching book details:', bookResponse.data.error);
        }
    } catch (error) {
        console.error('Error fetching book:', error);
    }
};

const editCategory = async (categoryId) => {
    try {
        // Fetch category details by ID
        const categoryResponse = await axiosWithAuth('GET', `/api/categories/${categoryId}`);

        if (categoryResponse.status === 200) {
            const category = categoryResponse.data;

            // Create the editable form
            const editFormHTML = `
                <div class="category-edit-form" data-id="${category.id}">
                    <h5>Edit Category</h5>
                    <form id="edit-category-form-${category.id}">
                        <div class="mb-3">
                            <label for="edit-category-name-${category.id}">Category Name</label>
                            <input type="text" id="edit-category-name-${category.id}" value="${category.category}" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-success" onclick="updateCategory(${category.id})">Update</button>
                        <button type="button" class="btn btn-danger" onclick="cancelEdit('category', ${category.id})">Cancel</button>
                    </form>
                </div>
            `;

            // Replace the existing category row with the edit form
            const categoryRow = document.querySelector(`.category-row[data-id="${categoryId}"]`);
            if (categoryRow) {
                categoryRow.outerHTML = editFormHTML;

                // Handle form submission
                document.getElementById(`edit-category-form-${category.id}`).addEventListener('submit', (event) => {
                    event.preventDefault();
                    updateCategory(category.id);
                });
            }
        } else {
            console.error('Error fetching category details:', categoryResponse.data.error);
        }
    } catch (error) {
        console.error('Error fetching category:', error);
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

const updateBook = async (bookId) => {
    try {
        // Gather updated data from the input fields
        const title = document.getElementById(`edit-title-${bookId}`).value;
        const author = document.getElementById(`edit-author-${bookId}`).value;
        const year = parseInt(document.getElementById(`edit-year-${bookId}`).value, 10); // Convert to integer
        const pages = parseInt(document.getElementById(`edit-pages-${bookId}`).value, 10); // Convert to integer
        const category = parseInt(document.getElementById(`edit-category-${bookId}`).value, 10); // Convert to integer

        // Ensure that year and pages are valid numbers
        if (isNaN(year) || isNaN(pages) || isNaN(category)) {
            console.error('Year, Pages, and Category must be valid numbers');
            return;
        }

        // Prepare the data to be sent
        const updatedBookData = {
            title,
            author,
            year_published: year,
            number_of_pages: pages,
            category
        };

        // Send the PUT request to update book
        const response = await axiosWithAuth('PUT', `/api/books/${bookId}`, updatedBookData);

        if (response.status === 200) {
            // Successfully updated book
            console.log('Book updated successfully:', response.data);
            await getBooks(); // Fetch updated book list
        } else {
            console.error('Error updating book:', response.data.error);
        }
    } catch (error) {
        console.error('Update error:', error);
    }
};

const updateCategory = async (categoryId) => {
    try {
        const categoryName = document.getElementById(`edit-category-name-${categoryId}`).value;

        // Prepare the data to be sent
        const updatedCategoryData = {
            category: categoryName
        };

        // Send the PUT request to update the category
        const response = await axiosWithAuth('PUT', `/api/categories/${categoryId}`, updatedCategoryData);

        if (response.status === 200) {
            console.log('Category updated successfully:', response.data);
            await getCategories();  // Refresh the category list
        } else {
            console.error('Error updating category:', response.data.error);
        }
    } catch (error) {
        console.error('Update error:', error);
    }
};

// Function to handle canceling the edit
const cancelEdit = (type, id) => {
    if (type === 'user') {
        getUsers(); // Refresh the users list
    } else if (type === 'book') {
        getBooks(); // Refresh the books list
    } else if (type === 'category') {
        getCategories(); // Refresh the categories list
    } else {
        console.error(`Unknown type: ${type}`);
    }
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

const deleteBook = async (bookId) => {
    if (confirm("Are you sure you want to delete this book?")) {
        try {
            // Send the DELETE request to delete the book
            await axiosWithAuth('DELETE', `/api/books/${bookId}`);

            // Fetch and repopulate the books after deletion
            await getBooks();
        } catch (error) {
            console.error('Error deleting book:', error);
        }
    }
};

const deleteCategory = async (categoryId) => {
    if (confirm("Are you sure you want to delete this category?")) {
        try {
            // Send the DELETE request to delete the category
            await axiosWithAuth('DELETE', `/api/categories/${categoryId}`);

            // Fetch and repopulate categories after deletion
            await getCategories();
        } catch (error) {
            console.error('Error deleting category:', error);
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

const filterCities = () => {
    const showHiddenCheckbox = document.getElementById('show-hidden-cities');
    const hiddenOnlyCheckbox = document.getElementById('hidden-only-cities');
    const cityRows = document.querySelectorAll('.city-row'); // Use the appropriate class for city rows

    // Disable "Show Hidden" checkbox if "Hidden Only" is checked
    if (hiddenOnlyCheckbox.checked) {
        showHiddenCheckbox.checked = true; // Check it
        showHiddenCheckbox.disabled = true; // Disable it
    } else {
        showHiddenCheckbox.disabled = false; // Re-enable it
    }

    cityRows.forEach(row => {
        const isHidden = row.getAttribute('data-hidden') === 'true';

        if (hiddenOnlyCheckbox.checked) {
            // Show only hidden cities
            row.style.display = isHidden ? 'table-row' : 'none';
        } else if (showHiddenCheckbox.checked) {
            // Show all cities
            row.style.display = 'table-row';
        } else {
            // Show only non-hidden cities
            row.style.display = isHidden ? 'none' : 'table-row';
        }
    });
};

const filterBooks = () => {
    const showHiddenCheckbox = document.getElementById('show-hidden-books');
    const hiddenOnlyCheckbox = document.getElementById('hidden-only-books');
    const bookCards = document.querySelectorAll('.book-card');

    // Disable "Show Hidden" checkbox if "Hidden Only" is checked
    if (hiddenOnlyCheckbox.checked) {
        showHiddenCheckbox.checked = true; // Check it
        showHiddenCheckbox.disabled = true; // Disable it
    } else {
        showHiddenCheckbox.disabled = false; // Re-enable it
    }

    bookCards.forEach(card => {
        const isHidden = card.getAttribute('data-hidden') === 'true';

        if (hiddenOnlyCheckbox.checked) {
            // Show only hidden books
            card.style.display = isHidden ? 'block' : 'none';
        } else if (showHiddenCheckbox.checked) {
            // Show all books
            card.style.display = 'block';
        } else {
            // Show only non-hidden books
            card.style.display = isHidden ? 'none' : 'block';
        }
    });
};

const filterCategories = () => {
    const showHiddenCheckbox = document.getElementById('show-hidden-categories');
    const hiddenOnlyCheckbox = document.getElementById('hidden-only-categories');
    const categoryRows = document.querySelectorAll('.category-row');

    // Disable "Show Hidden" checkbox if "Hidden Only" is checked
    if (hiddenOnlyCheckbox.checked) {
        showHiddenCheckbox.checked = true; // Check it
        showHiddenCheckbox.disabled = true; // Disable it
    } else {
        showHiddenCheckbox.disabled = false; // Re-enable it
    }

    categoryRows.forEach(row => {
        const isHidden = row.getAttribute('data-hidden') === 'true';

        if (hiddenOnlyCheckbox.checked) {
            // Show only hidden categories
            row.style.display = isHidden ? 'table-row' : 'none';
        } else if (showHiddenCheckbox.checked) {
            // Show all categories
            row.style.display = 'table-row';
        } else {
            // Show only non-hidden categories
            row.style.display = isHidden ? 'none' : 'table-row';
        }
    });
};

// Run on page load
window.onload = loadUserInfo;

document.getElementById('users-link').addEventListener('click', async (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    wipeMainContent(); // Wipe the main content div clean first
    showUserSearchBar(); // Show search bar and checkboxes
    await getUsers(); // Fetch and display users
});

document.getElementById('cities-link').addEventListener('click', async (e) => {
    e.preventDefault();  // Prevent default anchor behavior
    wipeMainContent(); // Clear main content
    showCitySearchBar();  // Show the city search bar
    await getCities();  // Fetch and display cities
});

document.getElementById('books-link').addEventListener('click', async (e) => {
    e.preventDefault();  // Prevent default anchor behavior
    wipeMainContent();// Wipe the main content div clean first
    showBookSearchBar();  // Show the book search bar and checkboxes
    await getBooks();  // Fetch and display books
});

document.getElementById('categories-link').addEventListener('click', async (e) => {
    e.preventDefault();  // Prevent default anchor behavior
    wipeMainContent();  // Wipe the main content div clean first
    showCategorySearchBar();  // Show the category search bar and checkboxes
    await getCategories();  // Fetch and display categories
});

document.getElementById('book-types-link').addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    wipeMainContent(); // Clear the main content
    getBookTypes(); // Fetch and display the book types
});
