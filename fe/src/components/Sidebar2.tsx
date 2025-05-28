import React, { useEffect, useState } from 'react';

type Props = {
  visible: boolean;
};

const Sidebar2 = ({ visible }: Props) => {
  const [servers, setServers] = useState<string[]>([]);

  useEffect(() => {
    if (visible) {
      fetch('/api/instances')
        .then((res) => res.json())
        .then(setServers)
        .catch(console.error);
    }
  }, [visible]);

  if (!visible) return null;
  return (
    <aside className="w-56 h-full bg-gray-100 border-l border-gray-300 p-4 overflow-y-auto">
      <h3 className="text-lg font-semibold mb-3">🖥️ 서버 목록</h3>
      <ul className="space-y-2">
        {servers.map((server) => (
          <li
            key={server}
            className="bg-white p-2 rounded shadow-sm hover:bg-gray-200 text-sm cursor-pointer"
          >
            {server}
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar2;
