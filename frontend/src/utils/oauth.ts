// generate a random string (code_verifier)
export function generateCodeVerifier(length = 128): string {
    const array = new Uint8Array(length);
    window.crypto.getRandomValues(array);
    return Array.from(array)
      .map(b => ("00" + b.toString(16)).slice(-2))
      .join('');
  }
  
  // crypto.subtle to SHA-256 and base64url-encode
  export async function generateCodeChallenge(v: string): Promise<string> {
    const data = new TextEncoder().encode(v);
    const digest = await window.crypto.subtle.digest('SHA-256', data);
    const base64 = btoa(String.fromCharCode(...new Uint8Array(digest)));
    return base64
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
  }