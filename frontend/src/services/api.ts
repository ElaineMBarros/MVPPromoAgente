import axios from "axios";
import { ChatResponse, PromotionRecord, SystemStatus } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:7000"
});

export async function sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/api/chat", {
    message,
    session_id: sessionId
  });
  return response.data;
}

export async function fetchStatus(): Promise<SystemStatus> {
  const response = await api.get<SystemStatus>("/api/status");
  return response.data;
}

export async function fetchPromotions(): Promise<PromotionRecord[]> {
  try {
    const response = await api.get<{ promotions: PromotionRecord[]; count: number }>("/api/promotions");
    return response.data.promotions || [];
  } catch (error: unknown) {
    console.warn("Endpoint /api/promotions indisponível, retornando lista vazia.");
    return [];
  }
}

export async function getPromotionState(sessionId: string): Promise<any> {
  const response = await api.get(`/api/promotion-state/${sessionId}`);
  return response.data;
}

export async function validatePromotion(sessionId: string): Promise<any> {
  const response = await api.post(`/api/promotion-state/${sessionId}/validate`);
  return response.data;
}

export async function createSummary(sessionId: string): Promise<{ summary: string }> {
  const response = await api.post(`/api/promotion-state/${sessionId}/summary`);
  return response.data;
}

export async function savePromotion(sessionId: string): Promise<any> {
  const response = await api.post(`/api/promotion-state/${sessionId}/save`);
  return response.data;
}

export async function sendPromotionEmail(sessionId: string): Promise<any> {
  const response = await api.post(`/api/promotion-state/${sessionId}/send-email`);
  return response.data;
}

export async function resetPromotion(sessionId: string): Promise<any> {
  const response = await api.delete(`/api/promotion-state/${sessionId}`);
  return response.data;
}

export default api;
