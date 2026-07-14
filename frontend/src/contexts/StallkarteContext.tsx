"use client";

import React, { createContext, useCallback, useContext, useEffect } from "react";
import { apiService } from "@/services/api";
import type { Stallkarte } from "@/services/domain/stallkarte";

interface StallkarteContextType {
	stallkarte: Stallkarte | null;
	isLoading: boolean;
	replace: (stallkarte: Stallkarte) => void;
	refetch: () => Promise<void>;
}

const StallkarteContext = createContext<StallkarteContextType | undefined>(undefined);

interface StallkarteProviderProps {
	stallkarteId: number;
	children: React.ReactNode;
}

export function StallkarteProvider({ children, stallkarteId }: StallkarteProviderProps) {
	const [isLoading, setIsLoading] = React.useState(true);
	const [stallkarte, setStallkarte] = React.useState<Stallkarte | null>(null);

	const fetchStallkarte = useCallback(async () => {
		setIsLoading(true);
		try {
			const fetchedStallkarte = await apiService.stallkarte.getStallkarte(stallkarteId);
			setStallkarte(fetchedStallkarte);
		} catch (error) {
			console.error(`Failed to fetch stallkarte with id ${stallkarteId}:`, error);
		} finally {
			setIsLoading(false);
		}
	}, [stallkarteId]);

	useEffect(() => {
		// noinspection JSIgnoredPromiseFromCall
		fetchStallkarte();
	}, [fetchStallkarte]);

	const replace = (newStallkarte: Stallkarte) => {
		setStallkarte(newStallkarte);
	};

	return (
		<StallkarteContext.Provider
			value={{ stallkarte, isLoading, replace, refetch: fetchStallkarte }}
		>
			{children}
		</StallkarteContext.Provider>
	);
}

// Only to be used in subcomponents of this layout
export function useStallkarte(): StallkarteContextType {
	const context = useContext(StallkarteContext);
	if (context === undefined) {
		throw new Error("useStallkarte must be used within a StallkarteProvider");
	}
	return context;
}
