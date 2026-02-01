import { useState } from 'react';

function ActionPanel() {
    const [approved, setApproved] = useState(false);

    const handleApprove = () => {
        setApproved(true);
        // In a real app, this would call an API. Here it shows the command.
    };

    return (
        <div className="bg-gray-800 rounded-lg p-6 border border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
            <h2 className="text-xl font-bold mb-4 text-red-500 flex items-center gap-2">
                <span className="text-2xl">🚨</span> Critical Action Required
            </h2>

            <div className="bg-red-900/20 p-4 rounded-md border border-red-900/50 mb-6">
                <p className="text-red-200 font-medium mb-2">Proposal: Reallocate Server C Resources</p>
                <p className="text-sm text-red-300/70">
                    Shift 'Hands & Ears' (Server C) from DSD Audio processing to Mycelium Simulation to address the critical trend.
                </p>
            </div>

            {!approved ? (
                <button
                    onClick={handleApprove}
                    className="w-full py-4 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-all transform active:scale-95 shadow-lg border-2 border-red-400"
                >
                    [APPROVAL] AUTHORIZE RESOURCE REALLOCATION
                </button>
            ) : (
                <div className="animate-in fade-in zoom-in duration-300">
                    <div className="bg-black p-4 rounded-lg font-mono text-sm text-green-400 border border-green-500/30">
                        <p className="text-gray-500 mb-2"># Copy and run this command in your terminal:</p>
                        <div className="flex justify-between items-center bg-gray-900 p-3 rounded border border-gray-700">
                            <code>./scripts/reallocate_resources.sh</code>
                        </div>
                        <p className="mt-2 text-green-600">✓ Authorization Token Generated</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ActionPanel;
