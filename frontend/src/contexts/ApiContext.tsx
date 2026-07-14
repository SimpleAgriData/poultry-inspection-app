import type React from "react";
import { createContext, useContext, useEffect, useState } from "react";
import type { ConnectionState } from "@/services/api/client";
import { type ApiService, apiService } from "@/services/api/service";
import type { Status } from "@/services/domain/status";

interface ApiContextType {
	apiUrl: string;
	apiService: ApiService;
	connectionState: ConnectionState;
	lastStatus: Status | null;
}

const ApiContext = createContext<ApiContextType>({
	apiUrl: apiService.client.baseUrl,
	apiService: apiService,
	connectionState: apiService.client.connectionState.value,
	lastStatus: null,
});

export function ApiProvider({ children }: { children: React.ReactNode }) {
	const [connectionState, setConnectionState] = useState<ConnectionState>(
		apiService.client.connectionState.value,
	);
	const [lastStatus, setLastStatus] = useState<Status | null>(null);

	useEffect(() => {
		const unsubscribe = [
			apiService.client.connectionState.subscribe(setConnectionState, true),
			apiService.client.lastStatus.subscribe(setLastStatus, true),
		];
		return () => {
			for (const unsub of unsubscribe) {
				unsub();
			}
		};
	}, []);

	return (
		<ApiContext.Provider
			value={{
				apiUrl: apiService.client.baseUrl,
				apiService: apiService,
				connectionState: connectionState,
				lastStatus: lastStatus,
			}}
		>
			{children}
		</ApiContext.Provider>
	);
}

export function useApi() {
	const context = useContext(ApiContext);
	if (context === undefined) {
		throw new Error("useApi must be used within an ApiProvider");
	}
	return context;
}
