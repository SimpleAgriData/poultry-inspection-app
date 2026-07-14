"use client";

import type React from "react";
import { createContext, useContext, useState } from "react";

export interface SetBackdropOptions {
	blur?: string;
	color?: string;
}

export interface BackdropOverlayContextType {
	setBackdrop: (options: SetBackdropOptions) => void;
	clearBackdrop: () => void;
}

const BackdropOverlay = createContext<BackdropOverlayContextType | undefined>(undefined);

export function BackdropProvider({ children }: { children: React.ReactNode }) {
	const [backdrop, setBackdrop] = useState<SetBackdropOptions | null>(null);

	const clearBackdrop = () => setBackdrop(null);

	const shouldShowBackdrop = backdrop && (backdrop.blur || backdrop.color);

	const styles = shouldShowBackdrop
		? {
				backgroundColor: backdrop.color,
				backdropFilter: backdrop.blur ? `blur(${backdrop.blur})` : "none",
			}
		: {};

	return (
		<BackdropOverlay.Provider value={{ setBackdrop: setBackdrop, clearBackdrop }}>
			{children}
			<div
				className={`fixed inset-0 transition-all duration-75
				${!shouldShowBackdrop ? "pointer-events-none" : ""}
				`}
				style={styles}
			/>
		</BackdropOverlay.Provider>
	);
}

export function useBackdrop(): BackdropOverlayContextType {
	const context = useContext(BackdropOverlay);
	if (context === undefined) {
		throw new Error("useBackdrop must be used within a BackdropProvider");
	}
	return context;
}
