import { useQuery, useMutation } from "@tanstack/react-query";
import type { UseMutationResult } from "@tanstack/react-query";
import { getHealth, logIn, signUp, getMe } from "../api/api";
import type {
  LogInParams,
  LogInResponse,
  SignUpParams,
  SignUpResponse,
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
        toast;
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }

      return loginResponse;
    },
    onError(err) {
      console.error("Échec de la connexion :", err.message);
    },
  });
}

export function useGetMe() {
  const { accessToken } = useAuthStore();

  return useQuery({
    queryKey: ["useGetMe"],
    queryFn: () => {
      if (!accessToken) throw new Error("Not authenticated");
      return getMe(accessToken);
    },
    staleTime: 1000 * 60 * 2,
    retry: 1,
    enabled: !!accessToken, // only run query if we have a token
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
