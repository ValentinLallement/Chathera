import React from "react";

interface TitleProps {
  children: React.ReactNode;
}

export default function Title({ children }: TitleProps) {
  React.useEffect(() => {
    document.title = (children ?? "").toString();
  }, [children]);
  return null;
}
