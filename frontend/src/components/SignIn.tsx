import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/SignIn.css";

const SignIn: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSignIn = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/signin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.token); // Store token in localStorage
        navigate("/forecast");
      } else {
        const data = await response.json();
        setErrorMessage(data.message); // Set error message received from backend
      }
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };

  return (
    <div className="signin-container">
      <h1>Sign in</h1>
      {errorMessage && <p className="error-message">{errorMessage}</p>}{" "}
      {/* Display error message if present */}
      <form>
        <div className="mb-3">
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            type="text"
            className="form-control"
            id="username"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            type="password"
            className="form-control"
            id="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSignIn}
        >
          Sign In
        </button>
        <p className="signup-link">
          Don't have an account? <Link to="/signup">Sign up here</Link>
        </p>
      </form>
    </div>
  );
};

export default SignIn;
