import React from 'react';
import {render, screen, waitFor, fireEvent} from '@testing-library/react';
import App from './App';

const reply = (data: unknown) => Promise.resolve({ok: true, json: () => Promise.resolve(data)} as Response);
beforeEach(() => {window.history.replaceState({}, '', '/');});
afterEach(() => {jest.restoreAllMocks();});

test('restores login state and shows the admin link for staff', async () => {
  jest.spyOn(global, 'fetch').mockImplementation(() => reply({isauthenticated: true, userId: 7, isStaff: true, csrfToken: 'token'}));
  render(<App />);
  expect(screen.getByRole('heading', {name: 'Quantum Checkers'})).toBeInTheDocument();
  await waitFor(() => expect(screen.getAllByRole('link', {name: 'Edit levels'})[0]).toHaveAttribute('href', '/admin/'));
  expect(screen.getByText(/User ID: 7/)).toBeInTheDocument();
});

test('uses the rotated CSRF token when applying a gate and renders the winning state', async () => {
  window.history.replaceState({}, '', '/game/1');
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((input, init) => {
    const url = String(input);
    if (url === '/api/session/') return reply({isauthenticated: true, userId: 7, isStaff: false, csrfToken: 'fresh-token'});
    if (url === '/api/gamelevels/1/') return reply({level: 1, title: 'Flip', instructions: 'Apply X', allowed_gates: ['x'], win_conditions: [], circle11: 0});
    if (url === '/api/gamelevels/1/session/') return reply({id: 42, circles: {circle11: 1}, moves: 0, is_win: false});
    if (url === '/api/applygate/42/') return reply({id: 42, circles: {circle11: 0}, moves: 1, is_win: true});
    throw new Error('Unexpected request: ' + url);
  });
  render(<App />);
  const gate = await screen.findByRole('button', {name: 'Apply X gate'});
  expect(screen.getByRole('button', {name: 'Apply H gate'})).toBeDisabled();
  fireEvent.click(gate);
  expect(await screen.findByText(/Puzzle solved!/)).toBeInTheDocument();
  const gateRequest = fetchMock.mock.calls.find(([url]) => url === '/api/applygate/42/');
  const options = gateRequest?.[1] as RequestInit;
  expect(new Headers(options.headers).get('X-CSRFToken')).toBe('fresh-token');
  expect(JSON.parse(options.body as string)).toEqual({gate_type: 'x', qubit_idx: 0});
});
