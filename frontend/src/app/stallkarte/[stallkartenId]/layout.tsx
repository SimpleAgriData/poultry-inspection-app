"use client";

import { useRouter } from "next/navigation";
import type React from "react";
import { use, useEffect } from "react";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import { useShallowStallkarten } from "@/contexts/ShallowStallkartenContext";
import { StallkarteProvider } from "@/contexts/StallkarteContext";

interface PageProps {
	children: React.ReactNode;
	params: Promise<{ stallkartenId: string }>;
}

export default function Layout({ children, params }: PageProps) {
	const router = useRouter();
	const { activeStallkarten, archivedStallkarten, isLoading } = useShallowStallkarten();
	const { stallkartenId: stallkarteIdString } = use(params);
	const stallkarteId = parseInt(stallkarteIdString, 10);

	const allStallkarten = [...activeStallkarten, ...archivedStallkarten];

	const stallkarte = allStallkarten.find((s) => s.id === stallkarteId) || null;

	useEffect(() => {
		if (!isLoading && !stallkarte) {
			router.push("/stallkarten");
		}
	}, [isLoading, stallkarte, router]);

	if (isLoading || !stallkarte) {
		return <GenericLoaderPlaceholder text={"Lade Stallkarte"} />;
	}

	return <StallkarteProvider stallkarteId={stallkarteId}>{children}</StallkarteProvider>;
}
