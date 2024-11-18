import { useState, useEffect } from 'react';

interface AgentHeaders {
  agentCert?: string;
  agentSignature?: string;
  agentTimestamp?: string;
  agentId?: string;
}

export type { AgentHeaders };

export function useAgentHeaders() {
  const [headers, setHeaders] = useState<AgentHeaders | null>(null);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    // Get headers from the current request
    const currentHeaders = {
      agentCert: document.querySelector('meta[name="agent-cert"]')?.getAttribute('content'),
      agentSignature: document.querySelector('meta[name="agent-signature"]')?.getAttribute('content'),
      agentTimestamp: document.querySelector('meta[name="agent-timestamp"]')?.getAttribute('content'),
      agentId: document.querySelector('meta[name="agent-id"]')?.getAttribute('content')
    };

    console.log('Current headers found:', currentHeaders);

    // Log individual header presence
    Object.entries(currentHeaders).forEach(([key, value]) => {
      console.log(`${key}: ${value ? 'present' : 'missing'}`);
    });

    setHeaders(currentHeaders as AgentHeaders);
    
    const authorized = Boolean(
      currentHeaders.agentCert && 
      currentHeaders.agentSignature && 
      currentHeaders.agentTimestamp && 
      currentHeaders.agentId
    );

    console.log('Authorization status:', authorized);
    setIsAuthorized(authorized);
  }, []);

  return { headers, isAuthorized };
}