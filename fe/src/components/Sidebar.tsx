type Props = {
  onSelect: (menu: string) => void;
  selected: string | null;
};

const Sidebar = ({ onSelect, selected }: Props) => {
  const menus = [
    { id: 'overview', label: '📊 전체 대시보드' },
    { id: 'autoscale', label: '📈 오토스케일링' },
    { id: 'test', label: '🔥 부하 테스트' }
  ];

 return (
    <aside className="w-60 h-full bg-gray-900 text-white flex flex-col p-4 shadow-lg">
      <h2 className="text-xl font-bold mb-6">📁 메뉴</h2>
      {menus.map((menu) => (
        <button
          key={menu.id}
          onClick={() => onSelect(menu.id)}
          className={`text-left px-4 py-2 rounded hover:bg-gray-700 transition ${
            selected === menu.id ? 'bg-blue-600' : ''
          }`}
        >
          {menu.label}
        </button>
      ))}
    </aside>
  );
};


export default Sidebar;
