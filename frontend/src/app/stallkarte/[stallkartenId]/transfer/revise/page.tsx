"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import TransferForm, {
	type ReviseTransferFormData,
} from "@/app/stallkarte/[stallkartenId]/transfer/transfer-form";
import SubPageLayout from "@/components/sub-page-layout";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";

export default function ReviseTransferPage() {
	const { stallkarte, refetch } = useStallkarte();
	const router = useRouter();

	useEffect(() => {
		if (!stallkarte) return;
		if (!stallkarte.state.transfer || !stallkarte.state.fatteningFarm) {
			router.replace(`/stallkarte/${stallkarte.id}/transfer`);
		}
	}, [stallkarte, router]);

	if (!stallkarte) {
		return null;
	}
	if (!stallkarte.state.transfer || !stallkarte.state.fatteningFarm) {
		return null;
	}

	const onSubmit = async (data: ReviseTransferFormData) => {
		await apiService.stallkarte.runCommand("revise-transfer-details", {
			stallkarteId: stallkarte.id,
			animalsBySectionNumber: data.animalsBySectionNumber,
		});

		await refetch();

		router.push(`/stallkarte/${stallkarte.id}`);
	};

	return (
		<SubPageLayout title={"Umstallung überarbeiten"} backLink={`/stallkarte/${stallkarte.id}`}>
			<TransferForm
				type={"revise-transfer"}
				onSubmit={onSubmit}
				submitText={"Speichern"}
				initialData={{
					animalsBySectionNumber: stallkarte.state.transfer.animalsBySectionNumber,
					transferDate: stallkarte.state.transfer.date,
					selectedFatteningFarmId: stallkarte.state.fatteningFarm.id,
				}}
			/>
		</SubPageLayout>
	);
}
