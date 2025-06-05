import { useQuery } from "@tanstack/react-query";
import { getHealth } from "../api/api";

export function useHealth() {
  return useQuery({
    queryKey: ["useHealth"],
    queryFn: getHealth,
    staleTime: 1000 * 60 * 2,
    retry: 1,
  });
}
