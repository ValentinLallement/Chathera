export interface User {
    id: string
    email: string
    name: string
}

export interface AuthState {
    accessToken: string | null
    user: User | null
    setToken: (token: string) => void
    setUser: (user: User) => void
    clearAuth: () => void
}