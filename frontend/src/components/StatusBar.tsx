import styled from "styled-components";
import { SystemStatus } from "../types";

interface StatusBarProps {
  status: SystemStatus | null;
}

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
`;

const Brand = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const Logo = styled.img`
  height: 48px;
  width: auto;
  object-fit: contain;
`;

const Title = styled.h1`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.primary};
`;

const StatusList = styled.ul`
  list-style: none;
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 0;
  padding: 0;
`;

const StatusItem = styled.li<{ $online: boolean }>`
  font-size: 0.9rem;
  color: ${({ $online, theme }) => ($online ? theme.colors.secondary : "#d9534f")};
  display: flex;
  align-items: center;
  gap: 6px;

  &::before {
    content: "";
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: ${({ $online }) => ($online ? "#28a745" : "#d9534f")};
  }
`;

export function StatusBar({ status }: StatusBarProps) {
  return (
    <HeaderWrapper>
      <Brand>
        <Logo src="/logo_gera.png" alt="Gera" />
        <Title>PromoAgente GERA</Title>
      </Brand>
      <StatusList>
        <StatusItem $online={Boolean(status?.openai)}>OpenAI</StatusItem>
        <StatusItem $online={Boolean(status?.sqlite_db)}>SQLite</StatusItem>
      </StatusList>
    </HeaderWrapper>
  );
}
