import { useEffect, useState } from 'react';
import type { FleetProjection } from './fleet';
import { createSnapshotClient } from './publicationSnapshot';

export function usePublicationSnapshot() {
  const [data, setData] = useState<FleetProjection | null>(null);
  useEffect(() => {
    const client = createSnapshotClient({
      onChange: setData,
      stateStore: {
        read: () => sessionStorage.getItem('timonelo.publication.watermark.v1'),
        write: value => sessionStorage.setItem('timonelo.publication.watermark.v1', value),
      },
      async load(signal) {
        const response = await fetch(`${import.meta.env.BASE_URL}data/fleet.publication.json`, { signal, cache: 'no-store' });
        if (!response.ok) throw new Error('Publication snapshot unavailable');
        return response.json();
      },
    });
    const resume = () => { if (document.visibilityState === 'visible' && navigator.onLine) client.resume(); else client.suspend(); };
    document.addEventListener('visibilitychange', resume);
    window.addEventListener('online', resume);
    window.addEventListener('offline', resume);
    window.addEventListener('pageshow', resume);
    window.addEventListener('pagehide', client.suspend);
    resume();
    return () => {
      client.stop();
      document.removeEventListener('visibilitychange', resume);
      window.removeEventListener('online', resume);
      window.removeEventListener('offline', resume);
      window.removeEventListener('pageshow', resume);
      window.removeEventListener('pagehide', client.suspend);
    };
  }, []);
  return data;
}
