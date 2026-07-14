"use client";

import { usePathname } from "next/dist/client/components/navigation";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";
import {
	MdAutorenew,
	MdHome,
	MdOutlineHome,
	MdOutlineSettings,
	MdOutlineViewCarousel,
	MdSettings,
	MdViewCarousel,
	MdWarning,
} from "react-icons/md";
import Ellipsis from "@/components/ellipsis";
import { InfoBanner } from "@/components/info-banner";
import { NavigationBar } from "@/components/navigation-bar";
import { AuthProvider, HoldingProvider, useHolding } from "@/contexts";
import { ApiProvider } from "@/contexts/ApiContext";
import { BackdropProvider } from "@/contexts/BackdropOverlay";
import { ModalProvider } from "@/contexts/ModalContext";
import { ShallowStallkartenProvider } from "@/contexts/ShallowStallkartenContext";
import type { ConnectionState } from "@/services/api/client";
import { apiService } from "@/services/api/service";
import { authService } from "@/services/auth";
import styles from "./app.module.css";

function RequireSignedInWrapper({ children }: { children: ReactNode }) {
	const [authenticated, setAuthenticated] = useState(false);

	useEffect(() => {
		const hasSavedCredentials = authService.hasSavedCredentials();
		setAuthenticated(hasSavedCredentials); // Optimistically set to true if credentials exist

		(async () => {
			const authenticated = await authService.initialize();
			setAuthenticated(authenticated);
		})();
	}, []);
	return (
		<>
			{authenticated ? (
				children
			) : (
				<div className="flex flex-col items-center justify-center h-dvh">
					<div className="w-80 mb-8 text-center space-y-4">
						<h1 className={"text-4xl"}>Authenticating...</h1>
						<p>Bitte warten Sie einen Moment.</p>
					</div>
				</div>
			)}
		</>
	);
}

function ConnectionStatusBanner() {
	const [connectionState, setConnectionState] = useState<ConnectionState>(
		apiService.client.connectionState.value,
	);
	const [previousState, setPreviousState] = useState<ConnectionState | null>(null);

	useEffect(() => {
		return apiService.client.connectionState.subscribe((state) => {
			setConnectionState((previousState) => {
				setPreviousState(previousState);
				return state;
			});
		}, true);
	}, []);

	const wasDisconnected = previousState === "disconnected";
	const isReconnecting = connectionState === "connecting" && wasDisconnected;
	const showBanner = connectionState === "disconnected" || isReconnecting;

	const icon = isReconnecting ? <MdAutorenew size={"1.5em"} /> : <MdWarning size={"1.5em"} />;
	const type = connectionState === "disconnected" ? "error" : "warning";

	return (
		<>
			{showBanner && (
				<div className={"sticky top-0 z-10 p-4 w-full max-w-md mx-auto"}>
					<InfoBanner icon={icon} align={"center"} type={type}>
						{connectionState === "disconnected" &&
							"Verbindung zum Server verloren. Bitte überprüfen Sie Ihre Internetverbindung."}
						{connectionState === "connecting" && (
							<span>
								Wiederverbinden mit dem Server
								<Ellipsis delayMs={350} fixedWidth={true} />
							</span>
						)}
					</InfoBanner>
				</div>
			)}
		</>
	);
}

function AppHeader() {
	return (
		<div>
			<div
				className={
					"bg-surface-container-low max-h-17.5 flex flex-row justify-center gutter-stable overflow-y-hidden"
				}
			>
				<div className={"flex flex-row justify-start gap-4 w-full max-w-md px-4"}>
					<div className={"h-full shrink-0 aspect-square"}>
						<Link href={"/overview"}>
							<Image
								src={"/siad-logo.png"}
								width={808}
								height={711}
								alt={"SiAD Logo"}
								className={"h-full py-2 object-scale-down"}
							/>
						</Link>
					</div>
					<h1
						className={"text-on-surface-container font-medium text-xl my-auto text-nowrap shrink-0"}
					>
						Simple Agri Data Stallkarte
					</h1>
				</div>
			</div>
			<div className={`absolute w-full h-1 z-1 ${styles.headerShadow}`}></div>
		</div>
	);
}

function AppLayoutWrapper({ children }: { children: ReactNode }) {
	const navItems = [
		{
			label: "Übersicht",
			href: "/overview",
			icon: <MdOutlineHome />,
			iconActive: <MdHome />,
		},
		{
			label: "Stallkarten",
			href: "/stallkarten",
			icon: <MdOutlineViewCarousel />,
			iconActive: <MdViewCarousel />,
		},
		{
			label: "Einstellungen",
			href: "/settings",
			icon: <MdOutlineSettings />,
			iconActive: <MdSettings />,
		},
	];
	const knownHrefs = navItems.map((item) => item.href);
	const router = useRouter();
	const currentPath = usePathname();

	useEffect(() => {
		if (!knownHrefs.includes(currentPath)) {
			switch (currentPath) {
				case "/":
					router.push("/stallkarten");
			}
		}
	}, [currentPath, router, knownHrefs]);

	const isKnownRoute = knownHrefs.includes(currentPath);

	return (
		<div className={"flex flex-col h-dvh"}>
			{isKnownRoute && <AppHeader />}
			<ConnectionStatusBanner />
			<div className={"flex-auto min-h-0 relative"}>{children}</div>
			{isKnownRoute && (
				<div className={"shrink-0 bottom-0"}>
					<NavigationBar items={navItems}></NavigationBar>
				</div>
			)}
		</div>
	);
}

function RedirectToOnboardingIfNoHolding({ children }: { children: ReactNode }) {
	const router = useRouter();
	const { holding } = useHolding();
	const path = usePathname();

	useEffect(() => {
		if (holding === null && !path.startsWith("/onboarding")) {
			router.push("/onboarding");
		}
	}, [holding, router, path]);

	return <>{children}</>;
}

function ProvidersWrapper({ children }: { children: ReactNode }) {
	return (
		<BackdropProvider>
			<AuthProvider>
				<ApiProvider>
					<ShallowStallkartenProvider>
						<HoldingProvider>
							<ModalProvider>{children}</ModalProvider>
						</HoldingProvider>
					</ShallowStallkartenProvider>
				</ApiProvider>
			</AuthProvider>
		</BackdropProvider>
	);
}

export default function App({ children }: { children: ReactNode }) {
	return (
		<ProvidersWrapper>
			<RedirectToOnboardingIfNoHolding>
				<RequireSignedInWrapper>
					<AppLayoutWrapper>{children}</AppLayoutWrapper>
				</RequireSignedInWrapper>
			</RedirectToOnboardingIfNoHolding>
		</ProvidersWrapper>
	);
}
