import styled from "styled-components";
import { PromotionRecord } from "../types";

interface HistoryPanelProps {
  records: PromotionRecord[];
}

const Title = styled.h2`
  font-size: 1.25rem;
  margin-bottom: 20px;
`;

const PromoList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const PromoCard = styled.article`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: 14px;
  padding: 16px;
  border: 1px solid rgba(31, 60, 136, 0.12);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
`;

const PromoTitle = styled.h3`
  font-size: 1.05rem;
  margin-bottom: 8px;
`;

const PromoMeta = styled.p`
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.muted};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 24px;
  border: 1px dashed rgba(31, 60, 136, 0.2);
  border-radius: 12px;
  background: #ffffff;
  color: ${({ theme }) => theme.colors.muted};
`;

export function HistoryPanel({ records }: HistoryPanelProps) {
  if (records.length === 0) {
    return (
      <div>
        <Title>Promoções recentes</Title>
        <EmptyState>
          Ainda não enviamos promoções.<br />
          Inicie uma conversa no chat e acompanhe por aqui.
        </EmptyState>
      </div>
    );
  }

  return (
    <div>
      <Title>Promoções recentes ({records.length})</Title>
      <PromoList>
        {records.map(record => (
          <PromoCard key={record.id}>
            <PromoTitle>{record.titulo || "Promoção sem título"}</PromoTitle>
            <PromoMeta>
              {record.mecanica && `📊 ${record.mecanica} • `}
              {record.segmentacao || "Público geral"}
            </PromoMeta>
            <PromoMeta>
              📅 {record.periodo_inicio && record.periodo_fim 
                ? `${record.periodo_inicio} até ${record.periodo_fim}` 
                : "Período não especificado"}
            </PromoMeta>
            <PromoMeta>
              {record.sent_at 
                ? `✅ Enviada: ${new Date(record.sent_at).toLocaleString("pt-BR")}`
                : `💾 Criada: ${new Date(record.created_at).toLocaleString("pt-BR")}`}
            </PromoMeta>
          </PromoCard>
        ))}
      </PromoList>
    </div>
  );
}
