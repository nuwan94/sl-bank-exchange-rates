import { createRoot } from 'react-dom/client';
import App from './App.jsx';

const mount = document.getElementById('app');
if (!mount) {
  throw new Error('Cannot find app mount point');
}

createRoot(mount).render(<App />);
