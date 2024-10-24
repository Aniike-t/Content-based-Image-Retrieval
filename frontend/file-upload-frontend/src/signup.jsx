import React, { useState } from 'react';
import { Card, Form, Button } from 'react-bootstrap'; // Make sure to install react-bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import { useNavigate } from 'react-router-dom';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
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
        setMessage('');

        try {
            const response = await fetch('http://localhost:5000/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                navigate('/login');
            } else {
                setMessage(data.error);
            }
        } catch (error) {
            console.error('An error occurred', error);
            // CORS error handling
            if (error instanceof TypeError && error.message === 'NetworkError when attempting to fetch resource.') {
                setMessage('CORS error: Unable to reach the server. Please check your API endpoint.');
            } else {
                setMessage('An unexpected error occurred. Please try again.');
            }
        }
    };

    return (
        <section className="vh-100">
            <div className="container-fluid h-custom">
                <div className="row d-flex justify-content-center align-items-center h-100">
                    <div className="col-md-8 col-lg-6 col-xl-4">
                        <Card>
                            <Card.Body>
                                <h2 className="text-center">Sign Up</h2>
                                {message && <div className="alert alert-danger">{message}</div>} {/* Display error message */}
                                <Form onSubmit={handleSubmit}>
                                    <Form.Group className="mb-3">
                                        <Form.Control
                                            type="text"
                                            placeholder="Username"
                                            value={username}
                                            onChange={(e) => setUsername(e.target.value)}
                                            required
                                            id="signupinputs"
                                        />
                                    </Form.Group>
                                    <Form.Group className="mb-3">
                                        <Form.Control
                                            type="password"
                                            placeholder="Password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            required
                                            id="signupinputs"
                                        />
                                    </Form.Group>
                                    <Button type="submit" variant="secondary" className="w-100">Signup</Button>
                                </Form>
                            </Card.Body>
                        </Card>
                        <div className="text-center text-lg-start mt-4 pt-2">
                            <p className="small fw-bold mt-2 pt-1 mb-0">
                                Already have an account? <a href="/login" className="link-danger">Login</a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Signup;
