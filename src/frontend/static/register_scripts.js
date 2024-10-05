// Define the base URL as a constant
const SERVER = 'http://127.0.0.1:5000/';

// Arrow function to handle user registration
const registerUser = () => {
    // Get values from input fields
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const city = document.getElementById('city').value; // Assuming this is the city ID
    const age = document.getElementById('age').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Check if passwords match
    if (password !== confirmPassword) {
        document.getElementById("error-message").innerText = "Passwords do not match.";
        return; // Exit function if passwords don't match
    }

    console.log('Registering with:', { name, email, city, age, password }); // Debug log

    // Make the POST request to the register endpoint
    axios.post(`${SERVER}api/users/register`, {
        name: name,
        email: email,
        city: city,
        age: age,
        password: password
    })
    .then(response => {
        // Handle successful registration
        console.log("Registration successful:", response.data);
        // Redirect to login page or home page after successful registration
        window.location.href = 'login.html'; 
    })
    .catch(error => {
        console.error("Registration error:", error);
        // Handle error response
        const errorMessage = error.response ? error.response.data.error : "An error occurred during registration.";
        document.getElementById("error-message").innerText = errorMessage;
    });
}

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Attach the registerUser arrow function to the register form's submit event
    document.getElementById('register-form').onsubmit = (event) => {
        event.preventDefault(); // Prevent the default form submission
        registerUser(); // Call the registerUser function
    }

    // Attach click event for the login button
    document.getElementById('login-button').onclick = () => {
        // Redirect to the login page
        window.location.href = 'login.html'; // Redirect to login page
    }
});
