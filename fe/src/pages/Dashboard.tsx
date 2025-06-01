import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Sidebar2 from '../components/Sidebar2';
import Overview from '../components/Overview';

const Dashboard = () => {
    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [status, setStatus] = useState('상태: 대기 중');
    const [isStressOn, setIsStressOn] = useState(false);

    const handleMenuClick = (menu: string) => {
        setActiveMenu(prev => (prev === menu ? null : menu));
    };

    const toggleStressTest = async () => {
        try {
            const res = await fetch('http://localhost:5000/cpu/toggle', {
                method: 'POST',
            });
            const text = await res.text();

            if (text === 'started') {
                setIsStressOn(true);
                setStatus('🔥 부하 시작됨');
            } else if (text === 'stopped') {
                setIsStressOn(false);
                setStatus('🧊 부하 중지됨');
            } else {
                setStatus('⚠️ 알 수 없는 응답');
            }
        } catch (err) {
            setStatus('❌ 에러 발생');
            console.error(err);
        }
    };

    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar onSelect={handleMenuClick} selected={activeMenu} />
            <Sidebar2 visible={activeMenu === 'overview'} />

            <main className="flex-1 p-8 overflow-y-auto">
                <div className="bg-white p-6 rounded shadow">
                    {activeMenu === 'overview' && <Overview />}

                    <button
                        className={`mt-4 px-4 py-2 rounded font-bold text-white ${
                            isStressOn ? 'bg-gray-600 hover:bg-gray-700' : 'bg-red-500 hover:bg-red-600'
                        }`}
                        onClick={toggleStressTest}
                    >
                        {isStressOn ? '🛑 부하 중지' : '🔥 부하 테스트 시작'}
                    </button>

                    <p className="text-sm text-gray-500 mt-4">{status}</p>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
