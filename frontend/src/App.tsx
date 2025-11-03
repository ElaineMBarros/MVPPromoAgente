import { useEffect, useState } from "react";
import { ThemeProvider } from "styled-components";
import { GlobalStyle } from "./styles/GlobalStyle";
import { Layout } from "./components/Layout";
import { ChatPanel } from "./components/ChatPanel";
import { HistoryPanel } from "./components/HistoryPanel";
import { StatusBar } from "./components/StatusBar";
import { fetchStatus, fetchPromotions } from "./services/api";
import { ChatMessage, PromotionRecord, SystemStatus } from "./types";

const theme = {
  colors: {
    background: "#ffffff",
    surface: "#f5f7fa",
    primary: "#1f3c88",
    secondary: "#4f6d7a",
    accent: "#00a8e8",
    text: "#1a1a1a",
    muted: "#6f7a8a"
  }
};

function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [history, setHistory] = useState<PromotionRecord[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>(() => {
    return localStorage.getItem("promoagente-session") || undefined;
  });

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const response = await fetchStatus();
        setStatus(response);
      } catch (error) {
        console.error("Erro ao carregar status", error);
      }
    };

    const loadHistory = async () => {
      try {
        const records = await fetchPromotions();
        setHistory(records);
      } catch (error) {
        console.error("Erro ao carregar histórico", error);
      }
    };

    loadStatus();
    loadHistory();
  }, []);

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem("promoagente-session", sessionId);
    }
  }, [sessionId]);

  const reloadHistory = async () => {
    try {
      const records = await fetchPromotions();
      setHistory(records);
    } catch (error) {
      console.error("Erro ao recarregar histórico", error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Layout
        header={<StatusBar status={status} />}
        sidebar={<HistoryPanel records={history} />}
        main={
          <ChatPanel 
            messages={messages} 
            onMessagesChange={setMessages} 
            sessionId={sessionId} 
            onSessionChange={setSessionId}
            onPromotionCompleted={reloadHistory}
          />
        }
      />
    </ThemeProvider>
  );
}

export default App;
