import RadarStatus from './components/RadarStatus';
import ServerMonitor from './components/ServerMonitor';
import ActionPanel from './components/ActionPanel';
import ToDoList from './components/ToDoList';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 p-8 app-container">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 flex justify-between items-center border-b border-gray-800 pb-6">
          <div>
            <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-500">
              Jinan Project Control Tower
            </h1>
            <p className="text-gray-400 mt-2">Strategic Analysis & Resource Management System</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold font-mono text-white">2026.02.01</div>
            <div className="text-emerald-500 font-medium">System Online</div>
          </div>
        </header>

        <div className="mb-8">
          <ActionPanel />
        </div>

        <main className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-8">
            <RadarStatus />
          </div>

          <div className="space-y-8">
            <ToDoList />
            <ServerMonitor />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
