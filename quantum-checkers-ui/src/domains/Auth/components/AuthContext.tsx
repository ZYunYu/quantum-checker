import React, {createContext, useState, useContext, ReactNode, useEffect, useCallback} from 'react';
import {apiRequest, SessionInfo} from '../../../shared/api';

interface AuthContextType {
  isAuthenticated: boolean;
  loading: boolean;
  userId: number | null;
  isStaff: boolean;
  refreshSession: () => Promise<void>;
}
const AuthContext = createContext<AuthContextType>(null!);
export const AuthProvider: React.FC<{children: ReactNode}> = ({children}) => {
  const [session, setSession] = useState<SessionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshSession = useCallback(async () => {
    try {
      setSession(await apiRequest<SessionInfo>('/api/session/'));
    } catch {
      setSession(null);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {void refreshSession();}, [refreshSession]);
  return <AuthContext.Provider value={{
    isAuthenticated: session?.isauthenticated || false, loading,
    userId: session?.userId ?? null, isStaff: session?.isStaff || false, refreshSession,
  }}>{children}</AuthContext.Provider>;
};
export const useAuth = () => useContext(AuthContext);
export default AuthContext;
