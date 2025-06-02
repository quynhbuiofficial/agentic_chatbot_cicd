import { Langfuse } from "langfuse";

if (!import.meta.env.VITE_LANGFUSE_SECRET_KEY || !import.meta.env.VITE_LANGFUSE_PUBLIC_KEY) {
  throw new Error("Missing Langfuse environment variables");
}

export const langfuse = new Langfuse({
  secretKey: import.meta.env.VITE_LANGFUSE_SECRET_KEY,
  publicKey: import.meta.env.VITE_LANGFUSE_PUBLIC_KEY,
  baseUrl: import.meta.env.VITE_LANGFUSE_BASEURL || "https://cloud.langfuse.com",
}); 