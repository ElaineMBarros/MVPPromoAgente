import { ReactNode } from "react";
import styled, { DefaultTheme } from "styled-components";

interface LayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  main: ReactNode;
}

const background = ({ theme }: { theme: DefaultTheme }) => theme.colors.background;

const Wrapper = styled.div`
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  background: ${background};
`;

const Header = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  background: ${background};
  box-shadow: 0 2px 12px rgba(30, 74, 102, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
`;

const Content = styled.main`
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
  padding: 32px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const Sidebar = styled.aside`
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(31, 60, 136, 0.08);
`;

const Main = styled.section`
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(31, 60, 136, 0.08);
  display: flex;
  flex-direction: column;
`;

export function Layout({ header, sidebar, main }: LayoutProps) {
  return (
    <Wrapper>
      <Header>{header}</Header>
      <Content>
        <Sidebar>{sidebar}</Sidebar>
        <Main>{main}</Main>
      </Content>
    </Wrapper>
  );
}
