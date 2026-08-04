"use client";

import { useState, useEffect } from 'react';

interface KeyStatus {
    service: string;
    total_keys: number;
    available_keys: number;
    keys: Array<{
        key_id: string;
        is_active: boolean;
        is_available: boolean;
        daily_usage: number;
        monthly_usage: number;
        daily_limit?: number;
        monthly_limit?: number;
        error_count: number;
        last_used?: string;
    }>;
}

export default function AdminDashboard() {
    const [vaultStatus, setVaultStatus] = useState<KeyStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchVaultStatus();
    }, []);

    const fetchVaultStatus = async () => {
        try {
            const token = localStorage.getItem('admin_token');
            const response = await fetch('http://localhost:8001/api/v1/admin/vault/status', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch vault status');
            }

            const data = await response.json();
            setVaultStatus(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                    <p className="mt-1 text-sm text-gray-600">Manage API vault, users, and subscriptions</p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                {error && (
                    <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                        {error}
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
                        <p className="mt-4 text-gray-600">Loading vault status...</p>
                    </div>
                ) : (
                    <>
                        {/* Stats Overview */}
                        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="text-3xl">🔑</div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Total Services
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {vaultStatus?.total_services || 0}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="text-3xl">✅</div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Active Keys
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {Object.values(vaultStatus?.services || {}).reduce(
                                                        (acc: number, svc: any) => acc + svc.available_keys,
                                                        0
                                                    )}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white overflow-hidden shadow rounded-lg">
                                <div className="p-5">
                                    <div className="flex items-center">
                                        <div className="flex-shrink-0">
                                            <div className="text-3xl">🔒</div>
                                        </div>
                                        <div className="ml-5 w-0 flex-1">
                                            <dl>
                                                <dt className="text-sm font-medium text-gray-500 truncate">
                                                    Encryption
                                                </dt>
                                                <dd className="text-lg font-medium text-gray-900">
                                                    {vaultStatus?.vault_encryption || 'AES-256'}
                                                </dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* API Keys by Service */}
                        <div className="bg-white shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                                    API Keys by Service
                                </h3>

                                {vaultStatus && Object.keys(vaultStatus.services).length === 0 ? (
                                    <p className="text-gray-500 text-center py-8">No API keys configured yet.</p>
                                ) : (
                                    <div className="space-y-4">
                                        {vaultStatus?.services && Object.entries(vaultStatus.services).map(([service, stats]: [string, any]) => (
                                            <div key={service} className="border border-gray-200 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <h4 className="text-md font-semibold text-gray-900 capitalize">
                                                        {service}
                                                    </h4>
                                                    <span className="text-sm text-gray-600">
                                                        {stats.available_keys} / {stats.total_keys} available
                                                    </span>
                                                </div>
                                                <div className="w-full bg-gray-200 rounded-full h-2">
                                                    <div
                                                        className="bg-blue-600 h-2 rounded-full"
                                                        style={{
                                                            width: `${(stats.available_keys / stats.total_keys) * 100}%`,
                                                        }}
                                                    ></div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}