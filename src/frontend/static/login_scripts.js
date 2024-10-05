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

        // Check if the user profile is valid (1, 2, or 3)
        if ([1, 2, 3].includes(userProfile)) {
            // Handle valid user profile
            console.log("Logged in successfully with profile:", userProfile);
            console.log("Access Token:", accessToken);
            
            // Store token for further use (e.g., local storage)
            localStorage.setItem('userToken', accessToken);
            
            // Redirect to Home_admin.html
            window.location.href = 'Home_admin.html'; 
        } else {
            // Handle invalid user profile
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
        // You can add logic for registration here, e.g., redirect to the registration page
        window.location.href = 'register.html'; // Redirect to register page
    }
});
