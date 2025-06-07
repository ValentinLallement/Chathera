import { use, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuthStore } from "../stores/authStore";
import { getMe } from "../api/api";

export default function GoogleCallback() {
  const navigate = useNavigate();
  const setToken = useAuthStore((state) => state.setToken);
  const setUser = useAuthStore((state) => state.setUser);
  const [tokens, setTokens] = useState<{
    id_token: string;
    access_token: string;
  } | null>(null);

  useEffect(() => {
    const verifier = localStorage.getItem("code_verifier");
    if (!verifier) {
      toast.error("Login failed: missing verifier");
      navigate("/auth");
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (!code) {
      toast.error("Login failed: no code returned");
      navigate("/auth");
      return;
    }

    (async () => {
      try {
        const body = new URLSearchParams({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          client_secret: import.meta.env.VITE_GOOGLE_CLIENT_SECRET,
          grant_type: "authorization_code",
          code,
          code_verifier: verifier,
          redirect_uri: `${window.location.origin}/auth/google/callback`,
        });

        const res = await fetch("https://oauth2.googleapis.com/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString(),
        });

        if (!res.ok) {
          const err = await res.text();
          throw new Error(err);
        }

        const { id_token, access_token } = await res.json();
        setTokens({ id_token, access_token });

        const appRes = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/auth/google`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              token: id_token,
              access_token,
            }),
          }
        );

        if (!appRes.ok) {
          const err = await appRes.text();
          toast.error("Login failed: " + err);
          throw new Error(err);
        }
        const data = await appRes.json();
        setToken(data.access_token);
        const userData = await getMe(data.access_token);
        setUser(userData);
        navigate("/dashboard");
      } catch (err: any) {
        console.error(err);
        toast.error("Token exchange failed: " + err.message);
        navigate("/auth");
      }
    })();
  }, [navigate]);

  if (!tokens) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-purple-500 border-t-transparent animate-slow-spin mx-auto" />
            <div className="absolute inset-0 animate-pulse rounded-full bg-purple-500/10" />
          </div>
          <p className="text-white/80 animate-floatIn font-medium">
            Authenticating
            <span className="inline-flex">
              <span className="animate-bounce">.</span>
              <span className="animate-bounce-delay-1">.</span>
              <span className="animate-bounce-delay-2">.</span>
            </span>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex items-center justify-center">
      <div className="text-center space-y-4 animate-floatIn">
        <div className="w-16 h-16 mx-auto relative">
          <svg
            className="w-full h-full text-green-500 animate-bounceScale"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="absolute inset-0 rounded-full gradient-conic animate-slow-spin opacity-50" />
        </div>
        <p className="text-white/80 font-medium">
          Login successful! Redirecting...
        </p>
      </div>
    </div>
  );
}
