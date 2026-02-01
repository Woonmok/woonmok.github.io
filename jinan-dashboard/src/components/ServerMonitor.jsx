function ServerMonitor() {
    const servers = [
        { name: "Server A (The Brain)", load: 92, task: "Learning", color: "bg-blue-500" },
        { name: "Server B (The Factory)", load: 45, task: "Inference", color: "bg-yellow-500" },
        { name: "Server C (Hands & Ears)", load: 12, task: "DSD Creation", color: "bg-purple-500" },
    ];

    return (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
                <span className="text-2xl">🖥️</span> Server Monitor
            </h2>
            <div className="space-y-6">
                {servers.map((server) => (
                    <div key={server.name}>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-300 font-medium">{server.name}</span>
                            <span className="text-gray-400">{server.task} | {server.load}%</span>
                        </div>
                        <div className="w-full bg-gray-900 rounded-full h-2.5">
                            <div
                                className={`${server.color} h-2.5 rounded-full transition-all duration-1000 ease-out`}
                                style={{ width: `${server.load}%` }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ServerMonitor;
