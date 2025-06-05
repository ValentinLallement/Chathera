/***************************** Imports *****************************/





/**************************** Settings ****************************/

const BASE_URL = import.meta.env.VITE_API_URL

export const urls = {
    "signUp": `${BASE_URL}/register`,
    "health": `${BASE_URL}/health`,
}


/****************************** Auth *****************************/

export interface SignUpParams { 
    name: string;    
    username: string;
    email: string;
    password: string;
}

export interface SignUpResponse {
 username: string;
 email: string;
 id: string;
 name: string;
 profile_picture: any;
 subscription: string;
}

export async function signUp({
  name,
  username,
  email,
  password,
}: SignUpParams): Promise<SignUpResponse> {
  const res = await fetch(`${BASE_URL}/register`, {
    method: "POST",
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