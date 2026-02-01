function RadarStatus() {
    return (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
                <span className="text-2xl">📡</span> Radar Status
            </h2>
            <div className="space-y-4">
                <div className="bg-gray-900/50 p-4 rounded-md border border-red-500/30">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-semibold text-white">Mycelium Cultured Meat</span>
                        <span className="px-2 py-1 bg-red-500/20 text-red-500 text-xs rounded-full border border-red-500/50 animate-pulse">🔥 TRENDING (+45%)</span>
                    </div>
                    <p className="text-gray-400 text-sm">Critical scaffold generation breakthrough required.</p>
                </div>

                <div className="bg-gray-900/50 p-4 rounded-md border border-gray-700">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-semibold text-gray-300">DSD Audio</span>
                        <span className="px-2 py-1 bg-gray-700 text-gray-400 text-xs rounded-full">Stable</span>
                    </div>
                    <p className="text-gray-500 text-sm">System sufficient for testing.</p>
                </div>

                <div className="bg-gray-900/50 p-4 rounded-md border border-gray-700">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-lg font-semibold text-gray-300">AI Infra</span>
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">High Demand</span>
                    </div>
                    <p className="text-gray-500 text-sm">Optimization needed for Bio-sims.</p>
                </div>
            </div>
        </div>
    );
}

export default RadarStatus;
