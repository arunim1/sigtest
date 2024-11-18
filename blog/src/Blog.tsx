import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import AppAppBar from './components/AppAppBar';
import MainContent from './components/MainContent';
import Latest from './components/Latest';
import Footer from './components/Footer';
import AppTheme from './theme/AppTheme';
import { useAgentHeaders } from './hooks/useAgentHeaders';

export default function Blog(props: { disableCustomTheme?: boolean }) {
  const { headers, isAuthorized } = useAgentHeaders();

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <AppAppBar isAuthorized={isAuthorized} agentId={headers?.agentId ?? null} />
      <Container
        maxWidth="lg"
        component="main"
        sx={{ display: 'flex', flexDirection: 'column', my: 16, gap: 4 }}
      >
        <MainContent isAuthorized={isAuthorized} headers={headers} />
        <Latest isAuthorized={isAuthorized} />
      </Container>
      <Footer />
    </AppTheme>
  );
}
