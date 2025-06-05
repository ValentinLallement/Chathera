/***************************** Imports *****************************/





/**************************** Settings ****************************/

const BASE_URL = import.meta.env.VITE_API_URL





/***************************** Tests *****************************/

export interface HealthResponse {
    status: string;
}

export async function getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }
    return res.json();
  }