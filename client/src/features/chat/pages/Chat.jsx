// ~/client/src/features/chat/pages/Chat.jsx
import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { useDispatch, useSelector } from 'react-redux';
import socket, { waitUntilConnected, sendChatMessage, snapshotSocket } from '../../../services/socket';
import { receiveMessage, sendMessageStart, sendMessageSuccess, sendMessageError, clearChat } from '../reducers/chatSlice';

export default function Chat() {
  const dispatch = useDispatch();
  const { messages = [], sending = false, error = null } = useSelector((s) => s.chat || {});

  // ✅ initialize from live socket state so UI doesn't get stuck
  const [status, setStatus] = useState(socket.connected ? 'connected' : 'connecting');
  const [lastErr, setLastErr] = useState(null);
  const [input, setInput] = useState('');

  useEffect(() => {
    const onConnect = () => { setStatus('connected'); setLastErr(null); console.log('[Chat] connected', socket.id); };
    const onDisconnect = (reason) => { setStatus('disconnected'); console.warn('[Chat] disconnected:', reason); };
    const onCE = (err) => { setStatus('connect_error'); setLastErr(err?.message || String(err)); console.error('[Chat] connect_error:', err); };
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('connect_error', onCE);

    const onInbound = (msg) => { console.log('[Chat] inbound chat:message', msg); dispatch(receiveMessage(msg)); };
    socket.on('chat:message', onInbound);

    // If we mounted while already connected, make sure UI is correct
    if (socket.connected) {
      setStatus('connected');
    } else {
      // Try to reach connected state in the background (doesn't block typing)
      waitUntilConnected(6000).catch((e) => console.warn('[Chat] initial wait failed:', e?.message || e));
    }

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('connect_error', onCE);
      socket.off('chat:message', onInbound);
    };
  }, [dispatch]);

  const pill = useMemo(() => {
    if (status === 'connected') return <Pill $ok>Connected</Pill>;
    if (status === 'connect_error') return <Pill $warn>Connect error{lastErr ? `: ${lastErr}` : ''}</Pill>;
    if (status === 'disconnected') return <Pill $warn>Disconnected</Pill>;
    return <Pill $warn>Connecting…</Pill>;
  }, [status, lastErr]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    dispatch(sendMessageStart());
    try {
      // Ensure the socket is up before emitting
      await waitUntilConnected(4000);
      const payload = { text, ts: Date.now(), mine: true };
      const ack = await sendChatMessage(payload, 5000);
      dispatch(sendMessageSuccess(payload));
      setInput('');
      console.log('[Chat] send OK', ack);
    } catch (err) {
      console.error('[Chat] send FAILED', err?.message || err);
      setStatus('connect_error');
      setLastErr(err?.message || String(err));
      dispatch(sendMessageError(err?.message || 'send_failed'));
    }
  }

  return (
    <Wrap>
      <Header>
        <h3>Team Chat</h3>
        <Right>
          {pill}
          <Btn type="button" onClick={() => snapshotSocket()}>Snapshot</Btn>
          <Btn type="button" onClick={() => dispatch(clearChat())}>Clear</Btn>
        </Right>
      </Header>

      <List>
        {messages.map((m, i) => (
          <Row key={i}>
            <Bubble mine={(m.mine ? 'true' : 'false')} title={new Date(m.ts || Date.now()).toLocaleString()}>
              {m.text}
            </Bubble>
          </Row>
        ))}
      </List>

      <Form onSubmit={handleSend}>
        {/* ✅ allow typing regardless of connection; only gate the Send action */}
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={status === 'connected' ? 'Type a message…' : 'You can type while connecting…'}
          disabled={sending}
        />
        <Btn type="submit" disabled={sending || !socket.connected}>Send</Btn>
      </Form>

      {error ? <Err>Last error: {error}</Err> : null}
    </Wrap>
  );
}

const Wrap = styled.div`padding:16px; display:flex; flex-direction:column; height:100%;`;
const Header = styled.div`display:flex; justify-content:space-between; align-items:center;`;
const Right = styled.div`display:flex; gap:8px; align-items:center;`;
const Pill = styled.span`
  padding:4px 8px; border-radius:12px; font-size:12px; color:white;
  background:${p => p.$ok ? '#198754' : p.$warn ? '#f59e0b' : '#6b7280'};
`;
const List = styled.div`flex:1; overflow:auto; padding:12px 0;`;
const Row = styled.div`margin-bottom:8px; display:flex;`;
const Bubble = styled.div`
  background:#eef2ff; border-radius:12px; padding:8px 12px; max-width:70%;
  &[mine="true"] { background:#d1fae5; }
`;
const Form = styled.form`display:flex; gap:8px;`;
const Input = styled.input`flex:1; padding:8px 12px;`;
const Btn = styled.button`padding:8px 12px;`;
const Err = styled.div`margin-top:8px; color:#dc2626;`;
