import { useEffect } from "react";

export default function useDocumentTitle(title) {
  useEffect(() => {
    const previous = document.title;
    document.title = title ? `Codestand — ${title}` : "Codestand — AI Code Review";
    return () => {
      document.title = previous;
    };
  }, [title]);
}