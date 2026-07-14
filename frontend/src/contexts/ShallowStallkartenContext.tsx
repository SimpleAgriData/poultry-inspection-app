"use client";

import type React from "react";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiService } from "@/services/api";
import type { ShallowStallkarte } from "@/services/domain/stallkarte";

export interface ShallowStallkartenContextType {
	activeStallkarten: ShallowStallkarte[];
	archivedStallkarten: ShallowStallkarte[];
	isLoading: boolean;
	refetch: () => Promise<void>;
	// replace: (stallkarte: Stallkarte) => void;
}

interface StallkartenContext {
	activeStallkarten: ShallowStallkarte[];
	archivedStallkarten: ShallowStallkarte[];
}

const ShallowStallkartenContext = createContext<ShallowStallkartenContextType | undefined>(
	undefined,
);

interface ShallowStallkartenProviderProps {
	children: React.ReactNode;
}

export function ShallowStallkartenProvider({ children }: ShallowStallkartenProviderProps) {
	const [ctx, setCtx] = useState<StallkartenContext>({
		activeStallkarten: [],
		archivedStallkarten: [],
	});
	const [isLoading, setIsLoading] = useState<boolean>(true);

	const fetchStallkarten = useCallback(async () => {
		setIsLoading(true);
		try {
			const result = await apiService.stallkarte.getStallkarten();
			setCtx(result);
		} catch (error) {
			console.error("Failed to fetch stallkarten:", error);
			setCtx({
				activeStallkarten: [],
				archivedStallkarten: [],
			});
		} finally {
			setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		// noinspection JSIgnoredPromiseFromCall
		fetchStallkarten();
	}, [fetchStallkarten]);

	return (
		<ShallowStallkartenContext.Provider
			value={{
				activeStallkarten: ctx.activeStallkarten,
				archivedStallkarten: ctx.archivedStallkarten,
				refetch: fetchStallkarten,
				isLoading,
			}}
		>
			{children}
		</ShallowStallkartenContext.Provider>
	);
}

export function useShallowStallkarten(): ShallowStallkartenContextType {
	const context = useContext(ShallowStallkartenContext);
	if (context === undefined) {
		throw new Error("useShallowStallkarten must be used within a ShallowStallkartenProvider");
	}
	return context;
}
