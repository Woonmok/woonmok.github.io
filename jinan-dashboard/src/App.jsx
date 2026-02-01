import RadarStatus from './components/RadarStatus';
import ServerMonitor from './components/ServerMonitor';
import ActionPanel from './components/ActionPanel';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-7xl mx-auto">
        <header className="mb-8 sm:mb-10 flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-800 pb-4 sm:pb-6 gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">
              Jinan Project Control Tower
            </h1>
            <p className="text-xs sm:text-sm lg:text-base text-gray-400 mt-2">Strategic Analysis & Resource Management System</p>
          </div>
          <div className="text-right">
            <div className="text-lg sm:text-xl lg:text-2xl font-bold font-mono text-white">2026.02.01</div>
            <div className="text-sm sm:text-base text-emerald-500 font-medium">System Online</div>
          </div>
        </header>

        <div className="mb-6 sm:mb-8">
          <ActionPanel />
        </div>

        <main className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          <div className="space-y-6 sm:space-y-8">
            <RadarStatus />
          </div>

          <div className="space-y-6 sm:space-y-8">
            <ServerMonitor />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
