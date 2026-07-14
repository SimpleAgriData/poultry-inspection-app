"use client";

import { useEffect, useState } from "react";
import { calculateAnimalsBySectionUntilProductionDay } from "@/app/stallkarte/[stallkartenId]/transfer/animal-counts";
import { fatteningFarmOptions } from "@/app/stallkarte/farm-options";
import BasicForm from "@/components/basic-form";
import Input from "@/components/input";
import PageSection from "@/components/page-section";
import Select from "@/components/select";
import { useHolding } from "@/contexts";
import { useStallkarte } from "@/contexts/StallkarteContext";
import type { Awaitable } from "@/services/awaitable";
import { todayUTC } from "@/services/dates";
import { getProductionDayOfDate, type StallkarteFarm } from "@/services/domain/stallkarte";

export interface TransferFormData {
	transferDate: Date;
	selectedFatteningFarmId: number;
	animalsBySectionNumber: Record<number, number>;
}

export interface ReviseTransferFormData {
	animalsBySectionNumber: Record<number, number>;
}

type FormData = {
	"new-transfer": TransferFormData;
	"revise-transfer": ReviseTransferFormData;
};

export type TransferFormType = keyof FormData;

interface TransferFormProps<T extends TransferFormType> {
	type: T;
	initialData?: Partial<TransferFormData>;
	onSubmit: (data: FormData[T]) => Awaitable<void>;
	submitText: string;
}

export default function TransferForm<T extends TransferFormType>(props: TransferFormProps<T>) {
	const animalCountFormatter = new Intl.NumberFormat("de-DE");
	const { stallkarte } = useStallkarte();
	const { holding } = useHolding();

	const [assignedFatteningFarmId, setAssignedFatteningFarmId] = useState<number | null>(
		props.initialData?.selectedFatteningFarmId ?? null,
	);
	const [farm, setFarm] = useState<StallkarteFarm | null>(null);
	const [animalsBySectionNumber, setAnimalsBySectionNumber] = useState<Record<number, number>>(
		props.initialData?.animalsBySectionNumber ?? {},
	);
	const [transferDate, setTransferDate] = useState<Date | null>(
		props.initialData?.transferDate ?? todayUTC(),
	);

	useEffect(() => {
		if (!holding) return;
		const selectedFarm = holding.farms.find((f) => f.id === assignedFatteningFarmId) || null;
		if (!selectedFarm) {
			setFarm(null);
			return;
		}
		setFarm({
			id: selectedFarm.id,
			name: selectedFarm.name,
			type: selectedFarm.type,
			vvvoNumber: selectedFarm.vvvoNumber,
			sections: selectedFarm.sections.map((section, index) => ({
				id: section.id,
				number: index + 1, // The section number starts at 1, since it is used for user input and identification in the stallkarte state.
				name: section.name,
			})),
		});
	}, [holding, assignedFatteningFarmId]);

	if (!stallkarte || !holding) {
		return null;
	}

	const currentAnimalsBySectionNumber =
		transferDate !== null
			? calculateAnimalsBySectionUntilProductionDay(
					stallkarte,
					getProductionDayOfDate(stallkarte.state, transferDate),
				)
			: {};

	const totalAvailableAnimals = (farm?.sections ?? []).reduce((sum, section) => {
		return sum + (currentAnimalsBySectionNumber[section.number] ?? 0);
	}, 0);
	const totalSelectedAnimals = (farm?.sections ?? []).reduce((sum, section) => {
		return sum + (animalsBySectionNumber[section.number] ?? 0);
	}, 0);
	const exceedsAvailableAnimalsInTotal = totalSelectedAnimals > totalAvailableAnimals;

	const onFarmSelect = (id: number | null) => {
		setAssignedFatteningFarmId(id);
	};

	const onAnimalsBySectionChange = (sectionNumber: number, count: number | null) => {
		if (count === null) {
			setAnimalsBySectionNumber((prev) => {
				const updated = { ...prev };
				delete updated[sectionNumber];
				return updated;
			});
			return;
		}

		setAnimalsBySectionNumber((prev) => ({
			...prev,
			[sectionNumber]: count,
		}));
	};

	const isValid = () => {
		if (!farm) {
			return false;
		}
		if (transferDate === null) {
			return false;
		}
		if (exceedsAvailableAnimalsInTotal) {
			return false;
		}
		return farm.sections.every((section) => {
			const count = animalsBySectionNumber[section.number];
			return count !== undefined && count >= 0;
		});
	};

	const onSubmit = async () => {
		if (!farm || transferDate === null) {
			return;
		}

		switch (props.type) {
			case "new-transfer":
				await props.onSubmit({
					transferDate,
					selectedFatteningFarmId: farm.id,
					animalsBySectionNumber: animalsBySectionNumber,
				});
				break;
			case "revise-transfer":
				await props.onSubmit({
					animalsBySectionNumber: animalsBySectionNumber,
				} as FormData[T]);
				break;
		}
	};

	const farms = holding.farms.filter((f) => f.sections.length > 0);
	const rearingFarm = stallkarte.state.rearingFarm;
	const canEditGeneralInfo = props.type === "new-transfer";

	return (
		<BasicForm
			submitText={props.submitText}
			isDisabled={!isValid()}
			onSubmit={onSubmit}
			isReadOnly={stallkarte.state.isFinished}
		>
			<PageSection title={"Allgemeine Informationen"}>
				<Select
					label={"Zugewiesene Mastfarm"}
					value={assignedFatteningFarmId}
					onChange={onFarmSelect}
					options={fatteningFarmOptions(farms, rearingFarm?.id ?? null)}
					disabled={!canEditGeneralInfo}
					description={!canEditGeneralInfo ? "Die Mastfarm kann nicht geändert werden." : ""}
					required={true}
				/>
				<Input
					type={"date"}
					options={{
						max: todayUTC(),
					}}
					value={transferDate}
					onChange={setTransferDate}
					label={"Umstallungsdatum"}
					disabled={!canEditGeneralInfo}
					description={
						!canEditGeneralInfo ? "Das Umstallungsdatum kann nicht geändert werden." : ""
					}
					required={true}
				/>
			</PageSection>
			{farm && (
				<PageSection title={"Tierzahl pro Abteil"}>
					{exceedsAvailableAnimalsInTotal && (
						<div className="mb-3 rounded-md border border-error bg-error-container p-3 text-sm text-on-error-container">
							Die Summe der umgestallten Tiere darf den verfügbaren Bestand nach Verlusten nicht
							überschreiten ( {animalCountFormatter.format(totalAvailableAnimals)}).
						</div>
					)}
					{farm.sections.map((section) => (
						<div key={section.id} className="mb-4">
							<div className="mb-2 text-sm text-on-surface-variant">
								Aktueller Bestand vor Umstallung:{" "}
								{animalCountFormatter.format(currentAnimalsBySectionNumber[section.number] ?? 0)}
							</div>
							<Input
								type={"number"}
								options={{
									min: 0,
								}}
								label={section.name}
								value={animalsBySectionNumber[section.number] ?? null}
								onChange={(value) => onAnimalsBySectionChange(section.number, value)}
								placeholder={`Anzahl der Tiere in ${section.name}`}
								required={true}
							/>
						</div>
					))}
				</PageSection>
			)}
		</BasicForm>
	);
}
