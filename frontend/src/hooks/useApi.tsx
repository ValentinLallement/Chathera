import { useQuery, useMutation } from "@tanstack/react-query";
import type { UseMutationResult } from "@tanstack/react-query";
import { getHealth, signUp } from "../api/api";
import type { SignUpParams, SignUpResponse } from "../api/api";

export function useSignUp(): UseMutationResult<
  SignUpResponse,
  Error,
  SignUpParams
> {
  return useMutation<SignUpResponse, Error, SignUpParams>({
    mutationFn: (params: SignUpParams) => signUp(params),
    onSuccess(data) {
      console.log("okk");
    },
    onError(err) {
      console.error("Échec de l’inscription :", err.message);
    },
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
