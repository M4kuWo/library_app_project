// Define the base URL as a constant
const SERVER = 'http://127.0.0.1:5000/';

// Arrow function to handle user login
const loginUser = () => {
    // Get email and password values from input fields
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    console.log('Logging in with:', { email, password }); // Debug log

    // Make the POST request to the login endpoint
    axios.post(`${SERVER}api/users/login`, {
        email: email,
        password: password
    })
    .then(response => {
        // Extract the access token and user profile from the response
        const accessToken = response.data.access_token; // Get the token
        const userProfile = response.data.user.profile; // Access the nested profile

        // Log the retrieved profile
        console.log("Logged in successfully with profile:", userProfile);
        console.log("Access Token:", accessToken);

        // Store token for further use (e.g., local storage)
        localStorage.setItem('userToken', accessToken);

        // Redirect based on user profile
        if (userProfile === 1 || userProfile === 2) {
            // Redirect for superadmin (profile 1) or admin (profile 2)
            window.location.href = 'home_admin.html'; 
        } else if (userProfile === 3) {
            // Redirect for regular user (profile 3)
            window.location.href = 'home_user.html'; 
        } else {
            // Handle unexpected profiles
            document.getElementById("error-message").innerText = "Invalid user profile.";
        }
    })
    .catch(error => {
        console.error("Login error:", error);
        // Handle error response
        const errorMessage = error.response ? error.response.data.message : "An error occurred during login.";
        document.getElementById("error-message").innerText = errorMessage;
    });
}

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Attach the loginUser arrow function to the login form's submit event
    document.getElementById('login-form').onsubmit = (event) => {
        event.preventDefault(); // Prevent the default form submission
        loginUser(); // Call the loginUser function
    }

    // Attach click event for the register button (if applicable)
    document.getElementById('register-button').onclick = () => {
        // Redirect to register page
        window.location.href = 'register.html'; // Redirect to register page
    }
});
