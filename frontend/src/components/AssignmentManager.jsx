import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const AssignmentManager = ({ issueId, currentAssignment, onAssignmentUpdated }) => {
    const { user } = useAuth();
    const [eligibleWorkers, setEligibleWorkers] = useState([]);
    const [selectedWorker, setSelectedWorker] = useState('');
    const [note, setNote] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (['MUNICIPAL_OFFICER', 'ADMIN'].includes(user?.role)) {
            fetchEligibleWorkers();
        }
    }, [issueId, user]);

    const fetchEligibleWorkers = async () => {
        try {
            const response = await api.get(`/api/assignments/eligible-workers/${issueId}`);
            setEligibleWorkers(response.data);
        } catch (err) {
            setError('Failed to fetch eligible field workers.');
            console.error(err);
        }
    };

    const handleAssign = async (e) => {
        e.preventDefault();
        if (!selectedWorker) return;
        
        setLoading(true);
        setError(null);
        try {
            let response;
            if (currentAssignment && !['COMPLETED', 'CANCELLED'].includes(currentAssignment.assignment_status)) {
                // Reassign
                response = await api.post(`/api/assignments/${currentAssignment.id}/reassign`, {
                    new_assignee: parseInt(selectedWorker),
                    reason: note || 'Reassigned by officer'
                });
            } else {
                // New Assign
                response = await api.post(`/api/assignments`, {
                    issue_id: issueId,
                    assigned_to: parseInt(selectedWorker),
                    note: note
                });
            }
            onAssignmentUpdated(response.data);
            setNote('');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to assign issue.');
        } finally {
            setLoading(false);
        }
    };

    const handleStatusTransition = async (status, reason = null) => {
        setLoading(true);
        setError(null);
        try {
            const payload = { status };
            if (reason) payload.reason = reason;
            
            const response = await api.patch(`/api/assignments/${currentAssignment.id}/status`, payload);
            onAssignmentUpdated(response.data);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to update assignment status.');
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    // Field Worker View
    if (user.role === 'FIELD_WORKER' && currentAssignment && currentAssignment.assigned_to === user.id) {
        return (
            <div className="bg-white shadow rounded-lg p-6 mt-6">
                <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Your Assignment</h3>
                {error && <div className="mb-4 text-red-600 bg-red-100 p-2 rounded">{error}</div>}
                
                <p className="text-sm text-gray-600 mb-4">
                    Status: <span className="font-bold text-blue-600">{currentAssignment.assignment_status}</span>
                </p>
                
                <div className="space-x-4">
                    {currentAssignment.assignment_status === 'ASSIGNED' && (
                        <>
                            <button 
                                onClick={() => handleStatusTransition('ACCEPTED')} 
                                disabled={loading}
                                className="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700"
                            >
                                Accept
                            </button>
                            <button 
                                onClick={() => {
                                    const reason = prompt("Reason for rejection:");
                                    if (reason) handleStatusTransition('REJECTED', reason);
                                }}
                                disabled={loading}
                                className="bg-red-600 text-white px-4 py-2 rounded shadow hover:bg-red-700"
                            >
                                Reject
                            </button>
                        </>
                    )}
                    {currentAssignment.assignment_status === 'ACCEPTED' && (
                        <button 
                            onClick={() => handleStatusTransition('IN_PROGRESS')} 
                            disabled={loading}
                            className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700"
                        >
                            Start Work (In Progress)
                        </button>
                    )}
                    {currentAssignment.assignment_status === 'IN_PROGRESS' && (
                        <button 
                            onClick={() => handleStatusTransition('COMPLETED')} 
                            disabled={loading}
                            className="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700"
                        >
                            Mark as Completed
                        </button>
                    )}
                </div>
            </div>
        );
    }

    // Officer / Admin View
    if (['MUNICIPAL_OFFICER', 'ADMIN'].includes(user.role)) {
        return (
            <div className="bg-white shadow rounded-lg p-6 mt-6">
                <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Assignment Management</h3>
                
                {currentAssignment && (
                    <div className="mb-6 p-4 bg-gray-50 border rounded-lg">
                        <p className="text-sm text-gray-700"><strong>Current Assignee ID:</strong> {currentAssignment.assigned_to}</p>
                        <p className="text-sm text-gray-700"><strong>Status:</strong> {currentAssignment.assignment_status}</p>
                        {currentAssignment.assignment_status === 'ASSIGNED' && (
                            <button 
                                onClick={() => handleStatusTransition('CANCELLED')} 
                                disabled={loading}
                                className="mt-2 bg-red-600 text-white px-3 py-1 text-sm rounded shadow hover:bg-red-700"
                            >
                                Cancel Assignment
                            </button>
                        )}
                    </div>
                )}

                <h4 className="text-md font-medium text-gray-900 mb-2">
                    {currentAssignment && !['COMPLETED', 'CANCELLED'].includes(currentAssignment.assignment_status) ? 'Reassign Issue' : 'Assign Issue'}
                </h4>
                
                {error && <div className="mb-4 text-red-600 bg-red-100 p-2 rounded">{error}</div>}

                <form onSubmit={handleAssign} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Eligible Field Workers</label>
                        <select 
                            value={selectedWorker}
                            onChange={(e) => setSelectedWorker(e.target.value)}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                            required
                        >
                            <option value="">Select a worker...</option>
                            {eligibleWorkers.map(w => (
                                <option key={w.user_id} value={w.user_id}>
                                    {w.full_name} ({w.employee_code}) - {w.designation}
                                </option>
                            ))}
                        </select>
                        {eligibleWorkers.length === 0 && <p className="text-xs text-red-500 mt-1">No available field workers in this ward/department.</p>}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Assignment Note / Reason</label>
                        <textarea
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                            rows="2"
                        ></textarea>
                    </div>
                    <button 
                        type="submit"
                        disabled={loading || !selectedWorker}
                        className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 disabled:opacity-50"
                    >
                        {currentAssignment && !['COMPLETED', 'CANCELLED'].includes(currentAssignment.assignment_status) ? 'Reassign' : 'Assign'}
                    </button>
                </form>
            </div>
        );
    }

    return null;
};

export default AssignmentManager;
