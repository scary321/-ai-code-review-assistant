import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("cs_token");
    if (!token) {
      setReady(true);
      return;
    }
    api
      .me()
      .then((res) => setUser(res.user))
      .catch(() => localStorage.removeItem("cs_token"))
      .finally(() => setReady(true));
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await api.login(email, password);
    localStorage.setItem("cs_token", res.token);
    setUser(res.user);
  }, []);

  const register = useCallback(async (name, email, password) => {
    const res = await api.register(name, email, password);
    localStorage.setItem("cs_token", res.token);
    setUser(res.user);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("cs_token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
