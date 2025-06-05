/***************************** Imports *****************************/





/**************************** Settings ****************************/

const BASE_URL = import.meta.env.VITE_API_URL

export const urls = {
    "signUp": `${BASE_URL}/register`,
    "health": `${BASE_URL}/health`,
}


/****************************** Auth *****************************/

export interface SignUpParams {
    fullName: string;
    username: string;
    email: string;
    password: string;
}

export interface SignUpResponse {

}

export async function signUp({fullName, username, email, password}: SignUpParams) {
    const res = await fetch(urls.signUp, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ fullName, username, email, password }),
      });

      if (!res.ok) {
        const errorText = await res.text().catch(() => res.statusText);
        throw new Error(`signUp failed (status ${res.status}): ${errorText}`);
      }
    

      const data: SignUpResponse = await res.json();
      return data;
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