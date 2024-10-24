import React, { useEffect, useState } from "react";
import axios from "axios";
import { Form, Button, Card } from "react-bootstrap";
import './login.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate(); // Initialize useNavigate


    // Check for UUID when component mounts
    useEffect(() => {
      const uuid = localStorage.getItem('uuid');
      console.log(uuid);
      if (uuid){
        localStorage.setItem('uuid', null);
      }
  }, [navigate]); // Dependency array includes navigate


  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/login", {
        username,
        password,
      });
      const uuid = response.data.token;
      if (uuid) {
        localStorage.setItem('uuid', uuid);
        console.log(uuid);
        navigate('/search');
      }
    } catch (error) {
      // Additional try-catch block for better error handling
      try {
        if (error.response) {
          // Server responded with a status other than 2xx
          console.error("Login failed:", error.response.data.error);
        } else if (error.request) {
          // The request was made but no response was received
          console.error("Login failed: No response received");
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error("Login failed:", error.message);
        }
      } catch (nestedError) {
        console.error("An error occurred while handling the error:", nestedError);
      }
    }
  };

  return (
    <section className="vh-100">
      <div className="container-fluid h-custom">
        <div className="row d-flex justify-content-center align-items-center h-100">
          <div className="col-md-9 col-lg-6 col-xl-5">
            <img 
              src="login.svg" 
              className="img-fluid" 
              alt="Sample"
            />
          </div>
          <div className="col-md-8 col-lg-6 col-xl-4 offset-xl-1">
            <Card>
              <Card.Body>
                <h2 className="text-center">Sign In</h2>
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Control
                      type="text"
                      placeholder="Username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      id="logininputs"
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Control
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      id="logininputs"
                    />
                  </Form.Group>
                  <Button type="submit" variant="secondary" className="w-100">Login</Button>
                </Form>
              </Card.Body>
            </Card>
            <div className="text-center text-lg-start mt-4 pt-2">
              <p className="small fw-bold mt-2 pt-1 mb-0">
                Don't have an account? <a href="/signup" className="link-danger">Register</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Login;
