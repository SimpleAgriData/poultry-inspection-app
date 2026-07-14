"use client";

import type React from "react";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { apiService } from "@/services/api";
import type { Holding } from "@/services/domain/holding";

interface HoldingContextType {
	holding: Holding | null | undefined;
	setHolding: (holding: Holding | null) => void;
	isLoading: boolean;
	refetch: () => Promise<void>;
}

const HoldingContext = createContext<HoldingContextType | undefined>(undefined);

interface HoldingProviderProps {
	children: React.ReactNode;
}

export function HoldingProvider({ children }: HoldingProviderProps) {
	const [holding, setHolding] = useState<Holding | null | undefined>(undefined);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const isMounted = useRef(true);

	useEffect(() => {
		isMounted.current = true;
		return () => {
			isMounted.current = false;
		};
	}, []);

	const fetchHolding = useCallback(async () => {
		setIsLoading(true);
		try {
			const result = await apiService.getHolding();
			if (isMounted.current) setHolding(result);
		} catch (error) {
			console.error("Failed to fetch holding:", error);
			if (isMounted.current) setHolding(undefined);
		} finally {
			if (isMounted.current) setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		// noinspection JSIgnoredPromiseFromCall
		fetchHolding();
	}, [fetchHolding]);

	return (
		<HoldingContext.Provider value={{ holding, setHolding, isLoading, refetch: fetchHolding }}>
			{children}
		</HoldingContext.Provider>
	);
}

export function useHolding(): HoldingContextType {
	const context = useContext(HoldingContext);
	if (context === undefined) {
		throw new Error("useHolding must be used within a HoldingProvider");
	}
	return context;
}

export type { Holding };
