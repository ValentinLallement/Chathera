/***************************** Imports *****************************/

/**************************** Settings ****************************/

const BASE_URL = import.meta.env.VITE_API_URL

export const urls = {
    "signUp": `${BASE_URL}/register`,
    "logIn": `${BASE_URL}/token`,
    "health": `${BASE_URL}/health`,
    "me": `${BASE_URL}/user/me`,
    "bots": `${BASE_URL}/my_bots`,
    "logout": `${BASE_URL}/logout`,
    "refresh": `${BASE_URL}/refresh`,
    "createBot": `${BASE_URL}/create_bot`,
    "deleteBot": `${BASE_URL}/delete_bot`,
    "conversations": `${BASE_URL}/conversations`,
    "messages": `${BASE_URL}/conversations/messages`,
    "stripe": `${BASE_URL}/stripe/create-checkout-session`,
    "subscriptionInfo": `${BASE_URL}/user/subscription/infos`,
    "requestPasswordReset": `${BASE_URL}/user/request-password-reset`,
    "changePassword": `${BASE_URL}/user/change-password`,
    "saveAvatar": `${BASE_URL}/save-avatar`,
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

export async function refreshToken(): Promise<LogInResponse> {
  const res = await fetch(urls.refresh, {
    method: "POST",
    credentials: "include", // pour envoyer le cookie contenant le refresh_token
    headers: {
      "Content-Type": "application/json"
    }
  });

  let payload: { detail?: string; [key: string]: any };

  try {
    payload = await res.json();
  } catch {
    throw new Error("Erreur lors du décodage de la réponse du serveur.");
  }

  if (!res.ok) {
    throw new Error(payload.detail || `Échec du rafraîchissement du token (statut ${res.status})`);
  }

  // On attend { message, access_token, token_type }
  const { access_token, token_type } = payload;

  if (!access_token || !token_type) {
    throw new Error("Réponse invalide du serveur lors du rafraîchissement.");
  }

  return {
    message: payload.message ?? "",
    access_token,
    token_type,
  };
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

export interface SubscriptionInfo {
    id: string;
    user_id: string;
    plan: string;
    start_date: string;
    message_count: number;
    message_limit: number | null;
    last_reset: string;
    status: string;
    remaining: number | null;
}

export interface SubscriptionInfoResponse {
    subscriptions: SubscriptionInfo | null;
}

export async function getSubscriptionInfo(token: string): Promise<SubscriptionInfoResponse> {
  const res = await fetch(urls.subscriptionInfo, {
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

/***************************** Bots ******************************/

export interface CreateBotParams {
    name: string;
    gender: "Male" | "Female";
    personality: "Friendly" | "Professional" | "Casual" | "Serious" | "Sweet";
  }

export interface CreateBotResponse {
  bot_id: string;
  conversation_id: string;
}

export async function createBot(
  token: string,
  params: CreateBotParams
): Promise<CreateBotResponse> {
  const res = await fetch(urls.createBot, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(params),
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

interface LastMessage {
  content: string;
  sender: "user" | "bot";
  created_at: string; // ISO date string
}
interface getBotsResponse {
  bot_id: string;
  name: string;
  gender: "Male" | "Female";
  avatar_url: string | null;
  url: string | null; // URL du modèle 3D
  last_message?: LastMessage | null; // facultatif ou null si pas de message
  type: "free" | "premium" | "payg"; // type de bot
}
  

export async function getBots(token: string): Promise<getBotsResponse[]> {
  const res = await fetch(`${urls.bots}`, {
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

export async function deleteBot(token: string, botId: string): Promise<void> {
  const res = await fetch(`${urls.deleteBot}/${botId}`, {
    method: "DELETE",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
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
}

/************************* Conversations *************************/
      
export interface getConversationsResponse {
  bot_id: string;
  id: string;
  user_id: string;
  created_at: string;
}

export async function getConversations(token: string): Promise<getConversationsResponse[]> {
  const res = await fetch(`${urls.conversations}`, {
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

export interface getMessagesInConversationResponse {
  messages: {
    content: string;
    user_id: string;
    conversation_id: string;
    id: string;
    created_at: string;
  }[];
  has_access: boolean;
}

export async function getMessagesInConversation(
  token: string,
  conversationId: string
): Promise<getMessagesInConversationResponse> {
  const res = await fetch(`${urls.messages}?conversation_id=${conversationId}`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ conversation_id: conversationId }),
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

// Helper function to handle API calls with token refresh
export async function apiCallWithRefresh<T>(
  apiFn: () => Promise<T>,
  setToken: (token: string) => void
): Promise<T> {
  try {
    return await apiFn();
  } catch (error: any) {
    if (error?.message?.includes("401") || error?.message?.includes("expired")) {
      try {
        const refreshResponse = await refreshToken();
        setToken(refreshResponse.access_token);
        return await apiFn();
      } catch (refreshError) {
        throw new Error("Session expired. Please log in again.");
      }
    }
    throw error;
  }
}

/***************************** Stripe *************************/

export interface CreateCheckoutSessionParams {
  plan: "premium" | "payg";
}

export interface CreateCheckoutSessionResponse {
  url: string;
}

export async function createCheckoutSession(
  token: string,
  params: CreateCheckoutSessionParams
): Promise<CreateCheckoutSessionResponse> {
  const res = await fetch(urls.stripe, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    let payload: { detail?: string; [key: string]: any } = { detail: "" };
    try {
      payload = await res.json();
    } catch {
      throw new Error("An unexpected error occurred.");
    }

    if (payload.detail) {
      throw new Error(payload.detail);
    } else {
      throw new Error(`Unknown error (status ${res.status})`);
    }
  }
  return res.json();
}

export interface RequestPasswordResetParams {
  email: string;
}

export async function requestPasswordReset({ email }: RequestPasswordResetParams): Promise<void> {
  const res = await fetch(urls.requestPasswordReset, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
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
}

export interface ChangePasswordParams {
  old_password: string;
  new_password: string;
}

export async function changePassword(token: string, { old_password, new_password }: ChangePasswordParams): Promise<void> {
  const res = await fetch(urls.changePassword, {
    method: "POST",
    credentials: "include",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ old_password, new_password }),
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
}


import axios from "axios";
export async function resetPassword(token: string, data: { new_password: string }) {
  // L’URL doit correspondre à celle de ton backend (port + chemin)
  return axios.post(
    `http://localhost:8000/api/user/reset-password`,
    {
      new_password: data.new_password,
      token: token,       // token envoyé dans le body aussi
    }
  );
}

export interface SaveAvatarParams {
  bot_id: string;
  glb_url: string;
}

export interface SaveAvatarResponse {
  message: string;
  bot_id: string;
  avatar_url: string;
}

export async function saveAvatar(
  token: string,
  params: SaveAvatarParams
): Promise<SaveAvatarResponse> {
  const res = await fetch(urls.saveAvatar, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(params),
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