// src/components/LoadingIndicator.tsx
import { useEffect } from "react";
import { useNavigation } from "react-router-dom";
import NProgress from "nprogress";
import { useLoading } from "../contexts/LoadingContext";

// Configure NProgress
NProgress.configure({
  showSpinner: false,
  minimum: 0.3,
  trickleSpeed: 200,
  easing: "ease",
  speed: 500,
});

export default function LoadingIndicator() {
  const navigation = useNavigation();
  const { isLoading } = useLoading();

  useEffect(() => {
    if (navigation.state === "loading" || isLoading) {
      NProgress.start();
    } else {
      NProgress.done(true);
    }
  }, [navigation.state, isLoading]);

  return null;
}
