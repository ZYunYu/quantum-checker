import React, { useEffect, useState } from 'react';

const UserIdDisplay: React.FC = () => {
    const [userId, setUserId] = useState<string | null>(null);

    useEffect(() => {
        fetch('http://localhost:8000/api/session/', {
            credentials: 'include',
        })
        .then(response => response.json())
        .then(data => {
            if (data.isauthenticated) {
                setUserId(data.userId.toString());
            } else {
                setUserId(null);
            }
        })
        .catch(error => console.error('Error fetching user session:', error));
    }, []);

    return (
        <div style={{ position: 'fixed', right: 0, bottom: 0, padding: '10px', backgroundColor: '#f0f0f0' }}>
            {userId ? `User ID: ${userId}` : 'No active session'}
        </div>
    );
};

export default UserIdDisplay;
