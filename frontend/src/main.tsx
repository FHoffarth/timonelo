import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';
import '@fontsource-variable/inter';
import '@fontsource-variable/newsreader';
import App from './App';
import ShipPage from './explorer/ShipPage';
import DeckPage from './explorer/DeckPage';
import CabinPage from './explorer/CabinPage';
import './index.css';

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/explore', element: <Navigate to="/ship/msc-meraviglia" replace /> },
  { path: '/ship/:shipId', element: <ShipPage /> },
  { path: '/ship/:shipId/deck/:deck', element: <DeckPage /> },
  { path: '/ship/:shipId/deck/:deck/cabin/:cabin', element: <CabinPage /> },
  { path: '*', element: <Navigate to="/" replace /> },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
