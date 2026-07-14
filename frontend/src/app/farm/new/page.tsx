"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import FarmForm, { type FarmFormData } from "@/app/farm/farm-form";
import SubPageLayout from "@/components/sub-page-layout";
import { useHolding } from "@/contexts";
import { apiService } from "@/services/api";

export default function NewFarmPage() {
	const { holding, refetch } = useHolding();
	const router = useRouter();

	useEffect(() => {
		if (holding === null) {
			router.push("/overview");
		}
	}, [holding, router]);

	const onSubmit = async (data: FarmFormData) => {
		if (!holding) {
			alert("Benutzer nicht authentifiziert.");
			return;
		}

		await apiService.addFarm({
			name: data.name,
			type: data.type,
			vvvoNumber: data.vvvoNumber,
			agriculturalHoldingId: holding.id,
		});
		await refetch();

		router.replace("/overview");
	};

	return (
		<SubPageLayout title="Neue Farm" backLink="/overview">
			<FarmForm onSubmit={onSubmit} submitText={"Speichern"}></FarmForm>
		</SubPageLayout>
	);
}
