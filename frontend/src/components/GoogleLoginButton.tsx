import { generateCodeVerifier, generateCodeChallenge } from "../utils/oauth";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID!;
const REDIRECT_URI = `${window.location.origin}/auth/google/callback`;
const SCOPE = "openid profile email";

export function GoogleLoginButton({
  children,
}: {
  children?: React.ReactNode;
}) {
  const onClick = async () => {
    const verifier = generateCodeVerifier();
    localStorage.setItem("code_verifier", verifier);

    const challenge = await generateCodeChallenge(verifier);
    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      response_type: "code",
      scope: SCOPE,
      code_challenge: challenge,
      code_challenge_method: "S256",
      // optional: state for CSRF
    });

    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  };

  return <div onClick={onClick}>{children}</div>;
}
