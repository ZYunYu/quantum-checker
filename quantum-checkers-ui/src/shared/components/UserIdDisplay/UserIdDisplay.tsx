import React from 'react';
import {useAuth} from '../../../domains/Auth/components/AuthContext';

const UserIdDisplay: React.FC = () => {
  const {userId, isStaff} = useAuth();
  return <div className="session-display">
    {userId !== null ? `User ID: ${userId}` : 'Guest'}
    {isStaff && <> · <a href="/admin/">Edit levels</a></>}
  </div>;
};
export default UserIdDisplay;
