/***************************** Imports *****************************/

/**************************** Settings ****************************/

const BASE_URL = import.meta.env.VITE_API_URL

export const urls = {
    "signUp": `${BASE_URL}/register`,
    "logIn": `${BASE_URL}/token`,
    "health": `${BASE_URL}/health`,
    "me": `${BASE_URL}/user/me`,
    "logout": `${BASE_URL}/logout`,
}


/****************************** Auth *****************************/

export interface SignUpParams { 
    name: string;    
    username: string;
    email: string;
    password: string;
}

export interface SignUpResponse {
    id: string;
    email: string;
    name: string;
    username: string;
    profile_picture: string | null;
    subscription: string | null;
}

export async function signUp({
  name,
  username,
  email,
  password,
}: SignUpParams): Promise<SignUpResponse> {
  const res = await fetch(urls.signUp, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, username, email, password }),
  });

  if (!res.ok) {
    let payload: { detail?: string; [key: string]: any } = { detail: "" };
    try {
      payload = await res.json();
    } catch {
      throw new Error("Une erreur inattendue est survenue.");
    }

    if (payload.detail) {
      throw new Error(payload.detail);
    } else {
      throw new Error(`Erreur inconnue (status ${res.status})`);
    }
  }
  return res.json();
}

export interface LogInParams {
  login: string;
  password: string;
}

export interface LogInResponse {
  message: string;
  access_token: string;
  token_type: string;
}

export async function logIn({login, password}: LogInParams): Promise<LogInResponse> {
  const res = await fetch(urls.logIn, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login, password }),
  });

  if (!res.ok) {
    let payload: { detail?: string; [key: string]: any } = { detail: "" };
    try {
      payload = await res.json();
    } catch {
      throw new Error("Une erreur inattendue est survenue.");
    }

    if (payload.detail) {
      throw new Error(payload.detail);
    } else {
      throw new Error(`Erreur inconnue (status ${res.status})`);
    }
  }
  return res.json();
}

export async function logout(): Promise<void> {
  const res = await fetch(urls.logout, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error("Logout failed");
  }
}

/***************************** Users *****************************/

export interface MeResponse {
    id: string;
    email: string;
    name: string;
    username: string;
    profile_picture: string | null;
    subscription: string | null;
}

export async function getMe(token: string): Promise<MeResponse> {
  const res = await fetch(urls.me, {
    method: "GET",
    credentials: "include",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
  });

  if (!res.ok) {
    let payload: { detail?: string; [key: string]: any } = { detail: "" };
    try {
      payload = await res.json();
    } catch {
      throw new Error("Une erreur inattendue est survenue.");
    }

    if (payload.detail) {
      throw new Error(payload.detail);
    } else {
      throw new Error(`Erreur inconnue (status ${res.status})`);
    }
  }
  return res.json();
}

/***************************** Tests *****************************/

export interface HealthResponse {
    status: string;
}

export async function getHealth(): Promise<HealthResponse> {
    const res = await fetch(urls.health);
    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }
    return res.json();
  }