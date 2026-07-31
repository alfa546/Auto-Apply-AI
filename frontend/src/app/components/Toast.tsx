import React from "react";
import { CheckCircleIcon } from "./Icons";

interface ToastProps {
  notification: { message: string; type: "success" | "error" } | null;
}

export default function Toast({ notification }: ToastProps) {
  if (!notification) return null;

  return (
    <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-2xl text-sm font-medium border flex items-center gap-2 backdrop-blur-md animate-bounce ${
      notification.type === "success" 
        ? "bg-rose-950/90 text-rose-300 border-rose-500/50 shadow-rose-500/20" 
        : "bg-red-950/90 text-red-300 border-red-500/50 shadow-red-500/20"
    }`}>
      <CheckCircleIcon />
      <span>{notification.message}</span>
    </div>
  );
}
