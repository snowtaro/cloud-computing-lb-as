type Props = {
    onSelect: (menu: string) => void;
    selected: string | null;
    isStressOn: boolean;
};

const Sidebar = ({ onSelect, selected, isStressOn }: Props) => {
    return (
        <aside className="w-60 h-full bg-gray-900 text-white flex flex-col p-4 shadow-lg">
            <h2 className="text-xl font-bold mb-6">📁 메뉴</h2>
            <button
                onClick={() => onSelect('overview')}
                className={`text-left px-4 py-2 rounded hover:bg-gray-700 transition ${
                    selected === 'overview' ? 'bg-blue-600' : ''
                }`}
            >
                📊 전체 대시보드
            </button>

            <button
                onClick={() => onSelect('test')}
                className={`text-left px-4 py-2 mt-4 rounded font-bold text-white ${
                    isStressOn
                        ? 'bg-gray-600 hover:bg-gray-700'
                        : 'bg-red-500 hover:bg-red-600'
                }`}
            >
                {isStressOn ? '🛑 부하 중지' : '🔥 부하 테스트 시작'}
            </button>
        </aside>
    );
};

export default Sidebar;
