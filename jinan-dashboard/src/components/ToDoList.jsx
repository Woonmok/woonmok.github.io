import { useEffect, useState } from 'react';

function ToDoList() {
    const [todos, setTodos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        const loadTodos = async () => {
            const cacheBust = `ts=${Date.now()}`;
            const candidates = [
                `../dashboard_data.json?${cacheBust}`,
                `/dashboard_data.json?${cacheBust}`,
                `dashboard_data.json?${cacheBust}`,
            ];

            for (const url of candidates) {
                try {
                    const res = await fetch(url, { cache: 'no-store' });
                    if (!res.ok) {
                        continue;
                    }
                    const data = await res.json();
                    const list = Array.isArray(data?.todo_list) ? data.todo_list : [];
                    const normalized = list
                        .map((item, index) => ({
                            id: Number.isInteger(item?.id) ? item.id : index + 1,
                            text: String(item?.text || '').trim(),
                            completed: Boolean(item?.completed),
                        }))
                        .filter((item) => item.text.length > 0);

                    if (mounted) {
                        setTodos(normalized);
                        setLoading(false);
                    }
                    return;
                } catch {
                }
            }

            if (mounted) {
                setTodos([]);
                setLoading(false);
            }
        };

        loadTodos();
        return () => {
            mounted = false;
        };
    }, []);

    return (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
                <span className="text-2xl">📋</span> 오늘의 할일
            </h2>
            <div className="space-y-3">
                {loading && (
                    <div className="flex items-start bg-gray-900/50 p-4 rounded border border-gray-700">
                        <p className="text-gray-300 text-sm font-medium">할일 로딩 중...</p>
                    </div>
                )}

                {!loading && todos.length === 0 && (
                    <div className="flex items-start bg-gray-900/50 p-4 rounded border border-gray-700">
                        <p className="text-gray-300 text-sm font-medium">할일 없음</p>
                    </div>
                )}

                {!loading && todos.map((todo) => (
                    <div key={todo.id} className="flex items-start bg-gray-900/50 p-4 rounded border border-gray-700 hover:border-emerald-500/30 transition-colors">
                        <div className={`mt-1 w-2 h-2 rounded-full mr-3 ${todo.completed ? 'bg-emerald-500' : 'bg-gray-500'}`} />
                        <div className="flex-1">
                            <p className={`text-sm font-medium ${todo.completed ? 'text-gray-500 line-through' : 'text-gray-200'}`}>
                                {todo.text}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ToDoList;
