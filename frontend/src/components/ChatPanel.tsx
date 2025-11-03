import { FormEvent, useState } from "react";
import styled from "styled-components";
import { sendChatMessage } from "../services/api";
import { ChatMessage } from "../types";

interface ChatPanelProps {
  messages: ChatMessage[];
  onMessagesChange: (messages: ChatMessage[]) => void;
  sessionId?: string;
  onSessionChange: (sessionId: string) => void;
  onPromotionCompleted?: () => void;
}

const ChatWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const ChatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const Title = styled.h2`
  font-size: 1.5rem;
`;

const ScrollArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageBubble = styled.div<{ $origin: "user" | "agent" }>`
  align-self: ${({ $origin }) => ($origin === "user" ? "flex-end" : "flex-start")};
  background: ${({ $origin, theme }) => ($origin === "user" ? theme.colors.primary : theme.colors.surface)};
  color: ${({ $origin }) => ($origin === "user" ? "#ffffff" : "#1a1a1a")};
  padding: 14px 18px;
  border-radius: 18px;
  max-width: 70%;
  line-height: 1.6;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
  border: ${({ $origin, theme }) => ($origin === "agent" ? `1px solid ${theme.colors.muted}33` : "none")};
`;

const MessageMeta = styled.span`
  display: block;
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 6px;
`;

const Form = styled.form`
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
`;

const Input = styled.textarea`
  flex: 1;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  padding: 12px 16px;
  min-height: 90px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
  background: #fdfdfd;
`;

const Button = styled.button`
  border-radius: 12px;
  border: none;
  padding: 16px 24px;
  background: ${({ theme }) => theme.colors.primary};
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(31, 60, 136, 0.2);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

export function ChatPanel({ messages, onMessagesChange, sessionId, onSessionChange, onPromotionCompleted }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const currentSession = sessionId;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      timestamp: new Date().toISOString()
    };

    const updated = [...messages, userMessage];
    onMessagesChange(updated);
    setInput("");
    setIsSending(true);

    try {
      const response = await sendChatMessage(trimmed, currentSession);

      const agentMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "agent",
        content: response.response,
        timestamp: response.timestamp
      };

      onMessagesChange([...updated, agentMessage]);
      if (response.session_id && response.session_id !== currentSession) {
        onSessionChange(response.session_id);
      }

      // Detecta se a promoção foi concluída/salva
      if (onPromotionCompleted && (response.response.includes("Promoção enviada com sucesso") || response.response.includes("Promoção salva no sistema"))) {
        // Aguarda um pouco para garantir que o backend salvou
        setTimeout(() => {
          onPromotionCompleted();
        }, 500);
      }
    } catch (error) {
      console.error("Erro ao enviar mensagem", error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <ChatWrapper>
      <ChatHeader>
        <Title>PromoAgente chat</Title>
      </ChatHeader>
      <ScrollArea>
        {messages.map(message => (
          <MessageBubble key={message.id} $origin={message.role}>
            {message.content}
            <MessageMeta>{new Date(message.timestamp).toLocaleString()}</MessageMeta>
          </MessageBubble>
        ))}
      </ScrollArea>
      <Form onSubmit={handleSubmit}>
        <Input
          value={input}
          onChange={event => setInput(event.target.value)}
          placeholder="Descreva a promoção ou peça uma sugestão ao agente"
        />
        <Button type="submit" disabled={isSending}>
          {isSending ? "Enviando..." : "Enviar"}
        </Button>
      </Form>
    </ChatWrapper>
  );
}
