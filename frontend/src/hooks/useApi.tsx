import { useQuery, useMutation } from "@tanstack/react-query";
import type { UseMutationResult } from "@tanstack/react-query";
import {
  getHealth,
  logIn,
  signUp,
  getMe,
  getBots,
  apiCallWithRefresh,
  refreshToken,
  createBot,
  getConversations,
  getMessagesInConversation,
  createCheckoutSession,
  getSubscriptionInfo,
  deleteBot,
} from "../api/api";
import type {
  CreateBotParams,
  CreateBotResponse,
  LogInParams,
  LogInResponse,
  SignUpParams,
  SignUpResponse,
  CreateCheckoutSessionParams,
} from "../api/api";
import { useAuthStore } from "../stores/authStore";
import toast from "react-hot-toast";

export function useSignUp(): UseMutationResult<
  SignUpResponse,
  Error,
  SignUpParams
> {
  return useMutation<SignUpResponse, Error, SignUpParams>({
    mutationFn: (params: SignUpParams) => signUp(params),
    onSuccess(data) {
      console.log(data);
    },
    onError(err) {
      console.error("Échec de l’inscription :", err.message);
    },
  });
}

export function useLogIn(): UseMutationResult<
  LogInResponse,
  Error,
  LogInParams
> {
  const { setToken, setUser } = useAuthStore();

  return useMutation<LogInResponse, Error, LogInParams>({
    mutationFn: async (params: LogInParams) => {
      const loginResponse = await logIn(params);
      setToken(loginResponse.access_token);

      try {
        const userData = await getMe(loginResponse.access_token);
        setUser(userData);
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }

      return loginResponse;
    },
    onError(err) {
      console.error("Login failed:", err.message);
    },
  });
}

export function useGetMe() {
  const { accessToken, setToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetMe"],
    queryFn: () => {
      if (!accessToken) throw new Error("Not authenticated");
      return apiCallWithRefresh(() => getMe(accessToken), setToken);
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken,
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ["useHealth"],
    queryFn: getHealth,
    staleTime: 1000 * 60 * 2,
    retry: 1,
  });
}

export function useGetBots() {
  const { accessToken, setToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetBots"],
    queryFn: () => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(() => getBots(accessToken), setToken);
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken,
  });
}

export function useGetConversations() {
  const { accessToken, setToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetConversations"],
    queryFn: () => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(() => getConversations(accessToken), setToken);
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken,
  });
}

export function useCreateBot(): UseMutationResult<
  CreateBotResponse,
  Error,
  CreateBotParams
> {
  const { accessToken, setToken } = useAuthStore();

  return useMutation<CreateBotResponse, Error, CreateBotParams>({
    mutationFn: async (params: CreateBotParams) => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(() => createBot(accessToken, params), setToken);
    },
  });
}

export function useGetMessagesInConversation(conversationId: string) {
  const { accessToken, setToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetMessagesInConversation", conversationId],
    queryFn: () => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(
        () => getMessagesInConversation(accessToken, conversationId),
        setToken
      );
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken && !!conversationId,
  });
}

export function useRefreshToken() {
  const { setToken, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      const refreshResponse = await refreshToken();
      setToken(refreshResponse.access_token);

      try {
        const userData = await getMe(refreshResponse.access_token);
        setUser(userData);
      } catch (error) {
        console.error("Failed to fetch user data after refresh:", error);
        throw error;
      }

      return refreshResponse;
    },
    onError: (error) => {
      console.error("Token refresh failed:", error);
      toast.error("Session expired. Please log in again.", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #e53e3e",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
    },
  });
}

export function useCreateCheckoutSession() {
  const { accessToken, setToken } = useAuthStore();

  return useMutation({
    mutationFn: async (params: CreateCheckoutSessionParams) => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(
        () => createCheckoutSession(accessToken, params),
        setToken
      );
    },
  });
}

export function useGetSubscriptionInfos() {
  const { accessToken, setToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetSubscriptionInfos"],
    queryFn: () => {
      if (!accessToken) {
        toast.error("Not authenticated", {
          style: {
            borderRadius: "10px",
            background: "#1f1f1f",
            border: "1px solid #e53e3e",
            boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
            color: "#fff",
            padding: "12px 16px",
            fontSize: "0.95rem",
          },
        });
        throw new Error("Not authenticated");
      }
      return apiCallWithRefresh(
        () => getSubscriptionInfo(accessToken),
        setToken
      );
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken,
  });
}

export function useDeleteBot() {
  const { accessToken } = useAuthStore();
  return useMutation({
    mutationFn: (botId: string) => deleteBot(accessToken!, botId),
  });
}
