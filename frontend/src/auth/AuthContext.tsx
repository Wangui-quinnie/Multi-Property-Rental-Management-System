import { createContext, useState, useEffect, ReactNode } from "react";
import { apiClient } from "../api/client";

export type Role = "ADMIN" | "LANDLORD" | "TENANT";

export interface User {
  id: string;
  email: string;
  role: Role;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setIsLoading(false);
      return;
    }

    apiClient
      .get("/auth/profile/")
      .then((res) => setUser(res.data.data))
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      })
      .finally(() => setIsLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const { data } = await apiClient.post("/auth/login/", { email, password });
    localStorage.setItem("access_token", data.data.access);
    localStorage.setItem("refresh_token", data.data.refresh);
    setUser(data.data.user);
  }

  async function logout() {
    const refreshToken = localStorage.getItem("refresh_token");
    try {
      await apiClient.post("/auth/logout/", { refresh: refreshToken });
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}