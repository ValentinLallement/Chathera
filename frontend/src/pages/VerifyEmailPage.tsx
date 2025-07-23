import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function VerifyEmailPage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Email passé via state
  const email = (location.state as { email?: string })?.email || "";

  // Tableau pour les 6 chiffres du code
  const [codeDigits, setCodeDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);

  // Gérer la saisie / coller dans chaque case
  const handleChange = (index: number, value: string) => {
    // Autoriser uniquement chiffres
    if (!/^\d*$/.test(value)) return;

    // Si l'utilisateur colle un code entier (6 chiffres) dans une case, on remplit tout
    if (value.length === 6 && /^\d{6}$/.test(value)) {
      setCodeDigits(value.split(""));
      // Focus sur dernier input
      const lastInput = document.getElementById(`code-digit-5`);
      lastInput?.focus();
      return;
    }

    // Sinon, remplir uniquement la case concernée avec max 1 chiffre
    if (value.length > 1) return; // pas plus de 1 caractère ici

    const newCode = [...codeDigits];
    newCode[index] = value;
    setCodeDigits(newCode);

    // Focus sur case suivante si chiffre saisi
    if (value && index < 5) {
      const nextInput = document.getElementById(`code-digit-${index + 1}`);
      nextInput?.focus();
    }
  };

  // Soumettre le code
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const code = codeDigits.join("");
    if (code.length !== 6) {
      toast.error("Veuillez saisir les 6 chiffres du code.");
      return;
    }
    if (!email) {
      toast.error("Adresse email manquante.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/verify-email-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Erreur lors de la vérification");
      }

      const data = await res.json();
      toast.success(data.message || "Email vérifié avec succès !");

      setTimeout(() => {
        navigate("/auth");
      }, 1500);
    } catch (err: any) {
      toast.error(err.message || "Erreur lors de la vérification du code.");
    } finally {
      setIsLoading(false);
    }
  };

  // Fonction pour renvoyer le mail de vérification (réappeler /register)
  const handleResend = async () => {
    if (!email) {
      toast.error("Adresse email manquante.");
      return;
    }
    setIsResending(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }), // envoyer au minimum l'email, ajouter autres champs si besoin
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Erreur lors de l'envoi du code");
      }

      toast.success("Code de vérification renvoyé !");
    } catch (err: any) {
      toast.error(err.message || "Erreur lors de la tentative de renvoi.");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-zinc-950 px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-white">Vérification de l'email</h1>
      <p className="text-gray-400 mb-8 text-center max-w-sm">
        Un code à 6 chiffres a été envoyé à <strong>{email}</strong>. Merci de le saisir ci-dessous.
      </p>

      <form
        onSubmit={handleSubmit}
        className="flex gap-2 justify-center mb-6"
        aria-label="Formulaire de saisie du code de vérification"
      >
        {codeDigits.map((digit, i) => (
          <input
            key={i}
            id={`code-digit-${i}`}
            type="text"
            inputMode="numeric"
            maxLength={6} // permet coller jusqu'à 6 chiffres
            value={digit}
            onChange={(e) => handleChange(i, e.target.value)}
            className="w-12 h-12 text-center text-2xl rounded-md bg-black/20 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
            autoComplete="one-time-code"
            aria-label={`Chiffre ${i + 1} du code`}
          />
        ))}
      </form>

      <button
        disabled={isLoading}
        type="submit"
        onClick={handleSubmit}
        className="px-8 py-3 bg-violet-600 rounded-md text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed mb-4"
      >
        {isLoading ? "Vérification..." : "Vérifier le code"}
      </button>

      <button
        disabled={isResending}
        type="button"
        onClick={handleResend}
        className="text-sm text-gray-400 underline hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isResending ? "Renvoyer..." : "Renvoyer le code"}
      </button>
    </div>
  );
}
