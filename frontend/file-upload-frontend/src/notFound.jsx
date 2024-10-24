import React from 'react';

const NotFound = () => {
    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <h1 style={{color:'white'}}>404 - Page Not Found</h1>
            <p style={{color:'white'}}>The page you are looking for does not exist.</p>
            <p style={{color:'white'}}><a href='/login'>Login Page</a></p>
        </div>
    );
};

export default NotFound;