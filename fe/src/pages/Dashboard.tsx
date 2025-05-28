import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Sidebar2 from '../components/Sidebar2';
import Overview from '../components/Overview';


const Dashboard = () => {
    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [status, setStatus] = useState('상태: 대기 중');
    const handleMenuClick = (menu: string) => {
        setActiveMenu(prev => (prev === menu ? null : menu));
    };
    const startStressTest = () => {
        setStatus('📡 부하 주는 중...');
        let count = 0;
        const interval = setInterval(() => {
            fetch('http://localhost:5000/')
                .then(() => {
                    count++;
                    setStatus(`📊 요청 횟수: ${count}`);
                    if (count >= 100) {
                        clearInterval(interval);
                        setStatus('✅ 완료');
                    }
                })
                .catch(() => {
                    setStatus('❌ 실패!');
                    clearInterval(interval);
                });
        }, 100);
    };

    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar onSelect={handleMenuClick} selected={activeMenu} />
            <Sidebar2 visible={activeMenu === 'overview'} />

            <main className="flex-1 p-8 overflow-y-auto">
                <div className="bg-white p-6 rounded shadow">
                    {activeMenu === 'overview' && <Overview />}
                    <p className="text-sm text-gray-500 mt-4">{status}</p>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
