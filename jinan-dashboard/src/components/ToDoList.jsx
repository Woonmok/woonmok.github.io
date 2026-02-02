import { useState } from 'react';

function ToDoList() {
    const todos = [
        {
            id: 1,
            category: 'R&D',
            content: ' Accelerate Precision Fermentation Hybrid Tech',
            priority: 'High',
            status: 'Pending'
        },
        {
            id: 2,
            category: 'Safety',
            content: 'Strengthen HACCP/GMP & AI Monitoring for Listeria',
            priority: 'Critical',
            status: 'Pending'
        },
        {
            id: 3,
            category: 'Audio',
            content: 'Review DSD Format Support for High-End Audio',
            priority: 'Medium',
            status: 'Pending'
        }
    ];

    return (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 text-emerald-400 flex items-center gap-2">
                <span className="text-2xl">📋</span> Strategic To-Do List
            </h2>
            <div className="space-y-3">
                {todos.map((todo) => (
                    <div key={todo.id} className="flex items-start bg-gray-900/50 p-4 rounded border border-gray-700 hover:border-emerald-500/30 transition-colors">
                        <div className={`mt-1 w-2 h-2 rounded-full mr-3 ${todo.priority === 'Critical' ? 'bg-red-500' :
                                todo.priority === 'High' ? 'bg-orange-500' : 'bg-blue-500'
                            }`} />
                        <div className="flex-1">
                            <div className="flex justify-between items-start mb-1">
                                <span className="text-xs font-mono text-gray-400 border border-gray-700 px-1.5 py-0.5 rounded">
                                    {todo.category}
                                </span>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${todo.priority === 'Critical' ? 'bg-red-900/30 text-red-400' :
                                        todo.priority === 'High' ? 'bg-orange-900/30 text-orange-400' : 'bg-blue-900/30 text-blue-400'
                                    }`}>
                                    {todo.priority}
                                </span>
                            </div>
                            <p className="text-gray-200 text-sm font-medium">{todo.content}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ToDoList;
