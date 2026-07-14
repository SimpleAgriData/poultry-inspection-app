"use client";

import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import SectionForm, { type SectionFormData } from "@/app/farm/[farmId]/section/section-form";
import SubPageLayout from "@/components/sub-page-layout";
import { useHolding } from "@/contexts";
import { apiService, type Farm } from "@/services/api";

interface NewBarnPageProps {
	params: Promise<{ farmId: string }>;
}

export default function NewBarnPage({ params }: NewBarnPageProps) {
	const { holding, refetch } = useHolding();
	const router = useRouter();

	const [farm, setFarm] = useState<Farm | null>(null);

	const { farmId: farmIdString } = use(params);
	const farmId = parseInt(farmIdString, 10);

	const onSubmit = async (data: SectionFormData) => {
		await apiService.addSection({
			farmId: farmId,
			name: data.name,
		});
		await refetch();

		router.push("/overview");
	};

	useEffect(() => {
		if (holding) {
			const farm = holding.farms.find((f) => f.id === farmId) || null;
			if (farm) {
				setFarm(farm);
			} else {
				router.replace("/overview");
			}
		} else {
			setFarm(null);
		}
	}, [holding, farmId, router]);

	if (!farm) {
		return (
			<SubPageLayout title="Neues Abteil" backLink="/overview">
				<div>Lade Daten...</div>
			</SubPageLayout>
		);
	}

	return (
		<SubPageLayout title="Neues Abteil" backLink="/overview">
			<SectionForm onSubmit={onSubmit} submitText={"Speichern"} farm={farm}></SectionForm>
		</SubPageLayout>
	);
}
