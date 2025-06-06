export interface User {
    id: string;
    email: string;
    name: string;
    username: string;
    profile_picture: string | null;
    subscription: string | null;
}

export interface AuthState {
    accessToken: string | null;
    user: User | null;
    setToken: (token: string) => void;
    setUser: (user: User) => void;
    clearAuth: () => void;
}