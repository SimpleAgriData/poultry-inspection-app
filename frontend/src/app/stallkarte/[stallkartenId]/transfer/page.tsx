"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { calculateAnimalsBySectionUntilProductionDay } from "@/app/stallkarte/[stallkartenId]/transfer/animal-counts";
import TransferForm, {
	type TransferFormData,
} from "@/app/stallkarte/[stallkartenId]/transfer/transfer-form";
import GenericLoaderPlaceholder from "@/components/generic-loader-placeholder";
import SubPageLayout from "@/components/sub-page-layout";
import { useStallkarte } from "@/contexts/StallkarteContext";
import { apiService } from "@/services/api";
import { todayUTC } from "@/services/dates";
import { getProductionDayOfDate, type Stallkarte } from "@/services/domain/stallkarte";

const submitTransferFormData = async (
	stallkarte: Stallkarte,
	transferDate: Date,
	selectedFatteningFarmId: number,
	animalsBySectionNumber: Record<number, number>,
) => {
	const currentAssignedFatteningFarm = stallkarte.state.fatteningFarm;

	const needsFatteningFarmAssignment =
		!currentAssignedFatteningFarm || currentAssignedFatteningFarm.id !== selectedFatteningFarmId;

	if (needsFatteningFarmAssignment) {
		await apiService.stallkarte.runCommand("assign-fattening-farm", {
			stallkarteId: stallkarte.id,
			farmId: selectedFatteningFarmId,
		});
	}

	await apiService.stallkarte.runCommand("transfer-flock", {
		stallkarteId: stallkarte.id,
		transferDate: transferDate,
		animalsBySectionNumber: animalsBySectionNumber,
	});
};

export default function TransferPage() {
	const { stallkarte, refetch } = useStallkarte();
	const [didSubmit, setDidSubmit] = useState(false);
	const router = useRouter();

	const numberOfAnimalsBySectionNumber = useMemo(() => {
		if (!stallkarte) return {};
		const todayProductionDay = getProductionDayOfDate(stallkarte.state, todayUTC());
		return calculateAnimalsBySectionUntilProductionDay(stallkarte, todayProductionDay);
	}, [stallkarte]);

	useEffect(() => {
		if (!stallkarte) return;
		if (didSubmit) return;

		if (stallkarte.state.transfer) {
			router.replace(`/stallkarte/${stallkarte.id}/transfer/revise`);
		}
	}, [stallkarte, router, didSubmit]);

	const onSubmit = async (data: TransferFormData) => {
		if (!stallkarte) return;
		await submitTransferFormData(
			stallkarte,
			data.transferDate,
			data.selectedFatteningFarmId,
			data.animalsBySectionNumber,
		);
		setDidSubmit(true);

		await refetch();

		router.replace(`/stallkarte/${stallkarte.id}/check/fattening`);
	};

	if (!stallkarte) {
		return (
			<SubPageLayout title={"Umstallen"}>
				<GenericLoaderPlaceholder text={"Lade Stallkarte"} />
			</SubPageLayout>
		);
	}

	return (
		<SubPageLayout title={"Umstallen"} backLink={`/stallkarte/${stallkarte.id}`}>
			<TransferForm
				type={"new-transfer"}
				onSubmit={onSubmit}
				submitText={"Umstallen"}
				initialData={{
					selectedFatteningFarmId: stallkarte.state.fatteningFarm?.id,
					animalsBySectionNumber: numberOfAnimalsBySectionNumber,
				}}
			/>
		</SubPageLayout>
	);
}
