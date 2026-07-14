"use client";

import type React from "react";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { authService, type User } from "@/services/auth";

export interface AuthContextType {
	user: User | null | undefined;
	setUser: (user: User | null) => void;
	isLoading: boolean;
	refetch: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
	children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
	const [user, setUser] = useState<User | null | undefined>(undefined);
	const [isLoading, setIsLoading] = useState<boolean>(true);
	const isMounted = useRef(true);

	useEffect(() => {
		isMounted.current = true;
		return () => {
			isMounted.current = false;
		};
	}, []);

	const fetchUserInfo = useCallback(async () => {
		setIsLoading(true);
		try {
			await authService.initialized;
			const result = await authService.getUserInfo();
			if (isMounted.current) setUser(result);
		} catch (error) {
			console.error("Failed to fetch user info:", error);
			if (isMounted.current) setUser(null);
		} finally {
			if (isMounted.current) setIsLoading(false);
		}
	}, []);

	useEffect(() => {
		// noinspection JSIgnoredPromiseFromCall
		fetchUserInfo();
	}, [fetchUserInfo]);

	return (
		<AuthContext.Provider
			value={{ user: user, setUser: setUser, isLoading, refetch: fetchUserInfo }}
		>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth(): AuthContextType {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within a AuthProvider");
	}
	return context;
}
